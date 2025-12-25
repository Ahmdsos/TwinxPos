"""
Twinx POS System - Product Management Screen
File: product_screen.py

This module implements the product management screen for Twinx POS application.
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QFrame, QComboBox,
    QSpinBox, QTextEdit, QMessageBox, QSplitter, QGroupBox,
    QFormLayout, QCheckBox, QProgressBar, QHeaderView, QAbstractItemView,
    QDialog, QDialogButtonBox, QScrollArea, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

# Import custom modules
from product_controller import ProductController
from translations import TranslationManager
from config_manager import ConfigManager
from styles import TwinxTheme


class ProductScreen(QWidget):
    """Product management screen for Twinx POS application."""

    # Signals
    product_updated = pyqtSignal(dict)  # Emits when product is updated

    def __init__(self, db_manager, config_manager, translation_manager, user_data):
        """
        Initialize the product screen.

        Args:
            db_manager: DatabaseManager instance
            config_manager: ConfigManager instance
            translation_manager: TranslationManager instance
            user_data: Current user data
        """
        super().__init__()

        self.db_manager = db_manager
        self.config_manager = config_manager
        self.translation_manager = translation_manager
        self.user_data = user_data

        # Initialize product controller
        self.product_controller = ProductController(db_manager)

        # Current language and theme
        self.current_language = self.translation_manager.get_current_lang()
        self.current_theme = self.config_manager.get_theme()

        # Current product data
        self.current_product = None
        self.products_data = []
        self.filtered_products = []

        # Search timer for debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        self.setup_ui()
        self.load_products()
        self.apply_language_direction()

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header section
        header_frame = self.create_header()
        main_layout.addWidget(header_frame)

        # Search and filters section
        search_frame = self.create_search_filters()
        main_layout.addWidget(search_frame)

        # Main content splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setSizes([600, 400])

        # Products table
        table_frame = self.create_products_table()
        content_splitter.addWidget(table_frame)

        # Product details panel
        details_frame = self.create_product_details()
        content_splitter.addWidget(details_frame)

        main_layout.addWidget(content_splitter, stretch=1)

        # Status bar
        status_frame = self.create_status_bar()
        main_layout.addWidget(status_frame)

        self.setLayout(main_layout)

    def create_header(self):
        """Create the header section."""
        header = QFrame()
        header.setObjectName("productHeader")
        header.setFixedHeight(60)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title_label = QLabel("📦 " + self.translation_manager.get('products'))
        title_label.setObjectName("screenTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)

        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Add product button
        self.add_btn = QPushButton("➕ " + self.translation_manager.get('add_product'))
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.setMinimumHeight(35)
        self.add_btn.clicked.connect(self.add_product)
        buttons_layout.addWidget(self.add_btn)

        # Edit product button
        self.edit_btn = QPushButton("✏️ " + self.translation_manager.get('edit'))
        self.edit_btn.setObjectName("secondaryButton")
        self.edit_btn.setMinimumHeight(35)
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_product)
        buttons_layout.addWidget(self.edit_btn)

        # Delete product button
        self.delete_btn = QPushButton("🗑️ " + self.translation_manager.get('delete'))
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.setMinimumHeight(35)
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_product)
        buttons_layout.addWidget(self.delete_btn)

        layout.addWidget(title_label)
        layout.addSpacerItem(spacer)
        layout.addLayout(buttons_layout)

        header.setLayout(layout)
        return header

    def create_search_filters(self):
