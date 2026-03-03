"""
Styles Module
Contains QSS stylesheets and color schemes for the banking application.
"""

# Color Palette
COLORS = {
    'primary': '#1a237e',           # Deep indigo
    'primary_light': '#534bae',     # Light indigo
    'primary_dark': '#000051',      # Dark indigo
    'secondary': '#00bcd4',         # Cyan
    'accent': '#ff4081',            # Pink accent
    'background': '#f5f5f5',        # Light gray background
    'surface': '#ffffff',           # White surface
    'error': '#b00020',             # Red error
    'success': '#4caf50',           # Green success
    'text_primary': '#212121',      # Primary text
    'text_secondary': '#757575',    # Secondary text
    'text_on_primary': '#ffffff',   # Text on primary color
    'divider': '#e0e0e0',           # Divider color
}

# Main application stylesheet
MAIN_STYLE = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

QWidget {{
    font-family: 'Segoe UI', 'Arial', sans-serif;
}}

/* Card Style Widgets */
QFrame#card {{
    background-color: {COLORS['surface']};
    border-radius: 12px;
    border: 1px solid {COLORS['divider']};
}}

/* Labels - Fixed for stability */
QLabel {{
    color: {COLORS['text_primary']};
    min-height: 20px;
}}

QLabel#title {{
    font-size: 28px;
    font-weight: bold;
    color: {COLORS['primary']};
    min-height: 36px;
    max-height: 36px;
}}

QLabel#subtitle {{
    font-size: 14px;
    color: {COLORS['text_secondary']};
    min-height: 20px;
}}

QLabel#header {{
    font-size: 16px;
    font-weight: bold;
    color: {COLORS['primary']};
    min-height: 24px;
    max-height: 24px;
    margin-bottom: 4px;
}}

QLabel#fieldLabel {{
    font-size: 13px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    min-height: 18px;
    max-height: 18px;
    margin-bottom: 4px;
}}

/* Line Edits - Fixed for stability */
QLineEdit {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['divider']};
    border-radius: 8px;
    padding: 10px 15px;
    font-size: 14px;
    color: {COLORS['text_primary']};
    min-height: 42px;
    max-height: 42px;
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
    outline: none;
}}

QLineEdit::placeholder {{
    color: {COLORS['text_secondary']};
}}

QLineEdit:hover {{
    border: 2px solid #bdbdbd;
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_on_primary']};
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_light']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:disabled {{
    background-color: {COLORS['divider']};
    color: {COLORS['text_secondary']};
}}

QPushButton#secondary {{
    background-color: transparent;
    color: {COLORS['primary']};
    border: 2px solid {COLORS['primary']};
}}

QPushButton#secondary:hover {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_on_primary']};
}}

QPushButton#danger {{
    background-color: {COLORS['error']};
}}

QPushButton#danger:hover {{
    background-color: #cf6679;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: none;
    background-color: transparent;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 12px 24px;
    margin-right: 4px;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 14px;
    font-weight: bold;
}}

QTabBar::tab:selected {{
    color: {COLORS['primary']};
    border-bottom-color: {COLORS['primary']};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS['text_primary']};
    background-color: rgba(0, 0, 0, 0.05);
}}

/* Group Box */
QGroupBox {{
    font-size: 14px;
    font-weight: bold;
    color: {COLORS['primary']};
    border: 1px solid {COLORS['divider']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
}}

/* Scroll Area */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

/* Message Box */
QMessageBox {{
    background-color: {COLORS['surface']};
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}
"""

# Login panel specific styles
LOGIN_STYLE = f"""
QFrame#loginCard {{
    background-color: {COLORS['surface']};
    border-radius: 16px;
    border: 1px solid {COLORS['divider']};
    padding: 40px;
}}

QLabel#bankLogo {{
    font-size: 48px;
    font-weight: bold;
    color: {COLORS['primary']};
}}

QLabel#welcomeText {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS['text_primary']};
}}
"""

# Admin panel styles
ADMIN_STYLE = f"""
QFrame#sidebar {{
    background-color: {COLORS['primary']};
    min-width: 250px;
}}

QLabel#sidebarTitle {{
    color: {COLORS['text_on_primary']};
    font-size: 20px;
    font-weight: bold;
    padding: 20px;
}}

QPushButton#sidebarButton {{
    background-color: transparent;
    color: {COLORS['text_on_primary']};
    text-align: left;
    padding: 15px 20px;
    border-radius: 0;
    border-left: 4px solid transparent;
}}

QPushButton#sidebarButton:hover {{
    background-color: rgba(255, 255, 255, 0.1);
}}

QPushButton#sidebarButton:checked {{
    background-color: rgba(255, 255, 255, 0.15);
    border-left-color: {COLORS['secondary']};
}}
"""

# Customer panel styles
CUSTOMER_STYLE = f"""
QFrame#accountCard {{
    background-color: {COLORS['surface']};
    border-radius: 12px;
    border: 1px solid {COLORS['divider']};
    padding: 20px;
}}

QLabel#balanceLabel {{
    font-size: 32px;
    font-weight: bold;
    color: {COLORS['primary']};
}}

QLabel#accountNumber {{
    font-size: 14px;
    color: {COLORS['text_secondary']};
    letter-spacing: 2px;
}}
"""


def get_stylesheet():
    """Get the complete application stylesheet."""
    return MAIN_STYLE + LOGIN_STYLE + ADMIN_STYLE + CUSTOMER_STYLE
