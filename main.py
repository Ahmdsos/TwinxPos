"""
Twinx POS System - Main Application Entry Point
File: main.py

This is the main entry point for the Twinx POS application.
"""

import sys
import os
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

# Import custom modules
from database import DatabaseManager
from auth_controller import AuthController
from config_manager import ConfigManager, get_config_manager
from translations import TranslationManager, get_translator
from styles import TwinxTheme, apply_theme
from login_screen import LoginScreen
from dashboard import DashboardWindow

class MainWindow(QMainWindow):
    """Main dashboard window for Twinx POS (temporary placeholder)."""
    
    logout_requested = pyqtSignal()
    
    def __init__(self, user_data, config_manager, translation_manager):
        """
        Initialize the main window.
        
        Args:
            user_data: Dictionary with user information
            config_manager: ConfigManager instance
            translation_manager: TranslationManager instance
        """
        super().__init__()
        
        self.user_data = user_data
        self.config_manager = config_manager
        self.translation_manager = translation_manager
        
        self.setup_ui()
        self.setup_window()
    
    def setup_window(self):
        """Setup window properties."""
        self.setWindowTitle("Twinx POS - Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set application icon if available
        if os.path.exists("icon.png"):
            self.setWindowIcon(QIcon("icon.png"))
    
    def setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Welcome message
        welcome_text = f"Welcome, {self.user_data.get('full_name', self.user_data.get('username', 'User'))}!"
        welcome_label = QLabel(welcome_text)
        welcome_label.setObjectName("header")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # App title
        app_title = QLabel("Twinx POS System")
        app_title.setObjectName("subheader")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Status message
        status_label = QLabel("Main dashboard under construction...")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # User info display
        user_info = f"""
        <b>User Information:</b><br>
        Username: {self.user_data.get('username', 'N/A')}<br>
        Role: {self.user_data.get('role', 'N/A')}<br>
        Employee ID: {self.user_data.get('employee_id', 'N/A')}<br>
        Last Login: {self.user_data.get('last_login', 'N/A')}
        """
        user_info_label = QLabel(user_info)
        user_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logout button
        logout_btn = QPushButton(self.translation_manager.get('logout'))
        logout_btn.setObjectName("danger")
        logout_btn.setMinimumHeight(45)
        logout_btn.clicked.connect(self.logout)
        
        # Spacers
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(app_title)
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(status_label)
        main_layout.addWidget(user_info_label)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(logout_btn)
        
        central_widget.setLayout(main_layout)
    
    def logout(self):
        """Handle logout."""
        reply = QMessageBox.question(
            self, 
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emit logout signal
            self.logout_requested.emit()
            self.close()


class ApplicationController:
    """Controls the application flow between login and main windows."""
    
    def __init__(self, app):
        """
        Initialize application controller.
        
        Args:
            app: QApplication instance
        """
        self.app = app
        self.db_manager = None
        self.config_manager = None
        self.translation_manager = None
        self.auth_controller = None
        
        self.login_screen = None
        self.main_window = None
        
        # Try to initialize with error handling
        self.initialize_application()
    
    def initialize_application(self):
        """Initialize all application components with error handling."""
        try:
            # Initialize database
            print("Initializing database...")
            self.db_manager = DatabaseManager("twinx_pos.db")
            
            # Initialize config manager
            print("Initializing config manager...")
            self.config_manager = get_config_manager(self.db_manager)
            
            # Initialize translation manager
            print("Initializing translation manager...")
            self.translation_manager = get_translator()
            
            # Set language from config
            language = self.config_manager.get_language()
            self.translation_manager.set_language(language)
            
            # Initialize auth controller
            print("Initializing auth controller...")
            self.auth_controller = AuthController(self.db_manager)
            
            # Apply theme
            theme = self.config_manager.get_theme()
            apply_theme(self.app, theme)
            
            print("Application initialization completed successfully!")
            
        except Exception as e:
            print(f"Error during application initialization: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            
            # Show error message
            QMessageBox.critical(
                None,
                "Application Error",
                f"Failed to initialize application:\n{str(e)}\n\nPlease check database connection and try again.",
                QMessageBox.StandardButton.Ok
            )
            sys.exit(1)
    
    def start(self):
        """Start the application by showing the login screen."""
        if not self.db_manager:
            print("Database not initialized. Cannot start application.")
            return
        
        # Create and show login screen
        self.show_login_screen()
        
        # Start application event loop
        return self.app.exec()
    
    def show_login_screen(self):
        """Show the login screen."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        self.login_screen = LoginScreen(self.db_manager)
        self.login_screen.login_successful.connect(self.show_main_window)
        self.login_screen.show()
        
        # Center on screen
        self.center_window(self.login_screen)
    
    def show_main_window(self, user_data):
        """Show the main window after successful login."""
        if self.login_screen:
            self.login_screen.close()
            self.login_screen = None
        
        self.main_window = DashboardWindow(user_data, self.config_manager, self.translation_manager)
        self.main_window.logout_requested.connect(self.show_login_screen)
        self.main_window.show()
        
        # Center on screen
        self.center_window(self.main_window)
    
    def center_window(self, window):
        """Center a window on the screen."""
        frame_geometry = window.frameGeometry()
        screen_center = self.app.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        window.move(frame_geometry.topLeft())


def main():
    """Main application entry point."""
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Twinx POS")
        app.setOrganizationName("Twinx")
        
        # Set high DPI support if available
        # Note: Qt 6 automatically enables high-DPI scaling, so attributes are not needed
        # For Qt 5 compatibility, you could conditionally check Qt version
        try:
            # For Qt 5/PyQt5 compatibility check
            from PyQt6.QtCore import QT_VERSION_STR
            qt_version = [int(v) for v in QT_VERSION_STR.split('.')]
            if qt_version[0] == 5:  # Qt 5
                QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
                QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except (ImportError, AttributeError):
            # Qt 6 - attributes are deprecated or removed, do nothing
            pass
        
        print("=" * 50)
        print("Twinx POS System - Starting Application")
        print("=" * 50)
        
        # Create and start application controller
        controller = ApplicationController(app)
        exit_code = controller.start()
        
        print("=" * 50)
        print("Twinx POS System - Shutting Down")
        print("=" * 50)
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"Fatal error in main application: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        
        # Show error message
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"A fatal error occurred:\n{str(e)}\n\nApplication will now exit.",
            QMessageBox.StandardButton.Ok
        )
        sys.exit(1)


if __name__ == "__main__":
    main()