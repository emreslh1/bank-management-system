"""
Customer Panel Module
Contains the customer dashboard interface.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QScrollArea, QSizePolicy,
    QDialog, QGridLayout, QLineEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ..auth.auth_manager import auth_manager
from ..database.db_manager import db_manager


class CustomerPanel(QFrame):
    """
    Customer dashboard panel with sidebar navigation.
    """
    
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("customerPanel")
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        layout.addWidget(self.sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        
        # Create content pages
        self.dashboard_page = CustomerDashboardPage()
        self.transactions_page = TransactionsPage()
        self.settings_page = CustomerSettingsPage()
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.transactions_page)
        self.content_stack.addWidget(self.settings_page)
        
        layout.addWidget(self.content_stack, 1)
        
        # Set minimum size
        self.setMinimumSize(900, 600)
    
    def create_sidebar(self):
        """Create the sidebar navigation."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1a237e;
                min-width: 250px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Bank Title
        title = QLabel("🏦 SecureBank")
        title.setObjectName("sidebarTitle")
        title.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 20px;
        """)
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setFixedHeight(50)
        layout.addWidget(title)
        
        # Customer badge
        customer_badge = QLabel("👤 Customer")
        customer_badge.setStyleSheet("""
            color: #00bcd4;
            font-size: 12px;
            padding: 0 20px 10px 20px;
        """)
        customer_badge.setFixedHeight(25)
        layout.addWidget(customer_badge)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Dashboard button
        self.dashboard_btn = QPushButton("📊 My Account")
        self.dashboard_btn.setObjectName("sidebarButton")
        self.dashboard_btn.setCheckable(True)
        self.dashboard_btn.setChecked(True)
        self.dashboard_btn.setFixedHeight(45)
        self.dashboard_btn.setStyleSheet(self.get_sidebar_button_style())
        self.dashboard_btn.clicked.connect(lambda: self.switch_page(0))
        layout.addWidget(self.dashboard_btn)
        self.nav_buttons.append(self.dashboard_btn)
        
        # Transactions button
        self.transactions_btn = QPushButton("📜 Transactions")
        self.transactions_btn.setObjectName("sidebarButton")
        self.transactions_btn.setCheckable(True)
        self.transactions_btn.setFixedHeight(45)
        self.transactions_btn.setStyleSheet(self.get_sidebar_button_style())
        self.transactions_btn.clicked.connect(lambda: self.switch_page(1))
        layout.addWidget(self.transactions_btn)
        self.nav_buttons.append(self.transactions_btn)
        
        # Settings button
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setObjectName("sidebarButton")
        self.settings_btn.setCheckable(True)
        self.settings_btn.setFixedHeight(45)
        self.settings_btn.setStyleSheet(self.get_sidebar_button_style())
        self.settings_btn.clicked.connect(lambda: self.switch_page(2))
        layout.addWidget(self.settings_btn)
        self.nav_buttons.append(self.settings_btn)
        
        layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setObjectName("sidebarButton")
        logout_btn.setFixedHeight(45)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ff4081;
                text-align: left;
                padding: 15px 20px;
                border-radius: 0;
                border-left: 4px solid transparent;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 64, 129, 0.2);
            }
        """)
        logout_btn.clicked.connect(self.on_logout)
        layout.addWidget(logout_btn)
        
        return sidebar
    
    def get_sidebar_button_style(self):
        """Get the style for sidebar buttons."""
        return """
            QPushButton {
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 15px 20px;
                border-radius: 0;
                border-left: 4px solid transparent;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.15);
                border-left-color: #00bcd4;
            }
        """
    
    def switch_page(self, index):
        """Switch to a different content page."""
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Switch content
        self.content_stack.setCurrentIndex(index)
        
        # Refresh data when switching pages
        if index == 0:
            self.dashboard_page.refresh_data()
        elif index == 1:
            self.transactions_page.refresh_data()
    
    def on_logout(self):
        """Handle logout button click."""
        reply = QMessageBox.question(
            self,
            'Confirm Logout',
            'Are you sure you want to logout?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            auth_manager.logout()
            self.logout_requested.emit()


class CustomerDashboardPage(QWidget):
    """Customer dashboard overview page with IBAN and balance display."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header with fixed height
        header = QLabel("My Account")
        header.setObjectName("title")
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setFixedHeight(35)
        main_layout.addWidget(header)
        
        # Welcome message with fixed height
        self.welcome_label = QLabel()
        self.welcome_label.setObjectName("subtitle")
        welcome_font = QFont("Segoe UI", 14)
        self.welcome_label.setFont(welcome_font)
        self.welcome_label.setFixedHeight(25)
        main_layout.addWidget(self.welcome_label)
        
        main_layout.addSpacing(10)
        
        # Account Card with stylish IBAN display
        self.account_card = QFrame()
        self.account_card.setFixedHeight(200)
        self.account_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a237e, stop:1 #534bae);
                border-radius: 16px;
            }
        """)
        
        card_layout = QVBoxLayout(self.account_card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(25, 20, 25, 20)
        
        # Account type label
        account_type = QLabel("💳 Savings Account")
        account_type.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 13px;")
        account_type.setFixedHeight(20)
        card_layout.addWidget(account_type)
        
        # IBAN label
        iban_title = QLabel("IBAN")
        iban_title.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 11px;")
        iban_title.setFixedHeight(15)
        card_layout.addWidget(iban_title)
        
        # IBAN value - stylish display
        self.iban_label = QLabel("GB00 XXXX 0000 0000 0000 00")
        self.iban_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 2px;
            font-family: 'Consolas', 'Monaco', monospace;
        """)
        self.iban_label.setFixedHeight(30)
        card_layout.addWidget(self.iban_label)
        
        card_layout.addSpacing(15)
        
        # Balance section
        balance_title = QLabel("Available Balance")
        balance_title.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 11px;")
        balance_title.setFixedHeight(15)
        card_layout.addWidget(balance_title)
        
        # Balance value
        self.balance_label = QLabel("$0.00")
        self.balance_label.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: bold;
        """)
        self.balance_label.setFixedHeight(45)
        card_layout.addWidget(self.balance_label)
        
        main_layout.addWidget(self.account_card)
        
        # Quick Actions section
        actions_label = QLabel("Quick Actions")
        actions_label.setObjectName("header")
        actions_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        actions_label.setFont(actions_font)
        actions_label.setFixedHeight(25)
        main_layout.addWidget(actions_label)
        
        # Action buttons with fixed sizes
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        # Deposit button
        self.deposit_btn = QPushButton("💰 Deposit")
        self.deposit_btn.setFixedSize(150, 55)
        self.deposit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.deposit_btn.clicked.connect(self.show_deposit_dialog)
        actions_layout.addWidget(self.deposit_btn)
        
        # Withdraw button
        self.withdraw_btn = QPushButton("💸 Withdraw")
        self.withdraw_btn.setFixedSize(150, 55)
        self.withdraw_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        self.withdraw_btn.clicked.connect(self.show_withdraw_dialog)
        actions_layout.addWidget(self.withdraw_btn)
        
        # Transfer button
        self.transfer_btn = QPushButton("↔️ Transfer")
        self.transfer_btn.setFixedSize(150, 55)
        self.transfer_btn.setStyleSheet("""
            QPushButton {
                background-color: #00bcd4;
                color: white;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00acc1;
            }
        """)
        self.transfer_btn.clicked.connect(self.show_transfer_dialog)
        actions_layout.addWidget(self.transfer_btn)
        
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)
        
        main_layout.addStretch()
        
        # Load initial data
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh account data from database."""
        user = auth_manager.current_user
        if user:
            self.welcome_label.setText(f"Welcome back, {user.get('full_name', user.get('username'))}!")
            
            # Get account info
            account = db_manager.get_user_account(user['id'])
            if account:
                # Update IBAN display
                iban = account.get('iban', '')
                formatted_iban = db_manager.format_iban(iban) if iban else "N/A"
                self.iban_label.setText(formatted_iban)
                
                # Update balance display
                balance = account.get('balance', 0.0)
                self.balance_label.setText(f"${balance:,.2f}")
    
    def show_deposit_dialog(self):
        """Show deposit dialog."""
        dialog = DepositDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount = dialog.get_amount()
            if amount > 0:
                user = auth_manager.current_user
                if user:
                    success, message = db_manager.deposit(user['id'], amount)
                    if success:
                        QMessageBox.information(self, "Success", f"Deposited ${amount:,.2f} successfully!")
                        self.refresh_data()
                    else:
                        QMessageBox.warning(self, "Error", message)
    
    def show_withdraw_dialog(self):
        """Show withdraw dialog."""
        dialog = WithdrawDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount = dialog.get_amount()
            if amount > 0:
                user = auth_manager.current_user
                if user:
                    success, message = db_manager.withdraw(user['id'], amount)
                    if success:
                        QMessageBox.information(self, "Success", f"Withdrew ${amount:,.2f} successfully!")
                        self.refresh_data()
                    else:
                        QMessageBox.warning(self, "Error", message)
    
    def show_transfer_dialog(self):
        """Show transfer dialog."""
        dialog = TransferDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            iban, amount = dialog.get_transfer_info()
            if iban and amount > 0:
                user = auth_manager.current_user
                if user:
                    success, message = db_manager.transfer_money(user['id'], iban, amount)
                    if success:
                        QMessageBox.information(self, "Success", f"Transferred ${amount:,.2f} successfully!")
                        self.refresh_data()
                    else:
                        QMessageBox.warning(self, "Error", message)


class TransactionsPage(QWidget):
    """Customer transactions history page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Transaction History")
        header.setObjectName("title")
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setFixedHeight(35)
        layout.addWidget(header)
        
        # Info text
        info = QLabel("View your recent transactions and account activity")
        info.setObjectName("subtitle")
        info.setFixedHeight(20)
        layout.addWidget(info)
        
        layout.addSpacing(10)
        
        # Transactions table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Date", "Type", "Description", "Amount"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #1a237e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1a237e;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFixedSize(120, 40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a237e;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #534bae;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
    
    def refresh_data(self):
        """Refresh transaction data."""
        user = auth_manager.current_user
        if user:
            transactions = db_manager.get_transactions(user['id'])
            
            self.table.setRowCount(len(transactions))
            
            for row, txn in enumerate(transactions):
                # Date
                timestamp = txn.get('timestamp', '')
                date_str = timestamp[:16] if timestamp else ""
                self.table.setItem(row, 0, QTableWidgetItem(date_str))
                
                # Type with color
                txn_type = txn.get('transaction_type', '').upper()
                type_item = QTableWidgetItem(txn_type)
                if txn_type == 'CREDIT':
                    type_item.setForeground(QColor('#4caf50'))
                else:
                    type_item.setForeground(QColor('#f44336'))
                self.table.setItem(row, 1, type_item)
                
                # Description
                self.table.setItem(row, 2, QTableWidgetItem(txn.get('description', '')))
                
                # Amount with color
                amount = txn.get('amount', 0)
                amount_str = f"+${amount:,.2f}" if txn_type == 'CREDIT' else f"-${amount:,.2f}"
                amount_item = QTableWidgetItem(amount_str)
                if txn_type == 'CREDIT':
                    amount_item.setForeground(QColor('#4caf50'))
                else:
                    amount_item.setForeground(QColor('#f44336'))
                self.table.setItem(row, 3, amount_item)
            
            if not transactions:
                self.table.setRowCount(1)
                no_data = QTableWidgetItem("No transactions yet")
                no_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setSpan(0, 0, 1, 4)
                self.table.setItem(0, 0, no_data)


class CustomerSettingsPage(QWidget):
    """Customer settings page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Account Settings")
        header.setObjectName("title")
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setFixedHeight(35)
        layout.addWidget(header)
        
        # Settings info card
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        info_layout = QGridLayout(info_frame)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(25, 20, 25, 20)
        
        # Fixed label width
        label_width = 120
        value_width = 300
        
        row = 0
        user = auth_manager.current_user
        if user:
            # Username
            username_label = QLabel("Username:")
            username_label.setStyleSheet("font-weight: bold; color: #1a237e;")
            username_label.setFixedWidth(label_width)
            info_layout.addWidget(username_label, row, 0)
            
            username_value = QLabel(user.get('username', ''))
            username_value.setStyleSheet("color: #424242;")
            username_value.setFixedWidth(value_width)
            info_layout.addWidget(username_value, row, 1)
            row += 1
            
            # Full Name
            name_label = QLabel("Full Name:")
            name_label.setStyleSheet("font-weight: bold; color: #1a237e;")
            name_label.setFixedWidth(label_width)
            info_layout.addWidget(name_label, row, 0)
            
            name_value = QLabel(user.get('full_name', ''))
            name_value.setStyleSheet("color: #424242;")
            name_value.setFixedWidth(value_width)
            info_layout.addWidget(name_value, row, 1)
            row += 1
            
            # Email
            email_label = QLabel("Email:")
            email_label.setStyleSheet("font-weight: bold; color: #1a237e;")
            email_label.setFixedWidth(label_width)
            info_layout.addWidget(email_label, row, 0)
            
            email_value = QLabel(user.get('email', ''))
            email_value.setStyleSheet("color: #424242;")
            email_value.setFixedWidth(value_width)
            info_layout.addWidget(email_value, row, 1)
            row += 1
            
            # Account Type
            type_label = QLabel("Account Type:")
            type_label.setStyleSheet("font-weight: bold; color: #1a237e;")
            type_label.setFixedWidth(label_width)
            info_layout.addWidget(type_label, row, 0)
            
            type_value = QLabel("Savings Account")
            type_value.setStyleSheet("color: #424242;")
            type_value.setFixedWidth(value_width)
            info_layout.addWidget(type_value, row, 1)
            row += 1
            
            # IBAN
            account = db_manager.get_user_account(user['id'])
            if account:
                iban_label = QLabel("IBAN:")
                iban_label.setStyleSheet("font-weight: bold; color: #1a237e;")
                iban_label.setFixedWidth(label_width)
                info_layout.addWidget(iban_label, row, 0)
                
                formatted_iban = db_manager.format_iban(account.get('iban', ''))
                iban_value = QLabel(formatted_iban)
                iban_value.setStyleSheet("color: #424242; font-family: monospace; letter-spacing: 1px;")
                iban_value.setFixedWidth(value_width)
                info_layout.addWidget(iban_value, row, 1)
        
        layout.addWidget(info_frame)
        
        # Customer info
        customer_info = QLabel(
            "ℹ️ As a Customer, you can view your account balance, "
            "make deposits and withdrawals, and view your transaction history."
        )
        customer_info.setWordWrap(True)
        customer_info.setStyleSheet("color: #757575; padding: 10px;")
        layout.addWidget(customer_info)
        
        layout.addStretch()


class DepositDialog(QDialog):
    """Dialog for depositing money."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Deposit Money")
        self.setFixedSize(350, 180)
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Amount label
        amount_label = QLabel("Amount ($):")
        amount_label.setStyleSheet("font-weight: bold; color: #1a237e;")
        layout.addWidget(amount_label, 0, 0)
        
        # Amount input
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$ ")
        self.amount_input.setFixedHeight(35)
        self.amount_input.setFixedWidth(200)
        layout.addWidget(self.amount_input, 0, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        deposit_btn = QPushButton("Deposit")
        deposit_btn.setFixedSize(100, 35)
        deposit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        deposit_btn.clicked.connect(self.accept)
        btn_layout.addWidget(deposit_btn)
        
        layout.addLayout(btn_layout, 1, 0, 1, 2)
    
    def get_amount(self):
        return self.amount_input.value()


class WithdrawDialog(QDialog):
    """Dialog for withdrawing money."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Withdraw Money")
        self.setFixedSize(350, 180)
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Amount label
        amount_label = QLabel("Amount ($):")
        amount_label.setStyleSheet("font-weight: bold; color: #1a237e;")
        layout.addWidget(amount_label, 0, 0)
        
        # Amount input
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$ ")
        self.amount_input.setFixedHeight(35)
        self.amount_input.setFixedWidth(200)
        layout.addWidget(self.amount_input, 0, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        withdraw_btn = QPushButton("Withdraw")
        withdraw_btn.setFixedSize(100, 35)
        withdraw_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        withdraw_btn.clicked.connect(self.accept)
        btn_layout.addWidget(withdraw_btn)
        
        layout.addLayout(btn_layout, 1, 0, 1, 2)
    
    def get_amount(self):
        return self.amount_input.value()


class TransferDialog(QDialog):
    """Dialog for transferring money."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transfer Money")
        self.setFixedSize(400, 220)
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # IBAN label
        iban_label = QLabel("Destination IBAN:")
        iban_label.setStyleSheet("font-weight: bold; color: #1a237e;")
        layout.addWidget(iban_label, 0, 0)
        
        # IBAN input
        self.iban_input = QLineEdit()
        self.iban_input.setPlaceholderText("GB00 XXXX 0000 0000 0000 00")
        self.iban_input.setFixedHeight(35)
        self.iban_input.setFixedWidth(280)
        layout.addWidget(self.iban_input, 0, 1)
        
        # Amount label
        amount_label = QLabel("Amount ($):")
        amount_label.setStyleSheet("font-weight: bold; color: #1a237e;")
        layout.addWidget(amount_label, 1, 0)
        
        # Amount input
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$ ")
        self.amount_input.setFixedHeight(35)
        self.amount_input.setFixedWidth(280)
        layout.addWidget(self.amount_input, 1, 1)
        
        # Info label
        info_label = QLabel("Enter the recipient's IBAN to transfer funds.")
        info_label.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(info_label, 2, 0, 1, 2)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        transfer_btn = QPushButton("Transfer")
        transfer_btn.setFixedSize(100, 35)
        transfer_btn.setStyleSheet("""
            QPushButton {
                background-color: #00bcd4;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00acc1;
            }
        """)
        transfer_btn.clicked.connect(self.accept)
        btn_layout.addWidget(transfer_btn)
        
        layout.addLayout(btn_layout, 3, 0, 1, 2)
    
    def get_transfer_info(self):
        return self.iban_input.text().strip(), self.amount_input.value()
