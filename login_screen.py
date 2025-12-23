"""
Twinx POS System - Login Screen
File: login_screen.py

This module implements the login screen for Twinx POS application.
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

# Import our modules
from auth_controller import AuthController
from config_manager import ConfigManager
from translations import TranslationManager
from styles import TwinxTheme, apply_theme


class LoginScreen(QWidget):
    """Login screen for Twinx POS application."""
    
    # Signals
    login_successful = pyqtSignal(dict)  # Emits user data on successful login
    
    def __init__(self, db_manager):
        """
        Initialize the login screen.
        
        Args:
            db_manager: DatabaseManager instance
        """
        super().__init__()
        
        # Initialize controllers
        self.db_manager = db_manager
        self.auth_controller = AuthController(db_manager)
        self.config_manager = ConfigManager(db_manager)
        self.translation_manager = TranslationManager()
        
        # Set default theme and language from config
        self.current_theme = self.config_manager.get_theme()
        self.current_language = self.config_manager.get_language()
        
        # Apply language
        self.translation_manager.set_language(self.current_language)
        
        # Setup UI
        self.setup_ui()
        
        # Apply theme
        self.apply_theme_to_window()
        
        # Update UI text
        self.update_ui_text()
        
        # Set window properties
        self.setWindowTitle("Twinx POS - Login")
        self.setMinimumSize(900, 600)
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Center spacer
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Login card
        login_card = self.create_login_card()
        main_layout.addWidget(login_card, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Bottom spacer
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.setLayout(main_layout)
        
    def create_top_bar(self):
        """Create the top bar with theme and language buttons."""
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setObjectName("topBar")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo
        logo_label = QLabel("Twinx")
        logo_label.setObjectName("logo")
        logo_font = QFont()
        logo_font.setPointSize(18)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        
        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Theme toggle button
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("iconButton")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        # Language toggle button
        self.lang_btn = QPushButton()
        self.lang_btn.setObjectName("langButton")
        self.lang_btn.setFixedSize(100, 40)
        self.lang_btn.clicked.connect(self.toggle_language)
        
        layout.addWidget(logo_label)
        layout.addSpacerItem(spacer)
        layout.addWidget(self.theme_btn)
        layout.addWidget(self.lang_btn)
        
        top_bar.setLayout(layout)
        return top_bar
    
    def create_login_card(self):
        """Create the login card with form."""
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(400, 450)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Twinx POS")
        title_label.setObjectName("loginTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel(self.translation_manager.get('welcome'))
        subtitle_label.setObjectName("loginSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Username input
        username_label = QLabel(self.translation_manager.get('username'))
        self.username_input = QLineEdit()
        self.username_input.setObjectName("usernameInput")
        self.username_input.setPlaceholderText(self.translation_manager.get('username'))
        self.username_input.setMinimumHeight(45)
        
        # Password input
        password_label = QLabel(self.translation_manager.get('password'))
        self.password_input = QLineEdit()
        self.password_input.setObjectName("passwordInput")
        self.password_input.setPlaceholderText(self.translation_manager.get('password'))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        
        # Forgot password (optional)
        forgot_btn = QPushButton(self.translation_manager.get('forgot_password'))
        forgot_btn.setObjectName("textButton")
        forgot_btn.setFlat(True)
        
        # Error label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        
        # Login button
        self.login_btn = QPushButton(self.translation_manager.get('login'))
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.clicked.connect(self.attempt_login)
        
        # Connect Enter key to login
        self.username_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        
        layout.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.error_label)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(self.login_btn)
        
        card.setLayout(layout)
        return card
    
    def attempt_login(self):
        """Attempt to login with provided credentials."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not username or not password:
            self.show_error(self.translation_manager.get('login_failed'))
            return
        
        # Disable login button during attempt
        self.login_btn.setEnabled(False)
        self.login_btn.setText(self.translation_manager.get('loading'))
        
        # Attempt login
        result = self.auth_controller.login(username, password)
        
        if result['success']:
            # Login successful
            self.error_label.setVisible(False)
            self.login_btn.setEnabled(True)
            self.login_btn.setText(self.translation_manager.get('login'))
            
            # Emit signal with user data
            self.login_successful.emit(result['user_data'])
        else:
            # Login failed
            self.show_error(result['message'])
            self.login_btn.setEnabled(True)
            self.login_btn.setText(self.translation_manager.get('login'))
    
    def show_error(self, message):
        """Show error message."""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        
        # Clear password field
        self.password_input.clear()
        self.password_input.setFocus()
    
    def toggle_language(self):
        """Toggle between Arabic and English."""
        # Toggle language in manager
        new_lang = self.translation_manager.toggle_language()
        
        # Save to config
        self.config_manager.set_language(new_lang)
        self.current_language = new_lang
        
        # Update UI text
        self.update_ui_text()
        
        # Set layout direction based on language
        if new_lang == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        # Apply theme again to refresh styles
        self.apply_theme_to_window()
    
    def toggle_theme(self):
        """Toggle between dark and light theme."""
        # Toggle theme
        if self.current_theme == 'dark':
            self.current_theme = 'light'
        else:
            self.current_theme = 'dark'
        
        # Save to config
        self.config_manager.set_theme(self.current_theme)
        
        # Apply theme
        self.apply_theme_to_window()
    
    def apply_theme_to_window(self):
        """Apply current theme to the window."""
        # Get application instance
        app = self.window().window() if self.window() else None
        
        if app:
            # Apply theme to entire application
            apply_theme(app, self.current_theme)
            
            # Update theme button icon
            if self.current_theme == 'dark':
                self.theme_btn.setText("🌙")
            else:
                self.theme_btn.setText("☀️")
    
    def update_ui_text(self):
        """Update all UI text based on current language."""
        # Update top bar
        if self.current_language == 'ar':
            self.lang_btn.setText("English")
        else:
            self.lang_btn.setText("العربية")
        
        # Update login card
        self.username_input.setPlaceholderText(self.translation_manager.get('username'))
        self.password_input.setPlaceholderText(self.translation_manager.get('password'))
        
        # Get widgets from login card
        login_card = self.findChild(QFrame, "loginCard")
        if login_card:
            # Update title and subtitle
            subtitle = login_card.findChild(QLabel, "loginSubtitle")
            if subtitle:
                subtitle.setText(self.translation_manager.get('welcome'))
            
            # Update labels
            for widget in login_card.findChildren(QLabel):
                if widget.objectName() == "":
                    text = widget.text()
                    if text in [self.translation_manager.get('username'), 
                                self.translation_manager.get('password'),
                                self.translation_manager.get('forgot_password')]:
                        widget.setText(self.translation_manager.get(text.lower().replace(' ', '_')))
            
            # Update forgot password button
            forgot_btn = login_card.findChild(QPushButton, "textButton")
            if forgot_btn:
                forgot_btn.setText(self.translation_manager.get('forgot_password'))
        
        # Update login button
        self.login_btn.setText(self.translation_manager.get('login'))
        
        # Clear error if visible
        if self.error_label.isVisible():
            self.error_label.clear()
            self.error_label.setVisible(False)
    
    def clear_form(self):
        """Clear the login form."""
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.clear()
        self.error_label.setVisible(False)
        self.login_btn.setEnabled(True)
        self.login_btn.setText(self.translation_manager.get('login'))
    
    def set_focus_to_username(self):
        """Set focus to username field."""
        self.username_input.setFocus()


# Test the login screen
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from database import DatabaseManager
    
    app = QApplication(sys.argv)
    
    # Initialize database
    db = DatabaseManager("twinx_pos.db")
    
    # Create and show login screen
    login_screen = LoginScreen(db)
    
    # Connect login signal
    def on_login_success(user_data):
        print(f"Login successful! User: {user_data['username']}")
        print(f"Role: {user_data['role']}")
        # In real app, this would switch to main window
    
    login_screen.login_successful.connect(on_login_success)
    
    login_screen.show()
    sys.exit(app.exec())