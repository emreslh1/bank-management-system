"""
Authentication Manager Module
Handles user authentication, registration, and session management.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from ..database.db_manager import db_manager, UserRole


class AuthManager(QObject):
    """
    Manages authentication state and operations.
    Emits signals for login/logout events.
    """
    
    # Signals
    user_logged_in = pyqtSignal(dict)  # Emits user data dict
    user_logged_out = pyqtSignal()
    registration_successful = pyqtSignal(str)  # Emits success message
    registration_failed = pyqtSignal(str)  # Emits error message
    login_failed = pyqtSignal(str)  # Emits error message
    
    def __init__(self):
        """Initialize the authentication manager."""
        super().__init__()
        self._current_user = None
    
    @property
    def current_user(self):
        """Get the currently logged in user."""
        return self._current_user
    
    @property
    def is_authenticated(self):
        """Check if a user is currently authenticated."""
        return self._current_user is not None
    
    @property
    def is_admin(self):
        """Check if the current user is an admin."""
        if self._current_user:
            return self._current_user.get('role') == UserRole.ADMIN.value
        return False
    
    @property
    def is_customer(self):
        """Check if the current user is a customer."""
        if self._current_user:
            return self._current_user.get('role') == UserRole.CUSTOMER.value
        return False
    
    def login(self, username, password):
        """
        Attempt to log in a user.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        user = db_manager.authenticate_user(username, password)
        
        if user:
            self._current_user = user
            db_manager.update_last_login(user['id'])
            self.user_logged_in.emit(user)
            return True
        else:
            self.login_failed.emit("Invalid username or password")
            return False
    
    def logout(self):
        """Log out the current user."""
        self._current_user = None
        self.user_logged_out.emit()
    
    def register_customer(self, username, password, email, full_name):
        """
        Register a new customer account.
        
        Args:
            username: Desired username
            password: Password
            email: Email address
            full_name: Full name
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        # Validate inputs
        if not username or len(username) < 3:
            self.registration_failed.emit("Username must be at least 3 characters")
            return False
        
        if not password or len(password) < 6:
            self.registration_failed.emit("Password must be at least 6 characters")
            return False
        
        if not email or '@' not in email:
            self.registration_failed.emit("Please enter a valid email address")
            return False
        
        if not full_name or len(full_name) < 2:
            self.registration_failed.emit("Please enter your full name")
            return False
        
        # Attempt registration
        success, message = db_manager.register_customer(username, password, email, full_name)
        
        if success:
            self.registration_successful.emit(message)
            return True
        else:
            self.registration_failed.emit(message)
            return False
    
    def get_user_role(self):
        """Get the role of the current user."""
        if self._current_user:
            return self._current_user.get('role')
        return None
    
    def get_user_display_name(self):
        """Get the display name of the current user."""
        if self._current_user:
            return self._current_user.get('full_name') or self._current_user.get('username')
        return None


# Singleton instance
auth_manager = AuthManager()
