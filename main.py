#!/usr/bin/env python3
"""
SecureBank - Modern Banking Desktop Application
Main entry point for the application.

This application uses:
- PyQt6 for the GUI
- SQLite for database storage
- Role-based authentication (Admin/Customer)
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase

# Import UI components
from src.ui.login_panel import LoginPanel
from src.ui.admin_panel import AdminPanel
from src.ui.customer_panel import CustomerPanel
from src.ui.styles import get_stylesheet

# Import authentication
from src.auth.auth_manager import auth_manager


class MainWindow(QMainWindow):
    """
    Main application window with QStackedWidget for view management.
    
    The stack contains:
    - Index 0: Login Panel
    - Index 1: Admin Panel (shown after admin login)
    - Index 2: Customer Panel (shown after customer login)
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureBank - Modern Banking System")
        self.setMinimumSize(1000, 700)
        
        # Apply global stylesheet
        self.setStyleSheet(get_stylesheet())
        
        # Set application font
        self.setup_fonts()
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        layout = QVBoxLayout(self.central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget for different views
        self.stack = QStackedWidget()
        
        # Create panels
        self.login_panel_container = self.create_login_container()
        self.admin_panel = AdminPanel()
        self.customer_panel = CustomerPanel()
        
        # Add panels to stack
        self.stack.addWidget(self.login_panel_container)  # Index 0
        self.stack.addWidget(self.admin_panel)             # Index 1
        self.stack.addWidget(self.customer_panel)          # Index 2
        
        layout.addWidget(self.stack)
        
        # Connect signals
        self.connect_signals()
        
        # Show login screen initially
        self.show_login_screen()
    
    def setup_fonts(self):
        """Setup application fonts."""
        # Try to use Segoe UI on Windows, fallback to system default
        font = QFont("Segoe UI", 10)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        QApplication.setFont(font)
    
    def create_login_container(self):
        """Create a centered container for the login panel."""
        container = QWidget()
        container.setStyleSheet("background-color: #f5f5f5;")
        
        layout = QHBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create login panel
        self.login_panel = LoginPanel()
        self.login_panel.login_successful.connect(self.on_login_success)
        
        layout.addWidget(self.login_panel)
        
        return container
    
    def connect_signals(self):
        """Connect authentication signals."""
        # Auth manager signals
        auth_manager.login_failed.connect(self.on_login_failed)
        auth_manager.registration_failed.connect(self.on_registration_failed)
        
        # Panel logout signals
        self.admin_panel.logout_requested.connect(self.on_logout)
        self.customer_panel.logout_requested.connect(self.on_logout)
    
    def show_login_screen(self):
        """Show the login screen."""
        self.stack.setCurrentIndex(0)
        self.login_panel.login_tab.clear_form()
        self.setWindowTitle("SecureBank - Login")
    
    def on_login_success(self, user_data):
        """Handle successful login."""
        role = user_data.get('role')
        username = user_data.get('username', 'User')
        
        if role == 'admin':
            self.stack.setCurrentIndex(1)
            self.setWindowTitle(f"SecureBank - Admin Dashboard ({username})")
        elif role == 'customer':
            self.stack.setCurrentIndex(2)
            self.setWindowTitle(f"SecureBank - Customer Portal ({username})")
        else:
            QMessageBox.critical(
                self,
                "Login Error",
                "Unknown user role. Please contact support."
            )
            auth_manager.logout()
    
    def on_login_failed(self, error_message):
        """Handle failed login."""
        QMessageBox.warning(
            self,
            "Login Failed",
            error_message
        )
    
    def on_registration_failed(self, error_message):
        """Handle failed registration."""
        QMessageBox.warning(
            self,
            "Registration Failed",
            error_message
        )
    
    def on_logout(self):
        """Handle logout."""
        self.show_login_screen()


def main():
    """Application entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("SecureBank")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SecureBank Inc.")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
