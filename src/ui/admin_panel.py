"""
Admin Panel Module
Contains the admin dashboard interface with customer management and IBAN transfers.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QSizePolicy, QSpacerItem, QScrollArea,
    QDialog, QGridLayout, QLineEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ..auth.auth_manager import auth_manager
from ..database.db_manager import db_manager


class AdminPanel(QFrame):
    """
    Admin dashboard panel with sidebar navigation.
    """
    
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("adminPanel")
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
        self.dashboard_page = AdminDashboardPage()
        self.customers_page = CustomersPage()
        self.settings_page = AdminSettingsPage()
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.customers_page)
        self.content_stack.addWidget(self.settings_page)
        
        layout.addWidget(self.content_stack, 1)
        
        # Set minimum size
        self.setMinimumSize(900, 600)
    
    def create_sidebar(self):
        """Create the sidebar navigation."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Bank Title
        title = QLabel("🏦 SecureBank")
        title.setObjectName("sidebarTitle")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 20px;")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setFixedHeight(50)
        layout.addWidget(title)
        
        # Admin badge
        admin_badge = QLabel("👤 Administrator")
        admin_badge.setStyleSheet("color: #00bcd4; font-size: 12px; padding: 0 20px 10px 20px;")
        admin_badge.setFixedHeight(25)
        layout.addWidget(admin_badge)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Dashboard button
        self.dashboard_btn = QPushButton("📊 Dashboard")
        self.dashboard_btn.setObjectName("sidebarButton")
        self.dashboard_btn.setCheckable(True)
        self.dashboard_btn.setChecked(True)
        self.dashboard_btn.setFixedHeight(45)
        self.dashboard_btn.clicked.connect(lambda: self.switch_page(0))
        layout.addWidget(self.dashboard_btn)
        self.nav_buttons.append(self.dashboard_btn)
        
        # Customers button
        self.customers_btn = QPushButton("👥 Customers")
        self.customers_btn.setObjectName("sidebarButton")
        self.customers_btn.setCheckable(True)
        self.customers_btn.setFixedHeight(45)
        self.customers_btn.clicked.connect(lambda: self.switch_page(1))
        layout.addWidget(self.customers_btn)
        self.nav_buttons.append(self.customers_btn)
        
        # Settings button
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setObjectName("sidebarButton")
        self.settings_btn.setCheckable(True)
        self.settings_btn.setFixedHeight(45)
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
    
    def switch_page(self, index):
        """Switch to a different content page."""
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Switch content
        self.content_stack.setCurrentIndex(index)
        
        # Refresh data if needed
        if index == 0:  # Dashboard
            self.dashboard_page.refresh_stats()
        elif index == 1:  # Customers page
            self.customers_page.refresh_data()
    
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


class AdminDashboardPage(QWidget):
    """Admin dashboard overview page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Admin Dashboard")
        header.setObjectName("title")
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setFixedHeight(35)
        layout.addWidget(header)
        
        # Welcome message
        self.welcome_label = QLabel()
        self.welcome_label.setObjectName("subtitle")
        welcome_font = QFont("Segoe UI", 14)
        self.welcome_label.setFont(welcome_font)
        self.welcome_label.setFixedHeight(25)
        layout.addWidget(self.welcome_label)
        
        layout.addSpacing(20)
        
        # Stats cards container
        self.stats_layout = QHBoxLayout()
        
        # Create stat cards
        self.customers_card = self.create_stat_card("👥 Total Customers", "0", "Registered customer accounts")
        self.stats_layout.addWidget(self.customers_card)
        
        self.balance_card = self.create_stat_card("💰 Total Balance", "$0.00", "Combined account balance")
        self.stats_layout.addWidget(self.balance_card)
        
        self.accounts_card = self.create_stat_card("💳 Total Accounts", "0", "Active bank accounts")
        self.stats_layout.addWidget(self.accounts_card)
        
        layout.addLayout(self.stats_layout)
        
        layout.addStretch()
        
        # Load initial data
        self.refresh_stats()
    
    def create_stat_card(self, title, value, subtitle):
        """Create a statistics card widget."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 20px;
                min-width: 200px;
            }
        """)
        card.setFixedSize(220, 120)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #757575; font-size: 12px;")
        title_label.setFixedHeight(18)
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #1a237e; font-size: 28px; font-weight: bold;")
        value_label.setFixedHeight(35)
        card_layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #9e9e9e; font-size: 11px;")
        subtitle_label.setFixedHeight(15)
        card_layout.addWidget(subtitle_label)
        
        # Store value label for updating
        card.value_label = value_label
        
        return card
    
    def refresh_stats(self):
        """Refresh dashboard statistics."""
        user = auth_manager.current_user
        if user:
            self.welcome_label.setText(f"Welcome back, {user.get('full_name', user.get('username'))}!")
        
        # Get customer stats
        customers = db_manager.get_all_customers_with_accounts()
        total_customers = len(customers)
        total_balance = sum(c.get('balance', 0) or 0 for c in customers)
        
        # Update cards
        self.customers_card.value_label.setText(str(total_customers))
        self.balance_card.value_label.setText(f"${total_balance:,.2f}")
        self.accounts_card.value_label.setText(str(total_customers))


class CustomersPage(QWidget):
    """Customer management page with IBAN display and transfer functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header with fixed height
        header_layout = QHBoxLayout()
        
        header = QLabel("Customer Management")
        header.setObjectName("title")
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setFixedHeight(35)
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Transfer button
        transfer_btn = QPushButton("💸 Transfer Money")
        transfer_btn.setFixedSize(150, 40)
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
        transfer_btn.clicked.connect(self.show_transfer_dialog)
        header_layout.addWidget(transfer_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFixedSize(100, 40)
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
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Customers table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Username", "Full Name", "Email", "IBAN", "Balance", "Actions"
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
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1a237e;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Load initial data
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh the customers table data."""
        customers = db_manager.get_all_customers_with_accounts()
        
        self.table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(customer.get('username', '')))
            self.table.setItem(row, 1, QTableWidgetItem(customer.get('full_name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(customer.get('email', '')))
            
            # Format IBAN
            iban = customer.get('iban', '')
            formatted_iban = db_manager.format_iban(iban) if iban else "N/A"
            iban_item = QTableWidgetItem(formatted_iban)
            iban_item.setFont(QFont("Consolas", 9))
            self.table.setItem(row, 3, iban_item)
            
            # Balance
            balance = customer.get('balance', 0) or 0
            balance_item = QTableWidgetItem(f"${balance:,.2f}")
            if balance > 0:
                balance_item.setForeground(QColor('#4caf50'))
            self.table.setItem(row, 4, balance_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setSpacing(5)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(60, 28)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196f3;
                    color: white;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976d2;
                }
            """)
            edit_btn.clicked.connect(lambda checked, c=customer: self.edit_customer(c))
            actions_layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(60, 28)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            delete_btn.clicked.connect(lambda checked, c=customer: self.delete_customer(c))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 5, actions_widget)
    
    def edit_customer(self, customer):
        """Edit customer information."""
        dialog = EditCustomerDialog(customer, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name, new_email = dialog.get_values()
            success, message = db_manager.update_customer(
                customer['id'], 
                full_name=new_name if new_name else None,
                email=new_email if new_email else None
            )
            if success:
                QMessageBox.information(self, "Success", "Customer updated successfully!")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def delete_customer(self, customer):
        """Delete a customer."""
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f"Are you sure you want to delete customer '{customer.get('username')}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = db_manager.delete_customer(customer['id'])
            if success:
                QMessageBox.information(self, "Success", "Customer deleted successfully!")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def show_transfer_dialog(self):
        """Show transfer money dialog."""
        dialog = AdminTransferDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            iban, amount = dialog.get_transfer_info()
            if iban and amount > 0:
                # Admin transfers from their account
                success, message = db_manager.transfer_money(1, iban, amount)  # Admin ID is 1
                if success:
                    QMessageBox.information(self, "Success", f"Transferred ${amount:,.2f} successfully!")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", message)


class AdminTransferDialog(QDialog):
    """Dialog for admin to transfer money using IBAN."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transfer Money")
        self.setFixedSize(450, 200)
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Title
        title = QLabel("Transfer Money to Customer")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a237e;")
        layout.addWidget(title, 0, 0, 1, 2)
        
        # IBAN label
        iban_label = QLabel("Destination IBAN:")
        iban_label.setStyleSheet("font-weight: bold; color: #1a237e;")
        layout.addWidget(iban_label, 1, 0)
        
        # IBAN input
        self.iban_input = QLineEdit()
        self.iban_input.setPlaceholderText("GB00 XXXX 0000 0000 0000 00")
        self.iban_input.setFixedHeight(35)
        self.iban_input.setFixedWidth(300)
        layout.addWidget(self.iban_input, 1, 1)
        
        # Amount label
        amount_label = QLabel("Amount ($):")
        amount_label.setStyleSheet("font-weight: bold; color: #1a237e;")
        layout.addWidget(amount_label, 2, 0)
        
        # Amount input
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 10000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$ ")
        self.amount_input.setFixedHeight(35)
        self.amount_input.setFixedWidth(300)
        layout.addWidget(self.amount_input, 2, 1)
        
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


class EditCustomerDialog(QDialog):
    """Dialog for editing customer information."""
    
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Edit Customer")
        self.setFixedSize(350, 200)
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Full Name
        name_label = QLabel("Full Name:")
        name_label.setStyleSheet("font-weight: bold; color: #1a237e;")
        layout.addWidget(name_label, 0, 0)
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.customer.get('full_name', ''))
        self.name_input.setFixedHeight(35)
        self.name_input.setFixedWidth(200)
        layout.addWidget(self.name_input, 0, 1)
        
        # Email
        email_label = QLabel("Email:")
        email_label.setStyleSheet("font-weight: bold; color: #1a237e;")
        layout.addWidget(email_label, 1, 0)
        
        self.email_input = QLineEdit()
        self.email_input.setText(self.customer.get('email', ''))
        self.email_input.setFixedHeight(35)
        self.email_input.setFixedWidth(200)
        layout.addWidget(self.email_input, 1, 1)
        
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
        
        save_btn = QPushButton("Save")
        save_btn.setFixedSize(100, 35)
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout, 2, 0, 1, 2)
    
    def get_values(self):
        return self.name_input.text().strip(), self.email_input.text().strip()


class AdminSettingsPage(QWidget):
    """Admin settings page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Settings")
        header.setObjectName("title")
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setFixedHeight(35)
        layout.addWidget(header)
        
        # Settings info
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
        
        label_width = 100
        value_width = 300
        
        row = 0
        user = auth_manager.current_user
        if user:
            info_items = [
                ("Username:", user.get('username', '')),
                ("Full Name:", user.get('full_name', '')),
                ("Email:", user.get('email', '')),
                ("Role:", user.get('role', '').capitalize()),
            ]
            
            for label_text, value_text in info_items:
                label = QLabel(label_text)
                label.setStyleSheet("font-weight: bold; color: #1a237e;")
                label.setFixedWidth(label_width)
                info_layout.addWidget(label, row, 0)
                
                value = QLabel(value_text)
                value.setStyleSheet("color: #424242;")
                value.setFixedWidth(value_width)
                info_layout.addWidget(value, row, 1)
                row += 1
        
        layout.addWidget(info_frame)
        
        # Admin info
        admin_info = QLabel(
            "ℹ️ As an Administrator, you have full access to manage customers, "
            "view account information, transfer money via IBAN, and configure system settings."
        )
        admin_info.setWordWrap(True)
        admin_info.setStyleSheet("color: #757575; padding: 10px;")
        layout.addWidget(admin_info)
        
        layout.addStretch()
