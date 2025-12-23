"""
Twinx POS System - Translation Manager
File: translations.py

This module handles Arabic/English localization for Twinx POS system.
Contains only application-specific business terms.
"""

class TranslationManager:
    """Manages translations for Twinx POS system in English and Arabic."""
    
    # Application-specific translation dictionary
    TRANSLATIONS = {
        'en': {
            # 1. General Actions
            'save': 'Save',
            'cancel': 'Cancel',
            'delete': 'Delete',
            'edit': 'Edit',
            'update': 'Update',
            'search': 'Search',
            'clear': 'Clear',
            'back': 'Back',
            'next': 'Next',
            'print': 'Print',
            'export_to_excel': 'Export to Excel',
            'import': 'Import',
            'confirm': 'Confirm',
            'close': 'Close',
            
            # 2. Authentication
            'login': 'Login',
            'username': 'Username',
            'password': 'Password',
            'forgot_password': 'Forgot Password?',
            'welcome': 'Welcome',
            'login_failed': 'Login Failed',
            'logout': 'Logout',
            'dark_mode': 'Dark Mode',
            'light_mode': 'Light Mode',
            'language': 'Language',
            
            # 3. Sidebar Menu
            'dashboard': 'Dashboard',
            'point_of_sale': 'Point of Sale',
            'inventory': 'Inventory',
            'products': 'Products',
            'customers': 'Customers',
            'suppliers': 'Suppliers (Wholesale)',
            'hr_payroll': 'HR & Payroll',
            'expenses': 'Expenses',
            'reports': 'Reports',
            'settings': 'Settings',
            'audit_log': 'Audit Log',
            'delivery': 'Delivery',
            
            # 4. POS Screen
            'invoice_no': 'Invoice No',
            'customer': 'Customer',
            'scan_barcode': 'Scan Barcode',
            'search_product': 'Search Product',
            'price': 'Price',
            'qty': 'Qty',
            'total': 'Total',
            'subtotal': 'Subtotal',
            'tax': 'Tax',
            'discount': 'Discount',
            'grand_total': 'Grand Total',
            'pay_now': 'Pay Now',
            'payment_method': 'Payment Method',
            'cash': 'Cash',
            'visa': 'Visa',
            'credit': 'Credit',
            'change_due': 'Change Due',
            'hold_sale': 'Hold Sale',
            'retrieve_sale': 'Retrieve Sale',
            
            # 5. Products & Inventory
            'product_name': 'Product Name',
            'sku': 'SKU',
            'barcode': 'Barcode',
            'cost_price': 'Cost Price',
            'selling_price': 'Selling Price',
            'stock_quantity': 'Stock Quantity',
            'low_stock_alert': 'Low Stock Alert',
            'category': 'Category',
            'brand': 'Brand',
            'attributes': 'Attributes',
            'variations': 'Variations',
            'color': 'Color',
            'size': 'Size',
            'expiry_date': 'Expiry Date',
            'batch_number': 'Batch Number',
            'warehouse': 'Warehouse',
            
            # 6. HR & Employees
            'employee_name': 'Employee Name',
            'role': 'Role',
            'phone': 'Phone',
            'basic_salary': 'Basic Salary',
            'net_salary': 'Net Salary',
            'overtime': 'Overtime',
            'deductions': 'Deductions',
            'bonus': 'Bonus',
            'check_in': 'Check-In',
            'check_out': 'Check-Out',
            'attendance_status': 'Attendance Status',
            'present': 'Present',
            'absent': 'Absent',
            'late': 'Late',
            
            # 7. Wholesale & Accounts
            'supplier_name': 'Supplier Name',
            'balance_due': 'Balance (Due)',
            'credit_limit': 'Credit Limit',
            'pay_supplier': 'Pay Supplier',
            'receive_payment': 'Receive Payment',
            'transaction_date': 'Transaction Date',
            'debit': 'Debit',
            'credit': 'Credit',
        },
        
        'ar': {
            # 1. General Actions
            'save': 'حفظ',
            'cancel': 'إلغاء',
            'delete': 'حذف',
            'edit': 'تعديل',
            'update': 'تحديث',
            'search': 'بحث',
            'clear': 'مسح',
            'back': 'رجوع',
            'next': 'التالي',
            'print': 'طباعة',
            'export_to_excel': 'تصدير إلى إكسل',
            'import': 'استيراد',
            'confirm': 'تأكيد',
            'close': 'إغلاق',
            
            # 2. Authentication
            'login': 'تسجيل الدخول',
            'username': 'اسم المستخدم',
            'password': 'كلمة المرور',
            'forgot_password': 'نسيت كلمة المرور؟',
            'welcome': 'مرحبا',
            'login_failed': 'فشل تسجيل الدخول',
            'logout': 'تسجيل الخروج',
            'dark_mode': 'الوضع الداكن',
            'light_mode': 'الوضع الفاتح',
            'language': 'اللغة',
            
            # 3. Sidebar Menu
            'dashboard': 'لوحة التحكم',
            'point_of_sale': 'نقطة البيع',
            'inventory': 'المخزون',
            'products': 'المنتجات',
            'customers': 'العملاء',
            'suppliers': 'الموردون (الجملة)',
            'hr_payroll': 'الموارد البشرية والرواتب',
            'expenses': 'المصروفات',
            'reports': 'التقارير',
            'settings': 'الإعدادات',
            'audit_log': 'سجل المراجعة',
            'delivery': 'التوصيل',
            
            # 4. POS Screen
            'invoice_no': 'رقم الفاتورة',
            'customer': 'العميل',
            'scan_barcode': 'مسح الباركود',
            'search_product': 'بحث عن منتج',
            'price': 'السعر',
            'qty': 'الكمية',
            'total': 'الإجمالي',
            'subtotal': 'المجموع الفرعي',
            'tax': 'الضريبة',
            'discount': 'الخصم',
            'grand_total': 'المجموع الكلي',
            'pay_now': 'ادفع الآن',
            'payment_method': 'طريقة الدفع',
            'cash': 'نقداً',
            'visa': 'فيزا',
            'credit': 'ائتمان',
            'change_due': 'الباقي',
            'hold_sale': 'تعليق البيع',
            'retrieve_sale': 'استرجاع بيع معلق',
            
            # 5. Products & Inventory
            'product_name': 'اسم المنتج',
            'sku': 'كود المنتج',
            'barcode': 'الباركود',
            'cost_price': 'سعر التكلفة',
            'selling_price': 'سعر البيع',
            'stock_quantity': 'كمية المخزون',
            'low_stock_alert': 'تنبيه نفاد المخزون',
            'category': 'الفئة',
            'brand': 'العلامة التجارية',
            'attributes': 'الخصائص',
            'variations': 'المتغيرات',
            'color': 'اللون',
            'size': 'المقاس',
            'expiry_date': 'تاريخ الصلاحية',
            'batch_number': 'رقم الدفعة',
            'warehouse': 'المستودع',
            
            # 6. HR & Employees
            'employee_name': 'اسم الموظف',
            'role': 'الدور',
            'phone': 'الهاتف',
            'basic_salary': 'الراتب الأساسي',
            'net_salary': 'صافي الراتب',
            'overtime': 'العمل الإضافي',
            'deductions': 'الخصومات',
            'bonus': 'المكافأة',
            'check_in': 'تسجيل الحضور',
            'check_out': 'تسجيل المغادرة',
            'attendance_status': 'حالة الحضور',
            'present': 'حاضر',
            'absent': 'غائب',
            'late': 'متأخر',
            
            # 7. Wholesale & Accounts
            'supplier_name': 'اسم المورد',
            'balance_due': 'الرصيد (المستحق)',
            'credit_limit': 'حد الائتمان',
            'pay_supplier': 'دفع للمورد',
            'receive_payment': 'استلام دفعة',
            'transaction_date': 'تاريخ المعاملة',
            'debit': 'مدين',
            'credit': 'دائن',
        }
    }
    
    def __init__(self, default_language: str = 'ar'):
        """
        Initialize Translation Manager.
        
        Args:
            default_language: Default language code ('en' or 'ar')
        """
        self.current_language = default_language if default_language in self.TRANSLATIONS else 'ar'
    
    def get(self, key: str) -> str:
        """
        Get translated text for the given key.
        
        Args:
            key: Translation key
            
        Returns:
            Translated text or formatted key if not found
        """
        try:
            return self.TRANSLATIONS[self.current_language][key]
        except KeyError:
            # If key not found, return the key formatted nicely
            return key.replace('_', ' ').title()
    
    def set_language(self, lang_code: str) -> bool:
        """
        Set the current language.
        
        Args:
            lang_code: Language code ('en' or 'ar')
            
        Returns:
            True if language was set successfully, False otherwise
        """
        if lang_code in self.TRANSLATIONS:
            self.current_language = lang_code
            return True
        return False
    
    def toggle_language(self) -> str:
        """
        Toggle between English and Arabic.
        
        Returns:
            New language code
        """
        if self.current_language == 'en':
            self.current_language = 'ar'
        else:
            self.current_language = 'en'
        return self.current_language
    
    def get_current_lang(self) -> str:
        """
        Get current language code.
        
        Returns:
            Current language code ('en' or 'ar')
        """
        return self.current_language
    
    def get_available_languages(self) -> list:
        """
        Get list of available language codes.
        
        Returns:
            List of available language codes
        """
        return list(self.TRANSLATIONS.keys())
    
    def get_all_translations(self, key: str) -> dict:
        """
        Get translations for a key in all available languages.
        
        Args:
            key: Translation key
            
        Returns:
            Dictionary with language codes as keys and translations as values
        """
        result = {}
        for lang_code, translations in self.TRANSLATIONS.items():
            result[lang_code] = translations.get(key, '')
        return result


# Singleton instance for easy access
_translation_manager = TranslationManager()

def get_translator() -> TranslationManager:
    """
    Get the singleton translation manager instance.
    
    Returns:
        TranslationManager instance
    """
    return _translation_manager


if __name__ == "__main__":
    # Test the translation manager
    translator = TranslationManager()
    
    print(f"Current language: {translator.get_current_lang()}")
    print(f"Login in current language: {translator.get('login')}")
    print(f"Save in current language: {translator.get('save')}")
    
    # Switch to English
    translator.set_language('en')
    print(f"\nSwitched to English")
    print(f"Login: {translator.get('login')}")
    print(f"Save: {translator.get('save')}")
    
    # Toggle back to Arabic
    translator.toggle_language()
    print(f"\nToggled to Arabic")
    print(f"Login: {translator.get('login')}")
    print(f"Save: {translator.get('save')}")
    
    # Test non-existent key
    print(f"\nNon-existent key: {translator.get('nonexistent_key')}")