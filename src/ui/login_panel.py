"""
Login Panel Module
Contains the login and registration interface with tabbed navigation.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QFrame, QMessageBox, QSizePolicy,
    QGridLayout, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..auth.auth_manager import auth_manager


class LoginPanel(QFrame):
    """
    Main login panel with tabbed interface for login and registration.
    """
    
    # Signal emitted when login is successful
    login_successful = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("loginCard")
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Bank Logo/Title
        logo_label = QLabel("🏦 SecureBank")
        logo_label.setObjectName("bankLogo")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        logo_label.setFont(logo_font)
        logo_label.setFixedHeight(50)
        layout.addWidget(logo_label)
        
        # Welcome text
        welcome_label = QLabel("Welcome to Your Digital Bank")
        welcome_label.setObjectName("welcomeText")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_font = QFont("Segoe UI", 16)
        welcome_label.setFont(welcome_font)
        welcome_label.setFixedHeight(25)
        layout.addWidget(welcome_label)
        
        # Subtitle
        subtitle_label = QLabel("Secure, Fast, and Reliable Banking")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFixedHeight(20)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(20)
        
        # Tab Widget for Login/Register
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # Create tabs
        self.login_tab = LoginTab()
        self.register_tab = RegisterTab()
        
        self.tab_widget.addTab(self.login_tab, "🔐 Login")
        self.tab_widget.addTab(self.register_tab, "📝 Register")
        
        layout.addWidget(self.tab_widget)
        
        # Set fixed size for stability
        self.setFixedSize(480, 580)
    
    def connect_signals(self):
        """Connect signals from child widgets."""
        self.login_tab.login_attempted.connect(self.handle_login)
        self.register_tab.registration_attempted.connect(self.handle_registration)
        
        # Connect auth manager signals
        auth_manager.registration_successful.connect(self.on_registration_success)
    
    def handle_login(self, credentials):
        """Handle login attempt."""
        username = credentials['username']
        password = credentials['password']
        
        if auth_manager.login(username, password):
            self.login_successful.emit(auth_manager.current_user)
        else:
            # Error message is shown via auth_manager.login_failed signal
            pass
    
    def handle_registration(self, user_data):
        """Handle registration attempt."""
        auth_manager.register_customer(
            user_data['username'],
            user_data['password'],
            user_data['email'],
            user_data['full_name']
        )
    
    def on_registration_success(self, message):
        """Handle successful registration."""
        QMessageBox.information(
            self,
            "Registration Successful",
            "Your account has been created successfully!\nPlease log in with your credentials."
        )
        # Switch to login tab
        self.tab_widget.setCurrentIndex(0)
        # Clear registration form
        self.register_tab.clear_form()


class LoginTab(QWidget):
    """Login form tab."""
    
    login_attempted = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Use QGridLayout for stable input alignment
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Fixed dimensions for all elements
        label_height = 22
        input_height = 42
        input_width = 400
        
        # Username label
        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")
        username_label.setFixedSize(input_width, label_height)
        grid_layout.addWidget(username_label, 0, 0)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedSize(input_width, input_height)
        grid_layout.addWidget(self.username_input, 1, 0)
        
        # Spacer
        grid_layout.addItem(QSpacerItem(20, 12), 2, 0)
        
        # Password label
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        password_label.setFixedSize(input_width, label_height)
        grid_layout.addWidget(password_label, 3, 0)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedSize(input_width, input_height)
        grid_layout.addWidget(self.password_input, 4, 0)
        
        main_layout.addLayout(grid_layout)
        
        # Spacer before button
        main_layout.addSpacing(20)
        
        # Login Button - Fixed size
        self.login_button = QPushButton("🔐 Sign In")
        self.login_button.setFixedSize(input_width, 48)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.on_login_clicked)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Hint text
        hint_label = QLabel("Default Admin: username='admin', password='admin123'")
        hint_label.setObjectName("subtitle")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setFixedHeight(20)
        hint_label.setStyleSheet("font-size: 11px; color: #757575;")
        main_layout.addSpacing(10)
        main_layout.addWidget(hint_label)
        
        main_layout.addStretch()
    
    def on_login_clicked(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username:
            QMessageBox.warning(self, "Input Error", "Please enter your username")
            return
        
        if not password:
            QMessageBox.warning(self, "Input Error", "Please enter your password")
            return
        
        self.login_attempted.emit({
            'username': username,
            'password': password
        })
    
    def clear_form(self):
        """Clear the form fields."""
        self.username_input.clear()
        self.password_input.clear()


class RegisterTab(QWidget):
    """Registration form tab."""
    
    registration_attempted = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 10, 20, 20)
        
        # Use QGridLayout for stable input alignment
        grid_layout = QGridLayout()
        grid_layout.setSpacing(6)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Fixed dimensions for all elements
        label_height = 20
        input_height = 38
        input_width = 400
        
        row = 0
        
        # Full Name
        fullname_label = QLabel("Full Name")
        fullname_label.setObjectName("fieldLabel")
        fullname_label.setFixedSize(input_width, label_height)
        grid_layout.addWidget(fullname_label, row, 0)
        row += 1
        
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Enter your full name")
        self.fullname_input.setFixedSize(input_width, input_height)
        grid_layout.addWidget(self.fullname_input, row, 0)
        row += 1
        
        # Username
        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")
        username_label.setFixedSize(input_width, label_height)
        grid_layout.addWidget(username_label, row, 0)
        row += 1
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username (min 3 characters)")
        self.username_input.setFixedSize(input_width, input_height)
        grid_layout.addWidget(self.username_input, row, 0)
        row += 1
        
        # Email
        email_label = QLabel("Email")
        email_label.setObjectName("fieldLabel")
        email_label.setFixedSize(input_width, label_height)
        grid_layout.addWidget(email_label, row, 0)
        row += 1
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setFixedSize(input_width, input_height)
        grid_layout.addWidget(self.email_input, row, 0)
        row += 1
        
        # Password
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        password_label.setFixedSize(input_width, label_height)
        grid_layout.addWidget(password_label, row, 0)
        row += 1
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Create a password (min 6 characters)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedSize(input_width, input_height)
        grid_layout.addWidget(self.password_input, row, 0)
        row += 1
        
        # Confirm Password
        confirm_label = QLabel("Confirm Password")
        confirm_label.setObjectName("fieldLabel")
        confirm_label.setFixedSize(input_width, label_height)
        grid_layout.addWidget(confirm_label, row, 0)
        row += 1
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm your password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setFixedSize(input_width, input_height)
        grid_layout.addWidget(self.confirm_input, row, 0)
        
        main_layout.addLayout(grid_layout)
        
        # Spacer before button
        main_layout.addSpacing(16)
        
        # Register Button - Fixed size
        self.register_button = QPushButton("📝 Create Account")
        self.register_button.setObjectName("secondary")
        self.register_button.setFixedSize(input_width, 48)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.clicked.connect(self.on_register_clicked)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.register_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        main_layout.addStretch()
    
    def on_register_clicked(self):
        """Handle register button click."""
        full_name = self.fullname_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        
        # Validation
        if not full_name:
            QMessageBox.warning(self, "Input Error", "Please enter your full name")
            return
        
        if not username or len(username) < 3:
            QMessageBox.warning(self, "Input Error", "Username must be at least 3 characters")
            return
        
        if not email or '@' not in email:
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address")
            return
        
        if not password or len(password) < 6:
            QMessageBox.warning(self, "Input Error", "Password must be at least 6 characters")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match")
            return
        
        self.registration_attempted.emit({
            'full_name': full_name,
            'username': username,
            'email': email,
            'password': password
        })
    
    def clear_form(self):
        """Clear all form fields."""
        self.fullname_input.clear()
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
