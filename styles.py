"""
Twinx POS System - PyQt6 Styles
File: styles.py

This module defines the visual theme and styles for the Twinx POS application.
"""

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication


class TwinxTheme:
    """Defines the visual theme and styles for Twinx POS application."""
    
    # Color palettes
    PALETTES = {
        'dark': {
            'background': '#121212',
            'surface': '#1e1e1e',
            'primary': '#e74c3c',
            'primary_light': '#ff6b5c',
            'primary_dark': '#c0392b',
            'secondary': '#3498db',
            'accent': '#2ecc71',
            'text_primary': '#ffffff',
            'text_secondary': '#bdc3c7',
            'text_disabled': '#7f8c8d',
            'input_background': '#2c2c2c',
            'input_border': '#404040',
            'input_focus': '#e74c3c',
            'table_header': '#2c3e50',
            'table_row_even': '#1e1e1e',
            'table_row_odd': '#242424',
            'table_row_hover': '#2c3e50',
            'table_row_selected': '#e74c3c',
            'table_border': '#404040',
            'tab_active': '#e74c3c',
            'tab_inactive': '#2c3e50',
            'tab_hover': '#3498db',
            'scrollbar': '#404040',
            'scrollbar_handle': '#7f8c8d',
            'scrollbar_handle_hover': '#95a5a6',
            'success': '#27ae60',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'info': '#3498db',
            'shadow': 'rgba(0, 0, 0, 0.3)',
        },
        
        'light': {
            'background': '#f5f6fa',
            'surface': '#ffffff',
            'primary': '#e74c3c',
            'primary_light': '#ff6b5c',
            'primary_dark': '#c0392b',
            'secondary': '#3498db',
            'accent': '#2ecc71',
            'text_primary': '#2c3e50',
            'text_secondary': '#7f8c8d',
            'text_disabled': '#bdc3c7',
            'input_background': '#ecf0f1',
            'input_border': '#dcdde1',
            'input_focus': '#e74c3c',
            'table_header': '#dfe6e9',
            'table_row_even': '#ffffff',
            'table_row_odd': '#f8f9fa',
            'table_row_hover': '#e3f2fd',
            'table_row_selected': '#e74c3c',
            'table_border': '#dfe6e9',
            'tab_active': '#e74c3c',
            'tab_inactive': '#bdc3c7',
            'tab_hover': '#3498db',
            'scrollbar': '#dfe6e9',
            'scrollbar_handle': '#95a5a6',
            'scrollbar_handle_hover': '#7f8c8d',
            'success': '#27ae60',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'info': '#3498db',
            'shadow': 'rgba(0, 0, 0, 0.1)',
        }
    }
    
    @classmethod
    def get_stylesheet(cls, theme_name='dark'):
        """
        Get the complete QSS stylesheet for the specified theme.
        
        Args:
            theme_name: 'dark' or 'light'
            
        Returns:
            QSS stylesheet string
        """
        if theme_name not in cls.PALETTES:
            theme_name = 'dark'
        
        colors = cls.PALETTES[theme_name]
        
        return f"""
        /* ===== GLOBAL STYLES ===== */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 10pt;
            outline: none;
        }}
        
        QMainWindow, QDialog {{
            background-color: {colors['background']};
            border: none;
        }}
        
        /* ===== LABELS ===== */
        QLabel {{
            color: {colors['text_primary']};
            font-size: 10pt;
            font-weight: normal;
        }}
        
        QLabel.header {{
            font-size: 16pt;
            font-weight: bold;
            color: {colors['primary']};
            padding: 10px 0;
        }}
        
        QLabel.subheader {{
            font-size: 12pt;
            font-weight: bold;
            color: {colors['text_secondary']};
            padding: 5px 0;
        }}
        
        QLabel.error {{
            color: {colors['error']};
            font-weight: bold;
        }}
        
        QLabel.success {{
            color: {colors['success']};
            font-weight: bold;
        }}
        
        QLabel.warning {{
            color: {colors['warning']};
            font-weight: bold;
        }}
        
        QLabel.info {{
            color: {colors['info']};
            font-weight: bold;
        }}
        
        /* ===== BUTTONS ===== */
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 10pt;
            min-height: 40px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary_light']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_dark']};
            padding-top: 11px;
            padding-bottom: 9px;
        }}
        
        QPushButton:disabled {{
            background-color: {colors['text_disabled']};
            color: {colors['text_secondary']};
        }}
        
        /* Primary Action Button */
        QPushButton.primary {{
            background-color: {colors['primary']};
            font-size: 11pt;
            padding: 12px 24px;
            min-height: 45px;
        }}
        
        /* Secondary Button */
        QPushButton.secondary {{
            background-color: {colors['secondary']};
        }}
        
        QPushButton.secondary:hover {{
            background-color: #5dade2;
        }}
        
        /* Success Button */
        QPushButton.success {{
            background-color: {colors['success']};
        }}
        
        QPushButton.success:hover {{
            background-color: #2ecc71;
        }}
        
        /* Danger Button */
        QPushButton.danger {{
            background-color: {colors['error']};
        }}
        
        QPushButton.danger:hover {{
            background-color: #ff6b5c;
        }}
        
        /* Outline Button */
        QPushButton.outline {{
            background-color: transparent;
            border: 2px solid {colors['primary']};
            color: {colors['primary']};
        }}
        
        QPushButton.outline:hover {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        /* Small Button */
        QPushButton.small {{
            padding: 6px 12px;
            min-height: 30px;
            font-size: 9pt;
        }}
        
        /* Icon Button */
        QPushButton.icon {{
            background-color: transparent;
            border: none;
            padding: 8px;
            min-width: 40px;
            min-height: 40px;
            border-radius: 20px;
        }}
        
        QPushButton.icon:hover {{
            background-color: rgba(231, 76, 60, 0.1);
        }}
        
        /* ===== INPUT FIELDS ===== */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['input_background']};
            color: {colors['text_primary']};
            border: 2px solid {colors['input_border']};
            border-radius: 6px;
            padding: 10px;
            font-size: 10pt;
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {colors['input_focus']};
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {colors['text_disabled']};
            color: {colors['text_secondary']};
            border-color: {colors['text_disabled']};
        }}
        
        QLineEdit.error, QTextEdit.error, QPlainTextEdit.error {{
            border: 2px solid {colors['error']};
        }}
        
        /* Search Input */
        QLineEdit.search {{
            padding-left: 35px;
            background-image: url(search_icon.png);
            background-repeat: no-repeat;
            background-position: 10px center;
        }}
        
        /* Numeric Input */
        QLineEdit.numeric {{
            font-family: "Courier New", monospace;
            text-align: right;
            font-size: 11pt;
        }}
        
        /* ===== COMBOBOXES ===== */
        QComboBox {{
            background-color: {colors['input_background']};
            color: {colors['text_primary']};
            border: 2px solid {colors['input_border']};
            border-radius: 6px;
            padding: 8px;
            padding-right: 30px;
            min-height: 40px;
            font-size: 10pt;
        }}
        
        QComboBox:hover {{
            border-color: {colors['primary']};
        }}
        
        QComboBox:focus {{
            border-color: {colors['input_focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
            border-left: 3px solid transparent;
            border-right: 3px solid transparent;
            border-top: 6px solid {colors['text_primary']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 2px solid {colors['input_border']};
            border-radius: 6px;
            padding: 5px;
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}
        
        /* ===== CHECKBOXES & RADIO BUTTONS ===== */
        QCheckBox, QRadioButton {{
            color: {colors['text_primary']};
            spacing: 8px;
            font-size: 10pt;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors['input_border']};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        QRadioButton::indicator {{
            border-radius: 9px;
        }}
        
        QCheckBox::indicator:checked {{
            image: url(checkbox_checked.png);
        }}
        
        /* ===== TABLES ===== */
        QTableWidget {{
            background-color: {colors['surface']};
            alternate-background-color: {colors['table_row_odd']};
            color: {colors['text_primary']};
            gridline-color: {colors['table_border']};
            border: 1px solid {colors['table_border']};
            border-radius: 8px;
            font-size: 10pt;
            selection-background-color: {colors['table_row_selected']};
            selection-color: white;
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {colors['table_border']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {colors['table_row_selected']};
            color: white;
        }}
        
        QTableWidget::item:hover {{
            background-color: {colors['table_row_hover']};
        }}
        
        QHeaderView::section {{
            background-color: {colors['table_header']};
            color: {colors['text_primary']};
            padding: 12px 8px;
            border: none;
            border-right: 1px solid {colors['table_border']};
            border-bottom: 2px solid {colors['primary']};
            font-weight: bold;
            font-size: 10pt;
        }}
        
        QHeaderView::section:last {{
            border-right: none;
        }}
        
        QHeaderView::section:pressed {{
            background-color: {colors['primary']};
        }}
        
        /* ===== TABS ===== */
        QTabWidget::pane {{
            border: 1px solid {colors['input_border']};
            border-radius: 8px;
            background-color: {colors['surface']};
            margin-top: 5px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['tab_inactive']};
            color: {colors['text_primary']};
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-weight: bold;
            font-size: 10pt;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['tab_active']};
            color: white;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors['tab_hover']};
            color: white;
        }}
        
        /* ===== GROUP BOXES ===== */
        QGroupBox {{
            color: {colors['text_primary']};
            border: 2px solid {colors['input_border']};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            font-weight: bold;
            font-size: 11pt;
            background-color: {colors['surface']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: {colors['primary']};
        }}
        
        /* ===== SCROLLBARS ===== */
        QScrollBar:vertical {{
            background-color: {colors['scrollbar']};
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['scrollbar_handle']};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['scrollbar_handle_hover']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['scrollbar']};
            height: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['scrollbar_handle']};
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['scrollbar_handle_hover']};
        }}
        
        /* ===== PROGRESS BARS ===== */
        QProgressBar {{
            border: 1px solid {colors['input_border']};
            border-radius: 6px;
            text-align: center;
            background-color: {colors['input_background']};
            color: {colors['text_primary']};
            height: 20px;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 5px;
        }}
        
        /* ===== LIST VIEWS ===== */
        QListView, QListWidget {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['input_border']};
            border-radius: 6px;
            outline: none;
            font-size: 10pt;
        }}
        
        QListView::item, QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {colors['table_border']};
        }}
        
        QListView::item:selected, QListWidget::item:selected {{
            background-color: {colors['table_row_selected']};
            color: white;
        }}
        
        QListView::item:hover, QListWidget::item:hover {{
            background-color: {colors['table_row_hover']};
        }}
        
        /* ===== TREE VIEWS ===== */
        QTreeView, QTreeWidget {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['input_border']};
            border-radius: 6px;
            outline: none;
            font-size: 10pt;
        }}
        
        QTreeView::item, QTreeWidget::item {{
            padding: 6px;
        }}
        
        QTreeView::item:selected, QTreeWidget::item:selected {{
            background-color: {colors['table_row_selected']};
            color: white;
        }}
        
        QTreeView::item:hover, QTreeWidget::item:hover {{
            background-color: {colors['table_row_hover']};
        }}
        
        /* ===== MENU BAR ===== */
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border-bottom: 1px solid {colors['input_border']};
            padding: 4px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['input_border']};
            padding: 6px;
            border-radius: 6px;
        }}
        
        QMenu::item {{
            padding: 8px 30px 8px 20px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {colors['input_border']};
            margin: 6px 8px;
        }}
        
        /* ===== STATUS BAR ===== */
        QStatusBar {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border-top: 1px solid {colors['input_border']};
            padding: 6px;
        }}
        
        /* ===== TOOL TIPS ===== */
        QToolTip {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['input_border']};
            border-radius: 4px;
            padding: 8px;
            font-size: 9pt;
        }}
        
        /* ===== SPIN BOXES ===== */
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors['input_background']};
            color: {colors['text_primary']};
            border: 2px solid {colors['input_border']};
            border-radius: 6px;
            padding: 8px;
            min-height: 40px;
            font-size: 10pt;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {colors['input_focus']};
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            border: none;
            background-color: {colors['primary']};
            border-radius: 3px;
            width: 20px;
            height: 15px;
        }}
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            border: none;
            background-color: {colors['primary']};
            border-radius: 3px;
            width: 20px;
            height: 15px;
        }}
        
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 5px solid white;
        }}
        
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid white;
        }}
        
        /* ===== CUSTOM WIDGET CLASSES ===== */
        
        /* Login Card */
        QWidget.login-card {{
            background-color: {colors['surface']};
            border: 2px solid {colors['primary']};
            border-radius: 10px;
            padding: 30px;
        }}
        
        /* Dashboard Card */
        QWidget.dashboard-card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['input_border']};
            border-radius: 10px;
            padding: 20px;
        }}
        
        QWidget.dashboard-card:hover {{
            border-color: {colors['primary']};
            box-shadow: 0 4px 12px {colors['shadow']};
        }}
        
        /* Sidebar */
        QWidget.sidebar {{
            background-color: {colors['surface']};
            border-right: 1px solid {colors['input_border']};
        }}
        
        /* Product Card */
        QWidget.product-card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['input_border']};
            border-radius: 8px;
            padding: 15px;
        }}
        
        QWidget.product-card:hover {{
            border-color: {colors['primary']};
            box-shadow: 0 2px 8px {colors['shadow']};
        }}
        
        /* Sale Item Row */
        QWidget.sale-item-row {{
            background-color: {colors['table_row_even']};
            border-bottom: 1px solid {colors['table_border']};
            padding: 10px;
            border-radius: 4px;
        }}
        
        QWidget.sale-item-row:hover {{
            background-color: {colors['table_row_hover']};
        }}
        
        /* Receipt Preview */
        QWidget.receipt-preview {{
            background-color: white;
            color: black;
            border: 2px dashed {colors['input_border']};
            border-radius: 8px;
            padding: 20px;
            font-family: "Courier New", monospace;
        }}
        
        /* Customer Display */
        QWidget.customer-display {{
            background-color: #000000;
            color: #00FF00;
            font-family: "Courier New", monospace;
            font-size: 14pt;
            border: 3px solid {colors['primary']};
            border-radius: 8px;
            padding: 15px;
        }}
        
        /* Barcode Scanner Input */
        QLineEdit.barcode-input {{
            font-size: 14pt;
            font-weight: bold;
            letter-spacing: 2px;
            text-align: center;
            border: 3px solid {colors['primary']};
        }}
        
        /* POS Numeric Display */
        QLineEdit.pos-display {{
            background-color: #000000;
            color: #00FF00;
            font-family: "Courier New", monospace;
            font-size: 18pt;
            font-weight: bold;
            text-align: right;
            border: 3px solid {colors['primary']};
            border-radius: 8px;
            padding: 15px;
        }}
        
        /* POS Button Grid */
        QWidget.pos-buttons {{
            background-color: {colors['surface']};
            border-radius: 8px;
            padding: 10px;
        }}
        
        /* Keyboard Key */
        QPushButton.keyboard-key {{
            background-color: {colors['input_background']};
            color: {colors['text_primary']};
            border: 1px solid {colors['input_border']};
            border-radius: 4px;
            padding: 15px;
            font-size: 12pt;
            font-weight: normal;
            min-width: 60px;
            min-height: 60px;
        }}
        
        QPushButton.keyboard-key:hover {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QPushButton.keyboard-key:pressed {{
            background-color: {colors['primary_dark']};
        }}
        
        /* Price Display */
        QLabel.price {{
            color: {colors['primary']};
            font-size: 14pt;
            font-weight: bold;
        }}
        
        QLabel.price-total {{
            color: {colors['success']};
            font-size: 16pt;
            font-weight: bold;
        }}
        
        /* Stock Status */
        QLabel.stock-in {{
            color: {colors['success']};
            font-weight: bold;
        }}
        
        QLabel.stock-low {{
            color: {colors['warning']};
            font-weight: bold;
        }}
        
        QLabel.stock-out {{
            color: {colors['error']};
            font-weight: bold;
        }}
        
        /* Status Indicators */
        QLabel.status-active {{
            color: {colors['success']};
            font-weight: bold;
        }}
        
        QLabel.status-inactive {{
            color: {colors['text_disabled']};
            font-weight: bold;
        }}
        
        QLabel.status-pending {{
            color: {colors['warning']};
            font-weight: bold;
        }}
        
        /* Arabic Text Support */
        QLabel[lang="ar"], QLineEdit[lang="ar"], QTextEdit[lang="ar"] {{
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 11pt;
        }}
        
        /* Right-to-Left Support */
        QWidget[layoutDirection="rtl"] * {{
            text-align: right;
        }}
        
        QWidget[layoutDirection="rtl"] QPushButton {{
            padding: 10px 20px;
        }}
        
        /* ===== SPECIFIC COMPONENTS ===== */
        
        /* Login Logo */
        QLabel.logo {{
            font-size: 24pt;
            font-weight: bold;
            color: {colors['primary']};
            padding: 20px 0;
        }}
        
        /* Dashboard Stat */
        QLabel.stat-value {{
            font-size: 24pt;
            font-weight: bold;
            color: {colors['primary']};
        }}
        
        QLabel.stat-label {{
            font-size: 10pt;
            color: {colors['text_secondary']};
        }}
        
        /* Sidebar Menu */
        QPushButton.menu-button {{
            background-color: transparent;
            color: {colors['text_primary']};
            text-align: left;
            padding: 12px 20px;
            border-radius: 0;
            border-left: 4px solid transparent;
            font-weight: normal;
        }}
        
        QPushButton.menu-button:hover {{
            background-color: rgba(231, 76, 60, 0.1);
            border-left: 4px solid {colors['primary']};
        }}
        
        QPushButton.menu-button:checked {{
            background-color: {colors['primary']};
            color: white;
            border-left: 4px solid {colors['primary']};
        }}
        
        /* Sidebar Icon */
        QLabel.menu-icon {{
            font-size: 14pt;
            padding-right: 10px;
        }}
        
        /* Notification Badge */
        QLabel.badge {{
            background-color: {colors['error']};
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 8pt;
            font-weight: bold;
            min-width: 20px;
        }}
        """
    
    @classmethod
    def apply_font(cls, app):
        """
        Apply application-wide font settings.
        
        Args:
            app: QApplication instance
        """
        # Try to load Arabic-supporting fonts
        font_families = ["Segoe UI", "Arial", "Tahoma", "DejaVu Sans"]
        
        # Check for Arabic font support
        for font_family in font_families:
            if font_family in QFontDatabase.families():
                font = QFont(font_family)
                font.setPointSize(10)
                app.setFont(font)
                return
        
        # Fallback to default font
        font = app.font()
        font.setPointSize(10)
        app.setFont(font)


# Utility function to apply theme to application
def apply_theme(app, theme_name='dark'):
    """
    Apply theme to the entire application.
    
    Args:
        app: QApplication instance
        theme_name: 'dark' or 'light'
    """
    stylesheet = TwinxTheme.get_stylesheet(theme_name)
    app.setStyleSheet(stylesheet)
    
    # Apply font
    TwinxTheme.apply_font(app)


if __name__ == "__main__":
    # Test the theme
    import sys
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget
    
    app = QApplication(sys.argv)
    
    # Create a test window
    window = QWidget()
    window.setWindowTitle("Twinx Theme Test")
    window.setGeometry(100, 100, 800, 600)
    
    layout = QVBoxLayout()
    
    # Add test widgets
    label = QLabel("Test Label")
    button = QPushButton("Test Button")
    button.setProperty("class", "primary")
    
    line_edit = QLineEdit("Test input")
    
    # Create table
    table = QTableWidget(5, 3)
    table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
    
    layout.addWidget(label)
    layout.addWidget(button)
    layout.addWidget(line_edit)
    layout.addWidget(table)
    
    window.setLayout(layout)
    
    # Apply dark theme
    apply_theme(app, 'dark')
    
    window.show()
    sys.exit(app.exec())