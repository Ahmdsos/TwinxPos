"""
Twinx POS System - Product Management Screen
File: product_screen.py

This module implements the product management screen with search, view, and edit capabilities.
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QComboBox,
    QMessageBox, QTextEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QGroupBox, QTabWidget, QSplitter, QScrollArea,
    QProgressBar, QToolButton, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QAction

from product_controller import ProductController
from translations import TranslationManager
from config_manager import ConfigManager
# Add these imports at the top
import os
import csv
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QTextEdit, QCheckBox, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QTabWidget, QGroupBox
)
from PyQt6.QtCore import Qt


class ProductFormDialog(QDialog):
    """Dialog for adding/editing products (Complete Edition)."""
    
    def __init__(self, db_manager, translation_manager, product_data=None, parent=None):
        """
        Initialize product form dialog with ALL fields.
        
        Args:
            db_manager: Database manager
            translation_manager: Translation manager
            product_data: Existing product data for editing (None for new)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.db = db_manager
        self.translator = translation_manager
        self.product_data = product_data
        self.is_edit = product_data is not None
        
        self.setup_ui()
        self.setup_window()
        
        if self.is_edit:
            self.load_existing_data()
    
    def setup_window(self):
        """Setup window properties."""
        if self.is_edit:
            self.setWindowTitle(self.translator.get('edit_product'))
        else:
            self.setWindowTitle(self.translator.get('add_new_product'))
        
        self.setMinimumSize(900, 700)
        self.setModal(True)
    
    def setup_ui(self):
        """Setup the user interface with tabs for all fields."""
        layout = QVBoxLayout()
        
        # Tab widget for organization
        tabs = QTabWidget()
        
        # Tab 1: Basic Information
        basic_tab = QWidget()
        basic_layout = QFormLayout()
        
        # Required Fields Group
        required_group = QGroupBox("Required Information")
        required_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        required_layout.addRow(self.translator.get('product_name') + " *:", self.name_input)
        
        self.sku_input = QLineEdit()
        required_layout.addRow(self.translator.get('sku') + ":", self.sku_input)
        
        self.barcode_input = QLineEdit()
        required_layout.addRow(self.translator.get('barcode') + ":", self.barcode_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['simple', 'variable', 'grouped', 'digital'])
        required_layout.addRow(self.translator.get('type') + ":", self.type_combo)
        
        self.category_input = QLineEdit()
        required_layout.addRow(self.translator.get('category') + ":", self.category_input)
        
        self.subcategory_input = QLineEdit()
        required_layout.addRow("Subcategory:", self.subcategory_input)
        
        required_group.setLayout(required_layout)
        basic_layout.addRow(required_group)
        
        # Brand & Manufacturer Group
        brand_group = QGroupBox("Brand & Manufacturer")
        brand_layout = QFormLayout()
        
        self.brand_input = QLineEdit()
        brand_layout.addRow(self.translator.get('brand') + ":", self.brand_input)
        
        self.manufacturer_input = QLineEdit()
        brand_layout.addRow("Manufacturer:", self.manufacturer_input)
        
        self.country_input = QLineEdit()
        brand_layout.addRow("Country of Origin:", self.country_input)
        
        brand_group.setLayout(brand_layout)
        basic_layout.addRow(brand_group)
        
        # Product Identification Group
        id_group = QGroupBox("Product Identification")
        id_layout = QFormLayout()
        
        self.upc_input = QLineEdit()
        id_layout.addRow("UPC:", self.upc_input)
        
        self.isbn_input = QLineEdit()
        id_layout.addRow("ISBN:", self.isbn_input)
        
        self.mpn_input = QLineEdit()
        id_layout.addRow("MPN:", self.mpn_input)
        
        self.product_code_input = QLineEdit()
        id_layout.addRow("Product Code:", self.product_code_input)
        
        id_group.setLayout(id_layout)
        basic_layout.addRow(id_group)
        
        basic_tab.setLayout(basic_layout)
        
        # Tab 2: Pricing
        pricing_tab = QWidget()
        pricing_layout = QFormLayout()
        
        # Pricing Group
        price_group = QGroupBox("Pricing")
        price_layout = QFormLayout()
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.00, 999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("$ ")
        price_layout.addRow(self.translator.get('price') + " *:", self.price_input)
        
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0.00, 999999.99)
        self.cost_input.setDecimals(2)
        self.cost_input.setPrefix("$ ")
        price_layout.addRow(self.translator.get('cost_price') + ":", self.cost_input)
        
        self.wholesale_input = QDoubleSpinBox()
        self.wholesale_input.setRange(0.00, 999999.99)
        self.wholesale_input.setDecimals(2)
        self.wholesale_input.setPrefix("$ ")
        price_layout.addRow("Wholesale Price:", self.wholesale_input)
        
        self.suggested_price_input = QDoubleSpinBox()
        self.suggested_price_input.setRange(0.00, 999999.99)
        self.suggested_price_input.setDecimals(2)
        self.suggested_price_input.setPrefix("$ ")
        price_layout.addRow("Suggested Retail:", self.suggested_price_input)
        
        price_group.setLayout(price_layout)
        pricing_layout.addRow(price_group)
        
        # Sale Pricing Group
        sale_group = QGroupBox("Sale Pricing")
        sale_layout = QFormLayout()
        
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setRange(0.00, 999999.99)
        self.sale_price_input.setDecimals(2)
        self.sale_price_input.setPrefix("$ ")
        sale_layout.addRow("Sale Price:", self.sale_price_input)
        
        self.sale_start_input = QLineEdit()
        self.sale_start_input.setPlaceholderText("YYYY-MM-DD")
        sale_layout.addRow("Sale Start Date:", self.sale_start_input)
        
        self.sale_end_input = QLineEdit()
        self.sale_end_input.setPlaceholderText("YYYY-MM-DD")
        sale_layout.addRow("Sale End Date:", self.sale_end_input)
        
        sale_group.setLayout(sale_layout)
        pricing_layout.addRow(sale_group)
        
        # Tax Group
        tax_group = QGroupBox("Tax")
        tax_layout = QFormLayout()
        
        self.tax_combo = QComboBox()
        self.tax_combo.addItems(['standard', 'reduced', 'zero', 'exempt'])
        tax_layout.addRow("Tax Class:", self.tax_combo)
        
        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setRange(0.00, 100.00)
        self.tax_rate_input.setDecimals(2)
        self.tax_rate_input.setSuffix(" %")
        self.tax_rate_input.setValue(15.00)
        tax_layout.addRow("Tax Rate:", self.tax_rate_input)
        
        self.taxable_check = QCheckBox("Taxable")
        self.taxable_check.setChecked(True)
        tax_layout.addRow("", self.taxable_check)
        
        tax_group.setLayout(tax_layout)
        pricing_layout.addRow(tax_group)
        
        pricing_tab.setLayout(pricing_layout)
        
        # Tab 3: Inventory
        inventory_tab = QWidget()
        inventory_layout = QFormLayout()
        
        # Stock Management Group
        stock_group = QGroupBox("Stock Management")
        stock_layout = QFormLayout()
        
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 999999)
        stock_layout.addRow(self.translator.get('stock_quantity') + ":", self.stock_input)
        
        self.low_stock_input = QSpinBox()
        self.low_stock_input.setRange(0, 9999)
        self.low_stock_input.setValue(5)
        stock_layout.addRow(self.translator.get('low_stock_threshold') + ":", self.low_stock_input)
        
        self.manage_stock_check = QCheckBox("Manage Stock")
        self.manage_stock_check.setChecked(True)
        stock_layout.addRow("", self.manage_stock_check)
        
        self.allow_backorders_check = QCheckBox("Allow Backorders")
        stock_layout.addRow("", self.allow_backorders_check)
        
        stock_group.setLayout(stock_layout)
        inventory_layout.addRow(stock_group)
        
        # Physical Properties Group
        physical_group = QGroupBox("Physical Properties")
        physical_layout = QFormLayout()
        
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0.000, 999.999)
        self.weight_input.setDecimals(3)
        self.weight_input.setSuffix(" kg")
        physical_layout.addRow(self.translator.get('weight') + ":", self.weight_input)
        
        dimensions_layout = QHBoxLayout()
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(0.00, 999.99)
        self.length_input.setDecimals(2)
        self.length_input.setSuffix(" cm")
        dimensions_layout.addWidget(QLabel("Length:"))
        dimensions_layout.addWidget(self.length_input)
        
        self.width_input = QDoubleSpinBox()
        self.width_input.setRange(0.00, 999.99)
        self.width_input.setDecimals(2)
        self.width_input.setSuffix(" cm")
        dimensions_layout.addWidget(QLabel("Width:"))
        dimensions_layout.addWidget(self.width_input)
        
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(0.00, 999.99)
        self.height_input.setDecimals(2)
        self.height_input.setSuffix(" cm")
        dimensions_layout.addWidget(QLabel("Height:"))
        dimensions_layout.addWidget(self.height_input)
        
        physical_layout.addRow("Dimensions:", dimensions_layout)
        
        self.volume_input = QDoubleSpinBox()
        self.volume_input.setRange(0.000, 999.999)
        self.volume_input.setDecimals(3)
        self.volume_input.setSuffix(" L")
        physical_layout.addRow("Volume:", self.volume_input)
        
        physical_group.setLayout(physical_layout)
        inventory_layout.addRow(physical_group)
        
        # Expiry & Batch Group
        expiry_group = QGroupBox("Expiry & Batch Tracking")
        expiry_layout = QFormLayout()
        
        self.shelf_life_input = QSpinBox()
        self.shelf_life_input.setRange(0, 3650)
        self.shelf_life_input.setSuffix(" days")
        expiry_layout.addRow("Shelf Life:", self.shelf_life_input)
        
        self.expiry_alert_input = QSpinBox()
        self.expiry_alert_input.setRange(0, 365)
        self.expiry_alert_input.setValue(30)
        self.expiry_alert_input.setSuffix(" days")
        expiry_layout.addRow("Expiry Alert Days:", self.expiry_alert_input)
        
        self.batch_tracking_check = QCheckBox("Batch Tracking Required")
        expiry_layout.addRow("", self.batch_tracking_check)
        
        self.serial_tracking_check = QCheckBox("Serial Tracking Required")
        expiry_layout.addRow("", self.serial_tracking_check)
        
        expiry_group.setLayout(expiry_layout)
        inventory_layout.addRow(expiry_group)
        
        inventory_tab.setLayout(inventory_layout)
        
        # Tab 4: Description & SEO
        desc_tab = QWidget()
        desc_layout = QVBoxLayout()
        
        # Description Group
        desc_group = QGroupBox("Descriptions")
        desc_group_layout = QVBoxLayout()
        
        desc_label = QLabel(self.translator.get('description') + ":")
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(150)
        
        short_desc_label = QLabel(self.translator.get('short_description') + ":")
        self.short_desc_input = QTextEdit()
        self.short_desc_input.setMaximumHeight(100)
        
        desc_group_layout.addWidget(desc_label)
        desc_group_layout.addWidget(self.desc_input)
        desc_group_layout.addWidget(short_desc_label)
        desc_group_layout.addWidget(self.short_desc_input)
        
        desc_group.setLayout(desc_group_layout)
        desc_layout.addWidget(desc_group)
        
        # SEO Group
        seo_group = QGroupBox("SEO & Metadata")
        seo_layout = QFormLayout()
        
        self.meta_title_input = QLineEdit()
        seo_layout.addRow("Meta Title:", self.meta_title_input)
        
        self.meta_desc_input = QTextEdit()
        self.meta_desc_input.setMaximumHeight(80)
        seo_layout.addRow("Meta Description:", self.meta_desc_input)
        
        self.meta_keywords_input = QLineEdit()
        self.meta_keywords_input.setPlaceholderText("comma, separated, keywords")
        seo_layout.addRow("Meta Keywords:", self.meta_keywords_input)
        
        seo_group.setLayout(seo_layout)
        desc_layout.addWidget(seo_group)
        
        desc_layout.addStretch()
        desc_tab.setLayout(desc_layout)
        
        # Tab 5: Additional Information
        additional_tab = QWidget()
        additional_layout = QFormLayout()
        
        # Warranty Group
        warranty_group = QGroupBox("Warranty & Support")
        warranty_layout = QFormLayout()
        
        self.warranty_period_input = QSpinBox()
        self.warranty_period_input.setRange(0, 120)
        self.warranty_period_input.setSuffix(" months")
        warranty_layout.addRow("Warranty Period:", self.warranty_period_input)
        
        self.warranty_type_input = QLineEdit()
        warranty_layout.addRow("Warranty Type:", self.warranty_type_input)
        
        self.has_warranty_check = QCheckBox("Has Warranty")
        warranty_layout.addRow("", self.has_warranty_check)
        
        self.support_email_input = QLineEdit()
        warranty_layout.addRow("Support Email:", self.support_email_input)
        
        self.support_phone_input = QLineEdit()
        warranty_layout.addRow("Support Phone:", self.support_phone_input)
        
        warranty_group.setLayout(warranty_layout)
        additional_layout.addRow(warranty_group)
        
        # Supplier Group
        supplier_group = QGroupBox("Supplier Information")
        supplier_layout = QFormLayout()
        
        # Load suppliers for dropdown
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("Select Supplier", 0)
        
        try:
            suppliers = self.db.execute_query("SELECT id, name FROM wholesale_partners WHERE status = 'active' ORDER BY name")
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier['name'], supplier['id'])
        except:
            pass
        
        supplier_layout.addRow("Supplier:", self.supplier_combo)
        
        self.supplier_sku_input = QLineEdit()
        supplier_layout.addRow("Supplier SKU:", self.supplier_sku_input)
        
        self.lead_time_input = QSpinBox()
        self.lead_time_input.setRange(0, 365)
        self.lead_time_input.setSuffix(" days")
        supplier_layout.addRow("Lead Time:", self.lead_time_input)
        
        supplier_group.setLayout(supplier_layout)
        additional_layout.addRow(supplier_group)
        
        # Shipping Group
        shipping_group = QGroupBox("Shipping")
        shipping_layout = QFormLayout()
        
        self.requires_shipping_check = QCheckBox("Requires Shipping")
        self.requires_shipping_check.setChecked(True)
        shipping_layout.addRow("", self.requires_shipping_check)
        
        self.shipping_class_input = QLineEdit()
        shipping_layout.addRow("Shipping Class:", self.shipping_class_input)
        
        self.shipping_weight_input = QDoubleSpinBox()
        self.shipping_weight_input.setRange(0.000, 999.999)
        self.shipping_weight_input.setDecimals(3)
        self.shipping_weight_input.setSuffix(" kg")
        shipping_layout.addRow("Shipping Weight:", self.shipping_weight_input)
        
        shipping_group.setLayout(shipping_layout)
        additional_layout.addRow(shipping_group)
        
        additional_tab.setLayout(additional_layout)
        
        # Add all tabs
        tabs.addTab(basic_tab, "Basic")
        tabs.addTab(pricing_tab, "Pricing")
        tabs.addTab(inventory_tab, "Inventory")
        tabs.addTab(desc_tab, "Description & SEO")
        tabs.addTab(additional_tab, "Additional")
        
        layout.addWidget(tabs)
        
        # Status & Actions
        status_layout = QHBoxLayout()
        
        self.active_checkbox = QCheckBox(self.translator.get('active'))
        self.active_checkbox.setChecked(True)
        
        self.featured_checkbox = QCheckBox("Featured Product")
        
        status_layout.addWidget(self.active_checkbox)
        status_layout.addWidget(self.featured_checkbox)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton(self.translator.get('save'))
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self.on_save)
        
        self.cancel_btn = QPushButton(self.translator.get('cancel'))
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_existing_data(self):
        """Load existing product data into ALL form fields (SAFE VERSION)."""
        if not self.product_data:
            return
        
        # Helper function to safely convert to float
        def safe_float(value, default=0.0):
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default
        
        # Helper function to safely convert to int
        def safe_int(value, default=0):
            try:
                return int(value) if value is not None else default
            except (ValueError, TypeError):
                return default
        
        # Helper function to get string or empty
        def safe_str(value):
            return str(value) if value is not None else ""
        
        # Basic Tab
        self.name_input.setText(safe_str(self.product_data.get('name')))
        self.sku_input.setText(safe_str(self.product_data.get('sku')))
        self.barcode_input.setText(safe_str(self.product_data.get('barcode')))
        
        product_type = self.product_data.get('type', 'simple')
        index = self.type_combo.findText(product_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        self.category_input.setText(safe_str(self.product_data.get('category')))
        self.subcategory_input.setText(safe_str(self.product_data.get('subcategory')))
        self.brand_input.setText(safe_str(self.product_data.get('brand')))
        self.manufacturer_input.setText(safe_str(self.product_data.get('manufacturer')))
        self.country_input.setText(safe_str(self.product_data.get('country_of_origin')))
        self.upc_input.setText(safe_str(self.product_data.get('upc')))
        self.isbn_input.setText(safe_str(self.product_data.get('isbn')))
        self.mpn_input.setText(safe_str(self.product_data.get('mpn')))
        self.product_code_input.setText(safe_str(self.product_data.get('product_code')))
        
        # Pricing Tab
        self.price_input.setValue(safe_float(self.product_data.get('price', 0.00)))
        self.cost_input.setValue(safe_float(self.product_data.get('cost_price', 0.00)))
        self.wholesale_input.setValue(safe_float(self.product_data.get('wholesale_price', 0.00)))
        self.suggested_price_input.setValue(safe_float(self.product_data.get('suggested_retail_price', 0.00)))
        self.sale_price_input.setValue(safe_float(self.product_data.get('sale_price', 0.00)))
        self.sale_start_input.setText(safe_str(self.product_data.get('sale_start_date')))
        self.sale_end_input.setText(safe_str(self.product_data.get('sale_end_date')))
        
        tax_class = self.product_data.get('tax_class', 'standard')
        index = self.tax_combo.findText(tax_class)
        if index >= 0:
            self.tax_combo.setCurrentIndex(index)
        
        self.tax_rate_input.setValue(safe_float(self.product_data.get('tax_rate', 15.00)))
        self.taxable_check.setChecked(bool(self.product_data.get('is_taxable', True)))
        
        # Inventory Tab
        self.stock_input.setValue(safe_int(self.product_data.get('stock_quantity', 0)))
        self.low_stock_input.setValue(safe_int(self.product_data.get('low_stock_threshold', 5)))
        self.manage_stock_check.setChecked(bool(self.product_data.get('manage_stock', True)))
        self.allow_backorders_check.setChecked(bool(self.product_data.get('allow_backorders', False)))
        self.weight_input.setValue(safe_float(self.product_data.get('weight_kg', 0.000)))
        self.length_input.setValue(safe_float(self.product_data.get('length_cm', 0.00)))
        self.width_input.setValue(safe_float(self.product_data.get('width_cm', 0.00)))
        self.height_input.setValue(safe_float(self.product_data.get('height_cm', 0.00)))
        self.volume_input.setValue(safe_float(self.product_data.get('volume_liters', 0.000)))
        self.shelf_life_input.setValue(safe_int(self.product_data.get('shelf_life_days', 0)))
        self.expiry_alert_input.setValue(safe_int(self.product_data.get('expiry_alert_days', 30)))
        self.batch_tracking_check.setChecked(bool(self.product_data.get('batch_tracking_required', False)))
        self.serial_tracking_check.setChecked(bool(self.product_data.get('serial_tracking_required', False)))
        
        # Description & SEO Tab
        self.desc_input.setText(safe_str(self.product_data.get('description')))
        self.short_desc_input.setText(safe_str(self.product_data.get('short_description')))
        self.meta_title_input.setText(safe_str(self.product_data.get('meta_title')))
        self.meta_desc_input.setText(safe_str(self.product_data.get('meta_description')))
        self.meta_keywords_input.setText(safe_str(self.product_data.get('meta_keywords')))
        
        # Additional Tab
        self.warranty_period_input.setValue(safe_int(self.product_data.get('warranty_period_months', 0)))
        self.warranty_type_input.setText(safe_str(self.product_data.get('warranty_type')))
        self.has_warranty_check.setChecked(bool(self.product_data.get('has_warranty', False)))
        self.support_email_input.setText(safe_str(self.product_data.get('support_email')))
        self.support_phone_input.setText(safe_str(self.product_data.get('support_phone')))
        
        supplier_id = self.product_data.get('supplier_id')
        if supplier_id:
            index = self.supplier_combo.findData(supplier_id)
            if index >= 0:
                self.supplier_combo.setCurrentIndex(index)
        
        self.supplier_sku_input.setText(safe_str(self.product_data.get('supplier_sku')))
        self.lead_time_input.setValue(safe_int(self.product_data.get('lead_time_days', 0)))
        self.requires_shipping_check.setChecked(bool(self.product_data.get('requires_shipping', True)))
        self.shipping_class_input.setText(safe_str(self.product_data.get('shipping_class')))
        self.shipping_weight_input.setValue(safe_float(self.product_data.get('shipping_weight', 0.000)))
        
        # Status
        self.active_checkbox.setChecked(bool(self.product_data.get('is_active', True)))
        self.featured_checkbox.setChecked(bool(self.product_data.get('is_featured', False)))
    
    def get_form_data(self):
        """Get data from ALL form fields (SAFE VERSION)."""
        def safe_float(value):
            try:
                return float(value) if value > 0 else None
            except (ValueError, TypeError):
                return None
        
        return {
            # Basic Information
            'name': self.name_input.text().strip(),
            'sku': self.sku_input.text().strip() or None,
            'barcode': self.barcode_input.text().strip() or None,
            'type': self.type_combo.currentText(),
            'category': self.category_input.text().strip() or None,
            'subcategory': self.subcategory_input.text().strip() or None,
            'brand': self.brand_input.text().strip() or None,
            'manufacturer': self.manufacturer_input.text().strip() or None,
            'country_of_origin': self.country_input.text().strip() or None,
            'upc': self.upc_input.text().strip() or None,
            'isbn': self.isbn_input.text().strip() or None,
            'mpn': self.mpn_input.text().strip() or None,
            'product_code': self.product_code_input.text().strip() or None,
            
            # Pricing
            'price': float(self.price_input.value()),
            'cost_price': safe_float(self.cost_input.value()),
            'wholesale_price': safe_float(self.wholesale_input.value()),
            'suggested_retail_price': safe_float(self.suggested_price_input.value()),
            'sale_price': safe_float(self.sale_price_input.value()),
            'sale_start_date': self.sale_start_input.text().strip() or None,
            'sale_end_date': self.sale_end_input.text().strip() or None,
            'tax_class': self.tax_combo.currentText(),
            'tax_rate': float(self.tax_rate_input.value()),
            'is_taxable': self.taxable_check.isChecked(),
            
            # Inventory
            'stock_quantity': self.stock_input.value(),
            'stock_status': 'instock' if self.stock_input.value() > 0 else 'outofstock',
            'low_stock_threshold': self.low_stock_input.value(),
            'manage_stock': self.manage_stock_check.isChecked(),
            'allow_backorders': self.allow_backorders_check.isChecked(),
            'weight_kg': safe_float(self.weight_input.value()),
            'length_cm': safe_float(self.length_input.value()),
            'width_cm': safe_float(self.width_input.value()),
            'height_cm': safe_float(self.height_input.value()),
            'volume_liters': safe_float(self.volume_input.value()),
            'dimensions_unit': 'cm',
            'shelf_life_days': self.shelf_life_input.value(),
            'expiry_alert_days': self.expiry_alert_input.value(),
            'batch_tracking_required': self.batch_tracking_check.isChecked(),
            'serial_tracking_required': self.serial_tracking_check.isChecked(),
            
            # Description & SEO
            'description': self.desc_input.toPlainText().strip() or None,
            'short_description': self.short_desc_input.toPlainText().strip() or None,
            'meta_title': self.meta_title_input.text().strip() or None,
            'meta_description': self.meta_desc_input.toPlainText().strip() or None,
            'meta_keywords': self.meta_keywords_input.text().strip() or None,
            
            # Additional
            'warranty_period_months': self.warranty_period_input.value(),
            'warranty_type': self.warranty_type_input.text().strip() or None,
            'has_warranty': self.has_warranty_check.isChecked(),
            'support_email': self.support_email_input.text().strip() or None,
            'support_phone': self.support_phone_input.text().strip() or None,
            'supplier_id': self.supplier_combo.currentData() if self.supplier_combo.currentData() > 0 else None,
            'supplier_sku': self.supplier_sku_input.text().strip() or None,
            'lead_time_days': self.lead_time_input.value(),
            'requires_shipping': self.requires_shipping_check.isChecked(),
            'shipping_class': self.shipping_class_input.text().strip() or None,
            'shipping_weight': safe_float(self.shipping_weight_input.value()),
            'is_virtual': False,
            'is_downloadable': False,
            
            # Status
            'is_active': self.active_checkbox.isChecked(),
            'is_featured': self.featured_checkbox.isChecked(),
        }
    
    def validate_form(self):
        """Validate form data."""
        data = self.get_form_data()
        
        # Required fields
        if not data['name']:
            QMessageBox.warning(self, "Validation Error", 
                               self.translator.get('product_name') + " is required.")
            return False
        
        if data['price'] <= 0:
            QMessageBox.warning(self, "Validation Error", 
                               self.translator.get('price') + " must be greater than 0.")
            return False
        
        if data['stock_quantity'] < 0:
            QMessageBox.warning(self, "Validation Error", 
                               self.translator.get('stock_quantity') + " cannot be negative.")
            return False
        
        return True
    
    def on_save(self):
        """Handle save button click."""
        if not self.validate_form():
            return
        
        self.accept()
    
    def get_result(self):
        """Get the result data from dialog."""
        return {
            'success': True,
            'data': self.get_form_data()
        }


class VariationsViewDialog(QDialog):
    """Dialog for viewing product variations."""
    
    def __init__(self, product_controller, product_id, translation_manager, parent=None):
        """
        Initialize variations view dialog.
        
        Args:
            product_controller: ProductController instance
            product_id: Product ID
            translation_manager: Translation manager
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.product_controller = product_controller
        self.product_id = product_id
        self.translator = translation_manager
        
        self.setup_ui()
        self.setup_window()
        self.load_variations()
    
    def setup_window(self):
        """Setup window properties."""
        self.setWindowTitle(self.translator.get('product_variations'))
        self.setMinimumSize(800, 500)
        self.setModal(True)
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Product info
        info_layout = QHBoxLayout()
        
        # Get product name for display
        query = "SELECT name FROM products WHERE id = ?"
        result = self.product_controller.db.execute_query(query, (self.product_id,))
        product_name = result[0]['name'] if result else f"Product #{self.product_id}"
        
        name_label = QLabel(f"<b>{product_name}</b> (ID: {self.product_id})")
        info_layout.addWidget(name_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # Variations table
        self.variations_table = QTableWidget()
        self.variations_table.setColumnCount(7)
        self.variations_table.setHorizontalHeaderLabels([
            self.translator.get('name'),
            self.translator.get('sku'),
            self.translator.get('price'),
            self.translator.get('cost_price'),
            self.translator.get('stock_quantity'),
            self.translator.get('status'),
            self.translator.get('created')
        ])
        
        # Configure table
        header = self.variations_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.variations_table.setAlternatingRowColors(True)
        self.variations_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.variations_table)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total variations: 0")
        self.active_label = QLabel("Active: 0")
        self.total_stock_label = QLabel("Total stock: 0")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.active_label)
        stats_layout.addWidget(self.total_stock_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Close button
        close_btn = QPushButton(self.translator.get('close'))
        close_btn.clicked.connect(self.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_variations(self):
        """Load variations from database."""
        result = self.product_controller.get_product_variations(self.product_id)
        
        if not result['success']:
            QMessageBox.warning(self, "Error", result['message'])
            return
        
        variations = result['variations']
        
        # Update table
        self.variations_table.setRowCount(len(variations))
        
        total_stock = 0
        active_count = 0
        
        for row, variation in enumerate(variations):
            # Name
            name_item = QTableWidgetItem(variation['name'])
            self.variations_table.setItem(row, 0, name_item)
            
            # SKU
            sku_item = QTableWidgetItem(variation['sku'] or "")
            self.variations_table.setItem(row, 1, sku_item)
            
            # Price
            price_item = QTableWidgetItem(f"${variation['price']:.2f}")
            self.variations_table.setItem(row, 2, price_item)
            
            # Cost Price
            cost_price = variation.get('cost_price')
            cost_item = QTableWidgetItem(f"${cost_price:.2f}" if cost_price else "")
            self.variations_table.setItem(row, 3, cost_item)
            
            # Stock Quantity
            stock_qty = variation.get('stock_quantity', 0)
            stock_item = QTableWidgetItem(str(stock_qty))
            
            # Color code based on stock
            if stock_qty <= variation.get('low_stock_threshold', 5):
                stock_item.setForeground(QColor('#f39c12'))
            elif stock_qty == 0:
                stock_item.setForeground(QColor('#e74c3c'))
            
            self.variations_table.setItem(row, 4, stock_item)
            total_stock += stock_qty
            
            # Status
            status_text = self.translator.get('active') if variation['is_active'] else self.translator.get('inactive')
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor('#27ae60') if variation['is_active'] else QColor('#7f8c8d'))
            self.variations_table.setItem(row, 5, status_item)
            
            if variation['is_active']:
                active_count += 1
            
            # Created date
            created_date = variation['created_at'][:10] if variation.get('created_at') else ""
            created_item = QTableWidgetItem(created_date)
            self.variations_table.setItem(row, 6, created_item)
        
        # Update statistics
        self.total_label.setText(f"Total variations: {len(variations)}")
        self.active_label.setText(f"Active: {active_count}")
        self.total_stock_label.setText(f"Total stock: {total_stock}")

class ProductScreen(QWidget):
    """Product management screen for Twinx POS."""
    
    # Signals
    product_selected = pyqtSignal(int)  # Emitted when product is selected
    refresh_requested = pyqtSignal()    # Emitted when data needs refresh
    
    def __init__(self, db_manager, translation_manager):
        """
        Initialize product screen.
        
        Args:
            db_manager: DatabaseManager instance
            translation_manager: TranslationManager instance
        """
        super().__init__()
        
        self.db_manager = db_manager
        self.translation_manager = translation_manager
        self.product_controller = ProductController(db_manager)
        
        self.current_language = self.translation_manager.get_current_lang()
        self.current_product_id = None
        
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setObjectName("productScreen")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header with title and actions
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel(self.translation_manager.get('products'))
        title_label.setObjectName("pageTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.new_product_btn = QPushButton(f"➕ {self.translation_manager.get('add_new')}")
        self.new_product_btn.setObjectName("primary")
        self.new_product_btn.clicked.connect(self.on_new_product)
        
        self.refresh_btn = QPushButton(f"🔄 {self.translation_manager.get('refresh')}")
        self.refresh_btn.setObjectName("secondary")
        self.refresh_btn.clicked.connect(self.on_refresh)
        
        self.export_btn = QPushButton(f"📤 {self.translation_manager.get('export')}")
        self.export_btn.setObjectName("secondary")
        self.export_btn.clicked.connect(self.on_export)
        
        button_layout.addWidget(self.new_product_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.export_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)
        header_frame.setLayout(header_layout)
        
        # Search bar
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText(self.translation_manager.get('search_products'))
        self.search_input.returnPressed.connect(self.on_search)
        
        search_btn = QPushButton(self.translation_manager.get('search'))
        search_btn.setObjectName("primary")
        search_btn.clicked.connect(self.on_search)
        
        # Filter dropdowns
        self.category_filter = QComboBox()
        self.category_filter.addItem(self.translation_manager.get('all_categories'), 0)
        self.category_filter.currentIndexChanged.connect(self.on_filter_changed)
        
        self.stock_filter = QComboBox()
        self.stock_filter.addItem(self.translation_manager.get('all_stock'), 'all')
        self.stock_filter.addItem(self.translation_manager.get('in_stock'), 'in_stock')
        self.stock_filter.addItem(self.translation_manager.get('low_stock'), 'low_stock')
        self.stock_filter.addItem(self.translation_manager.get('out_of_stock'), 'out_of_stock')
        self.stock_filter.currentIndexChanged.connect(self.on_filter_changed)
        
        search_layout.addWidget(self.search_input, stretch=2)
        search_layout.addWidget(QLabel(self.translation_manager.get('category') + ":"))
        search_layout.addWidget(self.category_filter)
        search_layout.addWidget(QLabel(self.translation_manager.get('stock') + ":"))
        search_layout.addWidget(self.stock_filter)
        search_layout.addWidget(search_btn)
        
        search_frame.setLayout(search_layout)
        
        # Splitter for table and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Products table
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.products_table = QTableWidget()
        self.products_table.setObjectName("productsTable")
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            self.translation_manager.get('product_name'),
            self.translation_manager.get('sku'),
            self.translation_manager.get('price'),
            self.translation_manager.get('stock_quantity'),
            self.translation_manager.get('category'),
            self.translation_manager.get('status')
        ])
        
        # Configure table
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.products_table.itemSelectionChanged.connect(self.on_product_selected)
        
        # Pagination controls
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 10, 0, 0)
        
        self.prev_page_btn = QPushButton("◀ " + self.translation_manager.get('previous'))
        self.prev_page_btn.setEnabled(False)
        self.prev_page_btn.clicked.connect(self.on_prev_page)
        
        self.page_label = QLabel("Page 1 of 1")
        
        self.next_page_btn = QPushButton(self.translation_manager.get('next') + " ▶")
        self.next_page_btn.setEnabled(False)
        self.next_page_btn.clicked.connect(self.on_next_page)
        
        pagination_layout.addWidget(self.prev_page_btn)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_page_btn)
        pagination_frame.setLayout(pagination_layout)
        
        table_layout.addWidget(self.products_table)
        table_layout.addWidget(pagination_frame)
        table_widget.setLayout(table_layout)
        
        # Right side: Product details
        details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(20, 0, 0, 0)
        
        self.details_frame = QFrame()
        self.details_frame.setObjectName("detailsFrame")
        self.details_frame.setVisible(False)
        
        details_header = QLabel(self.translation_manager.get('product_details'))
        details_header.setObjectName("detailsHeader")
        
        self.details_content = QLabel(self.translation_manager.get('select_product_to_view'))
        self.details_content.setWordWrap(True)
        self.details_content.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        details_buttons = QHBoxLayout()
        self.edit_btn = QPushButton(self.translation_manager.get('edit'))
        self.edit_btn.setObjectName("primary")
        self.edit_btn.clicked.connect(self.on_edit_product)
        
        self.delete_btn = QPushButton(self.translation_manager.get('delete'))
        self.delete_btn.setObjectName("danger")
        self.delete_btn.clicked.connect(self.on_delete_product)
        
        self.view_variations_btn = QPushButton(self.translation_manager.get('variations'))
        self.view_variations_btn.clicked.connect(self.on_view_variations)
        
        details_buttons.addWidget(self.edit_btn)
        details_buttons.addWidget(self.delete_btn)
        details_buttons.addWidget(self.view_variations_btn)
        details_buttons.addStretch()
        
        details_inner_layout = QVBoxLayout()
        details_inner_layout.addWidget(details_header)
        details_inner_layout.addWidget(self.details_content, stretch=1)
        details_inner_layout.addLayout(details_buttons)
        self.details_frame.setLayout(details_inner_layout)
        
        # Quick stats
        stats_frame = self.create_stats_frame()
        
        details_layout.addWidget(self.details_frame, stretch=2)
        details_layout.addWidget(stats_frame, stretch=1)
        details_widget.setLayout(details_layout)
        
        # Add widgets to splitter
        splitter.addWidget(table_widget)
        splitter.addWidget(details_widget)
        splitter.setSizes([600, 400])
        
        # Add to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(search_frame)
        main_layout.addWidget(splitter, stretch=1)
        
        self.setLayout(main_layout)
        
        # Initialize pagination
        self.current_page = 1
        self.page_size = 20
        self.total_products = 0
        
        # Set initial sizes
        self.setMinimumSize(1000, 600)
    
    def create_stats_frame(self):
        """Create statistics frame."""
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        stats_title = QLabel(self.translation_manager.get('quick_stats'))
        stats_title.setObjectName("statsTitle")
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Total products
        self.total_products_label = QLabel("0")
        self.total_products_label.setObjectName("statValue")
        stats_grid.addWidget(QLabel(self.translation_manager.get('total_products') + ":"), 0, 0)
        stats_grid.addWidget(self.total_products_label, 0, 1)
        
        # In stock
        self.in_stock_label = QLabel("0")
        self.in_stock_label.setObjectName("statValue")
        stats_grid.addWidget(QLabel(self.translation_manager.get('in_stock') + ":"), 1, 0)
        stats_grid.addWidget(self.in_stock_label, 1, 1)
        
        # Low stock
        self.low_stock_label = QLabel("0")
        self.low_stock_label.setObjectName("statValue")
        stats_grid.addWidget(QLabel(self.translation_manager.get('low_stock') + ":"), 2, 0)
        stats_grid.addWidget(self.low_stock_label, 2, 1)
        
        # Out of stock
        self.out_stock_label = QLabel("0")
        self.out_stock_label.setObjectName("statValue")
        stats_grid.addWidget(QLabel(self.translation_manager.get('out_of_stock') + ":"), 3, 0)
        stats_grid.addWidget(self.out_stock_label, 3, 1)
        
        stats_layout.addWidget(stats_title)
        stats_layout.addLayout(stats_grid)
        stats_layout.addStretch()
        
        # Refresh stats button
        refresh_stats_btn = QPushButton(self.translation_manager.get('refresh_stats'))
        refresh_stats_btn.clicked.connect(self.update_stats)
        stats_layout.addWidget(refresh_stats_btn)
        
        stats_frame.setLayout(stats_layout)
        return stats_frame
    
    def load_initial_data(self):
        """Load initial data including categories and first page."""
        self.load_categories()
        self.load_products_page()
        self.update_stats()
    
    def load_categories(self):
        """Load categories into filter dropdown."""
        try:
            query = "SELECT id, name FROM categories WHERE is_active = 1 ORDER BY name"
            categories = self.db_manager.execute_query(query)
            
            self.category_filter.clear()
            self.category_filter.addItem(self.translation_manager.get('all_categories'), 0)
            
            for category in categories:
                self.category_filter.addItem(category['name'], category['id'])
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def load_products_page(self):
        """Load products for current page with filters."""
        try:
            # Get filters
            search_text = self.search_input.text().strip()
            category_id = self.category_filter.currentData()
            stock_filter = self.stock_filter.currentData()
            
            # Map stock filter to controller parameters
            in_stock_only = (stock_filter == 'in_stock')
            
            # Calculate offset
            offset = (self.current_page - 1) * self.page_size
            
            # Search products
            result = self.product_controller.search_products(
                query=search_text,
                category_id=category_id if category_id else None,
                in_stock_only=in_stock_only,
                limit=self.page_size,
                offset=offset
            )
            
            if result['success']:
                self.display_products(result['products'])
                self.total_products = result['total_count']
                self.update_pagination_controls()
            else:
                QMessageBox.warning(self, "Error", result['message'])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
    
    def display_products(self, products):
        """Display products in the table."""
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Product name
            name_item = QTableWidgetItem(product['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, product['id'])
            self.products_table.setItem(row, 0, name_item)
            
            # SKU
            sku_item = QTableWidgetItem(product['sku'] or "")
            self.products_table.setItem(row, 1, sku_item)
            
            # Price
            price_item = QTableWidgetItem(product.get('display_price', 'N/A'))
            self.products_table.setItem(row, 2, price_item)
            
            # Stock quantity
            stock_qty = product.get('total_stock', 0)
            stock_item = QTableWidgetItem(str(stock_qty))
            
            # Color code based on stock level
            if stock_qty <= product.get('low_stock_threshold', 5):
                stock_item.setForeground(QColor('#f39c12'))  # Orange for low stock
            elif stock_qty == 0:
                stock_item.setForeground(QColor('#e74c3c'))  # Red for out of stock
            else:
                stock_item.setForeground(QColor('#27ae60'))  # Green for in stock
            
            self.products_table.setItem(row, 3, stock_item)
            
            # Category
            category_item = QTableWidgetItem(product['category'] or "")
            self.products_table.setItem(row, 4, category_item)
            
            # Status
            status_text = self.translation_manager.get('active') if product['is_active'] else self.translation_manager.get('inactive')
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor('#27ae60') if product['is_active'] else QColor('#7f8c8d'))
            self.products_table.setItem(row, 5, status_item)
    
    def update_pagination_controls(self):
        """Update pagination controls based on current page and total products."""
        total_pages = max(1, (self.total_products + self.page_size - 1) // self.page_size)
        
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)
    
    def update_stats(self):
        """Update statistics display."""
        try:
            # Total products
            total_query = "SELECT COUNT(*) as count FROM products WHERE is_active = 1"
            total_result = self.db_manager.execute_query(total_query)
            total_count = total_result[0]['count'] if total_result else 0
            self.total_products_label.setText(str(total_count))
            
            # In stock - FIXED QUERY
            in_stock_query = """
            SELECT COUNT(DISTINCT p.id) as count 
            FROM products p
            WHERE p.is_active = 1 
            AND (
                p.stock_quantity > 0 
                OR EXISTS (
                    SELECT 1 FROM product_variations pv 
                    WHERE pv.product_id = p.id 
                    AND pv.is_active = 1 
                    AND pv.stock_quantity > 0
                )
            )
            """
            in_stock_result = self.db_manager.execute_query(in_stock_query)
            in_stock_count = in_stock_result[0]['count'] if in_stock_result else 0
            self.in_stock_label.setText(str(in_stock_count))
            
            # Low stock (using default threshold of 5)
            low_stock_result = self.product_controller.get_low_stock_products(threshold=5)
            low_stock_count = len(low_stock_result['products']) if low_stock_result['success'] else 0
            self.low_stock_label.setText(str(low_stock_count))
            
            # Out of stock - FIXED QUERY
            out_stock_query = """
            SELECT COUNT(DISTINCT p.id) as count 
            FROM products p
            WHERE p.is_active = 1 
            AND p.stock_quantity = 0
            AND NOT EXISTS (
                SELECT 1 FROM product_variations pv 
                WHERE pv.product_id = p.id 
                AND pv.is_active = 1 
                AND pv.stock_quantity > 0
            )
            """
            out_stock_result = self.db_manager.execute_query(out_stock_query)
            out_stock_count = out_stock_result[0]['count'] if out_stock_result else 0
            self.out_stock_label.setText(str(out_stock_count))
            
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def on_search(self):
        """Handle search action."""
        self.current_page = 1
        self.load_products_page()
    
    def on_filter_changed(self):
        """Handle filter changes."""
        self.current_page = 1
        self.load_products_page()
    
    def on_prev_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_products_page()
    
    def on_next_page(self):
        """Go to next page."""
        self.current_page += 1
        self.load_products_page()
    
    def on_refresh(self):
        """Refresh all data."""
        self.current_page = 1
        self.load_products_page()
        self.update_stats()
        self.refresh_requested.emit()
    
    def on_new_product(self):
        """Create new product."""
        # Create dialog
        dialog = ProductFormDialog(
            db_manager=self.db_manager,
            translation_manager=self.translation_manager,
            product_data=None,
            parent=self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            product_data = result['data']
            
            # Add current user as creator
            # TODO: Get actual user ID from session
            product_data['created_by'] = 1
            
            # Create product using controller
            controller_result = self.product_controller.create_product(product_data)
            
            if controller_result['success']:
                QMessageBox.information(self, 
                    self.translation_manager.get('success'),
                    self.translation_manager.get('product_created_successfully')
                )
                
                # Refresh the list
                self.on_refresh()
                
                # Select the new product
                self.select_product_by_id(controller_result['product_id'])
            else:
                QMessageBox.critical(self, 
                    self.translation_manager.get('error'),
                    controller_result['message']
                )
    def select_product_by_id(self, product_id):
        """Select a product in the table by ID."""
        for row in range(self.products_table.rowCount()):
            item = self.products_table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == product_id:
                self.products_table.selectRow(row)
                self.on_product_selected()
                return True
        return False                
    
    def on_edit_product(self):
        """Edit selected product."""
        if not self.current_product_id:
            QMessageBox.warning(self, 
                self.translation_manager.get('warning'),
                self.translation_manager.get('please_select_product_first')
            )
            return
        
        # Get current product data
        result = self.product_controller.get_full_product(self.current_product_id)
        if not result['success']:
            QMessageBox.critical(self, 
                self.translation_manager.get('error'),
                result['message']
            )
            return
        
        product_data = result['product']
        
        # Create dialog with existing data
        dialog = ProductFormDialog(
            db_manager=self.db_manager,
            translation_manager=self.translation_manager,
            product_data=product_data,
            parent=self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            updated_data = result['data']
            
            # Add current user as updater
            # TODO: Get actual user ID from session
            updated_data['updated_by'] = 1
            
            # Update product using controller
            controller_result = self.product_controller.update_product(
                self.current_product_id,
                updated_data
            )
            
            if controller_result['success']:
                QMessageBox.information(self, 
                    self.translation_manager.get('success'),
                    self.translation_manager.get('product_updated_successfully')
                )
                
                # Refresh the list and details
                self.load_product_details(self.current_product_id)
                self.on_refresh()
            else:
                QMessageBox.critical(self, 
                    self.translation_manager.get('error'),
                    controller_result['message']
                )
    
    def on_delete_product(self):
        """Delete selected product."""
        if not self.current_product_id:
            QMessageBox.warning(self, 
                self.translation_manager.get('warning'),
                self.translation_manager.get('please_select_product_first')
            )
            return
        
        # Get product name for confirmation
        query = "SELECT name FROM products WHERE id = ?"
        result = self.db_manager.execute_query(query, (self.current_product_id,))
        product_name = result[0]['name'] if result else f"Product #{self.current_product_id}"
        
        reply = QMessageBox.question(
            self,
            self.translation_manager.get('confirm_delete'),
            f"{self.translation_manager.get('are_you_sure_delete_product')}\n\n" +
            f"ID: {self.current_product_id}\n" +
            f"{self.translation_manager.get('name')}: {product_name}\n\n" +
            self.translation_manager.get('this_action_cannot_be_undone'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # TODO: Get actual user ID from session
                user_id = 1
                
                # Use controller to delete
                controller_result = self.product_controller.delete_product(
                    self.current_product_id,
                    user_id
                )
                
                if controller_result['success']:
                    QMessageBox.information(self, 
                        self.translation_manager.get('success'),
                        self.translation_manager.get('product_deleted_successfully')
                    )
                    
                    # Refresh and clear details
                    self.on_refresh()
                    self.clear_product_details()
                else:
                    QMessageBox.critical(self, 
                        self.translation_manager.get('error'),
                        controller_result['message']
                    )
                    
            except Exception as e:
                QMessageBox.critical(self, 
                    self.translation_manager.get('error'),
                    f"{self.translation_manager.get('failed_to_delete_product')}: {str(e)}"
                )
    
    def on_view_variations(self):
        """View variations for selected product."""
        if not self.current_product_id:
            QMessageBox.warning(self, 
                self.translation_manager.get('warning'),
                self.translation_manager.get('please_select_product_first')
            )
            return
        
        # Create and show variations dialog
        dialog = VariationsViewDialog(
            product_controller=self.product_controller,
            product_id=self.current_product_id,
            translation_manager=self.translation_manager,
            parent=self
        )
        
        dialog.exec()
    
    def on_export(self):
        """Export products data."""
        try:
            # Ask for file location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                self.translation_manager.get('export_products'),
                "",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Ensure .csv extension
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'
            
            # Ask for export scope
            scope_reply = QMessageBox.question(
                self,
                self.translation_manager.get('export_scope'),
                self.translation_manager.get('export_all_or_selected'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if scope_reply == QMessageBox.StandardButton.Cancel:
                return
            
            product_ids = None
            if scope_reply == QMessageBox.StandardButton.No:
                # Export only selected product
                if self.current_product_id:
                    product_ids = [self.current_product_id]
                else:
                    QMessageBox.warning(self, 
                        self.translation_manager.get('warning'),
                        self.translation_manager.get('please_select_product_first_for_export')
                    )
                    return
            
            # Show progress
            progress = QMessageBox(self)
            progress.setWindowTitle(self.translation_manager.get('exporting'))
            progress.setText(self.translation_manager.get('exporting_products_please_wait'))
            progress.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress.show()
            
            # Use controller to export
            result = self.product_controller.export_products_csv(file_path, product_ids)
            
            progress.close()
            
            if result['success']:
                QMessageBox.information(self, 
                    self.translation_manager.get('success'),
                    f"{result['message']}\n\n" +
                    f"{self.translation_manager.get('file_saved_to')}: {file_path}"
                )
                
                # Log success
                print(f"Exported {result['exported_count']} products to {file_path}")
            else:
                QMessageBox.critical(self, 
                    self.translation_manager.get('error'),
                    result['message']
                )
                
        except Exception as e:
            QMessageBox.critical(self, 
                self.translation_manager.get('error'),
                f"{self.translation_manager.get('export_failed')}: {str(e)}"
            )
    
    def on_product_selected(self):
        """Handle product selection from table."""
        selected_items = self.products_table.selectedItems()
        if not selected_items:
            self.clear_product_details()
            return
        
        row = selected_items[0].row()
        product_id_item = self.products_table.item(row, 0)
        product_id = product_id_item.data(Qt.ItemDataRole.UserRole)
        
        self.current_product_id = product_id
        self.load_product_details(product_id)
    
    def load_product_details(self, product_id):
        """Load detailed information for selected product."""
        result = self.product_controller.get_full_product(product_id)
        
        if result['success']:
            product = result['product']
            variations = result['variations']
            
            # Prepare safe display values
            cost_display = f"${product['cost_price']:.2f}" if product.get('cost_price') else 'N/A'
            sku_display = product.get('sku', 'N/A')
            category_display = product.get('category', 'N/A')
            brand_display = product.get('brand', 'N/A')
            
            details_html = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif;">
                <h2 style="color: #e74c3c; margin-bottom: 10px;">{product.get('name', 'N/A')}</h2>
                <p><strong>ID:</strong> {product.get('id', 'N/A')}</p>
                <p><strong>SKU:</strong> {sku_display}</p>
                <p><strong>Type:</strong> {product.get('type', 'N/A')}</p>
                <p><strong>Category:</strong> {category_display}</p>
                <p><strong>Brand:</strong> {brand_display}</p>
                <p><strong>Price:</strong> ${product.get('price', 0.00):.2f}</p>
                <p><strong>Cost:</strong> {cost_display}</p>
                <p><strong>Stock:</strong> {product.get('stock_quantity', 0)} ({product.get('stock_status', 'N/A')})</p>
                <p><strong>Variations:</strong> {len(variations)}</p>
                <p><strong>Created:</strong> {product.get('created_at', 'N/A')}</p>
                <p><strong>Updated:</strong> {product.get('updated_at', 'N/A')}</p>
            </div>
            """
            
            if product.get('description'):
                details_html += f"<p><strong>Description:</strong><br>{product['description']}</p>"
            
            self.details_content.setText(details_html)
            self.details_frame.setVisible(True)
            
            # Enable action buttons
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.view_variations_btn.setEnabled(len(variations) > 0)
            
        else:
            self.details_content.setText(f"<p style='color: #e74c3c;'>{result['message']}</p>")
            self.details_frame.setVisible(True)
            
            # Disable action buttons
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.view_variations_btn.setEnabled(False)
    
    def update_language(self):
        """Update UI text when language changes."""
        self.current_language = self.translation_manager.get_current_lang()
        
        # Update static text
        title_label = self.findChild(QLabel, "pageTitle")
        if title_label:
            title_label.setText(self.translation_manager.get('products'))
        
        # Update buttons
        self.new_product_btn.setText(f"➕ {self.translation_manager.get('add_new')}")
        self.refresh_btn.setText(f"🔄 {self.translation_manager.get('refresh')}")
        self.export_btn.setText(f"📤 {self.translation_manager.get('export')}")
        
        # Update search
        self.search_input.setPlaceholderText(self.translation_manager.get('search_products'))
        
        search_btn = self.findChild(QPushButton)
        if search_btn and search_btn.objectName() != "new_product_btn":
            search_btn.setText(self.translation_manager.get('search'))
        
        # Update table headers
        headers = [
            self.translation_manager.get('product_name'),
            self.translation_manager.get('sku'),
            self.translation_manager.get('price'),
            self.translation_manager.get('stock_quantity'),
            self.translation_manager.get('category'),
            self.translation_manager.get('status')
        ]
        for col, header in enumerate(headers):
            self.products_table.horizontalHeaderItem(col).setText(header)
        
        # Update pagination
        self.prev_page_btn.setText("◀ " + self.translation_manager.get('previous'))
        self.next_page_btn.setText(self.translation_manager.get('next') + " ▶")
        
        # Update details
        details_header = self.findChild(QLabel, "detailsHeader")
        if details_header:
            details_header.setText(self.translation_manager.get('product_details'))
        
        self.edit_btn.setText(self.translation_manager.get('edit'))
        self.delete_btn.setText(self.translation_manager.get('delete'))
        self.view_variations_btn.setText(self.translation_manager.get('variations'))
        
        # Update stats
        stats_title = self.findChild(QLabel, "statsTitle")
        if stats_title:
            stats_title.setText(self.translation_manager.get('quick_stats'))
        
        # Update filter dropdowns
        self.category_filter.setItemText(0, self.translation_manager.get('all_categories'))
        
        self.stock_filter.blockSignals(True)
        self.stock_filter.setItemText(0, self.translation_manager.get('all_stock'))
        self.stock_filter.setItemText(1, self.translation_manager.get('in_stock'))
        self.stock_filter.setItemText(2, self.translation_manager.get('low_stock'))
        self.stock_filter.setItemText(3, self.translation_manager.get('out_of_stock'))
        self.stock_filter.blockSignals(False)
        
        # Refresh data
        self.on_refresh()


# Test the screen
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    from database import DatabaseManager
    
    app = QApplication(sys.argv)
    
    # Initialize database
    db = DatabaseManager(":memory:")  # In-memory DB for testing
    
    # Initialize translation manager
    translator = TranslationManager()
    
    # Create and show product screen
    screen = ProductScreen(db, translator)
    screen.setWindowTitle("Product Management - Test")
    screen.resize(1200, 700)
    screen.show()
    
    sys.exit(app.exec())