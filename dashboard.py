"""
Twinx POS System - Dashboard Window
File: dashboard.py

This module implements the main dashboard window for Twinx POS application.
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QStackedWidget, 
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

# Import custom modules
from translations import TranslationManager
from config_manager import ConfigManager


class DashboardWindow(QMainWindow):
    """Main dashboard window for Twinx POS application."""
    
    # Signals
    logout_requested = pyqtSignal()
    navigate_to_screen = pyqtSignal(str)  # Signal to navigate to specific screen
    
    def __init__(self, user_data, config_manager, translation_manager):
        """
        Initialize the dashboard window.
        
        Args:
            user_data: Dictionary with user information
            config_manager: ConfigManager instance
            translation_manager: TranslationManager instance
        """
        super().__init__()
        
        self.user_data = user_data
        self.config_manager = config_manager
        self.translation_manager = translation_manager
        
        self.current_language = self.translation_manager.get_current_lang()
        
        self.setup_window()
        self.setup_ui()
        self.apply_language_direction()
        
    def setup_window(self):
        """Setup window properties."""
        self.setWindowTitle("Twinx POS - Dashboard")
        self.setGeometry(100, 50, 1400, 850)
        self.setObjectName("dashboardWindow")
        
    def apply_language_direction(self):
        """Apply layout direction based on language."""
        if self.current_language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    
    def setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("dashboardCentralWidget")
        self.setCentralWidget(central_widget)
        
        # Main layout (header, content, sidebar)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Main content area (vertical: header + content)
        content_area = QWidget()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedWidget")
        
        # Create placeholder pages
        self.create_pages()
        
        content_layout.addWidget(self.stacked_widget)
        content_area.setLayout(content_layout)
        
        main_layout.addWidget(content_area, stretch=1)
        central_widget.setLayout(main_layout)
    
    def create_sidebar(self):
        """Create the sidebar menu."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)
        
        # Logo/Title
        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_layout = QVBoxLayout()
        logo_layout.setContentsMargins(20, 10, 20, 20)
        
        logo_label = QLabel("Twinx POS")
        logo_label.setObjectName("sidebarLogo")
        logo_font = QFont()
        logo_font.setPointSize(16)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_layout.addWidget(logo_label)
        logo_frame.setLayout(logo_layout)
        sidebar_layout.addWidget(logo_frame)
        
        # Menu buttons
        self.menu_buttons = []
        
        # Dashboard (Home)
        dashboard_btn = self.create_menu_button("dashboard", "🏠")
        dashboard_btn.setChecked(True)
        sidebar_layout.addWidget(dashboard_btn)
        self.menu_buttons.append(dashboard_btn)
        
        # POS (Cashier)
        pos_btn = self.create_menu_button("point_of_sale", "💰")
        sidebar_layout.addWidget(pos_btn)
        self.menu_buttons.append(pos_btn)
        
        # Products (Inventory)
        products_btn = self.create_menu_button("products", "📦")
        sidebar_layout.addWidget(products_btn)
        self.menu_buttons.append(products_btn)
        
        # Customers
        customers_btn = self.create_menu_button("customers", "👥")
        sidebar_layout.addWidget(customers_btn)
        self.menu_buttons.append(customers_btn)
        
        # Suppliers
        suppliers_btn = self.create_menu_button("suppliers", "🏭")
        sidebar_layout.addWidget(suppliers_btn)
        self.menu_buttons.append(suppliers_btn)
        
        # HR & Payroll
        hr_btn = self.create_menu_button("hr_payroll", "👨‍💼")
        sidebar_layout.addWidget(hr_btn)
        self.menu_buttons.append(hr_btn)
        
        # Reports
        reports_btn = self.create_menu_button("reports", "📊")
        sidebar_layout.addWidget(reports_btn)
        self.menu_buttons.append(reports_btn)
        
        # Settings
        settings_btn = self.create_menu_button("settings", "⚙️")
        sidebar_layout.addWidget(settings_btn)
        self.menu_buttons.append(settings_btn)
        
        # Spacer to push things up
        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Version info
        version_label = QLabel("v1.0.0")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)
        
        sidebar.setLayout(sidebar_layout)
        return sidebar
    
    def create_menu_button(self, screen_key, icon_text):
        """Create a menu button for the sidebar."""
        button = QPushButton()
        button.setObjectName(f"menuButton_{screen_key}")
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setMinimumHeight(50)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 0, 20, 0)
        button_layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel(icon_text)
        icon_label.setObjectName("menuIcon")
        icon_label.setFixedWidth(30)
        
        # Text
        text_label = QLabel(self.translation_manager.get(screen_key))
        text_label.setObjectName("menuText")
        
        button_layout.addWidget(icon_label)
        button_layout.addWidget(text_label, stretch=1)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        button.setLayout(button_layout)
        
        # Connect click event
        button.clicked.connect(lambda: self.on_menu_button_clicked(screen_key))
        
        # Store reference to labels for language updates
        button.text_label = text_label
        button.screen_key = screen_key
        
        return button
    
    def on_menu_button_clicked(self, screen_key):
        """Handle menu button clicks."""
        # Map screen keys to page indices
        page_map = {
            'dashboard': 0,
            'point_of_sale': 1,
            'products': 2,
            'customers': 3,
            'suppliers': 4,
            'hr_payroll': 5,
            'reports': 6,
            'settings': 7
        }
        
        if screen_key in page_map:
            self.stacked_widget.setCurrentIndex(page_map[screen_key])
        
        # Emit signal for external navigation if needed
        self.navigate_to_screen.emit(screen_key)
    
    def create_header(self):
        """Create the top header."""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(70)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Title (empty here since we have logo in sidebar)
        title_label = QLabel("")
        title_label.setObjectName("headerTitle")
        
        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # User info
        user_frame = QFrame()
        user_frame.setObjectName("userFrame")
        user_layout = QHBoxLayout()
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(15)
        
        user_icon = QLabel("👤")
        user_icon.setObjectName("userIcon")
        
        self.user_info_label = QLabel("")
        self.user_info_label.setObjectName("userInfo")
        self.update_user_info()
        
        # Logout button
        logout_btn = QPushButton(self.translation_manager.get('logout'))
        logout_btn.setObjectName("headerLogoutButton")
        logout_btn.setFixedSize(100, 35)
        logout_btn.clicked.connect(self.on_logout_clicked)
        
        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.user_info_label)
        user_layout.addWidget(logout_btn)
        user_frame.setLayout(user_layout)
        
        header_layout.addWidget(title_label)
        header_layout.addSpacerItem(spacer)
        header_layout.addWidget(user_frame)
        
        header.setLayout(header_layout)
        return header
    
    def update_user_info(self):
        """Update the user information display."""
        username = self.user_data.get('username', 'User')
        role = self.user_data.get('role', 'Employee')
        
        if self.current_language == 'ar':
            self.user_info_label.setText(f"{username} | {role}")
        else:
            self.user_info_label.setText(f"{username} | {role}")
    
    def on_logout_clicked(self):
        """Handle logout button click."""
        self.logout_requested.emit()
    
    def create_pages(self):
        """Create placeholder pages for the stacked widget."""
        # Dashboard Page
        dashboard_page = self.create_placeholder_page("dashboard", "🏠", "#e74c3c")
        self.stacked_widget.addWidget(dashboard_page)
        
        # POS Page
        pos_page = self.create_placeholder_page("point_of_sale", "💰", "#3498db")
        self.stacked_widget.addWidget(pos_page)
        
        # Products Page
        products_page = self.create_placeholder_page("products", "📦", "#2ecc71")
        self.stacked_widget.addWidget(products_page)
        
        # Customers Page
        customers_page = self.create_placeholder_page("customers", "👥", "#9b59b6")
        self.stacked_widget.addWidget(customers_page)
        
        # Suppliers Page
        suppliers_page = self.create_placeholder_page("suppliers", "🏭", "#e67e22")
        self.stacked_widget.addWidget(suppliers_page)
        
        # HR & Payroll Page
        hr_page = self.create_placeholder_page("hr_payroll", "👨‍💼", "#1abc9c")
        self.stacked_widget.addWidget(hr_page)
        
        # Reports Page
        reports_page = self.create_placeholder_page("reports", "📊", "#f39c12")
        self.stacked_widget.addWidget(reports_page)
        
        # Settings Page
        settings_page = self.create_placeholder_page("settings", "⚙️", "#7f8c8d")
        self.stacked_widget.addWidget(settings_page)
    
    def create_placeholder_page(self, screen_key, icon, color):
        """Create a placeholder page for a screen."""
        page = QWidget()
        page.setObjectName(f"page_{screen_key}")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Page header
        header_frame = QFrame()
        header_frame.setObjectName("pageHeader")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        # Icon and title
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_label = QLabel(icon)
        icon_label.setObjectName("pageIcon")
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        
        title_label = QLabel(self.translation_manager.get(screen_key))
        title_label.setObjectName("pageTitle")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Status message
        status_label = QLabel("This section is under development and will be available soon.")
        status_label.setObjectName("pageStatus")
        
        # Details
        details_label = QLabel(f"• Full functionality for {screen_key.replace('_', ' ').title()} will be implemented soon.<br>"
                              "• You can navigate between sections using the sidebar menu.<br>"
                              "• All data management features will be available in the next update.")
        details_label.setObjectName("pageDetails")
        
        header_layout.addLayout(title_layout)
        header_layout.addWidget(status_label)
        header_layout.addWidget(details_label)
        header_frame.setLayout(header_layout)
        
        # Spacer
        layout.addWidget(header_frame)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Stats/Quick info (placeholder)
        if screen_key == 'dashboard':
            stats_frame = self.create_dashboard_stats()
            layout.addWidget(stats_frame)
        
        page.setLayout(layout)
        return page
    
    def create_dashboard_stats(self):
        """Create dashboard statistics (placeholder)."""
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(0, 20, 0, 0)
        
        stats_title = QLabel("Quick Statistics")
        stats_title.setObjectName("statsTitle")
        
        # Stats grid
        stats_grid = QFrame()
        stats_grid_layout = QHBoxLayout()
        stats_grid_layout.setContentsMargins(0, 10, 0, 0)
        stats_grid_layout.setSpacing(20)
        
        # Stat 1: Today's Sales
        stat1 = self.create_stat_card("Today's Sales", "$1,250.50", "#e74c3c", "💰")
        
        # Stat 2: Total Products
        stat2 = self.create_stat_card("Total Products", "156", "#3498db", "📦")
        
        # Stat 3: Active Customers
        stat3 = self.create_stat_card("Active Customers", "42", "#2ecc71", "👥")
        
        # Stat 4: Pending Orders
        stat4 = self.create_stat_card("Pending Orders", "7", "#f39c12", "📋")
        
        stats_grid_layout.addWidget(stat1)
        stats_grid_layout.addWidget(stat2)
        stats_grid_layout.addWidget(stat3)
        stats_grid_layout.addWidget(stat4)
        stats_grid.setLayout(stats_grid_layout)
        
        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(stats_grid)
        stats_frame.setLayout(stats_layout)
        
        return stats_frame
    
    def create_stat_card(self, title, value, color, icon):
        """Create a statistic card."""
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(120)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Top row: Icon and title
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 5)
        
        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        
        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_label, stretch=1)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_font = QFont()
        value_font.setPointSize(28)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(top_layout)
        layout.addWidget(value_label, stretch=1)
        
        card.setLayout(layout)
        
        # Apply color via stylesheet
        card.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {color}15;
                border: 1px solid {color}30;
                border-radius: 10px;
            }}
            QLabel#statTitle {{
                color: {color};
                font-weight: bold;
                font-size: 12px;
            }}
            QLabel#statValue {{
                color: {color};
            }}
        """)
        
        return card
    
    def update_language(self):
        """Update all UI text when language changes."""
        self.current_language = self.translation_manager.get_current_lang()
        
        # Update menu buttons
        for button in self.menu_buttons:
            if hasattr(button, 'text_label') and hasattr(button, 'screen_key'):
                button.text_label.setText(self.translation_manager.get(button.screen_key))
        
        # Update header logout button
        logout_btn = self.findChild(QPushButton, "headerLogoutButton")
        if logout_btn:
            logout_btn.setText(self.translation_manager.get('logout'))
        
        # Update user info
        self.update_user_info()
        
        # Update page titles
        for i in range(self.stacked_widget.count()):
            page = self.stacked_widget.widget(i)
            if page:
                title_label = page.findChild(QLabel, "pageTitle")
                if title_label:
                    # Extract screen key from object name
                    obj_name = page.objectName()
                    if obj_name.startswith("page_"):
                        screen_key = obj_name[5:]
                        title_label.setText(self.translation_manager.get(screen_key))
        
        # Apply layout direction
        self.apply_language_direction()
        
        # Force style update
        self.style().unpolish(self)
        self.style().polish(self)


# Test the dashboard
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Mock user data
    user_data = {
        'username': 'admin',
        'role': 'Administrator',
        'full_name': 'System Administrator',
        'employee_id': 'EMP001'
    }
    
    # Create config manager and translation manager
    from database import DatabaseManager
    
    db = DatabaseManager(":memory:")  # In-memory DB for testing
    config_manager = ConfigManager(db)
    translation_manager = TranslationManager()
    
    # Create and show dashboard
    dashboard = DashboardWindow(user_data, config_manager, translation_manager)
    
    # Connect logout signal
    def on_logout():
        print("Logout requested")
        dashboard.close()
    
    dashboard.logout_requested.connect(on_logout)
    
    # Connect navigation signal
    def on_navigate(screen):
        print(f"Navigating to: {screen}")
    
    dashboard.navigate_to_screen.connect(on_navigate)
    
    dashboard.show()
    sys.exit(app.exec())