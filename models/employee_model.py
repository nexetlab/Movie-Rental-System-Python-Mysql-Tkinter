"""
Employee Authentication Model
Handles employee registration, login, and authentication with secure password hashing.
"""

import mysql.connector
from mysql.connector import Error
from config import hash_password, verify_password, get_db_config
import logging

logger = logging.getLogger(__name__)

class EmployeeModel:
    """Handles all employee-related database operations."""
    
    def __init__(self):
        self.db_config = get_db_config()
    
    def _get_connection(self):
        """Get database connection."""
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def register_employee(self, username, password, first_name, last_name, email, role='staff'):
        """
        Register a new employee with hashed password.
        
        Args:
            username (str): Unique username
            password (str): Plain text password
            first_name (str): Employee first name
            last_name (str): Employee last name
            email (str): Employee email
            role (str): Employee role (admin/manager/staff)
            
        Returns:
            tuple: (success: bool, message: str, employee_id: int)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT employee_id FROM employees WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already exists", None
            
            # Check if email already exists
            cursor.execute("SELECT employee_id FROM employees WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "Email already exists", None
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Insert new employee
            cursor.execute("""
                INSERT INTO employees (username, password_hash, first_name, last_name, email, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, hashed_password, first_name, last_name, email, role))
            
            employee_id = cursor.lastrowid
            connection.commit()
            
            logger.info(f"Employee registered successfully: {username} (ID: {employee_id})")
            return True, "Employee registered successfully", employee_id
            
        except Error as e:
            connection.rollback()
            logger.error(f"Employee registration failed: {e}")
            return False, f"Registration failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def login_employee(self, username, password):
        """
        Authenticate employee login with hashed password verification.
        
        Args:
            username (str): Employee username
            password (str): Plain text password
            
        Returns:
            tuple: (success: bool, message: str, employee_data: dict)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get employee data with hashed password
            cursor.execute("""
                SELECT employee_id, username, password_hash, first_name, last_name, email, role, is_active
                FROM employees 
                WHERE username = %s
            """, (username,))
            
            employee = cursor.fetchone()
            
            if not employee:
                return False, "Invalid username or password", None
            
            if not employee['is_active']:
                return False, "Account is deactivated", None
            
            # Verify password
            if not verify_password(employee['password_hash'], password):
                return False, "Invalid username or password", None
            
            # Remove password hash from returned data
            employee.pop('password_hash', None)
            
            logger.info(f"Employee login successful: {username} (ID: {employee['employee_id']})")
            return True, "Login successful", employee
            
        except Error as e:
            logger.error(f"Employee login failed: {e}")
            return False, f"Login failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def get_employee_by_id(self, employee_id):
        """
        Get employee data by ID.
        
        Args:
            employee_id (int): Employee ID
            
        Returns:
            tuple: (success: bool, message: str, employee_data: dict)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT employee_id, username, first_name, last_name, email, role, created_at, is_active
                FROM employees 
                WHERE employee_id = %s
            """, (employee_id,))
            
            employee = cursor.fetchone()
            
            if not employee:
                return False, "Employee not found", None
            
            return True, "Employee found", employee
            
        except Error as e:
            logger.error(f"Get employee failed: {e}")
            return False, f"Operation failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def update_employee_password(self, employee_id, old_password, new_password):
        """
        Update employee password with verification.
        
        Args:
            employee_id (int): Employee ID
            old_password (str): Current plain text password
            new_password (str): New plain text password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed"
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Get current password hash
            cursor.execute("SELECT password_hash FROM employees WHERE employee_id = %s", (employee_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "Employee not found"
            
            current_hash = result[0]
            
            # Verify old password
            if not verify_password(current_hash, old_password):
                return False, "Current password is incorrect"
            
            # Hash new password
            new_hash = hash_password(new_password)
            
            # Update password
            cursor.execute(
                "UPDATE employees SET password_hash = %s WHERE employee_id = %s",
                (new_hash, employee_id)
            )
            
            connection.commit()
            logger.info(f"Password updated for employee ID: {employee_id}")
            return True, "Password updated successfully"
            
        except Error as e:
            connection.rollback()
            logger.error(f"Password update failed: {e}")
            return False, f"Password update failed: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            connection.close()