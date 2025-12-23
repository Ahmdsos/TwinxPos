"""
Twinx POS System - Sales & Financial Controller
Senior Python Developer
File: sales_controller.py

This module handles POS transactions, inventory updates, and financial ledger entries.
"""

import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from database import DatabaseManager
from product_controller import ProductController


class SalesController:
    """Handles sales transactions, inventory updates, and financial accounting."""
    
    def __init__(self, db_manager: DatabaseManager, product_controller: ProductController):
        """
        Initialize SalesController with database and product controller.
        
        Args:
            db_manager: Instance of DatabaseManager
            product_controller: Instance of ProductController
        """
        self.db = db_manager
        self.product_ctrl = product_ctrl
    
    def process_sale(self, cart_items: List[Dict[str, Any]], 
                    customer_id: Optional[int], 
                    payment_details: Dict[str, Any],
                    user_id: int,
                    terminal_id: str = None,
                    shift_id: int = None) -> Dict[str, Any]:
        """
        Process a complete sale transaction with inventory and accounting updates.
        
        Args:
            cart_items: List of cart items with product/variation details
            customer_id: Customer ID (optional)
            payment_details: Payment method and details
            user_id: Cashier/User ID
            terminal_id: Terminal/Device ID
            shift_id: Shift ID
            
        Returns:
            Dictionary with sale results including invoice number
        """
        try:
            # Start transaction
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Validate cart items and check stock
                validation_result = self._validate_cart_items(cursor, cart_items)
                if not validation_result['success']:
                    return {
                        'success': False,
                        'message': validation_result['message'],
                        'invoice_no': None,
                        'sale_id': None
                    }
                
                # 2. Generate invoice number
                invoice_no = self._generate_invoice_number(cursor)
                
                # 3. Calculate totals
                calculation_result = self._calculate_totals(cart_items)
                if not calculation_result['success']:
                    return {
                        'success': False,
                        'message': calculation_result['message'],
                        'invoice_no': None,
                        'sale_id': None
                    }
                
                totals = calculation_result['totals']
                
                # 4. Get customer details if provided
                customer_details = {}
                if customer_id:
                    customer_details = self._get_customer_details(cursor, customer_id)
                
                # 5. Get cashier details
                cashier_details = self._get_user_details(cursor, user_id)
                if not cashier_details:
                    return {
                        'success': False,
                        'message': 'Cashier not found or inactive',
                        'invoice_no': None,
                        'sale_id': None
                    }
                
                # 6. Insert sales header
                sale_id = self._insert_sale_header(
                    cursor, invoice_no, totals, customer_id, 
                    customer_details, cashier_details, payment_details,
                    user_id, terminal_id, shift_id
                )
                
                # 7. Insert sale items and update stock
                sale_items_result = self._process_sale_items(
                    cursor, sale_id, cart_items, user_id, totals
                )
                
                if not sale_items_result['success']:
                    # Rollback will happen automatically when exception is raised
                    raise Exception(sale_items_result['message'])
                
                # 8. Process accounting entries
                accounting_result = self._process_accounting_entries(
                    cursor, sale_id, totals, payment_details, user_id
                )
                
                if not accounting_result['success']:
                    raise Exception(accounting_result['message'])
                
                # 9. Update customer loyalty points if applicable
                if customer_id:
                    loyalty_result = self._update_customer_loyalty(
                        cursor, customer_id, totals['grand_total']
                    )
                    if not loyalty_result['success']:
                        # Log warning but don't fail the transaction
                        self._log_audit_event(
                            user_id=user_id,
                            action='loyalty_update',
                            module='sales',
                            details=f'Loyalty update warning: {loyalty_result["message"]}',
                            status='warning'
                        )
                
                # 10. Update cash register session if shift_id provided
                if shift_id:
                    self._update_cash_register(cursor, shift_id, totals['grand_total'])
                
                # Commit transaction
                conn.commit()
                
                # 11. Log successful sale
                self._log_audit_event(
                    user_id=user_id,
                    action='process_sale',
                    module='sales',
                    details=f'Sale {invoice_no} processed successfully. Total: {totals["grand_total"]:.2f}',
                    status='success'
                )
                
                # 12. Generate receipt data
                receipt_data = self._generate_receipt_data(
                    sale_id, invoice_no, totals, cart_items, 
                    customer_details, cashier_details, payment_details
                )
                
                return {
                    'success': True,
                    'message': 'Sale processed successfully',
                    'invoice_no': invoice_no,
                    'sale_id': sale_id,
                    'totals': totals,
                    'receipt_data': receipt_data,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            # Transaction will be rolled back automatically
            self._log_audit_event(
                user_id=user_id,
                action='process_sale',
                module='sales',
                details=f'Sale processing failed: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Sale processing failed: {str(e)}',
                'invoice_no': None,
                'sale_id': None
            }
    
    def _validate_cart_items(self, cursor, cart_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate cart items and check stock availability."""
        try:
            for item in cart_items:
                # Check required fields
                required_fields = ['product_id', 'quantity']
                for field in required_fields:
                    if field not in item:
                        return {
                            'success': False,
                            'message': f'Missing required field: {field}'
                        }
                
                product_id = item['product_id']
                variation_id = item.get('product_variation_id')
                quantity = Decimal(str(item['quantity']))
                
                # Check stock availability
                if variation_id:
                    query = """
                    SELECT stock_quantity, name, sku, allow_backorders
                    FROM product_variations 
                    WHERE id = ? AND product_id = ? AND is_active = 1
                    """
                    params = (variation_id, product_id)
                else:
                    query = """
                    SELECT stock_quantity, name, sku, allow_backorders
                    FROM products 
                    WHERE id = ? AND is_active = 1
                    """
                    params = (product_id,)
                
                cursor.execute(query, params)
                product = cursor.fetchone()
                
                if not product:
                    return {
                        'success': False,
                        'message': f'Product/Variation not found or inactive: ID {product_id}/{variation_id}'
                    }
                
                # Check stock if product manages stock
                if product['stock_quantity'] is not None:
                    current_stock = Decimal(str(product['stock_quantity']))
                    if current_stock < quantity and not product['allow_backorders']:
                        return {
                            'success': False,
                            'message': f'Insufficient stock for {product["name"]}. Available: {current_stock}, Requested: {quantity}'
                        }
            
            return {'success': True, 'message': 'All items validated successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Validation error: {str(e)}'}
    
    def _generate_invoice_number(self, cursor) -> str:
        """Generate unique invoice number."""
        try:
            # Get current date prefix
            date_prefix = datetime.now().strftime('%Y%m%d')
            
            # Get today's invoice count
            query = """
            SELECT COUNT(*) as count 
            FROM sales 
            WHERE invoice_no LIKE ? AND DATE(invoice_date) = DATE('now')
            """
            
            cursor.execute(query, (f'{date_prefix}%',))
            result = cursor.fetchone()
            today_count = result['count'] if result else 0
            
            # Generate invoice number
            sequence = today_count + 1
            invoice_no = f"{date_prefix}-{sequence:04d}"
            
            return invoice_no
            
        except Exception as e:
            # Fallback to timestamp-based invoice
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            return f"INV-{timestamp}"
    
    def _calculate_totals(self, cart_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate subtotal, tax, discount, and grand total."""
        try:
            subtotal = Decimal('0.00')
            total_tax = Decimal('0.00')
            total_discount = Decimal('0.00')
            items_with_details = []
            
            for item in cart_items:
                quantity = Decimal(str(item['quantity']))
                unit_price = Decimal(str(item.get('unit_price', '0.00')))
                
                # Calculate item subtotal
                item_subtotal = quantity * unit_price
                
                # Apply item discount if any
                item_discount_percent = Decimal(str(item.get('discount_percent', '0.00')))
                item_discount_amount = Decimal(str(item.get('discount_amount', '0.00')))
                
                if item_discount_percent > 0:
                    item_discount_amount = item_subtotal * (item_discount_percent / Decimal('100.00'))
                elif item_discount_amount == 0:
                    item_discount_amount = Decimal('0.00')
                
                # Calculate item total after discount
                item_total_after_discount = item_subtotal - item_discount_amount
                
                # Calculate item tax
                tax_percent = Decimal(str(item.get('tax_percent', '0.00')))
                item_tax = item_total_after_discount * (tax_percent / Decimal('100.00'))
                
                # Update totals
                subtotal += item_subtotal
                total_discount += item_discount_amount
                total_tax += item_tax
                
                # Store calculated values for the item
                item_details = {
                    'product_id': item['product_id'],
                    'product_variation_id': item.get('product_variation_id'),
                    'quantity': float(quantity),
                    'unit_price': float(unit_price),
                    'subtotal': float(item_subtotal),
                    'discount_amount': float(item_discount_amount),
                    'discount_percent': float(item_discount_percent),
                    'tax_amount': float(item_tax),
                    'tax_percent': float(tax_percent),
                    'total': float(item_total_after_discount + item_tax)
                }
                items_with_details.append(item_details)
            
            # Apply global discount if any (from cart level)
            global_discount = Decimal('0.00')
            if 'global_discount_percent' in cart_items[0] if cart_items else False:
                global_discount_percent = Decimal(str(cart_items[0].get('global_discount_percent', '0.00')))
                global_discount = subtotal * (global_discount_percent / Decimal('100.00'))
                total_discount += global_discount
            
            # Calculate grand total
            grand_total = subtotal - total_discount + total_tax
            
            # Round to 2 decimal places
            subtotal = subtotal.quantize(Decimal('0.01'))
            total_discount = total_discount.quantize(Decimal('0.01'))
            total_tax = total_tax.quantize(Decimal('0.01'))
            grand_total = grand_total.quantize(Decimal('0.01'))
            
            return {
                'success': True,
                'message': 'Totals calculated successfully',
                'totals': {
                    'subtotal': float(subtotal),
                    'discount_amount': float(total_discount),
                    'tax_amount': float(total_tax),
                    'grand_total': float(grand_total),
                    'item_count': len(cart_items),
                    'global_discount': float(global_discount),
                    'items': items_with_details
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Calculation error: {str(e)}'}
    
    def _get_customer_details(self, cursor, customer_id: int) -> Dict[str, Any]:
        """Get customer details by ID."""
        try:
            query = """
            SELECT id, customer_code, first_name, last_name, company_name,
                   phone, email, tax_id, credit_limit, current_balance,
                   loyalty_card_number, loyalty_points_balance,
                   customer_type, payment_terms, discount_percent
            FROM customers 
            WHERE id = ? AND is_active = 1
            """
            
            cursor.execute(query, (customer_id,))
            customer = cursor.fetchone()
            
            return dict(customer) if customer else {}
            
        except Exception as e:
            return {}
    
    def _get_user_details(self, cursor, user_id: int) -> Dict[str, Any]:
        """Get user/cashier details by ID."""
        try:
            query = """
            SELECT id, username, first_name, last_name, employee_id, job_title
            FROM employees 
            WHERE id = ? AND is_active = 1
            """
            
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            
            return dict(user) if user else {}
            
        except Exception as e:
            return {}
    
    def _insert_sale_header(self, cursor, invoice_no: str, totals: Dict[str, Any],
                           customer_id: Optional[int], customer_details: Dict[str, Any],
                           cashier_details: Dict[str, Any], payment_details: Dict[str, Any],
                           user_id: int, terminal_id: str, shift_id: int) -> int:
        """Insert sales header record."""
        try:
            query = """
            INSERT INTO sales (
                invoice_no, invoice_date, invoice_status,
                customer_id, customer_name, customer_phone, customer_email,
                cashier_id, cashier_name,
                subtotal, discount_amount, discount_percent,
                tax_amount, total, amount_paid, change_amount,
                payment_method, payment_status,
                currency, terminal_id, shift_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Calculate discount percentage
            discount_percent = 0.0
            if totals['subtotal'] > 0:
                discount_percent = (totals['discount_amount'] / totals['subtotal']) * 100
            
            # Get payment details
            payment_method = payment_details.get('method', 'cash')
            amount_paid = payment_details.get('amount_paid', totals['grand_total'])
            change_amount = max(0, amount_paid - totals['grand_total'])
            
            # Execute insert
            cursor.execute(query, (
                invoice_no, datetime.now(), 'completed',
                customer_id,
                f"{customer_details.get('first_name', '')} {customer_details.get('last_name', '')}".strip() or 'Walk-in Customer',
                customer_details.get('phone'),
                customer_details.get('email'),
                user_id,
                f"{cashier_details.get('first_name', '')} {cashier_details.get('last_name', '')}",
                totals['subtotal'], totals['discount_amount'], discount_percent,
                totals['tax_amount'], totals['grand_total'],
                amount_paid, change_amount,
                payment_method, 'paid',
                'USD', terminal_id, shift_id,
                datetime.now(), datetime.now()
            ))
            
            return cursor.lastrowid
            
        except Exception as e:
            raise Exception(f'Error inserting sale header: {str(e)}')
    
    def _process_sale_items(self, cursor, sale_id: int, cart_items: List[Dict[str, Any]],
                           user_id: int, totals: Dict[str, Any]) -> Dict[str, Any]:
        """Insert sale items and update stock."""
        try:
            item_details = totals.get('items', [])
            
            for i, item in enumerate(cart_items):
                item_calc = item_details[i] if i < len(item_details) else {}
                
                # Get product details
                product_query = """
                SELECT p.name as product_name, p.sku as product_sku, 
                       p.barcode as product_barcode, p.cost_price,
                       pv.name as variation_name, pv.sku as variation_sku,
                       pv.barcode as variation_barcode
                FROM products p
                LEFT JOIN product_variations pv ON p.id = pv.product_id AND pv.id = ?
                WHERE p.id = ?
                """
                
                cursor.execute(product_query, (
                    item.get('product_variation_id'), item['product_id']
                ))
                product = cursor.fetchone()
                
                if not product:
                    raise Exception(f'Product not found: ID {item["product_id"]}')
                
                # Insert sale item
                item_query = """
                INSERT INTO sale_items (
                    sale_id, product_id, product_variation_id,
                    product_name, product_sku, product_barcode,
                    variation_description,
                    quantity, unit_price, subtotal,
                    discount_amount, discount_percent,
                    tax_amount, tax_percent, total,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(item_query, (
                    sale_id, item['product_id'], item.get('product_variation_id'),
                    product['product_name'],
                    product['variation_sku'] or product['product_sku'],
                    product['variation_barcode'] or product['product_barcode'],
                    product['variation_name'] or '',
                    item['quantity'], item_calc.get('unit_price', item.get('unit_price', 0)),
                    item_calc.get('subtotal', 0),
                    item_calc.get('discount_amount', 0),
                    item_calc.get('discount_percent', 0),
                    item_calc.get('tax_amount', 0),
                    item_calc.get('tax_percent', 0),
                    item_calc.get('total', 0),
                    datetime.now()
                ))
                
                item_id = cursor.lastrowid
                
                # Update stock using ProductController logic
                variation_id = item.get('product_variation_id')
                if variation_id:
                    # Update variation stock
                    stock_update = self.product_ctrl.update_stock(
                        variation_id=variation_id,
                        qty_change=-item['quantity'],  # Negative for sale
                        reason=f'sale_{sale_id}',
                        user_id=user_id,
                        reference_type='sale',
                        reference_id=sale_id,
                        notes=f'Sale item {item_id}'
                    )
                    
                    if not stock_update['success']:
                        raise Exception(f'Stock update failed: {stock_update["message"]}')
                
                # Log item processing
                self._log_audit_event(
                    user_id=user_id,
                    action='process_sale_item',
                    module='sales',
                    details=f'Processed item {item_id} for sale {sale_id}',
                    status='success'
                )
            
            return {'success': True, 'message': 'All items processed successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error processing items: {str(e)}'}
    
    def _process_accounting_entries(self, cursor, sale_id: int, 
                                   totals: Dict[str, Any], 
                                   payment_details: Dict[str, Any],
                                   user_id: int) -> Dict[str, Any]:
        """Create general ledger entries for the sale."""
        try:
            # Get accounting account codes from settings or defaults
            cash_account = self._get_account_code(cursor, 'cash_receivables')
            sales_account = self._get_account_code(cursor, 'sales_revenue')
            cogs_account = self._get_account_code(cursor, 'cost_of_goods_sold')
            inventory_account = self._get_account_code(cursor, 'inventory_asset')
            
            if not all([cash_account, sales_account, cogs_account, inventory_account]):
                raise Exception('Required accounting accounts not configured')
            
            # Calculate COGS (need to get cost prices for items)
            cogs_amount = self._calculate_cogs(cursor, sale_id)
            
            # Generate entry number
            entry_number = f"SL{sale_id:06d}"
            current_date = datetime.now().date()
            
            # 1. Debit Cash/Bank, Credit Sales Revenue
            self._create_ledger_entry(
                cursor, entry_number, current_date,
                f'Sale {sale_id} - Revenue',
                cash_account, totals['grand_total'], 0,  # Debit Cash
                sales_account, 0, totals['grand_total'],  # Credit Sales
                sale_id, 'sale', user_id
            )
            
            # 2. Debit COGS, Credit Inventory
            if cogs_amount > 0:
                self._create_ledger_entry(
                    cursor, f"{entry_number}-COGS", current_date,
                    f'Sale {sale_id} - COGS',
                    cogs_account, cogs_amount, 0,  # Debit COGS
                    inventory_account, 0, cogs_amount,  # Credit Inventory
                    sale_id, 'sale', user_id
                )
            
            return {'success': True, 'message': 'Accounting entries created'}
            
        except Exception as e:
            return {'success': False, 'message': f'Accounting error: {str(e)}'}
    
    def _get_account_code(self, cursor, account_type: str) -> str:
        """Get account code for accounting entries."""
        try:
            # First try to get from settings
            query = "SELECT setting_value FROM settings WHERE setting_key = ?"
            cursor.execute(query, (f'account_{account_type}',))
            result = cursor.fetchone()
            
            if result and result['setting_value']:
                return result['setting_value']
            
            # Default account codes (should be configured in settings)
            defaults = {
                'cash_receivables': '1010',
                'sales_revenue': '4010',
                'cost_of_goods_sold': '5010',
                'inventory_asset': '1210'
            }
            
            return defaults.get(account_type, '9999')
            
        except:
            return '9999'  # Default suspense account
    
    def _calculate_cogs(self, cursor, sale_id: int) -> float:
        """Calculate Cost of Goods Sold for the sale."""
        try:
            query = """
            SELECT si.quantity, p.cost_price, pv.cost_price as variation_cost
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            LEFT JOIN product_variations pv ON si.product_variation_id = pv.id
            WHERE si.sale_id = ?
            """
            
            cursor.execute(query, (sale_id,))
            items = cursor.fetchall()
            
            total_cogs = 0.0
            for item in items:
                quantity = item['quantity']
                cost_price = item['variation_cost'] or item['cost_price'] or 0
                total_cogs += quantity * cost_price
            
            return round(total_cogs, 2)
            
        except Exception as e:
            # If can't calculate COGS, return 0 (should be logged)
            self._log_audit_event(
                user_id=None,
                action='calculate_cogs',
                module='accounting',
                details=f'COGS calculation error for sale {sale_id}: {str(e)}',
                status='warning'
            )
            return 0.0
    
    def _create_ledger_entry(self, cursor, entry_number: str, entry_date: date,
                            description: str,
                            debit_account: str, debit_amount: float, credit_amount: float,
                            credit_account: str, contra_debit: float, contra_credit: float,
                            transaction_id: int, transaction_type: str, user_id: int) -> None:
        """Create a general ledger entry."""
        try:
            # Main entry (debit)
            query = """
            INSERT INTO general_ledger (
                entry_number, entry_date, posting_date, description,
                account_id, debit_amount, credit_amount,
                transaction_id, transaction_table, transaction_type,
                posted_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                entry_number, entry_date, entry_date, description,
                debit_account, debit_amount, credit_amount,
                transaction_id, 'sales', transaction_type,
                user_id, datetime.now()
            ))
            
            # Contra entry (credit)
            cursor.execute(query, (
                entry_number, entry_date, entry_date, description,
                credit_account, contra_debit, contra_credit,
                transaction_id, 'sales', transaction_type,
                user_id, datetime.now()
            ))
            
        except Exception as e:
            raise Exception(f'Ledger entry creation failed: {str(e)}')
    
    def _update_customer_loyalty(self, cursor, customer_id: int, 
                                sale_amount: float) -> Dict[str, Any]:
        """Update customer loyalty points."""
        try:
            # Get loyalty points per currency from settings
            query = "SELECT setting_value FROM settings WHERE setting_key = 'loyalty_points_per_currency'"
            cursor.execute(query)
            result = cursor.fetchone()
            
            points_per_currency = float(result['setting_value']) if result and result['setting_value'] else 1.0
            
            # Calculate earned points
            earned_points = int(sale_amount * points_per_currency)
            
            if earned_points > 0:
                # Update customer loyalty points
                update_query = """
                UPDATE customers 
                SET loyalty_points_balance = COALESCE(loyalty_points_balance, 0) + ?,
                    loyalty_points_total_earned = COALESCE(loyalty_points_total_earned, 0) + ?,
                    total_spent = COALESCE(total_spent, 0) + ?,
                    total_purchases = COALESCE(total_purchases, 0) + 1,
                    last_purchase_date = ?
                WHERE id = ?
                """
                
                cursor.execute(update_query, (
                    earned_points, earned_points, sale_amount,
                    datetime.now().date(), customer_id
                ))
                
                # Log loyalty update
                self._log_audit_event(
                    user_id=None,
                    action='update_loyalty',
                    module='sales',
                    details=f'Customer {customer_id} earned {earned_points} loyalty points',
                    status='success'
                )
            
            return {'success': True, 'message': f'Added {earned_points} loyalty points'}
            
        except Exception as e:
            return {'success': False, 'message': f'Loyalty update error: {str(e)}'}
    
    def _update_cash_register(self, cursor, shift_id: int, sale_amount: float) -> None:
        """Update cash register session totals."""
        try:
            query = """
            UPDATE cash_register_sessions 
            SET total_sales_count = total_sales_count + 1,
                total_sales_amount = total_sales_amount + ?,
                total_transactions_count = total_transactions_count + 1,
                total_transactions_amount = total_transactions_amount + ?,
                updated_at = ?
            WHERE id = ? AND status = 'open'
            """
            
            cursor.execute(query, (sale_amount, sale_amount, datetime.now(), shift_id))
            
        except Exception as e:
            # Log but don't fail transaction
            self._log_audit_event(
                user_id=None,
                action='update_cash_register',
                module='sales',
                details=f'Cash register update error: {str(e)}',
                status='warning'
            )
    
    def _generate_receipt_data(self, sale_id: int, invoice_no: str, 
                              totals: Dict[str, Any], cart_items: List[Dict[str, Any]],
                              customer_details: Dict[str, Any], 
                              cashier_details: Dict[str, Any],
                              payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate receipt data for printing/display."""
        try:
            # Get company details from settings
            company_query = """
            SELECT setting_key, setting_value 
            FROM settings 
            WHERE setting_key IN ('company_name', 'company_address', 'company_phone', 'company_email')
            """
            
            company_settings = self.db.execute_query(company_query)
            company_info = {s['setting_key']: s['setting_value'] for s in company_settings}
            
            # Get detailed sale items
            items_query = """
            SELECT product_name, variation_description, quantity, 
                   unit_price, discount_amount, tax_amount, total
            FROM sale_items 
            WHERE sale_id = ?
            ORDER BY id
            """
            
            items_result = self.db.execute_query(items_query, (sale_id,))
            receipt_items = [dict(item) for item in items_result]
            
            receipt_data = {
                'invoice_no': invoice_no,
                'sale_id': sale_id,
                'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'company': {
                    'name': company_info.get('company_name', 'Twinx POS'),
                    'address': company_info.get('company_address', ''),
                    'phone': company_info.get('company_phone', ''),
                    'email': company_info.get('company_email', '')
                },
                'customer': {
                    'name': f"{customer_details.get('first_name', '')} {customer_details.get('last_name', '')}".strip() or 'Walk-in Customer',
                    'phone': customer_details.get('phone'),
                    'email': customer_details.get('email')
                },
                'cashier': {
                    'name': f"{cashier_details.get('first_name', '')} {cashier_details.get('last_name', '')}",
                    'id': cashier_details.get('employee_id')
                },
                'items': receipt_items,
                'totals': {
                    'subtotal': totals['subtotal'],
                    'discount': totals['discount_amount'],
                    'tax': totals['tax_amount'],
                    'grand_total': totals['grand_total']
                },
                'payment': {
                    'method': payment_details.get('method', 'cash'),
                    'amount_paid': payment_details.get('amount_paid', totals['grand_total']),
                    'change': max(0, payment_details.get('amount_paid', totals['grand_total']) - totals['grand_total'])
                },
                'footer': {
                    'thank_you': 'Thank you for your business!',
                    'return_policy': 'Returns within 7 days with receipt',
                    'website': 'www.twinxpos.com'
                }
            }
            
            return receipt_data
            
        except Exception as e:
            # Return basic receipt data if detailed generation fails
            return {
                'invoice_no': invoice_no,
                'sale_id': sale_id,
                'date_time': datetime.now().isoformat(),
                'grand_total': totals['grand_total'],
                'items_count': len(cart_items)
            }
    
    def get_daily_sales(self, target_date: date = None) -> Dict[str, Any]:
        """
        Get total sales for a specific day.
        
        Args:
            target_date: Date to get sales for (default: today)
            
        Returns:
            Dictionary with daily sales summary
        """
        try:
            if not target_date:
                target_date = date.today()
            
            query = """
            SELECT 
                COUNT(*) as total_transactions,
                SUM(total) as total_sales,
                SUM(tax_amount) as total_tax,
                SUM(discount_amount) as total_discount,
                AVG(total) as average_sale,
                MIN(total) as min_sale,
                MAX(total) as max_sale,
                -- Payment method breakdown
                SUM(CASE WHEN payment_method = 'cash' THEN total ELSE 0 END) as cash_sales,
                SUM(CASE WHEN payment_method = 'card' THEN total ELSE 0 END) as card_sales,
                SUM(CASE WHEN payment_method = 'credit' THEN total ELSE 0 END) as credit_sales,
                -- Customer breakdown
                COUNT(DISTINCT customer_id) as unique_customers,
                SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as walkin_customers
            FROM sales 
            WHERE DATE(invoice_date) = ? 
            AND invoice_status = 'completed'
            """
            
            result = self.db.execute_query(query, (target_date,))
            
            if result:
                summary = dict(result[0])
                
                # Get top selling products
                products_query = """
                SELECT p.name, COUNT(si.id) as quantity_sold, SUM(si.total) as revenue
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN products p ON si.product_id = p.id
                WHERE DATE(s.invoice_date) = ? AND s.invoice_status = 'completed'
                GROUP BY p.id, p.name
                ORDER BY quantity_sold DESC
                LIMIT 10
                """
                
                top_products = self.db.execute_query(products_query, (target_date,))
                
                # Get hourly sales distribution
                hourly_query = """
                SELECT strftime('%H', invoice_date) as hour,
                       COUNT(*) as transactions,
                       SUM(total) as sales_amount
                FROM sales 
                WHERE DATE(invoice_date) = ? AND invoice_status = 'completed'
                GROUP BY strftime('%H', invoice_date)
                ORDER BY hour
                """
                
                hourly_sales = self.db.execute_query(hourly_query, (target_date,))
                
                return {
                    'success': True,
                    'message': f'Daily sales report for {target_date}',
                    'date': target_date.isoformat(),
                    'summary': summary,
                    'top_products': [dict(p) for p in top_products],
                    'hourly_sales': [dict(h) for h in hourly_sales],
                    'report_generated': datetime.now().isoformat()
                }
            else:
                return {
                    'success': True,
                    'message': f'No sales found for {target_date}',
                    'date': target_date.isoformat(),
                    'summary': {
                        'total_transactions': 0,
                        'total_sales': 0.00,
                        'total_tax': 0.00,
                        'total_discount': 0.00
                    },
                    'top_products': [],
                    'hourly_sales': []
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting daily sales: {str(e)}',
                'date': target_date.isoformat() if target_date else '',
                'summary': {},
                'top_products': [],
                'hourly_sales': []
            }
    
    def get_sale_details(self, sale_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific sale."""
        try:
            # Get sale header
            header_query = """
            SELECT s.*, 
                   c.first_name as customer_first_name,
                   c.last_name as customer_last_name,
                   c.phone as customer_phone,
                   e.first_name as cashier_first_name,
                   e.last_name as cashier_last_name
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            LEFT JOIN employees e ON s.cashier_id = e.id
            WHERE s.id = ?
            """
            
            header_result = self.db.execute_query(header_query, (sale_id,))
            
            if not header_result:
                return {
                    'success': False,
                    'message': 'Sale not found',
                    'sale': None,
                    'items': []
                }
            
            sale_header = dict(header_result[0])
            
            # Get sale items
            items_query = """
            SELECT si.*, p.name as product_name, p.sku as product_sku,
                   pv.name as variation_name, pv.sku as variation_sku
            FROM sale_items si
            LEFT JOIN products p ON si.product_id = p.id
            LEFT JOIN product_variations pv ON si.product_variation_id = pv.id
            WHERE si.sale_id = ?
            ORDER BY si.id
            """
            
            items_result = self.db.execute_query(items_query, (sale_id,))
            sale_items = [dict(item) for item in items_result]
            
            # Get related stock movements
            movements_query = """
            SELECT * FROM stock_movements 
            WHERE reference_type = 'sale' AND reference_id = ?
            ORDER BY movement_date
            """
            
            movements_result = self.db.execute_query(movements_query, (sale_id,))
            stock_movements = [dict(mov) for mov in movements_result]
            
            return {
                'success': True,
                'message': 'Sale details retrieved successfully',
                'sale': sale_header,
                'items': sale_items,
                'stock_movements': stock_movements
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting sale details: {str(e)}',
                'sale': None,
                'items': []
            }
    
    def process_refund(self, sale_id: int, refund_items: List[Dict[str, Any]],
                      user_id: int, reason: str = 'customer_return') -> Dict[str, Any]:
        """
        Process a refund/return transaction.
        
        Args:
            sale_id: Original sale ID
            refund_items: List of items to refund with quantities
            user_id: User processing the refund
            reason: Reason for refund
            
        Returns:
            Dictionary with refund results
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Get original sale details
                sale_query = "SELECT * FROM sales WHERE id = ?"
                cursor.execute(sale_query, (sale_id,))
                original_sale = cursor.fetchone()
                
                if not original_sale:
                    return {
                        'success': False,
                        'message': 'Original sale not found'
                    }
                
                original_sale = dict(original_sale)
                
                # 2. Validate refund items against original sale
                validation_result = self._validate_refund_items(cursor, sale_id, refund_items)
                if not validation_result['success']:
                    return validation_result
                
                # 3. Calculate refund totals
                calculation_result = self._calculate_refund_totals(cursor, sale_id, refund_items)
                if not calculation_result['success']:
                    return calculation_result
                
                refund_totals = calculation_result['totals']
                
                # 4. Generate refund invoice number
                refund_invoice = f"REF-{original_sale['invoice_no']}-{datetime.now().strftime('%H%M%S')}"
                
                # 5. Insert refund sale (negative sale)
                refund_sale_id = self._insert_refund_sale(
                    cursor, refund_invoice, original_sale, refund_totals, user_id, reason
                )
                
                # 6. Process refund items and restore stock
                refund_items_result = self._process_refund_items(
                    cursor, refund_sale_id, sale_id, refund_items, user_id, reason
                )
                
                if not refund_items_result['success']:
                    raise Exception(refund_items_result['message'])
                
                # 7. Update original sale status
                self._update_original_sale_status(cursor, sale_id, refund_totals['refund_amount'])
                
                # 8. Process refund accounting entries
                accounting_result = self._process_refund_accounting(
                    cursor, refund_sale_id, refund_totals, user_id
                )
                
                if not accounting_result['success']:
                    raise Exception(accounting_result['message'])
                
                conn.commit()
                
                # Log successful refund
                self._log_audit_event(
                    user_id=user_id,
                    action='process_refund',
                    module='sales',
                    details=f'Refund processed for sale {sale_id}. Amount: {refund_totals["refund_amount"]:.2f}',
                    status='success'
                )
                
                return {
                    'success': True,
                    'message': 'Refund processed successfully',
                    'refund_invoice': refund_invoice,
                    'refund_sale_id': refund_sale_id,
                    'original_sale_id': sale_id,
                    'refund_amount': refund_totals['refund_amount']
                }
                
        except Exception as e:
            self._log_audit_event(
                user_id=user_id,
                action='process_refund',
                module='sales',
                details=f'Refund processing failed for sale {sale_id}: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Refund processing failed: {str(e)}'
            }
    
    def _validate_refund_items(self, cursor, sale_id: int, 
                              refund_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate refund items against original sale."""
        try:
            # Get original sale items
            query = """
            SELECT product_id, product_variation_id, quantity as original_quantity,
                   COALESCE(return_quantity, 0) as already_returned
            FROM sale_items 
            WHERE sale_id = ?
            """
            
            cursor.execute(query, (sale_id,))
            original_items = {f"{row['product_id']}_{row['product_variation_id']}": row 
                            for row in cursor.fetchall()}
            
            for refund_item in refund_items:
                key = f"{refund_item['product_id']}_{refund_item.get('product_variation_id', 0)}"
                
                if key not in original_items:
                    return {
                        'success': False,
                        'message': f'Item not found in original sale: {key}'
                    }
                
                original_item = original_items[key]
                max_refundable = original_item['original_quantity'] - original_item['already_returned']
                
                if refund_item['quantity'] > max_refundable:
                    return {
                        'success': False,
                        'message': f'Cannot refund more than {max_refundable} units for item {key}'
                    }
            
            return {'success': True, 'message': 'Refund items validated'}
            
        except Exception as e:
            return {'success': False, 'message': f'Validation error: {str(e)}'}
    
    def _calculate_refund_totals(self, cursor, sale_id: int, 
                                refund_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate refund totals based on original prices."""
        try:
            refund_amount = 0.0
            
            for refund_item in refund_items:
                # Get original price from sale item
                query = """
                SELECT unit_price, discount_amount, tax_amount, total
                FROM sale_items 
                WHERE sale_id = ? AND product_id = ? 
                AND (product_variation_id = ? OR (product_variation_id IS NULL AND ? IS NULL))
                """
                
                cursor.execute(query, (
                    sale_id, refund_item['product_id'], 
                    refund_item.get('product_variation_id'),
                    refund_item.get('product_variation_id')
                ))
                
                original_item = cursor.fetchone()
                
                if original_item:
                    # Calculate proportional refund
                    original_total = original_item['total']
                    refund_proportion = refund_item['quantity'] / (
                        original_item['quantity'] if original_item['quantity'] > 0 else 1
                    )
                    
                    item_refund = original_total * refund_proportion
                    refund_amount += item_refund
            
            return {
                'success': True,
                'message': 'Refund totals calculated',
                'totals': {
                    'refund_amount': round(refund_amount, 2),
                    'item_count': len(refund_items)
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Calculation error: {str(e)}'}
    
    def _log_audit_event(self, user_id: Optional[int], action: str, module: str, 
                        details: str, status: str = 'success') -> None:
        """
        Log event to audit_logs table.
        
        Args:
            user_id: User ID (None for system events)
            action: Action performed
            module: Module where action occurred
            details: Detailed description
            status: Success/failure status
        """
        try:
            query = """
            INSERT INTO audit_logs 
            (user_id, action_type, module, details, status, action_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_update(query, (
                user_id, action, module, details, status, datetime.now()
            ))
        except Exception as e:
            print(f"Error logging audit event: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize database manager
    db = DatabaseManager("twinx_pos.db")
    
    # Create product controller first
    product_ctrl = ProductController(db)
    
    # Create sales controller
    sales_controller = SalesController(db, product_ctrl)
    
    print("Testing sales processing...")
    
    # Create test cart items
    cart_items = [
        {
            'product_id': 1,  # Assuming product ID 1 exists
            'quantity': 2,
            'unit_price': 19.99,
            'tax_percent': 15.0
        },
        {
            'product_id': 2,  # Assuming product ID 2 exists
            'product_variation_id': 1,  # Assuming variation exists
            'quantity': 1,
            'unit_price': 49.99,
            'tax_percent': 15.0,
            'discount_percent': 10.0  # 10% discount on this item
        }
    ]
    
    payment_details = {
        'method': 'cash',
        'amount_paid': 100.00
    }
    
    # Process sale
    sale_result = sales_controller.process_sale(
        cart_items=cart_items,
        customer_id=1,  # Assuming customer ID 1 exists
        payment_details=payment_details,
        user_id=1,  # Assuming user ID 1 exists
        terminal_id='POS-001',
        shift_id=1  # Assuming shift ID 1 exists
    )
    
    print(f"Sale result: {sale_result['success']}")
    if sale_result['success']:
        print(f"Invoice: {sale_result['invoice_no']}")
        print(f"Total: ${sale_result['totals']['grand_total']:.2f}")
        print(f"Change: ${sale_result['receipt_data']['payment']['change']:.2f}")
    
    # Test daily sales report
    print("\nTesting daily sales report...")
    daily_report = sales_controller.get_daily_sales()
    print(f"Daily report success: {daily_report['success']}")
    if daily_report['success']:
        summary = daily_report['summary']
        print(f"Total transactions: {summary.get('total_transactions', 0)}")
        print(f"Total sales: ${summary.get('total_sales', 0):.2f}")
    
    # Test sale details
    if sale_result['success']:
        print(f"\nTesting sale details for ID {sale_result['sale_id']}...")
        sale_details = sales_controller.get_sale_details(sale_result['sale_id'])
        print(f"Sale details retrieved: {sale_details['success']}")
        if sale_details['success']:
            print(f"Items in sale: {len(sale_details['items'])}")
    
    print("\nAll tests completed!")