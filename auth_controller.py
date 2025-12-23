"""
Twinx POS System - Authentication & HR Controller
Senior Python Developer
File: auth_controller.py

This module handles user authentication, permissions, and HR operations.
"""

import hashlib
import json
from datetime import datetime, date
from typing import Dict, Optional, Any, Tuple
from database import DatabaseManager


class AuthController:
    """Handles user authentication and permission management."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize AuthController with database connection.
        
        Args:
            db_manager: Instance of DatabaseManager
        """
        self.db = db_manager
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using SHA256.
        
        Args:
            password: Plain text password
            
        Returns:
            SHA256 hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and log login event.
        
        Args:
            username: User's username
            password: User's password (plain text)
            
        Returns:
            Dictionary with:
            - success: Boolean indicating login success
            - user_data: User information if successful
            - message: Error message if failed
            - permissions: User permissions if successful
        """
        try:
            # Hash the provided password
            hashed_password = self.hash_password(password)
            
            # Query user from database
            query = """
            SELECT id, username, role, first_name, last_name, email, 
                   phone, is_active, is_locked, permissions_json,
                   failed_login_attempts, access_level, 
                   last_login, employee_id, job_title
            FROM employees 
            WHERE username = ? AND passcode_hash = ? AND is_active = 1
            """
            
            result = self.db.execute_query(query, (username, hashed_password))
            
            if not result:
                # Log failed login attempt
                self._log_failed_login_attempt(username)
                return {
                    'success': False,
                    'message': 'Invalid username or password',
                    'user_data': None,
                    'permissions': None
                }
            
            user = result[0]
            
            # Check if account is locked
            if user['is_locked']:
                return {
                    'success': False,
                    'message': 'Account is locked. Please contact administrator.',
                    'user_data': None,
                    'permissions': None
                }
            
            # Check if account has expired password
            if user.get('password_expiry_date'):
                expiry_date = datetime.strptime(user['password_expiry_date'], '%Y-%m-%d').date()
                if expiry_date < date.today():
                    return {
                        'success': False,
                        'message': 'Password has expired. Please reset your password.',
                        'user_data': None,
                        'permissions': None
                    }
            
            # Reset failed login attempts on successful login
            self._reset_failed_login_attempts(user['id'])
            
            # Update last login time
            self._update_last_login(user['id'])
            
            # Parse permissions JSON
            permissions = {}
            if user['permissions_json']:
                try:
                    permissions = json.loads(user['permissions_json'])
                except json.JSONDecodeError:
                    permissions = {'full_access': False}
            else:
                permissions = self._get_default_permissions(user['role'])
            
            # Prepare user data (remove sensitive information)
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'full_name': f"{user['first_name']} {user['last_name']}",
                'email': user['email'],
                'phone': user['phone'],
                'employee_id': user['employee_id'],
                'job_title': user['job_title'],
                'access_level': user['access_level'],
                'last_login': user['last_login']
            }
            
            # Log successful login to audit_logs
            self._log_audit_event(
                user_id=user['id'],
                action='login',
                module='auth',
                details=f"User {username} logged in successfully",
                status='success'
            )
            
            return {
                'success': True,
                'message': 'Login successful',
                'user_data': user_data,
                'permissions': permissions
            }
            
        except Exception as e:
            # Log error to audit_logs
            self._log_audit_event(
                user_id=None,
                action='login',
                module='auth',
                details=f"Login error for {username}: {str(e)}",
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Login error: {str(e)}',
                'user_data': None,
                'permissions': None
            }
    
    def check_permission(self, user_id: int, permission_key: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_id: User ID
            permission_key: Permission key to check
            
        Returns:
            Boolean indicating if user has permission
        """
        try:
            # Get user's permissions
            query = """
            SELECT role, permissions_json, access_level 
            FROM employees 
            WHERE id = ? AND is_active = 1
            """
            
            result = self.db.execute_query(query, (user_id,))
            
            if not result:
                return False
            
            user = result[0]
            
            # Admin users have all permissions
            if user['role'] == 'admin':
                return True
            
            # Parse permissions JSON
            permissions = {}
            if user['permissions_json']:
                try:
                    permissions = json.loads(user['permissions_json'])
                except json.JSONDecodeError:
                    return False
            
            # Check for full_access permission
            if permissions.get('full_access'):
                return True
            
            # Check specific permission
            permission_parts = permission_key.split('.')
            
            # Navigate through nested permissions
            current_level = permissions
            for part in permission_parts:
                if isinstance(current_level, dict) and part in current_level:
                    current_level = current_level[part]
                else:
                    return False
            
            # Permission should be True or have a truthy value
            return bool(current_level)
            
        except Exception as e:
            # Log error
            self._log_audit_event(
                user_id=user_id,
                action='check_permission',
                module='auth',
                details=f"Permission check error: {str(e)}",
                status='failure'
            )
            return False
    
    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary of user permissions
        """
        try:
            query = """
            SELECT role, permissions_json, access_level 
            FROM employees 
            WHERE id = ? AND is_active = 1
            """
            
            result = self.db.execute_query(query, (user_id,))
            
            if not result:
                return {}
            
            user = result[0]
            
            # Admin users have all permissions
            if user['role'] == 'admin':
                return {'full_access': True}
            
            # Parse permissions JSON
            permissions = {}
            if user['permissions_json']:
                try:
                    permissions = json.loads(user['permissions_json'])
                except json.JSONDecodeError:
                    permissions = self._get_default_permissions(user['role'])
            else:
                permissions = self._get_default_permissions(user['role'])
            
            return permissions
            
        except Exception as e:
            self._log_audit_event(
                user_id=user_id,
                action='get_permissions',
                module='auth',
                details=f"Get permissions error: {str(e)}",
                status='failure'
            )
            return {}
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password (plain text)
            new_password: New password (plain text)
            
        Returns:
            Dictionary with success status and message
        """
        try:
            # Verify old password
            query = """
            SELECT passcode_hash FROM employees 
            WHERE id = ? AND is_active = 1
            """
            
            result = self.db.execute_query(query, (user_id,))
            
            if not result:
                return {'success': False, 'message': 'User not found'}
            
            current_hash = result[0]['passcode_hash']
            old_hash = self.hash_password(old_password)
            
            if current_hash != old_hash:
                return {'success': False, 'message': 'Current password is incorrect'}
            
            # Update with new password
            new_hash = self.hash_password(new_password)
            update_query = """
            UPDATE employees 
            SET passcode_hash = ?, last_password_change = ?, must_change_password = 0
            WHERE id = ?
            """
            
            self.db.execute_update(update_query, (new_hash, datetime.now(), user_id))
            
            # Log password change
            self._log_audit_event(
                user_id=user_id,
                action='change_password',
                module='auth',
                details='Password changed successfully',
                status='success'
            )
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            self._log_audit_event(
                user_id=user_id,
                action='change_password',
                module='auth',
                details=f"Password change error: {str(e)}",
                status='failure'
            )
            return {'success': False, 'message': f'Error changing password: {str(e)}'}
    
    def logout(self, user_id: int) -> bool:
        """
        Log user logout event.
        
        Args:
            user_id: User ID
            
        Returns:
            Boolean indicating success
        """
        try:
            self._log_audit_event(
                user_id=user_id,
                action='logout',
                module='auth',
                details='User logged out',
                status='success'
            )
            return True
        except Exception as e:
            # Even if logging fails, logout should succeed
            print(f"Error logging logout: {e}")
            return True
    
    def _log_failed_login_attempt(self, username: str) -> None:
        """Log failed login attempt and increment counter."""
        try:
            # Find user by username
            query = "SELECT id, failed_login_attempts FROM employees WHERE username = ?"
            result = self.db.execute_query(query, (username,))
            
            if result:
                user_id = result[0]['id']
                current_attempts = result[0]['failed_login_attempts'] or 0
                new_attempts = current_attempts + 1
                
                # Update failed attempts counter
                update_query = "UPDATE employees SET failed_login_attempts = ? WHERE id = ?"
                self.db.execute_update(update_query, (new_attempts, user_id))
                
                # Lock account if too many failed attempts
                max_attempts = 5  # Could be configurable
                if new_attempts >= max_attempts:
                    lock_query = """
                    UPDATE employees 
                    SET is_locked = 1, lock_reason = 'Too many failed login attempts'
                    WHERE id = ?
                    """
                    self.db.execute_update(lock_query, (user_id,))
                
                # Log failed attempt
                self._log_audit_event(
                    user_id=user_id,
                    action='login',
                    module='auth',
                    details=f'Failed login attempt {new_attempts}',
                    status='failure'
                )
            else:
                # Log failed attempt for non-existent user
                self._log_audit_event(
                    user_id=None,
                    action='login',
                    module='auth',
                    details=f'Failed login attempt for non-existent user: {username}',
                    status='failure'
                )
                
        except Exception as e:
            print(f"Error logging failed login attempt: {e}")
    
    def _reset_failed_login_attempts(self, user_id: int) -> None:
        """Reset failed login attempts counter."""
        try:
            update_query = "UPDATE employees SET failed_login_attempts = 0 WHERE id = ?"
            self.db.execute_update(update_query, (user_id,))
        except Exception as e:
            print(f"Error resetting failed login attempts: {e}")
    
    def _update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        try:
            update_query = "UPDATE employees SET last_login = ? WHERE id = ?"
            self.db.execute_update(update_query, (datetime.now(), user_id))
        except Exception as e:
            print(f"Error updating last login: {e}")
    
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
    
    def _get_default_permissions(self, role: str) -> Dict[str, Any]:
        """
        Get default permissions based on role.
        
        Args:
            role: User role
            
        Returns:
            Dictionary of default permissions
        """
        # Define default permissions for each role
        defaults = {
            'admin': {
                'full_access': True
            },
            'manager': {
                'sales': {
                    'view': True,
                    'create': True,
                    'edit': True,
                    'delete': True,
                    'refund': True
                },
                'inventory': {
                    'view': True,
                    'edit': True,
                    'adjust': True
                },
                'reports': {
                    'view': True,
                    'export': True
                },
                'employees': {
                    'view': True,
                    'edit': True
                }
            },
            'cashier': {
                'sales': {
                    'view': True,
                    'create': True,
                    'refund': True
                },
                'inventory': {
                    'view': True
                }
            },
            'accountant': {
                'reports': {
                    'view': True,
                    'export': True
                },
                'financial': {
                    'view': True,
                    'edit': True
                }
            },
            'storekeeper': {
                'inventory': {
                    'view': True,
                    'edit': True,
                    'adjust': True
                }
            },
            'hr': {
                'employees': {
                    'view': True,
                    'create': True,
                    'edit': True,
                    'delete': True
                },
                'attendance': {
                    'view': True,
                    'edit': True
                }
            }
        }
        
        return defaults.get(role, {})


class HRController:
    """Handles HR operations including attendance tracking."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize HRController with database connection.
        
        Args:
            db_manager: Instance of DatabaseManager
        """
        self.db = db_manager
    
    def clock_in(self, employee_id: int, method: str = 'manual', 
                 latitude: float = None, longitude: float = None,
                 device_id: str = None, device_ip: str = None) -> Dict[str, Any]:
        """
        Record employee clock-in.
        
        Args:
            employee_id: Employee ID
            method: Clock-in method ('pin', 'biometric', 'card', 'mobile', 'manual')
            latitude: GPS latitude (optional)
            longitude: GPS longitude (optional)
            device_id: Device identifier (optional)
            device_ip: Device IP address (optional)
            
        Returns:
            Dictionary with success status and details
        """
        try:
            # Check if employee exists and is active
            employee_query = """
            SELECT id, first_name, last_name, is_active 
            FROM employees 
            WHERE id = ? AND is_active = 1
            """
            
            employee_result = self.db.execute_query(employee_query, (employee_id,))
            
            if not employee_result:
                return {
                    'success': False,
                    'message': 'Employee not found or inactive',
                    'attendance_id': None
                }
            
            today = date.today()
            
            # Check if already clocked in today
            existing_query = """
            SELECT id, check_in_time, check_out_time 
            FROM attendance 
            WHERE employee_id = ? AND date = ?
            """
            
            existing_result = self.db.execute_query(existing_query, (employee_id, today))
            
            if existing_result:
                attendance_record = existing_result[0]
                if attendance_record['check_out_time']:
                    # Can clock in again after clocking out
                    pass
                else:
                    return {
                        'success': False,
                        'message': 'Already clocked in today',
                        'attendance_id': attendance_record['id']
                    }
            
            # Get current shift information
            shift_query = """
            SELECT id, shift_name, start_time, end_time 
            FROM shifts 
            WHERE is_active = 1 
            ORDER BY id DESC LIMIT 1
            """
            
            shift_result = self.db.execute_query(shift_query)
            shift_id = shift_result[0]['id'] if shift_result else None
            shift_name = shift_result[0]['shift_name'] if shift_result else 'Default Shift'
            
            # Insert clock-in record
            insert_query = """
            INSERT INTO attendance 
            (employee_id, date, check_in_time, check_in_method, 
             check_in_latitude, check_in_longitude, check_in_device_id, 
             check_in_device_ip, shift_id, shift_name, attendance_status,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            current_time = datetime.now()
            
            self.db.execute_update(insert_query, (
                employee_id, today, current_time, method,
                latitude, longitude, device_id, device_ip,
                shift_id, shift_name, 'present',
                current_time, current_time
            ))
            
            # Get the inserted attendance ID
            attendance_id_query = "SELECT last_insert_rowid()"
            attendance_id_result = self.db.execute_query(attendance_id_query)
            attendance_id = attendance_id_result[0]['last_insert_rowid()']
            
            # Log clock-in event
            self._log_audit_event(
                user_id=employee_id,
                action='clock_in',
                module='hr',
                details=f'Clocked in using {method} method',
                status='success'
            )
            
            return {
                'success': True,
                'message': 'Clock-in recorded successfully',
                'attendance_id': attendance_id,
                'check_in_time': current_time.isoformat(),
                'employee_name': f"{employee_result[0]['first_name']} {employee_result[0]['last_name']}"
            }
            
        except Exception as e:
            # Log error
            self._log_audit_event(
                user_id=employee_id,
                action='clock_in',
                module='hr',
                details=f'Clock-in error: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Error recording clock-in: {str(e)}',
                'attendance_id': None
            }
    
    def clock_out(self, employee_id: int, method: str = 'manual',
                  latitude: float = None, longitude: float = None,
                  device_id: str = None, device_ip: str = None) -> Dict[str, Any]:
        """
        Record employee clock-out.
        
        Args:
            employee_id: Employee ID
            method: Clock-out method (optional)
            latitude: GPS latitude (optional)
            longitude: GPS longitude (optional)
            device_id: Device identifier (optional)
            device_ip: Device IP address (optional)
            
        Returns:
            Dictionary with success status and details
        """
        try:
            today = date.today()
            
            # Find today's attendance record that hasn't been clocked out
            query = """
            SELECT id, check_in_time, check_out_time 
            FROM attendance 
            WHERE employee_id = ? AND date = ? AND check_out_time IS NULL
            ORDER BY check_in_time DESC LIMIT 1
            """
            
            result = self.db.execute_query(query, (employee_id, today))
            
            if not result:
                return {
                    'success': False,
                    'message': 'No active clock-in found for today',
                    'attendance_id': None
                }
            
            attendance_id = result[0]['id']
            check_in_time_str = result[0]['check_in_time']
            
            # Parse check-in time
            check_in_time = datetime.fromisoformat(check_in_time_str) if check_in_time_str else datetime.now()
            current_time = datetime.now()
            
            # Calculate worked minutes
            worked_minutes = int((current_time - check_in_time).total_seconds() / 60)
            
            # Update clock-out record
            update_query = """
            UPDATE attendance 
            SET check_out_time = ?, check_out_method = ?,
                check_out_latitude = ?, check_out_longitude = ?,
                check_out_device_id = ?, check_out_device_ip = ?,
                total_worked_minutes = ?, updated_at = ?
            WHERE id = ?
            """
            
            self.db.execute_update(update_query, (
                current_time, method, latitude, longitude,
                device_id, device_ip, worked_minutes,
                current_time, attendance_id
            ))
            
            # Log clock-out event
            self._log_audit_event(
                user_id=employee_id,
                action='clock_out',
                module='hr',
                details=f'Clocked out after {worked_minutes} minutes',
                status='success'
            )
            
            return {
                'success': True,
                'message': 'Clock-out recorded successfully',
                'attendance_id': attendance_id,
                'check_out_time': current_time.isoformat(),
                'worked_minutes': worked_minutes
            }
            
        except Exception as e:
            # Log error
            self._log_audit_event(
                user_id=employee_id,
                action='clock_out',
                module='hr',
                details=f'Clock-out error: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Error recording clock-out: {str(e)}',
                'attendance_id': None
            }
    
    def get_today_attendance(self, employee_id: int = None) -> Dict[str, Any]:
        """
        Get today's attendance records.
        
        Args:
            employee_id: Optional employee ID to filter
            
        Returns:
            Dictionary with attendance records
        """
        try:
            today = date.today()
            
            if employee_id:
                query = """
                SELECT a.*, e.first_name, e.last_name, e.employee_id, e.job_title
                FROM attendance a
                JOIN employees e ON a.employee_id = e.id
                WHERE a.date = ? AND a.employee_id = ?
                ORDER BY a.check_in_time DESC
                """
                params = (today, employee_id)
            else:
                query = """
                SELECT a.*, e.first_name, e.last_name, e.employee_id, e.job_title
                FROM attendance a
                JOIN employees e ON a.employee_id = e.id
                WHERE a.date = ?
                ORDER BY a.check_in_time DESC
                """
                params = (today,)
            
            result = self.db.execute_query(query, params)
            
            # Format the results
            attendance_records = []
            for row in result:
                record = dict(row)
                # Convert datetime objects to string for JSON serialization
                if record.get('check_in_time'):
                    record['check_in_time'] = record['check_in_time'].isoformat()
                if record.get('check_out_time'):
                    record['check_out_time'] = record['check_out_time'].isoformat()
                if record.get('created_at'):
                    record['created_at'] = record['created_at'].isoformat()
                if record.get('updated_at'):
                    record['updated_at'] = record['updated_at'].isoformat()
                
                attendance_records.append(record)
            
            # Calculate summary statistics
            total_employees = len(attendance_records)
            clocked_in = len([r for r in attendance_records if r['check_out_time'] is None])
            clocked_out = total_employees - clocked_in
            
            return {
                'success': True,
                'records': attendance_records,
                'summary': {
                    'total': total_employees,
                    'clocked_in': clocked_in,
                    'clocked_out': clocked_out,
                    'date': today.isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching attendance: {str(e)}',
                'records': [],
                'summary': {}
            }
    
    def get_employee_attendance_summary(self, employee_id: int, 
                                       start_date: date = None, 
                                       end_date: date = None) -> Dict[str, Any]:
        """
        Get attendance summary for an employee over a date range.
        
        Args:
            employee_id: Employee ID
            start_date: Start date (default: beginning of current month)
            end_date: End date (default: today)
            
        Returns:
            Dictionary with attendance summary
        """
        try:
            if not start_date:
                # Default to beginning of current month
                today = date.today()
                start_date = date(today.year, today.month, 1)
            
            if not end_date:
                end_date = date.today()
            
            query = """
            SELECT 
                COUNT(*) as total_days,
                SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) as days_present,
                SUM(CASE WHEN attendance_status = 'absent' THEN 1 ELSE 0 END) as days_absent,
                SUM(CASE WHEN attendance_status = 'late' THEN 1 ELSE 0 END) as days_late,
                SUM(CASE WHEN attendance_status = 'leave' THEN 1 ELSE 0 END) as days_leave,
                AVG(total_worked_minutes) as avg_worked_minutes,
                SUM(total_worked_minutes) as total_worked_minutes,
                SUM(CASE WHEN check_out_time IS NULL AND date < ? THEN 1 ELSE 0 END) as missing_clockout
            FROM attendance 
            WHERE employee_id = ? AND date BETWEEN ? AND ?
            """
            
            result = self.db.execute_query(query, (
                end_date, employee_id, start_date, end_date
            ))
            
            if result:
                summary = dict(result[0])
                # Convert numeric fields
                for key in ['avg_worked_minutes', 'total_worked_minutes']:
                    if summary[key] is not None:
                        summary[key] = float(summary[key])
                return {
                    'success': True,
                    'summary': summary,
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'No attendance records found',
                    'summary': {},
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching attendance summary: {str(e)}',
                'summary': {},
                'period': {}
            }
    
    def manual_attendance_correction(self, attendance_id: int, 
                                    corrections: Dict[str, Any],
                                    corrected_by: int) -> Dict[str, Any]:
        """
        Manually correct attendance record.
        
        Args:
            attendance_id: Attendance record ID
            corrections: Dictionary of corrections
            corrected_by: User ID of person making correction
            
        Returns:
            Dictionary with success status
        """
        try:
            # Verify the attendance record exists
            verify_query = "SELECT employee_id, date FROM attendance WHERE id = ?"
            verify_result = self.db.execute_query(verify_query, (attendance_id,))
            
            if not verify_result:
                return {'success': False, 'message': 'Attendance record not found'}
            
            employee_id = verify_result[0]['employee_id']
            
            # Build update query based on corrections
            update_fields = []
            params = []
            
            valid_fields = [
                'check_in_time', 'check_out_time', 'attendance_status',
                'total_worked_minutes', 'late_minutes', 'early_departure_minutes',
                'notes', 'is_approved', 'approved_by', 'approved_at'
            ]
            
            for field, value in corrections.items():
                if field in valid_fields:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if not update_fields:
                return {'success': False, 'message': 'No valid corrections provided'}
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            params.append(datetime.now())
            
            # Add attendance_id to params
            params.append(attendance_id)
            
            # Execute update
            update_query = f"UPDATE attendance SET {', '.join(update_fields)} WHERE id = ?"
            self.db.execute_update(update_query, tuple(params))
            
            # Log correction
            self._log_audit_event(
                user_id=corrected_by,
                action='attendance_correction',
                module='hr',
                details=f'Corrected attendance record {attendance_id} for employee {employee_id}',
                status='success'
            )
            
            return {
                'success': True,
                'message': 'Attendance corrected successfully',
                'attendance_id': attendance_id
            }
            
        except Exception as e:
            self._log_audit_event(
                user_id=corrected_by,
                action='attendance_correction',
                module='hr',
                details=f'Attendance correction error: {str(e)}',
                status='failure'
            )
            
            return {
                'success': False,
                'message': f'Error correcting attendance: {str(e)}'
            }
    
    def _log_audit_event(self, user_id: int, action: str, module: str, 
                        details: str, status: str = 'success') -> None:
        """
        Log event to audit_logs table.
        
        Args:
            user_id: User ID
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
    
    # Create controllers
    auth_controller = AuthController(db)
    hr_controller = HRController(db)
    
    # Test login
    print("Testing login...")
    result = auth_controller.login("admin", "admin123")
    print(f"Login result: {result['success']}")
    if result['success']:
        print(f"User data: {result['user_data']}")
        print(f"Permissions: {result['permissions']}")
    
    # Test permission check
    if result['success']:
        user_id = result['user_data']['id']
        has_permission = auth_controller.check_permission(user_id, "sales.create")
        print(f"Has sales.create permission: {has_permission}")
    
    # Test clock in/out
    print("\nTesting clock in...")
    clock_in_result = hr_controller.clock_in(1, method="manual")
    print(f"Clock in: {clock_in_result}")
    
    print("\nTesting clock out...")
    clock_out_result = hr_controller.clock_out(1, method="manual")
    print(f"Clock out: {clock_out_result}")
    
    print("\nTesting today's attendance...")
    attendance_result = hr_controller.get_today_attendance()
    print(f"Attendance records: {len(attendance_result['records'])}")
    
    print("\nAll tests completed!")