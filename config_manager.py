"""
Twinx POS System - Configuration Manager
File: config_manager.py

This module manages application configuration by bridging the settings table
in the database with the app's runtime behavior.
"""

import json
from functools import lru_cache
from typing import Any, Optional, Dict
from database import DatabaseManager


class ConfigManager:
    """Manages application configuration settings from the database."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize Configuration Manager.
        
        Args:
            db_manager: Instance of DatabaseManager
        """
        self.db = db_manager
        self._cache = {}
    
    @lru_cache(maxsize=128)
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value from the database.
        Uses LRU cache for performance.
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value (parsed according to type) or default
        """
        try:
            # Check memory cache first
            if key in self._cache:
                return self._cache[key]
            
            # Query database
            query = "SELECT setting_value, setting_type FROM settings WHERE setting_key = ?"
            result = self.db.execute_query(query, (key,))
            
            if not result:
                return default
            
            setting = result[0]
            value = setting['setting_value']
            setting_type = setting.get('setting_type', 'string')
            
            # Parse value based on type
            if value is None:
                parsed_value = default
            elif setting_type == 'json':
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    parsed_value = value
            elif setting_type == 'integer':
                try:
                    parsed_value = int(value)
                except (ValueError, TypeError):
                    parsed_value = default
            elif setting_type == 'decimal':
                try:
                    parsed_value = float(value)
                except (ValueError, TypeError):
                    parsed_value = default
            elif setting_type == 'boolean':
                parsed_value = str(value).lower() in ('true', '1', 'yes', 'on')
            elif setting_type == 'array':
                try:
                    parsed_value = json.loads(value)
                    if not isinstance(parsed_value, list):
                        parsed_value = [parsed_value]
                except json.JSONDecodeError:
                    parsed_value = [value] if value else []
            else:  # string or other types
                parsed_value = str(value)
            
            # Store in memory cache
            self._cache[key] = parsed_value
            
            return parsed_value
            
        except Exception as e:
            # Log error but don't crash
            print(f"Error getting setting '{key}': {e}")
            return default
    
    def set_setting(self, key: str, value: Any, setting_type: str = None) -> bool:
        """
        Set a setting value in the database.
        
        Args:
            key: Setting key
            value: Setting value
            setting_type: Optional type hint (string, integer, decimal, boolean, json, array)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine setting type if not provided
            if setting_type is None:
                if isinstance(value, bool):
                    setting_type = 'boolean'
                    str_value = 'true' if value else 'false'
                elif isinstance(value, int):
                    setting_type = 'integer'
                    str_value = str(value)
                elif isinstance(value, float):
                    setting_type = 'decimal'
                    str_value = str(value)
                elif isinstance(value, (list, dict)):
                    setting_type = 'json'
                    str_value = json.dumps(value, ensure_ascii=False)
                else:
                    setting_type = 'string'
                    str_value = str(value)
            else:
                # Convert value based on type
                if setting_type == 'boolean':
                    str_value = 'true' if bool(value) else 'false'
                elif setting_type == 'json':
                    str_value = json.dumps(value, ensure_ascii=False) if value else '{}'
                elif setting_type == 'array':
                    if isinstance(value, list):
                        str_value = json.dumps(value, ensure_ascii=False)
                    else:
                        str_value = json.dumps([value], ensure_ascii=False)
                else:
                    str_value = str(value)
            
            # Check if setting exists
            check_query = "SELECT id FROM settings WHERE setting_key = ?"
            exists = self.db.execute_query(check_query, (key,))
            
            if exists:
                # Update existing setting
                update_query = """
                UPDATE settings 
                SET setting_value = ?, setting_type = ?, updated_at = CURRENT_TIMESTAMP
                WHERE setting_key = ?
                """
                self.db.execute_update(update_query, (str_value, setting_type, key))
            else:
                # Insert new setting
                insert_query = """
                INSERT INTO settings 
                (setting_key, setting_value, setting_type, setting_group, display_name, created_at, updated_at)
                VALUES (?, ?, ?, 'general', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
                display_name = key.replace('_', ' ').title()
                self.db.execute_update(insert_query, (key, str_value, setting_type, display_name))
            
            # Clear cache for this key
            self._clear_key_from_cache(key)
            
            return True
            
        except Exception as e:
            print(f"Error setting setting '{key}': {e}")
            return False
    
    def get_theme(self) -> str:
        """
        Get the current theme setting.
        
        Returns:
            'dark' or 'light' (defaults to 'dark')
        """
        theme = self.get_setting('theme', 'dark')
        return theme if theme in ['dark', 'light'] else 'dark'
    
    def set_theme(self, theme: str) -> bool:
        """
        Set the theme setting.
        
        Args:
            theme: 'dark' or 'light'
            
        Returns:
            True if successful, False otherwise
        """
        if theme not in ['dark', 'light']:
            return False
        
        return self.set_setting('theme', theme)
    
    def get_language(self) -> str:
        """
        Get the current language setting.
        
        Returns:
            'ar' or 'en' (defaults to 'ar')
        """
        language = self.get_setting('language', 'ar')
        return language if language in ['ar', 'en'] else 'ar'
    
    def set_language(self, language: str) -> bool:
        """
        Set the language setting.
        
        Args:
            language: 'ar' or 'en'
            
        Returns:
            True if successful, False otherwise
        """
        if language not in ['ar', 'en']:
            return False
        
        return self.set_setting('language', language)
    
    def get_currency(self) -> str:
        """
        Get the current currency setting.
        
        Returns:
            Currency code (defaults to 'USD')
        """
        return self.get_setting('currency', 'USD')
    
    def set_currency(self, currency: str) -> bool:
        """
        Set the currency setting.
        
        Args:
            currency: Currency code (e.g., 'USD', 'EUR', 'SAR')
            
        Returns:
            True if successful, False otherwise
        """
        return self.set_setting('currency', currency)
    
    def get_date_format(self) -> str:
        """
        Get the date format setting.
        
        Returns:
            Date format string (defaults to 'YYYY-MM-DD')
        """
        return self.get_setting('date_format', 'YYYY-MM-DD')
    
    def get_time_format(self) -> str:
        """
        Get the time format setting.
        
        Returns:
            Time format string (defaults to '24h')
        """
        return self.get_setting('time_format', '24h')
    
    def get_decimal_places(self) -> int:
        """
        Get the number of decimal places for currency.
        
        Returns:
            Number of decimal places (defaults to 2)
        """
        return self.get_setting('decimal_places', 2)
    
    def get_tax_rate(self) -> float:
        """
        Get the default tax rate.
        
        Returns:
            Tax rate percentage (defaults to 15.0)
        """
        return self.get_setting('tax_rate', 15.0)
    
    def get_company_info(self) -> Dict[str, Any]:
        """
        Get company information.
        
        Returns:
            Dictionary with company details
        """
        return {
            'name': self.get_setting('company_name', 'Twinx POS'),
            'address': self.get_setting('company_address', ''),
            'phone': self.get_setting('company_phone', ''),
            'email': self.get_setting('company_email', ''),
            'tax_id': self.get_setting('company_tax_id', '')
        }
    
    def get_printer_config(self) -> Dict[str, Any]:
        """
        Get printer configuration.
        
        Returns:
            Dictionary with printer settings
        """
        return {
            'auto_print_receipt': self.get_setting('pos_print_receipt_auto', True),
            'printer_name': self.get_setting('printer_name', ''),
            'paper_width': self.get_setting('paper_width', 80),
            'receipt_header': self.get_setting('pos_receipt_header', 'Twinx POS\nThank You For Your Business!'),
            'receipt_footer': self.get_setting('pos_receipt_footer', 'Returns within 7 days with receipt\nVisit us online: www.twinxpos.com')
        }
    
    def get_inventory_settings(self) -> Dict[str, Any]:
        """
        Get inventory management settings.
        
        Returns:
            Dictionary with inventory settings
        """
        return {
            'low_stock_threshold': self.get_setting('low_stock_threshold', 5),
            'expiry_alert_days': self.get_setting('expiry_alert_days', 30),
            'allow_negative_stock': self.get_setting('allow_negative_stock', False),
            'inventory_valuation_method': self.get_setting('inventory_valuation_method', 'fifo')
        }
    
    def get_customer_settings(self) -> Dict[str, Any]:
        """
        Get customer-related settings.
        
        Returns:
            Dictionary with customer settings
        """
        return {
            'default_credit_limit': self.get_setting('customer_credit_limit_default', 1000.00),
            'default_payment_terms': self.get_setting('customer_default_payment_terms', 'COD'),
            'loyalty_points_per_currency': self.get_setting('loyalty_points_per_currency', 1.0)
        }
    
    def get_backup_settings(self) -> Dict[str, Any]:
        """
        Get backup settings.
        
        Returns:
            Dictionary with backup settings
        """
        return {
            'auto_enabled': self.get_setting('backup_auto_enabled', True),
            'auto_frequency': self.get_setting('backup_auto_frequency', 'daily'),
            'auto_time': self.get_setting('backup_auto_time', '02:00'),
            'retention_days': self.get_setting('backup_retention_days', 30),
            'location': self.get_setting('backup_location', './backups')
        }
    
    def get_security_settings(self) -> Dict[str, Any]:
        """
        Get security settings.
        
        Returns:
            Dictionary with security settings
        """
        return {
            'password_expiry_days': self.get_setting('password_expiry_days', 90),
            'max_login_attempts': self.get_setting('max_login_attempts', 5),
            'session_timeout_minutes': self.get_setting('session_timeout_minutes', 30),
            'require_strong_password': self.get_setting('require_strong_password', True),
            'two_factor_auth': self.get_setting('two_factor_auth', False)
        }
    
    def get_all_settings(self, group: str = None) -> Dict[str, Any]:
        """
        Get all settings or settings for a specific group.
        
        Args:
            group: Optional setting group to filter by
            
        Returns:
            Dictionary of all settings
        """
        try:
            if group:
                query = "SELECT setting_key, setting_value, setting_type FROM settings WHERE setting_group = ?"
                results = self.db.execute_query(query, (group,))
            else:
                query = "SELECT setting_key, setting_value, setting_type FROM settings"
                results = self.db.execute_query(query)
            
            settings = {}
            for row in results:
                key = row['setting_key']
                value = row['setting_value']
                setting_type = row.get('setting_type', 'string')
                
                # Parse value based on type
                if setting_type == 'json':
                    try:
                        settings[key] = json.loads(value) if value else {}
                    except json.JSONDecodeError:
                        settings[key] = value
                elif setting_type == 'integer':
                    try:
                        settings[key] = int(value)
                    except (ValueError, TypeError):
                        settings[key] = value
                elif setting_type == 'decimal':
                    try:
                        settings[key] = float(value)
                    except (ValueError, TypeError):
                        settings[key] = value
                elif setting_type == 'boolean':
                    settings[key] = str(value).lower() in ('true', '1', 'yes', 'on')
                elif setting_type == 'array':
                    try:
                        settings[key] = json.loads(value) if value else []
                    except json.JSONDecodeError:
                        settings[key] = [value] if value else []
                else:
                    settings[key] = str(value)
            
            return settings
            
        except Exception as e:
            print(f"Error getting all settings: {e}")
            return {}
    
    def _clear_key_from_cache(self, key: str) -> None:
        """Clear a specific key from all caches."""
        # Clear from memory cache
        if key in self._cache:
            del self._cache[key]
        
        # Clear from lru_cache by calling get_setting.cache_clear()
        # Note: This clears ALL cached items, not just the specific key
        # For more granular cache clearing, we'd need a different approach
        self.get_setting.cache_clear()
    
    def clear_cache(self) -> None:
        """Clear all configuration caches."""
        self._cache.clear()
        self.get_setting.cache_clear()
    
    def refresh_settings(self) -> None:
        """Refresh settings from database (alias for clear_cache)."""
        self.clear_cache()
    
    def save_bulk_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """
        Save multiple settings at once.
        
        Args:
            settings_dict: Dictionary of key-value pairs to save
            
        Returns:
            True if all settings saved successfully, False otherwise
        """
        try:
            success = True
            for key, value in settings_dict.items():
                if not self.set_setting(key, value):
                    success = False
            
            return success
            
        except Exception as e:
            print(f"Error saving bulk settings: {e}")
            return False


# Singleton instance for easy access
_config_manager = None

def get_config_manager(db_manager: DatabaseManager = None) -> ConfigManager:
    """
    Get the singleton configuration manager instance.
    
    Args:
        db_manager: DatabaseManager instance (required on first call)
        
    Returns:
        ConfigManager instance
        
    Raises:
        ValueError: If db_manager is not provided on first call
    """
    global _config_manager
    
    if _config_manager is None:
        if db_manager is None:
            raise ValueError("DatabaseManager must be provided on first call")
        _config_manager = ConfigManager(db_manager)
    
    return _config_manager


if __name__ == "__main__":
    # Test the configuration manager
    from database import DatabaseManager
    
    db = DatabaseManager("twinx_pos.db")
    config = ConfigManager(db)
    
    print("Testing ConfigManager...")
    
    # Test getting and setting settings
    print(f"Current theme: {config.get_theme()}")
    print(f"Current language: {config.get_language()}")
    
    # Test setting a new value
    config.set_theme('light')
    config.set_language('en')
    
    print(f"\nAfter changing:")
    print(f"Current theme: {config.get_theme()}")
    print(f"Current language: {config.get_language()}")
    
    # Test getting with default
    test_value = config.get_setting('non_existent_key', 'default_value')
    print(f"\nNon-existent key with default: {test_value}")
    
    # Test company info
    company_info = config.get_company_info()
    print(f"\nCompany name: {company_info['name']}")
    
    # Test clearing cache
    config.clear_cache()
    print("\nCache cleared successfully")
    
    # Test getting all settings
    all_settings = config.get_all_settings()
    print(f"\nTotal settings in database: {len(all_settings)}")