"""
Customer Management Model
Handles CRUD operations for customers with business logic constraints.
"""

import mysql.connector
from mysql.connector import Error
from config import get_db_config
import logging

logger = logging.getLogger(__name__)

class CustomerModel:
    """Handles all customer-related database operations."""
    
    def __init__(self):
        self.db_config = get_db_config()
    
    def _get_connection(self):
        """Get database connection."""
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def add_customer(self, first_name, last_name, email, phone, address):
        """
        Add a new customer to the database.
        
        Args:
            first_name (str): Customer first name
            last_name (str): Customer last name
            email (str): Customer email
            phone (str): Customer phone number
            address (str): Customer address
            
        Returns:
            tuple: (success: bool, message: str, customer_id: int)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Check if email already exists
            if email:
                cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (email,))
                if cursor.fetchone():
                    return False, "Email already exists", None
            
            # Insert new customer
            cursor.execute("""
                INSERT INTO customers (first_name, last_name, email, phone, address)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, email, phone, address))
            
            customer_id = cursor.lastrowid
            connection.commit()
            
            logger.info(f"Customer added successfully: {first_name} {last_name} (ID: {customer_id})")
            return True, "Customer added successfully", customer_id
            
        except Error as e:
            connection.rollback()
            logger.error(f"Add customer failed: {e}")
            return False, f"Failed to add customer: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def update_customer(self, customer_id, **kwargs):
        """
        Update customer details.
        
        Args:
            customer_id (int): Customer ID to update
            **kwargs: Fields to update (first_name, last_name, email, phone, address)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not kwargs:
            return False, "No fields to update"
        
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed"
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Check email uniqueness if email is being updated
            if 'email' in kwargs and kwargs['email']:
                cursor.execute(
                    "SELECT customer_id FROM customers WHERE email = %s AND customer_id != %s",
                    (kwargs['email'], customer_id)
                )
                if cursor.fetchone():
                    return False, "Email already exists for another customer"
            
            # Build dynamic update query
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(customer_id)
            
            query = f"UPDATE customers SET {set_clause} WHERE customer_id = %s"
            
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                return False, "Customer not found"
            
            connection.commit()
            logger.info(f"Customer updated successfully: ID {customer_id}")
            return True, "Customer updated successfully"
            
        except Error as e:
            connection.rollback()
            logger.error(f"Update customer failed: {e}")
            return False, f"Failed to update customer: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def delete_customer(self, customer_id):
        """
        Delete a customer if they have no active rentals.
        
        Args:
            customer_id (int): Customer ID to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed"
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Check if customer has active rentals
            cursor.execute("""
                SELECT COUNT(*) FROM rentals 
                WHERE customer_id = %s AND rental_status IN ('active', 'overdue')
            """, (customer_id,))
            
            active_rentals = cursor.fetchone()[0]
            
            if active_rentals > 0:
                return False, f"Cannot delete customer. They have {active_rentals} active rental(s)."
            
            # Delete customer (soft delete by setting is_active to False)
            cursor.execute(
                "UPDATE customers SET is_active = FALSE WHERE customer_id = %s",
                (customer_id,)
            )
            
            if cursor.rowcount == 0:
                return False, "Customer not found"
            
            connection.commit()
            logger.info(f"Customer deactivated successfully: ID {customer_id}")
            return True, "Customer deactivated successfully"
            
        except Error as e:
            connection.rollback()
            logger.error(f"Delete customer failed: {e}")
            return False, f"Failed to delete customer: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def get_customer_by_id(self, customer_id):
        """
        Get customer details by ID.
        
        Args:
            customer_id (int): Customer ID
            
        Returns:
            tuple: (success: bool, message: str, customer_data: dict)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT customer_id, first_name, last_name, email, phone, address,
                       date_registered, is_active
                FROM customers 
                WHERE customer_id = %s
            """, (customer_id,))
            
            customer = cursor.fetchone()
            
            if not customer:
                return False, "Customer not found", None
            
            return True, "Customer found", customer
            
        except Error as e:
            logger.error(f"Get customer failed: {e}")
            return False, f"Operation failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def search_customers(self, search_term=None, active_only=True):
        """
        Search customers by name or ID.
        
        Args:
            search_term (str): Search term for name or ID
            active_only (bool): Only show active customers
            
        Returns:
            tuple: (success: bool, message: str, customers: list)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            conditions = ["is_active = TRUE"] if active_only else []
            params = []
            
            if search_term:
                # Try to parse as customer ID
                try:
                    customer_id = int(search_term)
                    conditions.append("customer_id = %s")
                    params.append(customer_id)
                except ValueError:
                    # Search by name
                    conditions.append("(first_name LIKE %s OR last_name LIKE %s)")
                    params.extend([f"%{search_term}%", f"%{search_term}%"])
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT customer_id, first_name, last_name, email, phone, address,
                       date_registered, is_active
                FROM customers 
                WHERE {where_clause}
                ORDER BY last_name, first_name
            """
            
            cursor.execute(query, params)
            customers = cursor.fetchall()
            
            return True, f"Found {len(customers)} customers", customers
            
        except Error as e:
            logger.error(f"Search customers failed: {e}")
            return False, f"Search failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def get_all_customers(self, active_only=True):
        """
        Get all customers.
        
        Args:
            active_only (bool): Only return active customers
            
        Returns:
            tuple: (success: bool, message: str, customers: list)
        """
        return self.search_customers(None, active_only)
    
    def get_customer_rental_history(self, customer_id):
        """
        Get rental history for a customer.
        
        Args:
            customer_id (int): Customer ID
            
        Returns:
            tuple: (success: bool, message: str, rentals: list)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT r.rental_id, m.title, r.rental_date, r.due_date, r.actual_return_date,
                       r.rental_status, r.total_charge, r.late_fee,
                       CONCAT(e.first_name, ' ', e.last_name) as processed_by
                FROM rentals r
                JOIN movies m ON r.movie_id = m.movie_id
                JOIN employees e ON r.employee_id = e.employee_id
                WHERE r.customer_id = %s
                ORDER BY r.rental_date DESC
            """, (customer_id,))
            
            rentals = cursor.fetchall()
            
            return True, f"Found {len(rentals)} rentals", rentals
            
        except Error as e:
            logger.error(f"Get customer rental history failed: {e}")
            return False, f"Operation failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()