"""
Twinx POS System - Database Layer
Senior Python Software Architect
File: database.py

This module provides a comprehensive, future-proof database schema for the Twinx POS system.
All tables include extensive extra attributes and a 'meta_data' JSON column for dynamic expansion.
"""

import sqlite3
import json
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager


class DatabaseManager:
    """Main database manager for Twinx POS system."""
    
    def __init__(self, db_path: str = "twinx_pos.db"):
        """Initialize database manager with connection path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize the database with all tables and default data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create all tables
            self._create_product_tables(cursor)
            self._create_hr_tables(cursor)
            self._create_sales_tables(cursor)
            self._create_inventory_tables(cursor)
            self._create_customer_tables(cursor)
            self._create_wholesale_tables(cursor)
            self._create_financial_tables(cursor)
            self._create_system_tables(cursor)
            
            # Insert default admin user
            self._insert_default_admin(cursor)
            
            # Insert default settings
            self._insert_default_settings(cursor)
    
    def _create_product_tables(self, cursor):
        """Create product-related tables."""
        
        # Attributes table - for product attributes like Color, Size
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT,
            sort_order INTEGER DEFAULT 0,
            is_filterable BOOLEAN DEFAULT 1,
            is_visible BOOLEAN DEFAULT 1,
            is_variation BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}'  -- JSON field for future attribute metadata
        )
        """)
        
        # Attribute terms table - specific values for attributes (Red, Blue, XL, etc.)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attribute_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attribute_id INTEGER NOT NULL,
            term TEXT NOT NULL,
            slug TEXT UNIQUE,
            description TEXT,
            sort_order INTEGER DEFAULT 0,
            color_code TEXT,  -- For color swatches
            image_path TEXT,  -- For swatch images
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}',
            FOREIGN KEY (attribute_id) REFERENCES attributes(id) ON DELETE CASCADE,
            UNIQUE(attribute_id, term)
        )
        """)
        
        # Products table - Main products catalog with extensive attributes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('simple', 'variable', 'grouped', 'digital')),
            category TEXT,  -- Can be normalized to categories table in future
            subcategory TEXT,
            brand TEXT,
            description TEXT,
            short_description TEXT,
            image_path TEXT,
            image_gallery TEXT,  -- JSON array of additional image paths
            is_active BOOLEAN DEFAULT 1,
            is_featured BOOLEAN DEFAULT 0,
            is_taxable BOOLEAN DEFAULT 1,
            
            -- Inventory & Stock
            manage_stock BOOLEAN DEFAULT 1,
            stock_quantity INTEGER DEFAULT 0,
            stock_status TEXT DEFAULT 'instock' CHECK(stock_status IN ('instock', 'outofstock', 'onbackorder')),
            allow_backorders BOOLEAN DEFAULT 0,
            low_stock_threshold INTEGER DEFAULT 5,
            
            -- Pricing
            price DECIMAL(10,2) DEFAULT 0.00,
            cost_price DECIMAL(10,2) DEFAULT 0.00,  -- Purchase cost
            wholesale_price DECIMAL(10,2) DEFAULT 0.00,
            suggested_retail_price DECIMAL(10,2) DEFAULT 0.00,
            tax_class TEXT DEFAULT 'standard',
            tax_rate DECIMAL(5,2) DEFAULT 0.00,
            
            -- Product Identification
            sku TEXT UNIQUE,
            barcode TEXT,
            barcode_type TEXT DEFAULT 'EAN13',
            qr_code TEXT,
            upc TEXT,
            isbn TEXT,
            mpn TEXT,  -- Manufacturer Part Number
            
            -- Physical Properties
            weight_kg DECIMAL(8,3) DEFAULT 0.000,
            length_cm DECIMAL(8,2) DEFAULT 0.00,
            width_cm DECIMAL(8,2) DEFAULT 0.00,
            height_cm DECIMAL(8,2) DEFAULT 0.00,
            volume_liters DECIMAL(8,3) DEFAULT 0.000,
            dimensions_unit TEXT DEFAULT 'cm',
            
            -- Manufacturing & Origin
            manufacturer TEXT,
            manufacturer_country TEXT,
            country_of_origin TEXT,
            material_composition TEXT,
            product_code TEXT,
            
            -- Warranty & Support
            warranty_period_months INTEGER,
            warranty_type TEXT,
            warranty_terms TEXT,
            has_warranty BOOLEAN DEFAULT 0,
            support_email TEXT,
            support_phone TEXT,
            
            -- Sales & Marketing
            commission_rate DECIMAL(5,2) DEFAULT 0.00,
            margin_percentage DECIMAL(5,2),
            min_order_quantity INTEGER DEFAULT 1,
            max_order_quantity INTEGER,
            sale_price DECIMAL(10,2),
            sale_start_date DATE,
            sale_end_date DATE,
            tags TEXT,  -- JSON array of tags
            
            -- Product Lifecycle
            shelf_life_days INTEGER,
            expiry_alert_days INTEGER DEFAULT 30,
            batch_tracking_required BOOLEAN DEFAULT 0,
            serial_tracking_required BOOLEAN DEFAULT 0,
            
            -- Supplier Information
            supplier_id INTEGER,
            supplier_sku TEXT,
            lead_time_days INTEGER,
            reorder_point INTEGER,
            reorder_quantity INTEGER,
            
            -- Shipping
            shipping_class TEXT,
            shipping_weight DECIMAL(8,3),
            requires_shipping BOOLEAN DEFAULT 1,
            is_virtual BOOLEAN DEFAULT 0,
            is_downloadable BOOLEAN DEFAULT 0,
            
            -- SEO & Web
            meta_title TEXT,
            meta_description TEXT,
            meta_keywords TEXT,
            canonical_url TEXT,
            
            -- Audit & Control
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified_at TIMESTAMP,
            verified_by INTEGER,
            
            -- Future-Proof JSON field for any additional attributes
            meta_data TEXT DEFAULT '{}',
            
            -- Indexes for performance
            FOREIGN KEY (supplier_id) REFERENCES wholesale_partners(id)
        )
        """)
        
        # Product variations table - for variable products
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_variations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            name TEXT,
            sku TEXT UNIQUE,
            barcode TEXT UNIQUE,
            
            -- Pricing
            price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            cost_price DECIMAL(10,2) DEFAULT 0.00,
            wholesale_price DECIMAL(10,2) DEFAULT 0.00,
            sale_price DECIMAL(10,2),
            purchase_price DECIMAL(10,2),  -- Latest purchase price
            
            -- Inventory
            stock_quantity INTEGER DEFAULT 0,
            stock_status TEXT DEFAULT 'instock',
            manage_stock BOOLEAN DEFAULT 1,
            low_stock_threshold INTEGER DEFAULT 5,
            
            -- Physical Properties
            weight_kg DECIMAL(8,3),
            length_cm DECIMAL(8,2),
            width_cm DECIMAL(8,2),
            height_cm DECIMAL(8,2),
            
            -- Variation Attributes
            attribute_combination TEXT,  -- JSON: {"color": "red", "size": "xl"}
            image_path TEXT,
            
            -- Tracking Requirements
            batch_number_required BOOLEAN DEFAULT 0,
            serial_number_required BOOLEAN DEFAULT 0,
            expiry_date_required BOOLEAN DEFAULT 0,
            
            -- Supplier Information
            supplier_sku TEXT,
            
            -- Status
            is_active BOOLEAN DEFAULT 1,
            is_default_variation BOOLEAN DEFAULT 0,
            
            -- Audit
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        """)
        
        # Product attribute relationships
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_attribute_relations (
            product_id INTEGER NOT NULL,
            attribute_id INTEGER NOT NULL,
            attribute_term_id INTEGER NOT NULL,
            sort_order INTEGER DEFAULT 0,
            is_visible BOOLEAN DEFAULT 1,
            is_variation BOOLEAN DEFAULT 0,
            PRIMARY KEY (product_id, attribute_id, attribute_term_id),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (attribute_id) REFERENCES attributes(id) ON DELETE CASCADE,
            FOREIGN KEY (attribute_term_id) REFERENCES attribute_terms(id) ON DELETE CASCADE
        )
        """)
        
        # Product categories (normalized version for future expansion)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE,
            description TEXT,
            parent_id INTEGER,
            image_path TEXT,
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            meta_title TEXT,
            meta_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}',
            FOREIGN KEY (parent_id) REFERENCES categories(id)
        )
        """)
    
    def _create_hr_tables(self, cursor):
        """Create HR and employee management tables."""
        
        # Employees table - Comprehensive employee data with RBAC
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Authentication & Security
            username TEXT UNIQUE NOT NULL,
            passcode_hash TEXT NOT NULL,  -- Hashed passcode for POS login
            password_hash TEXT,  -- For web portal if applicable
            pin_code TEXT,  -- 4-6 digit PIN for quick access
            role TEXT NOT NULL CHECK(role IN ('admin', 'cashier', 'delivery', 'manager', 
                                              'accountant', 'storekeeper', 'hr', 'supervisor', 
                                              'assistant', 'technician', 'sales_rep')),
            
            -- RBAC & Permissions
            permissions_json TEXT DEFAULT '{}',  -- Granular permissions in JSON format
            access_level INTEGER DEFAULT 1,
            is_active BOOLEAN DEFAULT 1,
            is_locked BOOLEAN DEFAULT 0,
            locked_until TIMESTAMP,
            lock_reason TEXT,
            failed_login_attempts INTEGER DEFAULT 0,
            last_login TIMESTAMP,
            last_password_change TIMESTAMP,
            password_expiry_date DATE,
            must_change_password BOOLEAN DEFAULT 0,
            
            -- Personal Information
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            display_name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            secondary_phone TEXT,
            birth_date DATE,
            gender TEXT CHECK(gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
            marital_status TEXT CHECK(marital_status IN ('single', 'married', 'divorced', 'widowed')),
            nationality TEXT,
            
            -- Identification
            national_id TEXT UNIQUE,
            passport_number TEXT,
            passport_expiry DATE,
            tax_id TEXT,
            social_security_number TEXT UNIQUE,
            
            -- Physical Characteristics (for emergency/medical purposes)
            blood_type TEXT CHECK(blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
            height_cm INTEGER,
            weight_kg DECIMAL(5,2),
            medical_conditions TEXT,
            allergies TEXT,
            emergency_contact_name TEXT,
            emergency_contact_relation TEXT,
            emergency_contact_phone TEXT,
            emergency_contact_phone2 TEXT,
            
            -- Address Information
            address_line1 TEXT,
            address_line2 TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            country TEXT,
            residence_type TEXT CHECK(residence_type IN ('owned', 'rented', 'with_family', 'other')),
            
            -- Bank & Financial
            bank_name TEXT,
            bank_branch TEXT,
            bank_account_number TEXT,
            bank_iban TEXT,
            bank_swift_code TEXT,
            account_holder_name TEXT,
            payment_method TEXT DEFAULT 'bank_transfer' CHECK(payment_method IN ('bank_transfer', 'cash', 'cheque')),
            
            -- Employment Details
            employee_id TEXT UNIQUE,  -- Company employee ID
            job_title TEXT,
            department TEXT,
            manager_id INTEGER,
            hire_date DATE NOT NULL,
            contract_start_date DATE,
            contract_end_date DATE,
            contract_type TEXT CHECK(contract_type IN ('permanent', 'temporary', 'contractor', 'probation', 'intern')),
            employment_status TEXT DEFAULT 'active' CHECK(employment_status IN ('active', 'on_leave', 'suspended', 'terminated', 'resigned')),
            termination_date DATE,
            termination_reason TEXT,
            rehire_eligible BOOLEAN DEFAULT 0,
            
            -- Compensation & Benefits
            basic_salary DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            housing_allowance DECIMAL(10,2) DEFAULT 0.00,
            transportation_allowance DECIMAL(10,2) DEFAULT 0.00,
            meal_allowance DECIMAL(10,2) DEFAULT 0.00,
            communication_allowance DECIMAL(10,2) DEFAULT 0.00,
            other_allowance DECIMAL(10,2) DEFAULT 0.00,
            total_package DECIMAL(10,2) DEFAULT 0.00,
            salary_currency TEXT DEFAULT 'USD',
            payment_frequency TEXT DEFAULT 'monthly' CHECK(payment_frequency IN ('weekly', 'biweekly', 'monthly', 'quarterly')),
            bank_code TEXT,
            
            -- Leaves & Time Off
            annual_leaves_entitled INTEGER DEFAULT 21,
            annual_leaves_taken INTEGER DEFAULT 0,
            annual_leaves_balance INTEGER DEFAULT 21,
            sick_leaves_entitled INTEGER DEFAULT 10,
            sick_leaves_taken INTEGER DEFAULT 0,
            sick_leaves_balance INTEGER DEFAULT 10,
            
            -- Performance & Development
            performance_rating DECIMAL(3,2),
            last_performance_review DATE,
            next_review_date DATE,
            skills TEXT,  -- JSON array of skills
            certifications TEXT,  -- JSON array of certifications
            training_completed TEXT,  -- JSON array
            
            -- Work Details
            work_location TEXT,
            work_schedule TEXT,
            shift_pattern TEXT,
            overtime_eligible BOOLEAN DEFAULT 0,
            overtime_rate_multiplier DECIMAL(3,2) DEFAULT 1.5,
            max_overtime_hours_weekly INTEGER DEFAULT 10,
            
            -- Equipment & Access
            assigned_equipment TEXT,  -- JSON: {"terminal": "T001", "keys": "store_room"}
            system_access TEXT,  -- JSON: {"pos": true, "inventory": true, "reports": false}
            
            -- Emergency & Safety
            evacuation_assembly_point TEXT,
            safety_training_completed BOOLEAN DEFAULT 0,
            safety_training_date DATE,
            
            -- Documents
            id_copy_path TEXT,
            passport_copy_path TEXT,
            contract_copy_path TEXT,
            photo_path TEXT,
            
            -- Audit & Tracking
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Future-Proof JSON field
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (manager_id) REFERENCES employees(id)
        )
        """)
        
        # Attendance table - Comprehensive tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date DATE NOT NULL,
            
            -- Check In
            check_in_time TIMESTAMP,
            check_in_latitude DECIMAL(10,8),
            check_in_longitude DECIMAL(11,8),
            check_in_device_id TEXT,
            check_in_device_ip TEXT,
            check_in_method TEXT CHECK(check_in_method IN ('pin', 'biometric', 'card', 'mobile', 'manual')),
            check_in_photo_path TEXT,
            
            -- Check Out
            check_out_time TIMESTAMP,
            check_out_latitude DECIMAL(10,8),
            check_out_longitude DECIMAL(11,8),
            check_out_device_id TEXT,
            check_out_device_ip TEXT,
            check_out_method TEXT,
            check_out_photo_path TEXT,
            
            -- Shift Information
            shift_id INTEGER,
            shift_name TEXT,
            scheduled_start_time TIMESTAMP,
            scheduled_end_time TIMESTAMP,
            scheduled_break_minutes INTEGER DEFAULT 30,
            
            -- Calculations
            total_worked_minutes INTEGER,
            overtime_minutes INTEGER,
            late_minutes INTEGER,
            early_departure_minutes INTEGER,
            break_taken_minutes INTEGER,
            
            -- Status & Approval
            attendance_status TEXT DEFAULT 'present' CHECK(attendance_status IN ('present', 'absent', 'late', 'half_day', 'leave', 'holiday', 'off_day')),
            is_approved BOOLEAN DEFAULT 1,
            approved_by INTEGER,
            approved_at TIMESTAMP,
            approval_notes TEXT,
            
            -- Leaves & Time Off
            leave_type TEXT CHECK(leave_type IN ('annual', 'sick', 'maternity', 'paternity', 'unpaid', 'compensatory')),
            leave_hours INTEGER,
            leave_approved_by INTEGER,
            
            -- Location & Notes
            work_location TEXT,
            notes TEXT,
            tasks_completed TEXT,  -- JSON array of tasks
            issues_encountered TEXT,
            
            -- Device & Session Info
            session_id TEXT UNIQUE,
            device_model TEXT,
            app_version TEXT,
            battery_level_start INTEGER,
            battery_level_end INTEGER,
            
            -- Emergency & Safety
            safety_check_completed BOOLEAN DEFAULT 0,
            safety_issues TEXT,
            emergency_contact_notified BOOLEAN DEFAULT 0,
            
            -- Audit
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_to_server BOOLEAN DEFAULT 0,
            sync_timestamp TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            FOREIGN KEY (approved_by) REFERENCES employees(id),
            FOREIGN KEY (leave_approved_by) REFERENCES employees(id),
            UNIQUE(employee_id, date)
        )
        """)
        
        # Salary transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS salary_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            
            -- Transaction Details
            transaction_date DATE NOT NULL,
            payroll_period_start DATE,
            payroll_period_end DATE,
            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('salary', 'bonus', 'advance', 'deduction', 'reimbursement', 'overtime', 'allowance', 'adjustment')),
            
            -- Amounts
            amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            currency TEXT DEFAULT 'USD',
            exchange_rate DECIMAL(10,6) DEFAULT 1.0,
            converted_amount DECIMAL(10,2),
            
            -- Salary Components Breakdown
            basic_salary_amount DECIMAL(10,2),
            allowance_amount DECIMAL(10,2),
            overtime_amount DECIMAL(10,2),
            bonus_amount DECIMAL(10,2),
            commission_amount DECIMAL(10,2),
            
            -- Deductions
            deduction_amount DECIMAL(10,2),
            tax_deduction DECIMAL(10,2),
            social_security_deduction DECIMAL(10,2),
            other_deductions DECIMAL(10,2),
            
            -- Net Pay
            gross_amount DECIMAL(10,2),
            total_deductions DECIMAL(10,2),
            net_amount DECIMAL(10,2),
            
            -- Payment Details
            payment_method TEXT CHECK(payment_method IN ('cash', 'bank_transfer', 'cheque', 'mobile_money')),
            payment_reference TEXT,
            payment_date DATE,
            payment_status TEXT DEFAULT 'pending' CHECK(payment_status IN ('pending', 'paid', 'failed', 'cancelled', 'reversed')),
            payment_confirmed_by INTEGER,
            payment_confirmation_date DATE,
            
            -- Bank Details (if bank transfer)
            bank_name TEXT,
            bank_account TEXT,
            transaction_id TEXT,
            
            -- Advance Handling
            is_advance BOOLEAN DEFAULT 0,
            advance_settlement_id INTEGER,
            advance_settled_amount DECIMAL(10,2),
            
            -- Overtime Details
            overtime_hours DECIMAL(5,2),
            overtime_rate DECIMAL(10,2),
            overtime_multiplier DECIMAL(3,2) DEFAULT 1.5,
            
            -- Leave Adjustments
            leave_deduction_days INTEGER,
            leave_deduction_amount DECIMAL(10,2),
            
            -- Attendance Link
            attendance_summary TEXT,  -- JSON: {"days_present": 22, "days_absent": 0, ...}
            
            -- Notes & Documentation
            notes TEXT,
            description TEXT,
            supporting_document_path TEXT,
            
            -- Approval Workflow
            approved_by INTEGER,
            approved_at TIMESTAMP,
            approval_level INTEGER DEFAULT 1,
            approval_status TEXT DEFAULT 'pending' CHECK(approval_status IN ('pending', 'approved', 'rejected', 'on_hold')),
            rejection_reason TEXT,
            
            -- Accounting Integration
            gl_account_code TEXT,
            cost_center TEXT,
            expense_category TEXT,
            
            -- Audit
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reversal_of_id INTEGER,  -- If this is a reversal transaction
            reversal_reason TEXT,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            FOREIGN KEY (approved_by) REFERENCES employees(id),
            FOREIGN KEY (payment_confirmed_by) REFERENCES employees(id),
            FOREIGN KEY (created_by) REFERENCES employees(id),
            FOREIGN KEY (reversal_of_id) REFERENCES salary_transactions(id)
        )
        """)
        
        # Leaves table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL CHECK(leave_type IN ('annual', 'sick', 'maternity', 'paternity', 'unpaid', 'compensatory', 'bereavement', 'study')),
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_days INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'cancelled')),
            reason TEXT,
            medical_certificate_path TEXT,
            approved_by INTEGER,
            approved_at TIMESTAMP,
            rejection_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}',
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            FOREIGN KEY (approved_by) REFERENCES employees(id)
        )
        """)
    
    def _create_sales_tables(self, cursor):
        """Create sales and POS transaction tables."""
        
        # Sales table - Main POS transactions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Invoice Information
            invoice_no TEXT UNIQUE NOT NULL,
            invoice_prefix TEXT DEFAULT 'INV',
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invoice_status TEXT DEFAULT 'completed' CHECK(invoice_status IN ('pending', 'completed', 'cancelled', 'refunded', 'partially_refunded', 'on_hold', 'void')),
            
            -- Customer Information
            customer_id INTEGER,
            customer_name TEXT,
            customer_phone TEXT,
            customer_email TEXT,
            customer_tax_id TEXT,
            
            -- Sales Location & Context
            terminal_id TEXT,
            terminal_name TEXT,
            store_id INTEGER,
            store_name TEXT,
            shift_id INTEGER,
            shift_name TEXT,
            cashier_id INTEGER NOT NULL,
            cashier_name TEXT,
            
            -- Amounts
            subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            discount_amount DECIMAL(10,2) DEFAULT 0.00,
            discount_percent DECIMAL(5,2) DEFAULT 0.00,
            tax_amount DECIMAL(10,2) DEFAULT 0.00,
            shipping_amount DECIMAL(10,2) DEFAULT 0.00,
            handling_amount DECIMAL(10,2) DEFAULT 0.00,
            rounding_adjustment DECIMAL(10,2) DEFAULT 0.00,
            total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            amount_paid DECIMAL(10,2) DEFAULT 0.00,
            change_amount DECIMAL(10,2) DEFAULT 0.00,
            
            -- Currency & Exchange
            currency TEXT DEFAULT 'USD',
            exchange_rate DECIMAL(10,6) DEFAULT 1.0,
            base_currency_total DECIMAL(10,2),  -- Converted to base currency
            
            -- Payment Information
            payment_method TEXT NOT NULL CHECK(payment_method IN ('cash', 'card', 'credit', 'mobile', 'bank_transfer', 'cheque', 'multiple', 'loyalty_points')),
            payment_status TEXT DEFAULT 'paid' CHECK(payment_status IN ('paid', 'pending', 'partial', 'due', 'refunded')),
            card_last_four TEXT,
            card_type TEXT,
            card_authorization_code TEXT,
            mobile_payment_reference TEXT,
            cheque_number TEXT,
            bank_deposit_slip TEXT,
            
            -- Multiple Payments Support
            payment_breakdown TEXT DEFAULT '[]',  -- JSON array of payments
            
            -- Tax Details
            tax_breakdown TEXT DEFAULT '[]',  -- JSON: [{"name": "VAT", "rate": 15, "amount": 150}]
            is_tax_inclusive BOOLEAN DEFAULT 0,
            tax_calculation_method TEXT DEFAULT 'per_item' CHECK(tax_calculation_method IN ('per_item', 'total')),
            
            -- Shipping & Delivery
            shipping_method TEXT,
            shipping_tracking_number TEXT,
            shipping_carrier TEXT,
            shipping_cost DECIMAL(10,2),
            expected_delivery_date DATE,
            actual_delivery_date TIMESTAMP,
            delivery_person_id INTEGER,
            delivery_status TEXT CHECK(delivery_status IN ('pending', 'packed', 'shipped', 'delivered', 'failed', 'returned')),
            delivery_address TEXT,
            delivery_instructions TEXT,
            
            -- Location Data
            geo_latitude DECIMAL(10,8),
            geo_longitude DECIMAL(11,8),
            location_accuracy DECIMAL(5,2),
            location_address TEXT,
            
            -- Loyalty & Rewards
            loyalty_points_earned INTEGER DEFAULT 0,
            loyalty_points_redeemed INTEGER DEFAULT 0,
            loyalty_card_number TEXT,
            reward_program_id INTEGER,
            
            -- Order Source & Channel
            order_source TEXT DEFAULT 'pos' CHECK(order_source IN ('pos', 'online', 'phone', 'whatsapp', 'marketplace', 'walkin')),
            sales_channel TEXT,
            marketplace_order_id TEXT,
            web_order_id TEXT,
            is_exported_to_web BOOLEAN DEFAULT 0,
            export_timestamp TIMESTAMP,
            
            -- Customer Interaction
            customer_note TEXT,
            internal_note TEXT,
            staff_note TEXT,
            special_instructions TEXT,
            
            -- Returns & Refunds
            is_return BOOLEAN DEFAULT 0,
            original_invoice_id INTEGER,  -- For returns
            return_reason TEXT,
            refund_amount DECIMAL(10,2) DEFAULT 0.00,
            refund_method TEXT,
            refund_date TIMESTAMP,
            
            -- Discounts & Promotions
            coupon_code TEXT,
            coupon_discount DECIMAL(10,2),
            promotion_id INTEGER,
            promotion_name TEXT,
            
            -- Inventory & Stock
            inventory_updated BOOLEAN DEFAULT 0,
            stock_adjustment_id INTEGER,
            
            -- Accounting Integration
            gl_account_code TEXT,
            cost_center TEXT,
            revenue_account TEXT,
            is_reconciled BOOLEAN DEFAULT 0,
            reconciliation_id INTEGER,
            
            -- Device & Session
            device_id TEXT,
            device_ip TEXT,
            app_version TEXT,
            receipt_printer_name TEXT,
            receipt_printed_count INTEGER DEFAULT 0,
            
            -- Printing & Documentation
            receipt_number TEXT,
            receipt_path TEXT,
            invoice_printed BOOLEAN DEFAULT 0,
            invoice_printed_at TIMESTAMP,
            invoice_sent_via_email BOOLEAN DEFAULT 0,
            email_sent_at TIMESTAMP,
            
            -- Audit & Control
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cancelled_at TIMESTAMP,
            cancelled_by INTEGER,
            cancellation_reason TEXT,
            voided_at TIMESTAMP,
            voided_by INTEGER,
            void_reason TEXT,
            
            -- Sync & Integration
            sync_status TEXT DEFAULT 'pending' CHECK(sync_status IN ('pending', 'synced', 'failed', 'conflict')),
            last_sync_attempt TIMESTAMP,
            sync_errors TEXT,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (cashier_id) REFERENCES employees(id),
            FOREIGN KEY (delivery_person_id) REFERENCES employees(id),
            FOREIGN KEY (cancelled_by) REFERENCES employees(id),
            FOREIGN KEY (voided_by) REFERENCES employees(id)
        )
        """)
        
        # Sale items table - Line items in sales
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_variation_id INTEGER,
            
            -- Product Information
            product_name TEXT NOT NULL,
            product_sku TEXT,
            product_barcode TEXT,
            variation_description TEXT,
            
            -- Quantities
            quantity DECIMAL(10,3) NOT NULL DEFAULT 1.000,
            unit_of_measure TEXT DEFAULT 'pcs',
            conversion_factor DECIMAL(10,6) DEFAULT 1.0,
            base_quantity DECIMAL(10,3),  -- In base unit
            
            -- Pricing
            unit_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            original_price DECIMAL(10,2),  -- Price before any discounts
            cost_price DECIMAL(10,2),  -- For profit calculation
            wholesale_price DECIMAL(10,2),
            
            -- Amounts
            subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            discount_amount DECIMAL(10,2) DEFAULT 0.00,
            discount_percent DECIMAL(5,2) DEFAULT 0.00,
            tax_amount DECIMAL(10,2) DEFAULT 0.00,
            total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            
            -- Tax Details
            tax_percent DECIMAL(5,2) DEFAULT 0.00,
            tax_class TEXT,
            tax_inclusive BOOLEAN DEFAULT 0,
            tax_components TEXT DEFAULT '[]',  -- JSON array
            
            -- Discount Details
            discount_type TEXT CHECK(discount_type IN ('percentage', 'fixed', 'bulk', 'promotional')),
            discount_reason TEXT,
            promotion_id INTEGER,
            
            -- Batch & Serial Tracking
            batch_number TEXT,
            serial_number TEXT,
            production_date DATE,
            expiry_date DATE,
            warranty_end_date DATE,
            
            -- Returns & Refunds
            return_quantity DECIMAL(10,3) DEFAULT 0.000,
            return_reason TEXT,
            return_date TIMESTAMP,
            refund_amount DECIMAL(10,2) DEFAULT 0.00,
            
            -- Commission
            commission_rate DECIMAL(5,2) DEFAULT 0.00,
            commission_amount DECIMAL(10,2) DEFAULT 0.00,
            salesperson_id INTEGER,
            
            -- Inventory Tracking
            stock_movement_id INTEGER,  -- Link to stock movements table
            warehouse_id INTEGER,
            shelf_location TEXT,
            
            -- Customization
            customization_options TEXT DEFAULT '{}',  -- JSON for product customizations
            preparation_instructions TEXT,
            
            -- Status
            is_prepared BOOLEAN DEFAULT 0,
            prepared_by INTEGER,
            prepared_at TIMESTAMP,
            is_served BOOLEAN DEFAULT 0,
            served_by INTEGER,
            served_at TIMESTAMP,
            
            -- Notes
            item_note TEXT,
            chef_note TEXT,
            
            -- Audit
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (product_variation_id) REFERENCES product_variations(id),
            FOREIGN KEY (salesperson_id) REFERENCES employees(id),
            FOREIGN KEY (prepared_by) REFERENCES employees(id),
            FOREIGN KEY (served_by) REFERENCES employees(id)
        )
        """)
        
        # Shifts table - POS working shifts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_name TEXT NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            is_overnight BOOLEAN DEFAULT 0,
            max_early_check_in_minutes INTEGER DEFAULT 15,
            max_late_check_out_minutes INTEGER DEFAULT 15,
            break_duration_minutes INTEGER DEFAULT 30,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}'
        )
        """)
        
        # Cash register sessions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cash_register_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            terminal_id TEXT NOT NULL,
            employee_id INTEGER NOT NULL,
            shift_id INTEGER,
            
            -- Timing
            open_time TIMESTAMP NOT NULL,
            close_time TIMESTAMP,
            expected_close_time TIMESTAMP,
            
            -- Cash Handling
            opening_balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            expected_closing_balance DECIMAL(10,2),
            actual_closing_balance DECIMAL(10,2),
            counted_balance DECIMAL(10,2),
            difference_amount DECIMAL(10,2),
            
            -- Cash Breakdown
            cash_denominations TEXT DEFAULT '{}',  -- JSON: {"100": 10, "50": 5, ...}
            opening_denominations TEXT DEFAULT '{}',
            closing_denominations TEXT DEFAULT '{}',
            
            -- Transactions Summary
            total_sales_count INTEGER DEFAULT 0,
            total_sales_amount DECIMAL(10,2) DEFAULT 0.00,
            total_refunds_count INTEGER DEFAULT 0,
            total_refunds_amount DECIMAL(10,2) DEFAULT 0.00,
            total_transactions_count INTEGER DEFAULT 0,
            total_transactions_amount DECIMAL(10,2) DEFAULT 0.00,
            
            -- Payment Methods Breakdown
            payment_method_summary TEXT DEFAULT '{}',  -- JSON by payment method
            
            -- Status
            status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed', 'suspended', 'audited')),
            close_reason TEXT,
            
            -- Audit & Verification
            verified_by INTEGER,
            verification_time TIMESTAMP,
            verification_notes TEXT,
            audit_trail TEXT,  -- JSON log of all balance changes
            
            -- Declarations
            cash_declaration TEXT,
            discrepancy_explanation TEXT,
            manager_approval_required BOOLEAN DEFAULT 0,
            manager_approved_by INTEGER,
            manager_approval_time TIMESTAMP,
            
            -- Safety & Security
            safe_drop_amount DECIMAL(10,2) DEFAULT 0.00,
            safe_drop_count INTEGER DEFAULT 0,
            safe_drop_times TEXT DEFAULT '[]',  -- JSON array of drop times
            
            -- Device Information
            device_id TEXT,
            device_ip TEXT,
            app_version TEXT,
            
            -- Notes
            opening_notes TEXT,
            closing_notes TEXT,
            incident_reports TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (verified_by) REFERENCES employees(id),
            FOREIGN KEY (manager_approved_by) REFERENCES employees(id)
        )
        """)
    
    def _create_inventory_tables(self, cursor):
        """Create inventory and stock management tables."""
        
        # Stock batches table - For batch/expiry tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_variation_id INTEGER,
            
            -- Batch Information
            batch_number TEXT NOT NULL,
            batch_reference TEXT,  -- Manufacturer batch reference
            production_date DATE,
            expiry_date DATE,
            best_before_date DATE,
            shelf_life_days INTEGER,
            
            -- Quantities
            initial_quantity DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            current_quantity DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            reserved_quantity DECIMAL(12,4) DEFAULT 0.0000,
            allocated_quantity DECIMAL(12,4) DEFAULT 0.0000,
            
            -- Location
            warehouse_id INTEGER,
            shelf_location TEXT,
            rack_number TEXT,
            bin_number TEXT,
            
            -- Supplier Information
            supplier_id INTEGER,
            supplier_batch_number TEXT,
            purchase_order_id INTEGER,
            purchase_order_reference TEXT,
            
            -- Quality Control
            quality_status TEXT DEFAULT 'approved' CHECK(quality_status IN ('approved', 'quarantine', 'rejected', 'hold', 'tested')),
            qc_test_date DATE,
            qc_passed BOOLEAN DEFAULT 1,
            qc_notes TEXT,
            qc_inspector_id INTEGER,
            
            -- Cost & Pricing
            unit_cost DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            landed_cost DECIMAL(12,4),  -- Cost including shipping, duties, etc.
            total_cost DECIMAL(12,4),
            average_cost DECIMAL(12,4),
            
            -- Serial Numbers (if applicable)
            serial_numbers TEXT DEFAULT '[]',  -- JSON array of serial numbers
            serial_number_range_start TEXT,
            serial_number_range_end TEXT,
            
            -- Certifications
            certification_number TEXT,
            certification_authority TEXT,
            certification_valid_until DATE,
            
            -- Alerts & Notifications
            expiry_alert_sent BOOLEAN DEFAULT 0,
            expiry_alert_sent_date DATE,
            low_stock_alert_sent BOOLEAN DEFAULT 0,
            
            -- Status
            is_active BOOLEAN DEFAULT 1,
            is_blocked BOOLEAN DEFAULT 0,
            block_reason TEXT,
            
            -- Audit
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP,
            closed_by INTEGER,
            closure_reason TEXT,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (product_variation_id) REFERENCES product_variations(id),
            FOREIGN KEY (supplier_id) REFERENCES wholesale_partners(id),
            FOREIGN KEY (qc_inspector_id) REFERENCES employees(id),
            FOREIGN KEY (created_by) REFERENCES employees(id),
            UNIQUE(product_id, product_variation_id, batch_number)
        )
        """)
        
        # Stock movements table - Complete audit trail
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Product Information
            product_id INTEGER NOT NULL,
            product_variation_id INTEGER,
            product_name TEXT,
            product_sku TEXT,
            product_barcode TEXT,
            
            -- Batch Information
            batch_id INTEGER,
            batch_number TEXT,
            
            -- Movement Details
            movement_type TEXT NOT NULL CHECK(movement_type IN (
                'purchase', 'sale', 'return_customer', 'return_supplier',
                'adjustment', 'transfer_in', 'transfer_out', 'damage',
                'expiry', 'sample', 'production', 'assembly', 'disassembly',
                'correction', 'write_off', 'found', 'lost', 'loan_out', 'loan_return'
            )),
            movement_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            effective_date DATE,  -- When the movement takes effect
            
            -- Quantities
            quantity DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            unit_of_measure TEXT DEFAULT 'pcs',
            conversion_factor DECIMAL(10,6) DEFAULT 1.0,
            base_quantity DECIMAL(12,4),  -- In base unit
            
            -- Stock Levels
            balance_before DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            balance_after DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            batch_balance_before DECIMAL(12,4),
            batch_balance_after DECIMAL(12,4),
            
            -- Location
            warehouse_id INTEGER NOT NULL,
            from_warehouse_id INTEGER,
            to_warehouse_id INTEGER,
            shelf_location TEXT,
            
            -- Pricing
            unit_cost DECIMAL(12,4),
            unit_price DECIMAL(12,4),
            total_cost DECIMAL(12,4),
            total_value DECIMAL(12,4),
            
            -- Reference Documents
            reference_type TEXT CHECK(reference_type IN ('sale', 'purchase', 'transfer', 'adjustment', 'production')),
            reference_id INTEGER,  -- Link to source document
            reference_number TEXT,  -- Document number
            reference_line_id INTEGER,  -- Line item in source document
            
            -- Supplier/Customer
            partner_id INTEGER,  -- Supplier or customer
            partner_name TEXT,
            partner_type TEXT CHECK(partner_type IN ('supplier', 'customer', 'employee', 'other')),
            
            -- Reason & Justification
            reason_code TEXT,
            reason_description TEXT,
            adjustment_type TEXT CHECK(adjustment_type IN ('correction', 'damage', 'expiry', 'theft', 'sample', 'donation', 'other')),
            approval_required BOOLEAN DEFAULT 0,
            approved_by INTEGER,
            approval_date TIMESTAMP,
            
            -- Quality Information
            quality_notes TEXT,
            damage_type TEXT,
            damage_severity TEXT CHECK(damage_severity IN ('minor', 'moderate', 'severe', 'total')),
            expiry_status TEXT CHECK(expiry_status IN ('fresh', 'near_expiry', 'expired')),
            
            -- Transfer Details
            transfer_reference TEXT,
            transfer_status TEXT CHECK(transfer_status IN ('pending', 'in_transit', 'received', 'rejected', 'cancelled')),
            received_quantity DECIMAL(12,4),
            rejected_quantity DECIMAL(12,4),
            rejection_reason TEXT,
            
            -- Production Details
            production_order_id INTEGER,
            production_stage TEXT,
            output_product_id INTEGER,
            
            -- User & Session
            user_id INTEGER NOT NULL,
            user_name TEXT,
            terminal_id TEXT,
            shift_id INTEGER,
            session_id TEXT,
            
            -- Device & Location
            device_id TEXT,
            device_ip TEXT,
            geo_latitude DECIMAL(10,8),
            geo_longitude DECIMAL(11,8),
            
            -- Notes & Documentation
            notes TEXT,
            attachment_path TEXT,
            barcode_scan_data TEXT,
            
            -- Audit Trail
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reversed BOOLEAN DEFAULT 0,
            reversal_of_id INTEGER,
            reversal_reason TEXT,
            
            -- Integration
            synced_to_accounting BOOLEAN DEFAULT 0,
            accounting_entry_id INTEGER,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (product_variation_id) REFERENCES product_variations(id),
            FOREIGN KEY (batch_id) REFERENCES stock_batches(id),
            FOREIGN KEY (user_id) REFERENCES employees(id),
            FOREIGN KEY (approved_by) REFERENCES employees(id),
            FOREIGN KEY (reversal_of_id) REFERENCES stock_movements(id)
        )
        """)
        
        # Warehouses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS warehouses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'store' CHECK(type IN ('store', 'warehouse', 'cold_storage', 'bonded', 'transit', 'virtual')),
            
            -- Contact Information
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            country TEXT,
            phone TEXT,
            email TEXT,
            contact_person TEXT,
            
            -- Location
            geo_latitude DECIMAL(10,8),
            geo_longitude DECIMAL(11,8),
            location_description TEXT,
            
            -- Operational Details
            manager_id INTEGER,
            capacity_cubic_meters DECIMAL(10,2),
            current_occupancy DECIMAL(5,2),  -- Percentage
            temperature_controlled BOOLEAN DEFAULT 0,
            min_temperature_celsius DECIMAL(5,2),
            max_temperature_celsius DECIMAL(5,2),
            humidity_controlled BOOLEAN DEFAULT 0,
            
            -- Security
            security_level TEXT CHECK(security_level IN ('low', 'medium', 'high', 'maximum')),
            access_control_required BOOLEAN DEFAULT 0,
            surveillance_cameras BOOLEAN DEFAULT 0,
            alarm_system BOOLEAN DEFAULT 0,
            
            -- Status
            is_active BOOLEAN DEFAULT 1,
            is_operational BOOLEAN DEFAULT 1,
            opening_hours TEXT,  -- JSON format
            maintenance_schedule TEXT,
            
            -- Financial
            rental_cost DECIMAL(10,2),
            utility_cost DECIMAL(10,2),
            other_costs DECIMAL(10,2),
            cost_center TEXT,
            
            -- Inventory Settings
            default_bin_size TEXT,
            bin_labeling_system TEXT,
            picking_strategy TEXT DEFAULT 'fifo' CHECK(picking_strategy IN ('fifo', 'lifo', 'fefo', 'manual')),
            
            -- Audit
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (manager_id) REFERENCES employees(id)
        )
        """)
        
        # Stock takes (inventory counts)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_takes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_take_number TEXT UNIQUE NOT NULL,
            warehouse_id INTEGER NOT NULL,
            
            -- Timing
            planned_date DATE NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            completion_date TIMESTAMP,
            
            -- Scope
            count_type TEXT DEFAULT 'full' CHECK(count_type IN ('full', 'cycle', 'random', 'section', 'category')),
            include_categories TEXT,  -- JSON array of category IDs
            exclude_categories TEXT,  -- JSON array
            include_zones TEXT,  -- JSON array of warehouse zones
            exclude_zones TEXT,
            
            -- Team
            team_leader_id INTEGER NOT NULL,
            team_members TEXT DEFAULT '[]',  -- JSON array of employee IDs
            assigned_by INTEGER,
            
            -- Status
            status TEXT DEFAULT 'planned' CHECK(status IN ('planned', 'in_progress', 'completed', 'cancelled', 'verified')),
            verification_status TEXT DEFAULT 'pending' CHECK(verification_status IN ('pending', 'verified', 'discrepancy', 'adjusted')),
            
            -- Results
            total_items_counted INTEGER DEFAULT 0,
            total_expected_items INTEGER,
            items_with_discrepancy INTEGER DEFAULT 0,
            total_discrepancy_value DECIMAL(12,4) DEFAULT 0.0000,
            accuracy_percentage DECIMAL(5,2),
            
            -- Adjustments
            adjustment_document_id INTEGER,
            adjustment_date TIMESTAMP,
            adjusted_by INTEGER,
            
            -- Verification
            verified_by INTEGER,
            verification_date TIMESTAMP,
            verification_notes TEXT,
            verification_method TEXT CHECK(verification_method IN ('recount', 'sample', 'system', 'manager')),
            
            -- Notes
            purpose TEXT,
            instructions TEXT,
            notes TEXT,
            issues_encountered TEXT,
            
            -- Audit
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
            FOREIGN KEY (team_leader_id) REFERENCES employees(id),
            FOREIGN KEY (assigned_by) REFERENCES employees(id),
            FOREIGN KEY (adjusted_by) REFERENCES employees(id),
            FOREIGN KEY (verified_by) REFERENCES employees(id)
        )
        """)
        
        # Stock take items
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_take_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_take_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_variation_id INTEGER,
            batch_id INTEGER,
            
            -- Location
            warehouse_id INTEGER NOT NULL,
            shelf_location TEXT,
            
            -- Counts
            expected_quantity DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            counted_quantity DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            second_count_quantity DECIMAL(12,4),
            verified_quantity DECIMAL(12,4),
            
            -- Discrepancy
            discrepancy_quantity DECIMAL(12,4),
            discrepancy_percentage DECIMAL(7,4),
            discrepancy_value DECIMAL(12,4),  -- Monetary value of discrepancy
            discrepancy_type TEXT CHECK(discrepancy_type IN ('overage', 'shortage', 'correct')),
            
            -- Pricing
            unit_cost DECIMAL(12,4),
            unit_price DECIMAL(12,4),
            
            -- Counting Details
            counted_by INTEGER NOT NULL,
            counted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            count_method TEXT CHECK(count_method IN ('manual', 'barcode', 'rfid', 'weighing')),
            count_device_id TEXT,
            
            -- Verification
            verified_by INTEGER,
            verified_at TIMESTAMP,
            verification_method TEXT,
            verification_notes TEXT,
            
            -- Status
            status TEXT DEFAULT 'counted' CHECK(status IN ('pending', 'counted', 'verified', 'disputed', 'adjusted')),
            requires_recount BOOLEAN DEFAULT 0,
            recount_reason TEXT,
            
            -- Notes
            notes TEXT,
            product_condition TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (stock_take_id) REFERENCES stock_takes(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (product_variation_id) REFERENCES product_variations(id),
            FOREIGN KEY (batch_id) REFERENCES stock_batches(id),
            FOREIGN KEY (counted_by) REFERENCES employees(id),
            FOREIGN KEY (verified_by) REFERENCES employees(id),
            UNIQUE(stock_take_id, product_id, product_variation_id, batch_id, shelf_location)
        )
        """)
    
    def _create_customer_tables(self, cursor):
        """Create customer and CRM tables."""
        
        # Customers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Basic Information
            customer_code TEXT UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            display_name TEXT,
            company_name TEXT,
            
            -- Contact Information
            phone TEXT UNIQUE,
            secondary_phone TEXT,
            email TEXT UNIQUE,
            secondary_email TEXT,
            website TEXT,
            
            -- Social Media
            facebook_profile TEXT,
            twitter_handle TEXT,
            instagram_handle TEXT,
            linkedin_profile TEXT,
            
            -- Demographics
            birth_date DATE,
            gender TEXT CHECK(gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
            marital_status TEXT CHECK(marital_status IN ('single', 'married', 'divorced', 'widowed')),
            occupation TEXT,
            education_level TEXT,
            income_range TEXT,
            
            -- Addresses
            billing_address TEXT,
            billing_city TEXT,
            billing_state TEXT,
            billing_zip_code TEXT,
            billing_country TEXT,
            
            shipping_address TEXT,
            shipping_city TEXT,
            shipping_state TEXT,
            shipping_zip_code TEXT,
            shipping_country TEXT,
            is_shipping_same_as_billing BOOLEAN DEFAULT 1,
            
            -- Location
            geo_latitude DECIMAL(10,8),
            geo_longitude DECIMAL(11,8),
            timezone TEXT,
            preferred_language TEXT DEFAULT 'en',
            
            -- Tax & Legal
            tax_id TEXT,
            tax_exempt BOOLEAN DEFAULT 0,
            tax_exempt_certificate TEXT,
            vat_number TEXT,
            business_registration_number TEXT,
            
            -- Customer Classification
            customer_type TEXT DEFAULT 'retail' CHECK(customer_type IN ('retail', 'wholesale', 'corporate', 'dealer', 'distributor', 'vip')),
            customer_group TEXT,
            customer_segment TEXT,
            customer_tier TEXT DEFAULT 'regular' CHECK(customer_tier IN ('regular', 'silver', 'gold', 'platinum', 'diamond')),
            customer_category TEXT,
            
            -- Financial
            credit_limit DECIMAL(12,2) DEFAULT 0.00,
            current_balance DECIMAL(12,2) DEFAULT 0.00,
            total_credit DECIMAL(12,2) DEFAULT 0.00,
            available_credit DECIMAL(12,2),
            payment_terms TEXT DEFAULT 'COD' CHECK(payment_terms IN ('COD', 'Net 7', 'Net 15', 'Net 30', 'Net 60')),
            discount_percent DECIMAL(5,2) DEFAULT 0.00,
            
            -- Loyalty Program
            loyalty_card_number TEXT UNIQUE,
            loyalty_points_balance INTEGER DEFAULT 0,
            loyalty_points_total_earned INTEGER DEFAULT 0,
            loyalty_points_total_redeemed INTEGER DEFAULT 0,
            loyalty_tier TEXT,
            loyalty_member_since DATE,
            
            -- Sales Statistics
            first_purchase_date DATE,
            last_purchase_date DATE,
            total_purchases INTEGER DEFAULT 0,
            total_spent DECIMAL(12,2) DEFAULT 0.00,
            average_order_value DECIMAL(10,2) DEFAULT 0.00,
            purchase_frequency_days DECIMAL(7,2),
            recency_score INTEGER,
            frequency_score INTEGER,
            monetary_score INTEGER,
            customer_lifetime_value DECIMAL(12,2) DEFAULT 0.00,
            
            -- Communication Preferences
            marketing_opt_in BOOLEAN DEFAULT 1,
            sms_notifications BOOLEAN DEFAULT 1,
            email_notifications BOOLEAN DEFAULT 1,
            whatsapp_notifications BOOLEAN DEFAULT 1,
            preferred_contact_method TEXT DEFAULT 'phone' CHECK(preferred_contact_method IN ('phone', 'email', 'sms', 'whatsapp', 'app')),
            newsletter_subscription BOOLEAN DEFAULT 0,
            
            -- Source & Acquisition
            source TEXT DEFAULT 'walk_in' CHECK(source IN ('walk_in', 'referral', 'social_media', 'online_ad', 'event', 'telemarketing', 'email_campaign')),
            referral_code TEXT,
            referred_by_customer_id INTEGER,
            acquisition_channel TEXT,
            acquisition_cost DECIMAL(10,2) DEFAULT 0.00,
            acquisition_date DATE,
            
            -- Customer Service
            customer_satisfaction_score INTEGER CHECK(customer_satisfaction_score BETWEEN 1 AND 5),
            last_satisfaction_survey_date DATE,
            total_complaints INTEGER DEFAULT 0,
            total_compliments INTEGER DEFAULT 0,
            issue_resolution_rate DECIMAL(5,2),
            preferred_support_channel TEXT,
            
            -- Employee Relationship
            assigned_sales_rep_id INTEGER,
            account_manager_id INTEGER,
            
            -- Risk Assessment
            risk_level TEXT DEFAULT 'low' CHECK(risk_level IN ('low', 'medium', 'high', 'blacklisted')),
            credit_score INTEGER,
            payment_delinquency_days INTEGER DEFAULT 0,
            default_count INTEGER DEFAULT 0,
            blacklist_reason TEXT,
            blacklisted_at TIMESTAMP,
            blacklisted_by INTEGER,
            
            -- Notes & Preferences
            notes TEXT,
            preferences TEXT DEFAULT '{}',  -- JSON: {"preferred_payment": "cash", "favorite_categories": [1,2]}
            special_instructions TEXT,
            dietary_restrictions TEXT,
            allergy_information TEXT,
            
            -- Documents
            id_proof_path TEXT,
            address_proof_path TEXT,
            contract_path TEXT,
            
            -- Status
            is_active BOOLEAN DEFAULT 1,
            is_verified BOOLEAN DEFAULT 0,
            verification_date DATE,
            verification_method TEXT,
            verification_notes TEXT,
            
            -- Audit
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (referred_by_customer_id) REFERENCES customers(id),
            FOREIGN KEY (assigned_sales_rep_id) REFERENCES employees(id),
            FOREIGN KEY (account_manager_id) REFERENCES employees(id),
            FOREIGN KEY (blacklisted_by) REFERENCES employees(id)
        )
        """)
        
        # Customer contacts (multiple contacts per customer for businesses)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            contact_name TEXT NOT NULL,
            job_title TEXT,
            department TEXT,
            
            -- Contact Information
            phone TEXT,
            mobile TEXT,
            email TEXT,
            secondary_email TEXT,
            
            -- Communication Preferences
            preferred_contact_method TEXT,
            preferred_contact_time TEXT,
            do_not_call BOOLEAN DEFAULT 0,
            do_not_email BOOLEAN DEFAULT 0,
            
            -- Relationship
            is_primary_contact BOOLEAN DEFAULT 0,
            relationship_to_company TEXT,
            decision_maker_level TEXT CHECK(decision_maker_level IN ('influencer', 'recommender', 'decider', 'approver', 'buyer')),
            
            -- Personal Information
            birth_date DATE,
            gender TEXT,
            
            -- Social Media
            linkedin_profile TEXT,
            
            -- Notes
            notes TEXT,
            interests TEXT,
            
            -- Status
            is_active BOOLEAN DEFAULT 1,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
        """)
        
        # Customer communications log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_communications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            contact_id INTEGER,
            
            -- Communication Details
            communication_type TEXT NOT NULL CHECK(communication_type IN ('call', 'email', 'sms', 'whatsapp', 'meeting', 'visit', 'chat', 'social_media')),
            direction TEXT NOT NULL CHECK(direction IN ('inbound', 'outbound')),
            
            -- Timing
            communication_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            scheduled_date TIMESTAMP,
            duration_minutes INTEGER,
            
            -- Content
            subject TEXT,
            summary TEXT,
            details TEXT,
            attachments TEXT DEFAULT '[]',  -- JSON array of attachment paths
            
            -- Participants
            initiated_by INTEGER NOT NULL,  -- Employee ID
            participants TEXT DEFAULT '[]',  -- JSON array of participant names/IDs
            
            -- Follow-up
            requires_follow_up BOOLEAN DEFAULT 0,
            follow_up_date DATE,
            follow_up_action TEXT,
            follow_up_assigned_to INTEGER,
            follow_up_completed BOOLEAN DEFAULT 0,
            
            -- Outcome
            outcome TEXT,
            sentiment TEXT CHECK(sentiment IN ('positive', 'neutral', 'negative', 'mixed')),
            satisfaction_score INTEGER CHECK(satisfaction_score BETWEEN 1 AND 5),
            
            -- Campaign
            campaign_id INTEGER,
            campaign_name TEXT,
            
            -- Lead/ Opportunity
            lead_id INTEGER,
            opportunity_id INTEGER,
            
            -- Notes
            internal_notes TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
            FOREIGN KEY (contact_id) REFERENCES customer_contacts(id),
            FOREIGN KEY (initiated_by) REFERENCES employees(id),
            FOREIGN KEY (follow_up_assigned_to) REFERENCES employees(id)
        )
        """)
    
    def _create_wholesale_tables(self, cursor):
        """Create wholesale/B2B management tables."""
        
        # Wholesale partners table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wholesale_partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            legal_name TEXT,
            
            -- Partner Type
            partner_type TEXT NOT NULL CHECK(partner_type IN ('supplier', 'buyer', 'both', 'manufacturer', 'distributor', 'agent')),
            relationship_type TEXT CHECK(relationship_type IN ('primary', 'secondary', 'backup', 'exclusive', 'preferred')),
            
            -- Contact Information
            phone TEXT,
            secondary_phone TEXT,
            email TEXT,
            secondary_email TEXT,
            website TEXT,
            fax TEXT,
            
            -- Address
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            country TEXT,
            region TEXT,
            
            -- Location
            geo_latitude DECIMAL(10,8),
            geo_longitude DECIMAL(11,8),
            timezone TEXT,
            
            -- Tax & Legal
            tax_id TEXT UNIQUE,
            vat_number TEXT,
            business_registration_number TEXT,
            business_registration_date DATE,
            legal_structure TEXT,
            industry TEXT,
            
            -- Financial Information
            currency TEXT DEFAULT 'USD',
            credit_limit DECIMAL(12,2) DEFAULT 0.00,
            current_balance DECIMAL(12,2) DEFAULT 0.00,
            balance_type TEXT DEFAULT 'neutral' CHECK(balance_type IN ('we_owe', 'they_owe', 'neutral')),
            available_credit DECIMAL(12,2),
            
            -- Payment Terms
            payment_terms TEXT DEFAULT 'Net 30',
            early_payment_discount DECIMAL(5,2) DEFAULT 0.00,
            late_payment_penalty DECIMAL(5,2) DEFAULT 0.00,
            preferred_payment_method TEXT DEFAULT 'bank_transfer' CHECK(preferred_payment_method IN ('bank_transfer', 'cash', 'cheque', 'credit_card', 'online')),
            
            -- Bank Details
            bank_name TEXT,
            bank_branch TEXT,
            bank_account_number TEXT,
            bank_iban TEXT,
            bank_swift_code TEXT,
            account_holder_name TEXT,
            bank_address TEXT,
            routing_number TEXT,
            
            -- Contact Persons
            primary_contact_name TEXT,
            primary_contact_title TEXT,
            primary_contact_phone TEXT,
            primary_contact_email TEXT,
            
            secondary_contact_name TEXT,
            secondary_contact_title TEXT,
            secondary_contact_phone TEXT,
            secondary_contact_email TEXT,
            
            -- Performance Metrics
            reliability_score INTEGER CHECK(reliability_score BETWEEN 1 AND 5),
            quality_score INTEGER CHECK(quality_score BETWEEN 1 AND 5),
            delivery_score INTEGER CHECK(delivery_score BETWEEN 1 AND 5),
            overall_rating DECIMAL(3,2),
            last_performance_review DATE,
            
            -- Business Metrics
            annual_turnover DECIMAL(15,2),
            employee_count INTEGER,
            year_established INTEGER,
            export_percentage DECIMAL(5,2),
            import_percentage DECIMAL(5,2),
            
            -- Products & Services
            product_categories TEXT DEFAULT '[]',  -- JSON array
            service_areas TEXT,
            certifications TEXT DEFAULT '[]',  -- JSON array
            brands_handled TEXT,
            
            -- Logistics
            lead_time_days INTEGER DEFAULT 7,
            minimum_order_quantity DECIMAL(12,4),
            minimum_order_value DECIMAL(12,2),
            shipping_methods TEXT DEFAULT '[]',
            delivery_coverage TEXT,
            
            -- Quality & Compliance
            quality_certifications TEXT,
            compliance_standards TEXT,
            inspection_required BOOLEAN DEFAULT 0,
            inspection_frequency TEXT,
            
            -- Contract Information
            contract_reference TEXT,
            contract_start_date DATE,
            contract_end_date DATE,
            contract_terms TEXT,
            contract_document_path TEXT,
            auto_renewal BOOLEAN DEFAULT 0,
            renewal_notice_days INTEGER DEFAULT 30,
            
            -- Commission & Fees
            commission_rate DECIMAL(5,2) DEFAULT 0.00,
            rebate_percentage DECIMAL(5,2) DEFAULT 0.00,
            handling_fee DECIMAL(10,2) DEFAULT 0.00,
            
            -- Risk Assessment
            risk_level TEXT DEFAULT 'low' CHECK(risk_level IN ('low', 'medium', 'high', 'blacklisted')),
            credit_rating TEXT,
            payment_history TEXT DEFAULT '[]',  -- JSON array
            dispute_count INTEGER DEFAULT 0,
            blacklist_reason TEXT,
            blacklisted_at TIMESTAMP,
            blacklisted_by INTEGER,
            
            -- Communication Preferences
            preferred_communication_method TEXT,
            preferred_contact_time TEXT,
            marketing_opt_in BOOLEAN DEFAULT 1,
            
            -- Notes & Documents
            notes TEXT,
            internal_notes TEXT,
            document_paths TEXT DEFAULT '[]',  -- JSON array
            
            -- Status
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended', 'pending_approval', 'blacklisted')),
            approval_status TEXT DEFAULT 'approved' CHECK(approval_status IN ('pending', 'approved', 'rejected', 'on_hold')),
            approved_by INTEGER,
            approval_date DATE,
            rejection_reason TEXT,
            
            -- Audit
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (approved_by) REFERENCES employees(id),
            FOREIGN KEY (blacklisted_by) REFERENCES employees(id)
        )
        """)
        
        # Wholesale transactions (purchases/sales to partners)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wholesale_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_number TEXT UNIQUE NOT NULL,
            partner_id INTEGER NOT NULL,
            
            -- Transaction Type
            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('purchase', 'sale', 'return_supplier', 'return_customer', 'credit_note', 'debit_note')),
            document_type TEXT DEFAULT 'invoice' CHECK(document_type IN ('quotation', 'proforma', 'invoice', 'credit_note', 'debit_note', 'order', 'receipt')),
            
            -- Dates
            transaction_date DATE NOT NULL,
            due_date DATE,
            delivery_date DATE,
            payment_date DATE,
            
            -- Amounts
            subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            discount_amount DECIMAL(12,2) DEFAULT 0.00,
            tax_amount DECIMAL(12,2) DEFAULT 0.00,
            shipping_amount DECIMAL(12,2) DEFAULT 0.00,
            other_charges DECIMAL(12,2) DEFAULT 0.00,
            total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            
            -- Payment Information
            paid_amount DECIMAL(12,2) DEFAULT 0.00,
            remaining_amount DECIMAL(12,2),
            payment_status TEXT DEFAULT 'unpaid' CHECK(payment_status IN ('unpaid', 'partial', 'paid', 'overdue', 'cancelled', 'refunded')),
            overdue_days INTEGER,
            
            -- Currency
            currency TEXT DEFAULT 'USD',
            exchange_rate DECIMAL(10,6) DEFAULT 1.0,
            base_currency_amount DECIMAL(12,2),
            
            -- Terms
            payment_terms TEXT,
            early_payment_discount DECIMAL(5,2),
            discount_expiry_date DATE,
            late_payment_penalty DECIMAL(5,2),
            
            -- Shipping & Delivery
            shipping_method TEXT,
            tracking_number TEXT,
            carrier TEXT,
            shipping_address TEXT,
            delivery_status TEXT CHECK(delivery_status IN ('pending', 'processing', 'shipped', 'delivered', 'failed', 'returned')),
            
            -- Reference Documents
            reference_number TEXT,
            purchase_order_number TEXT,
            sales_order_number TEXT,
            original_invoice_id INTEGER,
            
            -- Tax Details
            tax_breakdown TEXT DEFAULT '[]',
            tax_exempt BOOLEAN DEFAULT 0,
            tax_exempt_certificate TEXT,
            
            -- Discount Details
            discount_type TEXT,
            discount_reason TEXT,
            
            -- Notes
            notes TEXT,
            terms_and_conditions TEXT,
            special_instructions TEXT,
            
            -- Status & Workflow
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'sent', 'confirmed', 'processing', 'completed', 'cancelled', 'closed')),
            approval_status TEXT DEFAULT 'pending' CHECK(approval_status IN ('pending', 'approved', 'rejected')),
            approved_by INTEGER,
            approved_at TIMESTAMP,
            rejection_reason TEXT,
            
            -- Audit
            created_by INTEGER NOT NULL,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP,
            closed_by INTEGER,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (partner_id) REFERENCES wholesale_partners(id),
            FOREIGN KEY (approved_by) REFERENCES employees(id),
            FOREIGN KEY (created_by) REFERENCES employees(id),
            FOREIGN KEY (closed_by) REFERENCES employees(id)
        )
        """)
        
        # Wholesale transaction items
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wholesale_transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_variation_id INTEGER,
            
            -- Product Information
            product_name TEXT NOT NULL,
            product_sku TEXT,
            product_barcode TEXT,
            description TEXT,
            
            -- Quantities
            quantity DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            unit_of_measure TEXT DEFAULT 'pcs',
            delivered_quantity DECIMAL(12,4) DEFAULT 0.0000,
            returned_quantity DECIMAL(12,4) DEFAULT 0.0000,
            
            -- Pricing
            unit_price DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            original_price DECIMAL(12,4),
            discount_percent DECIMAL(5,2) DEFAULT 0.00,
            discount_amount DECIMAL(12,4) DEFAULT 0.0000,
            tax_percent DECIMAL(5,2) DEFAULT 0.00,
            tax_amount DECIMAL(12,4) DEFAULT 0.0000,
            total_price DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
            
            -- Cost & Margin
            cost_price DECIMAL(12,4),
            margin_percent DECIMAL(7,4),
            margin_amount DECIMAL(12,4),
            
            -- Batch Information
            batch_number TEXT,
            expiry_date DATE,
            
            -- Warehouse
            warehouse_id INTEGER,
            shelf_location TEXT,
            
            -- Delivery Status
            delivery_status TEXT,
            expected_delivery_date DATE,
            actual_delivery_date DATE,
            
            -- Return Information
            return_reason TEXT,
            return_date DATE,
            return_condition TEXT,
            
            -- Notes
            notes TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (transaction_id) REFERENCES wholesale_transactions(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (product_variation_id) REFERENCES product_variations(id)
        )
        """)
        
        # Wholesale payments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wholesale_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_number TEXT UNIQUE NOT NULL,
            transaction_id INTEGER NOT NULL,
            partner_id INTEGER NOT NULL,
            
            -- Payment Details
            payment_date DATE NOT NULL,
            payment_method TEXT NOT NULL CHECK(payment_method IN ('cash', 'bank_transfer', 'cheque', 'credit_card', 'online', 'mobile_money', 'adjustment')),
            payment_type TEXT DEFAULT 'payment' CHECK(payment_type IN ('payment', 'deposit', 'refund', 'adjustment', 'write_off')),
            
            -- Amounts
            amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            currency TEXT DEFAULT 'USD',
            exchange_rate DECIMAL(10,6) DEFAULT 1.0,
            base_currency_amount DECIMAL(12,2),
            
            -- Allocation
            allocated_amount DECIMAL(12,2) DEFAULT 0.00,
            unallocated_amount DECIMAL(12,2),
            is_fully_allocated BOOLEAN,
            
            -- Payment Instruments
            cheque_number TEXT,
            cheque_date DATE,
            cheque_bank TEXT,
            bank_reference TEXT,
            transaction_reference TEXT,
            card_last_four TEXT,
            card_type TEXT,
            authorization_code TEXT,
            online_payment_id TEXT,
            
            -- Bank Details
            bank_name TEXT,
            bank_account TEXT,
            
            -- Status
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'cancelled', 'reversed', 'failed')),
            cleared BOOLEAN DEFAULT 0,
            clearance_date DATE,
            reconciliation_status TEXT DEFAULT 'unreconciled' CHECK(reconciliation_status IN ('unreconciled', 'reconciled', 'disputed')),
            
            -- Notes
            notes TEXT,
            memo TEXT,
            
            -- Approval
            approved_by INTEGER,
            approved_at TIMESTAMP,
            verification_required BOOLEAN DEFAULT 0,
            verified_by INTEGER,
            verified_at TIMESTAMP,
            
            -- Receipt
            receipt_number TEXT,
            receipt_path TEXT,
            
            -- Reversal
            reversed BOOLEAN DEFAULT 0,
            reversal_of_id INTEGER,
            reversal_reason TEXT,
            reversed_by INTEGER,
            reversed_at TIMESTAMP,
            
            -- Audit
            created_by INTEGER NOT NULL,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (transaction_id) REFERENCES wholesale_transactions(id),
            FOREIGN KEY (partner_id) REFERENCES wholesale_partners(id),
            FOREIGN KEY (approved_by) REFERENCES employees(id),
            FOREIGN KEY (verified_by) REFERENCES employees(id),
            FOREIGN KEY (created_by) REFERENCES employees(id),
            FOREIGN KEY (reversed_by) REFERENCES employees(id),
            FOREIGN KEY (reversal_of_id) REFERENCES wholesale_payments(id)
        )
        """)
        
        # Payment allocations (linking payments to specific invoices)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id INTEGER NOT NULL,
            transaction_id INTEGER NOT NULL,
            
            -- Allocation Details
            allocation_date DATE NOT NULL,
            allocated_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            
            -- Discount Applied
            discount_allowed DECIMAL(12,2) DEFAULT 0.00,
            early_payment_discount DECIMAL(12,2) DEFAULT 0.00,
            
            -- Status
            status TEXT DEFAULT 'allocated' CHECK(status IN ('allocated', 'adjusted', 'reversed')),
            
            -- Notes
            notes TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (payment_id) REFERENCES wholesale_payments(id) ON DELETE CASCADE,
            FOREIGN KEY (transaction_id) REFERENCES wholesale_transactions(id),
            UNIQUE(payment_id, transaction_id)
        )
        """)
    
    def _create_financial_tables(self, cursor):
        """Create financial and accounting tables."""
        
        # Chart of accounts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_code TEXT UNIQUE NOT NULL,
            account_name TEXT NOT NULL,
            account_type TEXT NOT NULL CHECK(account_type IN ('asset', 'liability', 'equity', 'revenue', 'expense', 'cost_of_sales')),
            account_subtype TEXT,
            
            -- Classification
            category TEXT,
            subcategory TEXT,
            classification TEXT CHECK(classification IN ('current', 'non_current', 'operating', 'non_operating')),
            
            -- Financial Reporting
            balance_sheet_category TEXT,
            income_statement_category TEXT,
            cash_flow_category TEXT CHECK(cash_flow_category IN ('operating', 'investing', 'financing')),
            
            -- Currency & Valuation
            currency TEXT DEFAULT 'USD',
            is_currency_account BOOLEAN DEFAULT 0,
            allows_multiple_currencies BOOLEAN DEFAULT 0,
            
            -- Accounting Rules
            normal_balance TEXT DEFAULT 'debit' CHECK(normal_balance IN ('debit', 'credit')),
            is_contra_account BOOLEAN DEFAULT 0,
            contra_to_account_id INTEGER,
            
            -- Tax
            tax_code TEXT,
            tax_rate DECIMAL(5,2),
            is_tax_account BOOLEAN DEFAULT 0,
            tax_type TEXT,
            
            -- Bank & Cash
            is_bank_account BOOLEAN DEFAULT 0,
            is_cash_account BOOLEAN DEFAULT 0,
            bank_name TEXT,
            bank_account_number TEXT,
            
            -- Budgeting
            budget_allowed BOOLEAN DEFAULT 0,
            budget_amount DECIMAL(15,2),
            budget_period TEXT CHECK(budget_period IN ('monthly', 'quarterly', 'annual')),
            
            -- Reconciliation
            requires_reconciliation BOOLEAN DEFAULT 0,
            last_reconciled_date DATE,
            reconciliation_frequency TEXT CHECK(reconciliation_frequency IN ('daily', 'weekly', 'monthly', 'quarterly')),
            
            -- Status & Control
            is_active BOOLEAN DEFAULT 1,
            is_system_account BOOLEAN DEFAULT 0,
            is_control_account BOOLEAN DEFAULT 0,
            requires_approval BOOLEAN DEFAULT 0,
            approval_limit DECIMAL(15,2),
            
            -- Parent-Child Relationship
            parent_account_id INTEGER,
            account_level INTEGER DEFAULT 1,
            is_detail_account BOOLEAN DEFAULT 1,
            
            -- Reporting
            financial_statement_line TEXT,
            segment_code TEXT,
            cost_center_code TEXT,
            project_code TEXT,
            
            -- Notes
            description TEXT,
            notes TEXT,
            
            -- Audit
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (parent_account_id) REFERENCES accounts(id),
            FOREIGN KEY (contra_to_account_id) REFERENCES accounts(id)
        )
        """)
        
        # Expenses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_number TEXT UNIQUE NOT NULL,
            
            -- Basic Information
            expense_date DATE NOT NULL,
            description TEXT NOT NULL,
            notes TEXT,
            
            -- Categorization
            category TEXT NOT NULL,
            subcategory TEXT,
            expense_type TEXT CHECK(expense_type IN ('operational', 'administrative', 'sales', 'marketing', 'financial', 'tax', 'employee', 'capital', 'other')),
            
            -- Amounts
            amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            tax_amount DECIMAL(10,2) DEFAULT 0.00,
            total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            
            -- Currency
            currency TEXT DEFAULT 'USD',
            exchange_rate DECIMAL(10,6) DEFAULT 1.0,
            base_currency_amount DECIMAL(10,2),
            
            -- Payment Information
            payment_method TEXT CHECK(payment_method IN ('cash', 'bank_transfer', 'cheque', 'credit_card', 'online')),
            payment_status TEXT DEFAULT 'unpaid' CHECK(payment_status IN ('unpaid', 'partial', 'paid', 'reimbursed')),
            paid_amount DECIMAL(10,2) DEFAULT 0.00,
            payment_date DATE,
            
            -- Supplier/Vendor
            supplier_id INTEGER,
            supplier_name TEXT,
            supplier_invoice_number TEXT,
            
            -- Employee/Claimant
            employee_id INTEGER NOT NULL,
            claim_id INTEGER,
            is_reimbursable BOOLEAN DEFAULT 0,
            reimbursed_amount DECIMAL(10,2) DEFAULT 0.00,
            reimbursement_date DATE,
            
            -- Project/Department
            project_id INTEGER,
            department TEXT,
            cost_center TEXT,
            
            -- Accounting
            account_id INTEGER,
            gl_account_code TEXT,
            is_capitalized BOOLEAN DEFAULT 0,
            capitalization_period_months INTEGER,
            depreciation_method TEXT,
            
            -- Recurring Expenses
            is_recurring BOOLEAN DEFAULT 0,
            recurrence_pattern TEXT CHECK(recurrence_pattern IN ('daily', 'weekly', 'monthly', 'quarterly', 'annual')),
            recurrence_end_date DATE,
            next_recurrence_date DATE,
            
            -- Approval Workflow
            status TEXT DEFAULT 'pending' CHECK(status IN ('draft', 'submitted', 'approved', 'rejected', 'paid', 'cancelled')),
            approved_by INTEGER,
            approved_at TIMESTAMP,
            approval_notes TEXT,
            rejection_reason TEXT,
            
            -- Documentation
            receipt_image_path TEXT,
            supporting_documents TEXT DEFAULT '[]',  -- JSON array
            receipt_number TEXT,
            receipt_date DATE,
            
            -- Tax
            tax_deductible BOOLEAN DEFAULT 1,
            tax_deduction_percent DECIMAL(5,2),
            vat_amount DECIMAL(10,2),
            vat_rate DECIMAL(5,2),
            
            -- Audit
            created_by INTEGER NOT NULL,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (supplier_id) REFERENCES wholesale_partners(id),
            FOREIGN KEY (approved_by) REFERENCES employees(id),
            FOREIGN KEY (created_by) REFERENCES employees(id)
        )
        """)
        
        # General ledger entries
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS general_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_number TEXT UNIQUE NOT NULL,
            
            -- Entry Details
            entry_date DATE NOT NULL,
            posting_date DATE NOT NULL,
            description TEXT NOT NULL,
            reference_number TEXT,
            
            -- Transaction Information
            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('sale', 'purchase', 'expense', 'payment', 'receipt', 'adjustment', 'journal', 'closing')),
            transaction_id INTEGER,
            transaction_table TEXT,  -- Source table name
            
            -- Amounts
            debit_amount DECIMAL(15,2) DEFAULT 0.00,
            credit_amount DECIMAL(15,2) DEFAULT 0.00,
            currency TEXT DEFAULT 'USD',
            exchange_rate DECIMAL(10,6) DEFAULT 1.0,
            base_currency_debit DECIMAL(15,2),
            base_currency_credit DECIMAL(15,2),
            
            -- Accounts
            account_id INTEGER NOT NULL,
            contra_account_id INTEGER,
            
            -- Dimensions
            department TEXT,
            cost_center TEXT,
            project TEXT,
            segment TEXT,
            
            -- Status
            status TEXT DEFAULT 'posted' CHECK(status IN ('draft', 'posted', 'reversed', 'adjusted')),
            is_adjusting_entry BOOLEAN DEFAULT 0,
            is_closing_entry BOOLEAN DEFAULT 0,
            is_reversing_entry BOOLEAN DEFAULT 0,
            
            -- Reversal
            reversed_entry_id INTEGER,
            reversal_date DATE,
            reversal_reason TEXT,
            
            -- Period
            fiscal_year INTEGER,
            period INTEGER,  -- Month or quarter
            period_closed BOOLEAN DEFAULT 0,
            
            -- Audit
            posted_by INTEGER NOT NULL,
            approved_by INTEGER,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (contra_account_id) REFERENCES accounts(id),
            FOREIGN KEY (posted_by) REFERENCES employees(id),
            FOREIGN KEY (approved_by) REFERENCES employees(id),
            FOREIGN KEY (reversed_entry_id) REFERENCES general_ledger(id)
        )
        """)
    
    def _create_system_tables(self, cursor):
        """Create system tables for audit, settings, etc."""
        
        # Audit logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- User Information
            user_id INTEGER NOT NULL,
            username TEXT,
            user_role TEXT,
            
            -- Action Details
            action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action_type TEXT NOT NULL CHECK(action_type IN ('create', 'read', 'update', 'delete', 'login', 'logout', 'export', 'import', 'print', 'approve', 'reject')),
            module TEXT NOT NULL,
            submodule TEXT,
            entity_type TEXT,  -- Table name
            entity_id INTEGER,
            
            -- Change Details
            old_values TEXT,  -- JSON of old values
            new_values TEXT,  -- JSON of new values
            changed_fields TEXT DEFAULT '[]',  -- JSON array of field names
            change_summary TEXT,
            
            -- Access Details
            ip_address TEXT,
            user_agent TEXT,
            device_type TEXT,
            device_id TEXT,
            
            -- Location
            geo_latitude DECIMAL(10,8),
            geo_longitude DECIMAL(11,8),
            location_accuracy DECIMAL(5,2),
            
            -- Session
            session_id TEXT,
            request_id TEXT,
            
            -- Performance
            execution_time_ms INTEGER,
            record_count INTEGER,
            
            -- Status
            status TEXT DEFAULT 'success' CHECK(status IN ('success', 'failure', 'warning', 'partial')),
            error_message TEXT,
            error_code TEXT,
            
            -- Related Data
            related_entity_type TEXT,
            related_entity_id INTEGER,
            batch_id TEXT,
            
            -- Security
            security_level TEXT DEFAULT 'normal' CHECK(security_level IN ('normal', 'sensitive', 'critical')),
            requires_review BOOLEAN DEFAULT 0,
            reviewed_by INTEGER,
            review_date TIMESTAMP,
            review_notes TEXT,
            
            -- Compliance
            compliance_requirement TEXT,
            retention_period_days INTEGER DEFAULT 365,
            
            -- Export/Backup
            exported BOOLEAN DEFAULT 0,
            export_date TIMESTAMP,
            backup_id TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (user_id) REFERENCES employees(id),
            FOREIGN KEY (reviewed_by) REFERENCES employees(id)
        )
        """)
        
        # Settings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Setting Identification
            setting_key TEXT UNIQUE NOT NULL,
            setting_group TEXT NOT NULL DEFAULT 'general',
            setting_category TEXT,
            
            -- Value
            setting_value TEXT,
            setting_type TEXT DEFAULT 'string' CHECK(setting_type IN ('string', 'integer', 'decimal', 'boolean', 'json', 'array', 'object')),
            data_type TEXT,
            
            -- Options & Validation
            allowed_values TEXT,  -- JSON array
            min_value TEXT,
            max_value TEXT,
            regex_pattern TEXT,
            validation_message TEXT,
            
            -- Display
            display_name TEXT NOT NULL,
            description TEXT,
            help_text TEXT,
            display_order INTEGER DEFAULT 0,
            is_visible BOOLEAN DEFAULT 1,
            is_editable BOOLEAN DEFAULT 1,
            
            -- Scope & Access
            scope TEXT DEFAULT 'global' CHECK(scope IN ('global', 'store', 'user', 'role', 'terminal')),
            scope_id INTEGER,  -- Store ID, User ID, etc.
            access_level INTEGER DEFAULT 1,
            requires_restart BOOLEAN DEFAULT 0,
            
            -- Versioning
            version TEXT,
            deprecated BOOLEAN DEFAULT 0,
            deprecated_since_version TEXT,
            replacement_setting_key TEXT,
            
            -- Audit
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}'
        )
        """)
        
        # Printers configuration
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS printers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            printer_type TEXT DEFAULT 'receipt' CHECK(printer_type IN ('receipt', 'invoice', 'label', 'report', 'kitchen')),
            
            -- Connection
            connection_type TEXT DEFAULT 'usb' CHECK(connection_type IN ('usb', 'network', 'bluetooth', 'serial', 'parallel')),
            connection_string TEXT,
            ip_address TEXT,
            port INTEGER,
            mac_address TEXT,
            
            -- Configuration
            paper_width_mm INTEGER DEFAULT 80,
            charset TEXT DEFAULT 'CP437',
            line_width_chars INTEGER DEFAULT 42,
            print_density INTEGER DEFAULT 10,
            print_speed INTEGER,
            
            -- Commands
            init_commands TEXT,
            cut_command TEXT,
            open_cash_drawer_command TEXT,
            
            -- Status
            is_default BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            last_used TIMESTAMP,
            last_status_check TIMESTAMP,
            status TEXT CHECK(status IN ('online', 'offline', 'error', 'paper_out', 'cover_open')),
            
            -- Location
            location TEXT,
            terminal_id TEXT,
            
            -- Audit
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            meta_data TEXT DEFAULT '{}'
        )
        """)
        
        # Backup and sync logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS backup_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_type TEXT NOT NULL CHECK(backup_type IN ('full', 'incremental', 'differential', 'sync', 'export')),
            
            -- Timing
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration_seconds INTEGER,
            
            -- Files
            backup_file_path TEXT,
            backup_size_bytes INTEGER,
            compression_ratio DECIMAL(5,2),
            
            -- Content
            tables_included TEXT DEFAULT '[]',  -- JSON array
            record_counts TEXT DEFAULT '{}',  -- JSON: {"table": count}
            
            -- Destination
            destination_type TEXT CHECK(destination_type IN ('local', 'cloud', 'external', 'network')),
            destination_path TEXT,
            cloud_provider TEXT,
            bucket_name TEXT,
            
            -- Status
            status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'completed', 'failed', 'partial', 'cancelled')),
            success_count INTEGER,
            failure_count INTEGER,
            error_messages TEXT,
            
            -- Verification
            verified BOOLEAN DEFAULT 0,
            verification_method TEXT,
            verification_timestamp TIMESTAMP,
            
            -- Encryption
            encrypted BOOLEAN DEFAULT 0,
            encryption_method TEXT,
            
            -- Retention
            retention_days INTEGER DEFAULT 30,
            scheduled_for_deletion DATE,
            
            -- Initiated By
            initiated_by INTEGER,
            initiated_by_system BOOLEAN DEFAULT 0,
            schedule_name TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta_data TEXT DEFAULT '{}',
            
            FOREIGN KEY (initiated_by) REFERENCES employees(id)
        )
        """)
    
    def _insert_default_admin(self, cursor):
        """Insert default admin user."""
        
        # Check if admin already exists
        cursor.execute("SELECT COUNT(*) FROM employees WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # Hash the default password
            default_password = "admin123"
            hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
            
            cursor.execute("""
            INSERT INTO employees (
                username, passcode_hash, role, first_name, last_name, email,
                phone, is_active, hire_date, basic_salary, permissions_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'admin',
                hashed_password,
                'admin',
                'System',
                'Administrator',
                'admin@twinxpos.com',
                '0000000000',
                1,
                datetime.now().date(),
                0.00,
                json.dumps({'full_access': True})
            ))
    
    def _insert_default_settings(self, cursor):
        """Insert default system settings."""
        
        default_settings = [
            # System Settings
            ('system_name', 'Twinx POS System', 'system', 'General'),
            ('system_version', '1.0.0', 'system', 'General'),
            ('company_name', 'Twinx Enterprises', 'company', 'General'),
            ('company_address', '123 Business Street, City, Country', 'company', 'General'),
            ('company_phone', '+1234567890', 'company', 'General'),
            ('company_email', 'info@twinxpos.com', 'company', 'General'),
            ('company_tax_id', 'TAX-123456', 'company', 'General'),
            
            # Currency & Locale
            ('base_currency', 'USD', 'currency', 'Financial'),
            ('default_currency', 'USD', 'currency', 'Financial'),
            ('currency_symbol', '$', 'currency', 'Financial'),
            ('decimal_places', '2', 'formatting', 'General'),
            ('date_format', 'YYYY-MM-DD', 'formatting', 'General'),
            ('time_format', '24h', 'formatting', 'General'),
            ('timezone', 'UTC', 'system', 'General'),
            
            # Tax Settings
            ('default_tax_rate', '15.00', 'tax', 'Financial'),
            ('tax_calculation_method', 'per_item', 'tax', 'Financial'),
            ('tax_inclusive_pricing', '0', 'tax', 'Financial'),
            
            # POS Settings
            ('pos_receipt_header', 'Twinx POS\\nThank You For Your Business!', 'pos', 'Sales'),
            ('pos_receipt_footer', 'Returns within 7 days with receipt\\nVisit us online: www.twinxpos.com', 'pos', 'Sales'),
            ('pos_print_receipt_auto', '1', 'pos', 'Sales'),
            ('pos_print_invoice_auto', '0', 'pos', 'Sales'),
            ('pos_require_customer_for_sale', '0', 'pos', 'Sales'),
            ('pos_default_payment_method', 'cash', 'pos', 'Sales'),
            ('pos_cash_rounding', '0', 'pos', 'Sales'),
            ('pos_rounding_nearest', '0.05', 'pos', 'Sales'),
            
            # Inventory Settings
            ('inventory_tracking', '1', 'inventory', 'Inventory'),
            ('inventory_valuation_method', 'fifo', 'inventory', 'Inventory'),
            ('low_stock_threshold', '5', 'inventory', 'Inventory'),
            ('expiry_alert_days', '30', 'inventory', 'Inventory'),
            ('allow_negative_stock', '0', 'inventory', 'Inventory'),
            
            # Customer Settings
            ('customer_credit_limit_default', '1000.00', 'customer', 'Sales'),
            ('customer_default_payment_terms', 'COD', 'customer', 'Sales'),
            ('loyalty_points_per_currency', '1', 'customer', 'Loyalty'),
            ('loyalty_points_redeem_ratio', '100', 'customer', 'Loyalty'),
            
            # Backup Settings
            ('backup_auto_enabled', '1', 'backup', 'System'),
            ('backup_auto_frequency', 'daily', 'backup', 'System'),
            ('backup_auto_time', '02:00', 'backup', 'System'),
            ('backup_retention_days', '30', 'backup', 'System'),
            ('backup_location', './backups', 'backup', 'System'),
            
            # Security Settings
            ('password_expiry_days', '90', 'security', 'System'),
            ('max_login_attempts', '5', 'security', 'System'),
            ('session_timeout_minutes', '30', 'security', 'System'),
            ('require_strong_password', '1', 'security', 'System'),
            ('two_factor_auth', '0', 'security', 'System'),
            
            # Email Settings
            ('smtp_server', 'smtp.gmail.com', 'email', 'System'),
            ('smtp_port', '587', 'email', 'System'),
            ('smtp_use_tls', '1', 'email', 'System'),
            ('email_from', 'noreply@twinxpos.com', 'email', 'System'),
            
            # Integration Settings
            ('web_sync_enabled', '0', 'integration', 'System'),
            ('web_sync_url', '', 'integration', 'System'),
            ('web_sync_api_key', '', 'integration', 'System'),
            ('web_sync_frequency', 'hourly', 'integration', 'System'),
        ]
        
        for key, value, group, category in default_settings:
            cursor.execute("""
            INSERT OR IGNORE INTO settings (setting_key, setting_value, setting_group, setting_category, display_name)
            VALUES (?, ?, ?, ?, ?)
            """, (key, value, group, category, key.replace('_', ' ').title()))
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query and return results as dictionaries.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries representing rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update/insert query and return affected row count.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database.
        
        Args:
            backup_path: Path to save the backup
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False


# Initialize database when module is imported
if __name__ == "__main__":
    # Create database manager instance
    db_manager = DatabaseManager()
    print("Twinx POS Database initialized successfully!")
    
    # Test connection
    test_result = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
    print(f"Created {len(test_result)} tables")
    
    # Show table names
    table_names = [row['name'] for row in test_result]
    print("Tables created:", ", ".join(sorted(table_names)))