"""
Twinx POS System - Product & Inventory Controller
Senior Python Developer
File: product_controller.py

This module handles product management, variations, attributes, and stock movements.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from database import DatabaseManager


class ProductController:
    """Handles product management, variations, attributes, and stock control."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize ProductController with database connection.
        
        Args:
            db_manager: Instance of DatabaseManager
        """
        self.db = db_manager
    
    def create_product(self, product_data: Dict[str, Any], 
                      variations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new product with variations using transaction.
        
        Args:
            product_data: Dictionary containing product details
            variations: List of variation dictionaries (optional)
            
        Returns:
            Dictionary with success status and product ID
        """
        try:
            # Start transaction
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Validate required fields
                required_fields = ['name', 'type']
                for field in required_fields:
                    if field not in product_data:
                        return {
                            'success': False,
                            'message': f'Missing required field: {field}',
                            'product_id': None
                        }
                
                # Generate slug if not provided
                if 'slug' not in product_data:
                    product_data['slug'] = self._generate_slug(product_data['name'])
                
                # Generate SKU if not provided
                if 'sku' not in product_data and product_data.get('generate_sku', True):
                    product_data['sku'] = self._generate_sku(product_data['name'])
                
                # Insert main product
                product_columns = [
                    'name', 'slug', 'type', 'category', 'subcategory', 'brand',
                    'description', 'short_description', 'image_path', 'image_gallery',
                    'is_active', 'is_featured', 'is_taxable', 'manage_stock',
                    'stock_quantity', 'stock_status', 'allow_backorders',
                    'low_stock_threshold', 'price', 'cost_price', 'wholesale_price',
                    'suggested_retail_price', 'tax_class', 'tax_rate', 'sku',
                    'barcode', 'barcode_type', 'qr_code', 'upc', 'isbn', 'mpn',
                    'weight_kg', 'length_cm', 'width_cm', 'height_cm', 'volume_liters',
                    'dimensions_unit', 'manufacturer', 'manufacturer_country',
                    'country_of_origin', 'material_composition', 'product_code',
                    'warranty_period_months', 'warranty_type', 'warranty_terms',
                    'has_warranty', 'support_email', 'support_phone',
                    'commission_rate', 'margin_percentage', 'min_order_quantity',
                    'max_order_quantity', 'sale_price', 'sale_start_date',
                    'sale_end_date', 'tags', 'shelf_life_days', 'expiry_alert_days',
                    'batch_tracking_required', 'serial_tracking_required',
                    'supplier_id', 'supplier_sku', 'lead_time_days',
                    'reorder_point', 'reorder_quantity', 'shipping_class',
                    'shipping_weight', 'requires_shipping', 'is_virtual',
                    'is_downloadable', 'meta_title', 'meta_description',
                    'meta_keywords', 'canonical_url', 'created_by'
                ]
                
                # Prepare column names and values
                columns = []
                placeholders = []
                values = []
                
                for col in product_columns:
                    if col in product_data and product_data[col] is not None:
                        columns.append(col)
                        placeholders.append('?')
                        values.append(product_data[col])
                
                # Add created_at and updated_at
                columns.extend(['created_at', 'updated_at'])
                placeholders.extend(['?', '?'])
                current_time = datetime.now()
                values.extend([current_time, current_time])
                
                # Execute insert
                query = f"""
                INSERT INTO products ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                """
                
                cursor.execute(query, tuple(values))
                product_id = cursor.lastrowid
                
                # Handle variations if product type is 'variable'
                if product_data.get('type') == 'variable' and variations:
                    for variation in variations:
                        self._create_variation(cursor, product_id, variation)
                
                # Handle attributes if provided
                if 'attributes' in product_data:
                    self._link_product_attributes(cursor, product_id, product_data['attributes'])
                
                # Commit transaction
                conn.commit()
                
                # Log audit event
                self._log_audit_event(
                    user_id=product_data.get('created_by'),
                    action='create',
                    entity_type='products',
                    entity_id=product_id,
                    details=f'Created product {product_id}: {product_data["name"]}',
                    status='success'
                )
                
                return {
                    'success': True,
                    'message': 'Product created successfully',
                    'product_id': product_id
                }
                
        except Exception as e:
            # Log error
            self._log_audit_event(
                user_id=product_data.get('created_by'),
                action='create',
                entity_type='products',
                entity_id=None,
                details=f'Product creation error: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Error creating product: {str(e)}',
                'product_id': None
            }
    
    def _create_variation(self, cursor, product_id: int, variation_data: Dict[str, Any]) -> int:
        """
        Create a product variation.
        
        Args:
            cursor: Database cursor
            product_id: Parent product ID
            variation_data: Variation data
            
        Returns:
            Variation ID
        """
        # Generate variation SKU if not provided
        if 'sku' not in variation_data:
            variation_data['sku'] = f"{variation_data.get('parent_sku', 'VAR')}-{product_id}-{datetime.now().timestamp()}"
        
        variation_columns = [
            'product_id', 'name', 'sku', 'barcode', 'price', 'cost_price',
            'wholesale_price', 'sale_price', 'purchase_price', 'stock_quantity',
            'stock_status', 'manage_stock', 'low_stock_threshold', 'weight_kg',
            'length_cm', 'width_cm', 'height_cm', 'attribute_combination',
            'image_path', 'batch_number_required', 'serial_number_required',
            'expiry_date_required', 'supplier_sku', 'is_active',
            'is_default_variation'
        ]
        
        # Set product_id
        variation_data['product_id'] = product_id
        
        # Prepare column names and values
        columns = []
        placeholders = []
        values = []
        
        for col in variation_columns:
            if col in variation_data:
                columns.append(col)
                placeholders.append('?')
                values.append(variation_data[col])
        
        # Add created_at and updated_at
        columns.extend(['created_at', 'updated_at'])
        placeholders.extend(['?', '?'])
        current_time = datetime.now()
        values.extend([current_time, current_time])
        
        # Execute insert
        query = f"""
        INSERT INTO product_variations ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        cursor.execute(query, tuple(values))
        return cursor.lastrowid
    
    def _link_product_attributes(self, cursor, product_id: int, attributes_data: List[Dict[str, Any]]) -> None:
        """
        Link attributes to product.
        
        Args:
            cursor: Database cursor
            product_id: Product ID
            attributes_data: List of attribute data
        """
        for attr_data in attributes_data:
            # Check if attribute exists, create if not
            attribute_id = self._get_or_create_attribute(cursor, attr_data['attribute_name'])
            
            # Get or create attribute term
            term_id = self._get_or_create_attribute_term(cursor, attribute_id, attr_data['term_value'])
            
            # Link product to attribute term
            query = """
            INSERT INTO product_attribute_relations 
            (product_id, attribute_id, attribute_term_id, is_variation, sort_order)
            VALUES (?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                product_id, attribute_id, term_id,
                attr_data.get('is_variation', False),
                attr_data.get('sort_order', 0)
            ))
    
    def _get_or_create_attribute(self, cursor, attribute_name: str) -> int:
        """
        Get existing attribute or create new one.
        
        Args:
            cursor: Database cursor
            attribute_name: Attribute name
            
        Returns:
            Attribute ID
        """
        # Try to get existing attribute
        query = "SELECT id FROM attributes WHERE name = ?"
        cursor.execute(query, (attribute_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new attribute
        insert_query = """
        INSERT INTO attributes (name, display_name, is_variation, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """
        
        current_time = datetime.now()
        cursor.execute(insert_query, (
            attribute_name, attribute_name, False, current_time, current_time
        ))
        
        return cursor.lastrowid
    
    def _get_or_create_attribute_term(self, cursor, attribute_id: int, term_value: str) -> int:
        """
        Get existing attribute term or create new one.
        
        Args:
            cursor: Database cursor
            attribute_id: Attribute ID
            term_value: Term value
            
        Returns:
            Term ID
        """
        # Try to get existing term
        query = "SELECT id FROM attribute_terms WHERE attribute_id = ? AND term = ?"
        cursor.execute(query, (attribute_id, term_value))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new term
        slug = term_value.lower().replace(' ', '-')
        insert_query = """
        INSERT INTO attribute_terms (attribute_id, term, slug, created_at)
        VALUES (?, ?, ?, ?)
        """
        
        current_time = datetime.now()
        cursor.execute(insert_query, (
            attribute_id, term_value, slug, current_time
        ))
        
        return cursor.lastrowid
    
    def get_full_product(self, product_id: int) -> Dict[str, Any]:
        """
        Get complete product details with all variations.
        
        Args:
            product_id: Product ID
            
        Returns:
            Dictionary with product details and variations
        """
        try:
            # Get main product details
            product_query = """
            SELECT p.*, 
                   w.name as supplier_name,
                   c.name as category_name
            FROM products p
            LEFT JOIN wholesale_partners w ON p.supplier_id = w.id
            LEFT JOIN categories c ON p.category = c.id
            WHERE p.id = ? AND p.is_active = 1
            """
            
            product_result = self.db.execute_query(product_query, (product_id,))
            
            if not product_result:
                return {
                    'success': False,
                    'message': 'Product not found or inactive',
                    'product': None,
                    'variations': []
                }
            
            product = dict(product_result[0])
            
            # Parse JSON fields
            json_fields = ['image_gallery', 'tags', 'meta_data']
            for field in json_fields:
                if product.get(field):
                    try:
                        product[field] = json.loads(product[field])
                    except:
                        product[field] = []
            
            # Get product variations
            variations_query = """
            SELECT * FROM product_variations 
            WHERE product_id = ? AND is_active = 1
            ORDER BY is_default_variation DESC, id ASC
            """
            
            variations_result = self.db.execute_query(variations_query, (product_id,))
            variations = []
            
            for var in variations_result:
                variation = dict(var)
                
                # Parse attribute combination JSON
                if variation.get('attribute_combination'):
                    try:
                        variation['attribute_combination'] = json.loads(variation['attribute_combination'])
                    except:
                        variation['attribute_combination'] = {}
                
                variations.append(variation)
            
            # Get product attributes
            attributes_query = """
            SELECT a.name as attribute_name, a.display_name, a.is_variation,
                   at.term, at.color_code, at.image_path,
                   par.sort_order, par.is_visible
            FROM product_attribute_relations par
            JOIN attributes a ON par.attribute_id = a.id
            JOIN attribute_terms at ON par.attribute_term_id = at.id
            WHERE par.product_id = ?
            ORDER BY a.sort_order, at.sort_order
            """
            
            attributes_result = self.db.execute_query(attributes_query, (product_id,))
            attributes = [dict(attr) for attr in attributes_result]
            
            # Group attributes by name for easier display
            grouped_attributes = {}
            for attr in attributes:
                attr_name = attr['attribute_name']
                if attr_name not in grouped_attributes:
                    grouped_attributes[attr_name] = {
                        'display_name': attr['display_name'],
                        'is_variation': attr['is_variation'],
                        'terms': []
                    }
                grouped_attributes[attr_name]['terms'].append({
                    'term': attr['term'],
                    'color_code': attr['color_code'],
                    'image_path': attr['image_path'],
                    'sort_order': attr['sort_order']
                })
            
            # Get stock summary
            stock_query = """
            SELECT 
                SUM(stock_quantity) as total_stock,
                COUNT(*) as total_variations,
                SUM(CASE WHEN stock_quantity <= low_stock_threshold THEN 1 ELSE 0 END) as low_stock_count,
                MIN(stock_quantity) as min_stock,
                MAX(stock_quantity) as max_stock
            FROM product_variations 
            WHERE product_id = ? AND is_active = 1
            """
            
            stock_result = self.db.execute_query(stock_query, (product_id,))
            stock_summary = dict(stock_result[0]) if stock_result else {}
            
            # Get recent stock movements
            movements_query = """
            SELECT sm.*, e.first_name, e.last_name
            FROM stock_movements sm
            LEFT JOIN employees e ON sm.user_id = e.id
            WHERE sm.product_id = ?
            ORDER BY sm.movement_date DESC
            LIMIT 10
            """
            
            movements_result = self.db.execute_query(movements_query, (product_id,))
            recent_movements = [dict(mov) for mov in movements_result]
            
            return {
                'success': True,
                'message': 'Product retrieved successfully',
                'product': product,
                'variations': variations,
                'attributes': grouped_attributes,
                'stock_summary': stock_summary,
                'recent_movements': recent_movements
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving product: {str(e)}',
                'product': None,
                'variations': []
            }
    
    def update_stock(self, variation_id: int, qty_change: int, 
                    reason: str, user_id: int, 
                    reference_type: str = None, reference_id: int = None,
                    batch_number: str = None, notes: str = None) -> Dict[str, Any]:
        """
        Update stock quantity with audit trail.
        
        Args:
            variation_id: Product variation ID
            qty_change: Quantity change (positive for increase, negative for decrease)
            reason: Reason for stock change
            user_id: User ID making the change
            reference_type: Type of reference document (sale, purchase, etc.)
            reference_id: Reference document ID
            batch_number: Batch number for batch tracking
            notes: Additional notes
            
        Returns:
            Dictionary with success status
        """
        try:
            # Start transaction
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current variation details
                variation_query = """
                SELECT pv.*, p.name as product_name, p.sku as product_sku,
                       p.barcode as product_barcode, p.allow_negative_stock
                FROM product_variations pv
                JOIN products p ON pv.product_id = p.id
                WHERE pv.id = ?
                """
                
                cursor.execute(variation_query, (variation_id,))
                variation_result = cursor.fetchone()
                
                if not variation_result:
                    return {
                        'success': False,
                        'message': 'Product variation not found'
                    }
                
                variation = dict(variation_result)
                
                # Check if negative stock is allowed
                current_stock = variation['stock_quantity'] or 0
                new_stock = current_stock + qty_change
                
                if new_stock < 0 and not variation['allow_negative_stock']:
                    return {
                        'success': False,
                        'message': 'Negative stock not allowed',
                        'current_stock': current_stock,
                        'requested_change': qty_change
                    }
                
                # Determine movement type based on qty_change and reason
                if qty_change > 0:
                    movement_type = self._get_movement_type(reason, 'incoming')
                else:
                    movement_type = self._get_movement_type(reason, 'outgoing')
                
                # Insert stock movement record (audit trail)
                movement_query = """
                INSERT INTO stock_movements (
                    product_id, product_variation_id, product_name,
                    product_sku, product_barcode, movement_type,
                    quantity, balance_before, balance_after,
                    reference_type, reference_id, reason_description,
                    batch_number, user_id, notes, movement_date,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                movement_data = (
                    variation['product_id'], variation_id,
                    variation['product_name'], variation['product_sku'],
                    variation['product_barcode'], movement_type,
                    abs(qty_change), current_stock, new_stock,
                    reference_type, reference_id, reason,
                    batch_number, user_id, notes,
                    datetime.now(), datetime.now(), datetime.now()
                )
                
                cursor.execute(movement_query, movement_data)
                movement_id = cursor.lastrowid
                
                # Update variation stock quantity
                update_query = """
                UPDATE product_variations 
                SET stock_quantity = ?, updated_at = ?
                WHERE id = ?
                """
                
                cursor.execute(update_query, (new_stock, datetime.now(), variation_id))
                
                # Update parent product stock if it manages stock
                if variation.get('manage_stock', True):
                    # Calculate total stock for parent product
                    total_stock_query = """
                    SELECT SUM(stock_quantity) as total 
                    FROM product_variations 
                    WHERE product_id = ? AND is_active = 1
                    """
                    
                    cursor.execute(total_stock_query, (variation['product_id'],))
                    total_result = cursor.fetchone()
                    total_stock = total_result[0] or 0
                    
                    # Update product stock status
                    stock_status = 'instock' if total_stock > 0 else 'outofstock'
                    if total_stock <= variation.get('low_stock_threshold', 5):
                        stock_status = 'lowstock'
                    
                    product_update_query = """
                    UPDATE products 
                    SET stock_quantity = ?, stock_status = ?, updated_at = ?
                    WHERE id = ?
                    """
                    
                    cursor.execute(product_update_query, (
                        total_stock, stock_status, datetime.now(), variation['product_id']
                    ))
                
                # Commit transaction
                conn.commit()
                
                # Log audit event
                self._log_audit_event(
                    user_id=user_id,
                    action='update',
                    entity_type='stock_movements',
                    entity_id=movement_id,
                    details=f'Stock updated for variation {variation_id}: {qty_change} ({reason})',
                    status='success'
                )
                
                return {
                    'success': True,
                    'message': 'Stock updated successfully',
                    'movement_id': movement_id,
                    'variation_id': variation_id,
                    'old_quantity': current_stock,
                    'new_quantity': new_stock,
                    'change': qty_change
                }
                
        except Exception as e:
            # Log error
            self._log_audit_event(
                user_id=user_id,
                action='update',
                entity_type='stock_movements',
                entity_id=None,
                details=f'Stock update error for variation {variation_id}: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Error updating stock: {str(e)}'
            }
    
    def _get_movement_type(self, reason: str, direction: str) -> str:
        """
        Determine stock movement type based on reason and direction.
        
        Args:
            reason: Reason for stock change
            direction: 'incoming' or 'outgoing'
            
        Returns:
            Movement type string (must match database constraint)
        """
        reason_lower = reason.lower()
        
        if direction == 'incoming':
            if 'purchase' in reason_lower:
                return 'purchase'
            elif 'return' in reason_lower and 'customer' in reason_lower:
                return 'return_customer'
            elif 'found' in reason_lower:
                return 'found'
            elif 'transfer' in reason_lower:
                return 'transfer_in'
            elif 'production' in reason_lower:
                return 'production'
            else:
                return 'adjustment'  # Valid type
        else:  # outgoing
            if 'sale' in reason_lower:
                return 'sale'
            elif 'return' in reason_lower and 'supplier' in reason_lower:
                return 'return_supplier'
            elif 'damage' in reason_lower:
                return 'damage'
            elif 'expiry' in reason_lower:
                return 'expiry'
            elif 'lost' in reason_lower:
                return 'lost'
            elif 'transfer' in reason_lower:
                return 'transfer_out'
            elif 'write_off' in reason_lower:
                return 'write_off'
            else:
                return 'adjustment'  # Valid type
    
    def search_products(self, query: str = "", category_id: int = None, 
                       brand: str = None, in_stock_only: bool = False,
                       limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Search products by name, SKU, or barcode.
        
        Args:
            query: Search query string
            category_id: Filter by category ID (optional)
            brand: Filter by brand (optional)
            in_stock_only: Only show products in stock
            limit: Maximum results to return
            offset: Results offset for pagination
            
        Returns:
            Dictionary with search results
        """
        try:
            # Prepare search conditions
            conditions = ["p.is_active = 1"]
            params = []
            
            if query:
                # Search in name, SKU, barcode, description
                conditions.append("""
                (p.name LIKE ? OR p.sku LIKE ? OR p.barcode LIKE ? 
                 OR p.description LIKE ? OR pv.sku LIKE ? OR pv.barcode LIKE ?)
                """)
                search_term = f"%{query}%"
                params.extend([search_term] * 6)
            
            if category_id:
                conditions.append("p.category = ?")
                params.append(category_id)
            
            if brand:
                conditions.append("p.brand = ?")
                params.append(brand)
            
            if in_stock_only:
                conditions.append("""
                (p.stock_status = 'instock' OR 
                 (SELECT COUNT(*) FROM product_variations pv2 
                  WHERE pv2.product_id = p.id AND pv2.stock_quantity > 0) > 0)
                """)
            
            # Build query
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            search_query = f"""
            SELECT DISTINCT
                p.id, p.name, p.slug, p.type, p.category, p.brand,
                p.description, p.short_description, p.image_path,
                p.is_active, p.price, p.cost_price, p.sku, p.barcode,
                p.stock_quantity, p.stock_status, p.low_stock_threshold,
                p.weight_kg, p.length_cm, p.width_cm, p.height_cm,
                p.created_at, p.updated_at,
                -- Get lowest variation price
                MIN(pv.price) as min_variation_price,
                MAX(pv.price) as max_variation_price,
                -- Check if has variations
                CASE WHEN p.type = 'variable' THEN 1 ELSE 0 END as has_variations,
                -- Total stock across variations
                COALESCE(SUM(pv.stock_quantity), p.stock_quantity) as total_stock
            FROM products p
            LEFT JOIN product_variations pv ON p.id = pv.product_id AND pv.is_active = 1
            WHERE {where_clause}
            GROUP BY p.id
            ORDER BY 
                CASE WHEN p.name LIKE ? THEN 1 ELSE 2 END,
                p.name ASC
            LIMIT ? OFFSET ?
            """
            
            # Add ordering parameter and pagination
            if query:
                params.append(f"{query}%")
            else:
                params.append("")
            
            params.extend([limit, offset])
            
            # Execute search
            results = self.db.execute_query(search_query, tuple(params))
            products = []
            
            for row in results:
                product = dict(row)
                
                # Format price information
                if product['has_variations']:
                    if product['min_variation_price'] == product['max_variation_price']:
                        product['display_price'] = f"${product['min_variation_price']:.2f}"
                    else:
                        product['display_price'] = f"${product['min_variation_price']:.2f} - ${product['max_variation_price']:.2f}"
                else:
                    product['display_price'] = f"${product['price']:.2f}" if product['price'] else "N/A"
                
                # Get variation count
                variation_query = """
                SELECT COUNT(*) as variation_count 
                FROM product_variations 
                WHERE product_id = ? AND is_active = 1
                """
                variation_result = self.db.execute_query(variation_query, (product['id'],))
                product['variation_count'] = variation_result[0]['variation_count'] if variation_result else 0
                
                products.append(product)
            
            # Get total count for pagination
            count_query = f"""
            SELECT COUNT(DISTINCT p.id) as total_count
            FROM products p
            LEFT JOIN product_variations pv ON p.id = pv.product_id AND pv.is_active = 1
            WHERE {where_clause}
            """
            
            # Remove ordering and pagination from params for count query
            # Remove the last 3 params (search_prefix, limit, offset)
            count_params = params[:-3]
            count_result = self.db.execute_query(count_query, tuple(count_params))
            total_count = count_result[0]['total_count'] if count_result else 0
            
            return {
                'success': True,
                'message': f'Found {len(products)} products',
                'products': products,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error searching products: {str(e)}',
                'products': [],
                'total_count': 0
            }
    
    def bulk_update_stock(self, updates: List[Dict[str, Any]], 
                         user_id: int, reason: str = 'bulk_adjustment') -> Dict[str, Any]:
        """
        Update stock for multiple variations in a single transaction.
        
        Args:
            updates: List of dictionaries with variation_id and qty_change
            user_id: User ID making the changes
            reason: Reason for bulk update
            
        Returns:
            Dictionary with success status and results
        """
        try:
            results = []
            failed_updates = []
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for update in updates:
                    variation_id = update.get('variation_id')
                    qty_change = update.get('qty_change')
                    notes = update.get('notes')
                    
                    if not variation_id or qty_change is None:
                        failed_updates.append({
                            'variation_id': variation_id,
                            'error': 'Missing variation_id or qty_change'
                        })
                        continue
                    
                    try:
                        # Get current stock
                        stock_query = "SELECT stock_quantity FROM product_variations WHERE id = ?"
                        cursor.execute(stock_query, (variation_id,))
                        result = cursor.fetchone()
                        
                        if not result:
                            failed_updates.append({
                                'variation_id': variation_id,
                                'error': 'Variation not found'
                            })
                            continue
                        
                        current_stock = result[0] or 0
                        new_stock = current_stock + qty_change
                        
                        # Insert stock movement
                        movement_query = """
                        INSERT INTO stock_movements (
                            product_variation_id, movement_type, quantity,
                            balance_before, balance_after, reason_description,
                            user_id, notes, movement_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        
                        movement_type = 'adjustment'  # Valid type
                        
                        cursor.execute(movement_query, (
                            variation_id, movement_type, abs(qty_change),
                            current_stock, new_stock, reason,
                            user_id, notes, datetime.now()
                        ))
                        
                        # Update stock
                        update_query = "UPDATE product_variations SET stock_quantity = ? WHERE id = ?"
                        cursor.execute(update_query, (new_stock, variation_id))
                        
                        results.append({
                            'variation_id': variation_id,
                            'old_quantity': current_stock,
                            'new_quantity': new_stock,
                            'change': qty_change,
                            'success': True
                        })
                        
                    except Exception as e:
                        failed_updates.append({
                            'variation_id': variation_id,
                            'error': str(e)
                        })
                
                conn.commit()
            
            # Log audit event
            self._log_audit_event(
                user_id=user_id,
                action='update',
                entity_type='stock_movements',
                entity_id=None,
                details=f'Bulk stock update: {len(results)} successful, {len(failed_updates)} failed',
                status='success' if not failed_updates else 'partial'
            )
            
            return {
                'success': True,
                'message': f'Bulk update completed: {len(results)} successful, {len(failed_updates)} failed',
                'results': results,
                'failed_updates': failed_updates,
                'total_processed': len(updates)
            }
            
        except Exception as e:
            self._log_audit_event(
                user_id=user_id,
                action='update',
                entity_type='stock_movements',
                entity_id=None,
                details=f'Bulk stock update error: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Error in bulk update: {str(e)}',
                'results': [],
                'failed_updates': updates,
                'total_processed': 0
            }
    
    def get_low_stock_products(self, threshold: int = None) -> Dict[str, Any]:
        """
        Get products with low stock.
        
        Args:
            threshold: Low stock threshold (uses product's threshold if not provided)
            
        Returns:
            Dictionary with low stock products
        """
        try:
            query = """
            SELECT 
                p.id, p.name, p.sku, p.barcode, p.image_path,
                p.stock_quantity as product_stock,
                p.low_stock_threshold,
                -- Get variations with low stock
                (
                    SELECT GROUP_CONCAT(
                        pv.id || ':' || pv.sku || ':' || pv.stock_quantity
                    )
                    FROM product_variations pv
                    WHERE pv.product_id = p.id 
                    AND pv.is_active = 1
                    AND pv.stock_quantity <= COALESCE(?, pv.low_stock_threshold)
                ) as low_variations
            FROM products p
            WHERE p.is_active = 1
            AND (
                -- Product itself has low stock (for simple products)
                (p.type = 'simple' AND p.stock_quantity <= COALESCE(?, p.low_stock_threshold))
                OR
                -- Has variations with low stock
                EXISTS (
                    SELECT 1 FROM product_variations pv
                    WHERE pv.product_id = p.id 
                    AND pv.is_active = 1
                    AND pv.stock_quantity <= COALESCE(?, pv.low_stock_threshold)
                )
            )
            ORDER BY p.stock_quantity ASC, p.name ASC
            """
            
            results = self.db.execute_query(query, (threshold, threshold, threshold))
            low_stock_products = []
            
            for row in results:
                product = dict(row)
                
                # Parse variations string
                variations_info = []
                if product['low_variations']:
                    for var_str in product['low_variations'].split(','):
                        var_parts = var_str.split(':')
                        if len(var_parts) >= 3:
                            variations_info.append({
                                'variation_id': int(var_parts[0]),
                                'sku': var_parts[1],
                                'stock_quantity': int(var_parts[2])
                            })
                
                product['low_variations_list'] = variations_info
                low_stock_products.append(product)
            
            return {
                'success': True,
                'message': f'Found {len(low_stock_products)} products with low stock',
                'products': low_stock_products,
                'threshold_used': threshold
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting low stock products: {str(e)}',
                'products': []
            }
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL slug from product name."""
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = re.sub(r'^-+|-+$', '', slug)
        return slug
    
    def _generate_sku(self, name: str) -> str:
        """Generate SKU from product name."""
        import uuid
        # Get first 3 letters of each word
        words = name.split()
        prefix = ''.join([word[:3].upper() for word in words[:2]])[:6]
        # Add unique suffix
        suffix = str(uuid.uuid4().int)[:6]
        return f"{prefix}-{suffix}"
    
    def _log_audit_event(self, user_id: int, action: str, entity_type: str, 
                        entity_id: Optional[int], details: str, status: str = 'success') -> None:
        """
        Log event to audit_logs table.
        
        Args:
            user_id: User ID
            action: Action performed (must be: create, read, update, delete, login, logout, export, import, print, approve, reject)
            entity_type: Entity type (table name)
            entity_id: Entity ID
            details: Detailed description (will be stored in change_summary)
            status: Success/failure status
        """
        try:
            query = """
            INSERT INTO audit_logs 
            (user_id, action_type, module, entity_type, entity_id, change_summary, status, action_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Use entity_type for both module and entity_type for now
            self.db.execute_update(query, (
                user_id, action, entity_type, entity_type, entity_id, details, status, datetime.now()
            ))
        except Exception as e:
            print(f"Error logging audit event: {e}")
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing product.
        
        Args:
            product_id: Product ID to update
            product_data: Dictionary with updated product details
            
        Returns:
            Dictionary with success status
        """
        try:
            # Start transaction
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if product exists
                check_query = "SELECT id FROM products WHERE id = ?"
                cursor.execute(check_query, (product_id,))
                if not cursor.fetchone():
                    return {
                        'success': False,
                        'message': 'Product not found'
                    }
                
                # Build update query
                update_fields = []
                values = []
                
                # Allowed fields to update
                allowed_fields = [
                    'name', 'category', 'subcategory', 'brand', 'description',
                    'short_description', 'price', 'cost_price', 'wholesale_price',
                    'suggested_retail_price', 'tax_class', 'tax_rate', 'sku',
                    'barcode', 'weight_kg', 'length_cm', 'width_cm', 'height_cm',
                    'manufacturer', 'country_of_origin', 'warranty_period_months',
                    'has_warranty', 'support_email', 'support_phone',
                    'min_order_quantity', 'max_order_quantity', 'is_active',
                    'is_featured', 'stock_quantity', 'low_stock_threshold',
                    'updated_by'
                ]
                
                for field in allowed_fields:
                    if field in product_data:
                        update_fields.append(f"{field} = ?")
                        values.append(product_data[field])
                
                # Add updated_at timestamp
                update_fields.append("updated_at = ?")
                values.append(datetime.now())
                
                # Add product_id for WHERE clause
                values.append(product_id)
                
                # Execute update
                update_query = f"""
                UPDATE products 
                SET {', '.join(update_fields)}
                WHERE id = ?
                """
                
                cursor.execute(update_query, tuple(values))
                
                # Commit transaction
                conn.commit()
                
                # Log audit event
                self._log_audit_event(
                    user_id=product_data.get('updated_by'),
                    action='update',
                    entity_type='products',
                    entity_id=product_id,
                    details=f'Updated product {product_id}',
                    status='success'
                )
                
                return {
                    'success': True,
                    'message': 'Product updated successfully',
                    'product_id': product_id
                }
                
        except Exception as e:
            # Log error
            self._log_audit_event(
                user_id=product_data.get('updated_by'),
                action='update',
                entity_type='products',
                entity_id=product_id,
                details=f'Product update error: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Error updating product: {str(e)}'
            }
    
    def delete_product(self, product_id: int, user_id: int) -> Dict[str, Any]:
        """
        Soft delete a product (set is_active = 0).
        
        Args:
            product_id: Product ID to delete
            user_id: User ID performing deletion
            
        Returns:
            Dictionary with success status
        """
        try:
            # Start transaction
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if product exists
                check_query = "SELECT id, name FROM products WHERE id = ?"
                cursor.execute(check_query, (product_id,))
                result = cursor.fetchone()
                
                if not result:
                    return {
                        'success': False,
                        'message': 'Product not found'
                    }
                
                product_name = result['name']
                
                # Soft delete product
                delete_query = """
                UPDATE products 
                SET is_active = 0, updated_at = ?, updated_by = ?
                WHERE id = ?
                """
                
                cursor.execute(delete_query, (datetime.now(), user_id, product_id))
                
                # Also soft delete variations
                variations_query = """
                UPDATE product_variations 
                SET is_active = 0, updated_at = ?
                WHERE product_id = ?
                """
                
                cursor.execute(variations_query, (datetime.now(), product_id))
                
                # Commit transaction
                conn.commit()
                
                # Log audit event
                self._log_audit_event(
                    user_id=user_id,
                    action='delete',
                    entity_type='products',
                    entity_id=product_id,
                    details=f'Soft deleted product {product_id}: {product_name}',
                    status='success'
                )
                
                return {
                    'success': True,
                    'message': 'Product deleted successfully',
                    'product_id': product_id
                }
                
        except Exception as e:
            # Log error
            self._log_audit_event(
                user_id=user_id,
                action='delete',
                entity_type='products',
                entity_id=product_id,
                details=f'Product deletion error: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Error deleting product: {str(e)}'
            }
    
    def export_products_csv(self, file_path: str, product_ids: List[int] = None) -> Dict[str, Any]:
        """
        Export products to CSV file.
        
        Args:
            file_path: Path to save CSV file
            product_ids: List of product IDs to export (None = all active products)
            
        Returns:
            Dictionary with success status and export stats
        """
        try:
            import csv
            
            # Build query with optional product filter
            if product_ids:
                placeholders = ','.join(['?'] * len(product_ids))
                query = f"""
                SELECT 
                    p.id, p.name, p.sku, p.barcode, p.type, p.category,
                    p.brand, p.price, p.cost_price, p.stock_quantity,
                    p.stock_status, p.low_stock_threshold, p.weight_kg,
                    p.length_cm, p.width_cm, p.height_cm, p.manufacturer,
                    p.country_of_origin, p.created_at, p.updated_at,
                    COUNT(pv.id) as variation_count
                FROM products p
                LEFT JOIN product_variations pv ON p.id = pv.product_id AND pv.is_active = 1
                WHERE p.id IN ({placeholders}) AND p.is_active = 1
                GROUP BY p.id
                ORDER BY p.name
                """
                params = product_ids
            else:
                query = """
                SELECT 
                    p.id, p.name, p.sku, p.barcode, p.type, p.category,
                    p.brand, p.price, p.cost_price, p.stock_quantity,
                    p.stock_status, p.low_stock_threshold, p.weight_kg,
                    p.length_cm, p.width_cm, p.height_cm, p.manufacturer,
                    p.country_of_origin, p.created_at, p.updated_at,
                    COUNT(pv.id) as variation_count
                FROM products p
                LEFT JOIN product_variations pv ON p.id = pv.product_id AND pv.is_active = 1
                WHERE p.is_active = 1
                GROUP BY p.id
                ORDER BY p.name
                """
                params = []
            
            # Fetch data
            products = self.db.execute_query(query, tuple(params))
            
            if not products:
                return {
                    'success': False,
                    'message': 'No products found to export',
                    'exported_count': 0,
                    'file_path': None
                }
            
            # Define CSV columns
            fieldnames = [
                'ID', 'Name', 'SKU', 'Barcode', 'Type', 'Category',
                'Brand', 'Price', 'Cost Price', 'Stock Quantity',
                'Stock Status', 'Low Stock Threshold', 'Weight (kg)',
                'Length (cm)', 'Width (cm)', 'Height (cm)', 'Manufacturer',
                'Country of Origin', 'Created At', 'Updated At',
                'Variation Count'
            ]
            
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in products:
                    writer.writerow({
                        'ID': product['id'],
                        'Name': product['name'],
                        'SKU': product['sku'] or '',
                        'Barcode': product['barcode'] or '',
                        'Type': product['type'],
                        'Category': product['category'] or '',
                        'Brand': product['brand'] or '',
                        'Price': f"{product['price']:.2f}",
                        'Cost Price': f"{product['cost_price']:.2f}" if product['cost_price'] else '',
                        'Stock Quantity': product['stock_quantity'],
                        'Stock Status': product['stock_status'],
                        'Low Stock Threshold': product['low_stock_threshold'],
                        'Weight (kg)': f"{product['weight_kg']:.3f}" if product['weight_kg'] else '',
                        'Length (cm)': f"{product['length_cm']:.2f}" if product['length_cm'] else '',
                        'Width (cm)': f"{product['width_cm']:.2f}" if product['width_cm'] else '',
                        'Height (cm)': f"{product['height_cm']:.2f}" if product['height_cm'] else '',
                        'Manufacturer': product['manufacturer'] or '',
                        'Country of Origin': product['country_of_origin'] or '',
                        'Created At': product['created_at'],
                        'Updated At': product['updated_at'],
                        'Variation Count': product['variation_count']
                    })
            
            # Log audit event
            self._log_audit_event(
                user_id=1,  # System user ID
                action='export',
                entity_type='products',
                entity_id=None,
                details=f'Exported {len(products)} products to {file_path}',
                status='success'
            )
            
            return {
                'success': True,
                'message': f'Successfully exported {len(products)} products',
                'exported_count': len(products),
                'file_path': file_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error exporting products: {str(e)}',
                'exported_count': 0,
                'file_path': None
            }
    
    def get_product_variations(self, product_id: int) -> Dict[str, Any]:
        """
        Get all variations for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Dictionary with variations list
        """
        try:
            query = """
            SELECT 
                pv.id, pv.name, pv.sku, pv.barcode, pv.price,
                pv.cost_price, pv.wholesale_price, pv.sale_price,
                pv.stock_quantity, pv.stock_status, pv.low_stock_threshold,
                pv.weight_kg, pv.length_cm, pv.width_cm, pv.height_cm,
                pv.attribute_combination, pv.image_path,
                pv.is_active, pv.is_default_variation,
                pv.created_at, pv.updated_at
            FROM product_variations pv
            WHERE pv.product_id = ? AND pv.is_active = 1
            ORDER BY 
                pv.is_default_variation DESC,
                pv.created_at ASC
            """
            
            results = self.db.execute_query(query, (product_id,))
            variations = []
            
            for row in results:
                variation = dict(row)
                
                # Parse JSON fields
                if variation.get('attribute_combination'):
                    try:
                        variation['attribute_combination'] = json.loads(variation['attribute_combination'])
                    except:
                        variation['attribute_combination'] = {}
                
                variations.append(variation)
            
            # Get parent product info for context
            product_query = "SELECT name, sku FROM products WHERE id = ?"
            product_result = self.db.execute_query(product_query, (product_id,))
            product_info = dict(product_result[0]) if product_result else {}
            
            return {
                'success': True,
                'message': f'Found {len(variations)} variations',
                'product_id': product_id,
                'product_name': product_info.get('name', 'Unknown'),
                'product_sku': product_info.get('sku', ''),
                'variations': variations,
                'variation_count': len(variations)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving variations: {str(e)}',
                'product_id': product_id,
                'variations': [],
                'variation_count': 0
            }

# Example usage and testing
if __name__ == "__main__":
    # Initialize database manager
    db = DatabaseManager("twinx_pos.db")
    
    # Create controller
    product_controller = ProductController(db)
    
    # Test product creation
    print("Testing product creation...")
    product_data = {
        'name': 'Test T-Shirt',
        'type': 'variable',
        'category': 'Clothing',
        'brand': 'Test Brand',
        'price': 19.99,
        'cost_price': 10.00,
        'sku': 'TSHIRT-001',
        'barcode': '123456789012',
        'description': 'A test t-shirt',
        'created_by': 1
    }
    
    variations = [
        {
            'name': 'Red / Small',
            'sku': 'TSHIRT-001-RED-S',
            'price': 19.99,
            'stock_quantity': 50,
            'attribute_combination': '{"color": "Red", "size": "S"}'
        },
        {
            'name': 'Red / Medium',
            'sku': 'TSHIRT-001-RED-M',
            'price': 19.99,
            'stock_quantity': 30,
            'attribute_combination': '{"color": "Red", "size": "M"}'
        }
    ]
    
    creation_result = product_controller.create_product(product_data, variations)
    print(f"Creation result: {creation_result}")
    
    if creation_result['success']:
        product_id = creation_result['product_id']
        
        # Test get full product
        print(f"\nTesting get full product for ID {product_id}...")
        product_result = product_controller.get_full_product(product_id)
        print(f"Product retrieved: {product_result['success']}")
        if product_result['success']:
            print(f"Product name: {product_result['product']['name']}")
            print(f"Variations count: {len(product_result['variations'])}")
        
        # Test stock update
        print(f"\nTesting stock update...")
        if product_result['variations']:
            variation_id = product_result['variations'][0]['id']
            stock_result = product_controller.update_stock(
                variation_id=variation_id,
                qty_change=-5,
                reason='sale',
                user_id=1
            )
            print(f"Stock update: {stock_result}")
        
        # Test product search
        print(f"\nTesting product search...")
        search_result = product_controller.search_products('T-Shirt')
        print(f"Search found: {len(search_result['products'])} products")
    
    # Test low stock alert
    print(f"\nTesting low stock products...")
    low_stock_result = product_controller.get_low_stock_products(threshold=10)
    print(f"Low stock products: {len(low_stock_result['products'])}")
    
    print("\nAll tests completed!")