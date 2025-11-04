"""
Rental Management Model - FIXED VERSION
Handles movie rentals, returns, late fee calculations, and rental searches.
"""

import mysql.connector
from mysql.connector import Error
from config import get_db_config
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RentalModel:
    """Handles all rental-related database operations."""
    
    def __init__(self):
        self.db_config = get_db_config()
        self.late_fee_per_day = 2.00  # Default late fee per day
    
    def _get_connection(self):
        """Get database connection."""
        try:
            connection = mysql.connector.connect(**self.db_config)
            return connection
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def rent_movie(self, customer_id, movie_id, employee_id, due_date):
        """
        Rent a movie to a customer.
        
        Args:
            customer_id (int): Customer ID
            movie_id (int): Movie ID
            employee_id (int): Employee ID processing the rental
            due_date (datetime.date): Due date for return
            
        Returns:
            tuple: (success: bool, message: str, rental_id: int)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Check if customer exists and is active
            cursor.execute("SELECT is_active FROM customers WHERE customer_id = %s", (customer_id,))
            customer_result = cursor.fetchone()
            if not customer_result:
                return False, "Customer not found", None
            if not customer_result[0]:
                return False, "Customer account is inactive", None
            
            # Check if movie exists and is available
            cursor.execute("""
                SELECT title, rental_rate, stock_quantity, is_available 
                FROM movies WHERE movie_id = %s
            """, (movie_id,))
            movie_result = cursor.fetchone()
            if not movie_result:
                return False, "Movie not found", None
            
            title, rental_rate, stock_quantity, is_available = movie_result
            
            if not is_available or stock_quantity <= 0:
                return False, "Movie is not available for rental", None
            
            # Calculate rental period and charge
            rental_date = datetime.now().date()
            rental_days = (due_date - rental_date).days
            
            if rental_days <= 0:
                return False, "Due date must be in the future", None
            
            total_charge = rental_rate * rental_days
            
            # Start transaction explicitly
            connection.autocommit = False
            
            # Insert rental record
            cursor.execute("""
                INSERT INTO rentals (customer_id, movie_id, employee_id, due_date, total_charge)
                VALUES (%s, %s, %s, %s, %s)
            """, (customer_id, movie_id, employee_id, due_date, total_charge))
            
            rental_id = cursor.lastrowid
            
            # Update movie stock quantity
            new_stock = stock_quantity - 1
            is_available_new = new_stock > 0
            
            cursor.execute("""
                UPDATE movies 
                SET stock_quantity = %s,
                    is_available = %s
                WHERE movie_id = %s
            """, (new_stock, is_available_new, movie_id))
            
            # Commit transaction
            connection.commit()
            
            logger.info(f"Movie rented successfully: {title} to customer {customer_id} (Rental ID: {rental_id})")
            return True, f"Movie '{title}' rented successfully. Charge: ${total_charge:.2f}", rental_id
            
        except Error as e:
            # Rollback transaction on error
            if connection:
                connection.rollback()
            logger.error(f"Rent movie failed: {e}")
            return False, f"Failed to rent movie: {str(e)}", None
        finally:
            # Reset autocommit and close connection
            if connection:
                connection.autocommit = True
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def return_movie(self, rental_id, employee_id):
        """
        Process movie return and calculate late fees if applicable.
        
        Args:
            rental_id (int): Rental ID to return
            employee_id (int): Employee ID processing the return
            
        Returns:
            tuple: (success: bool, message: str, return_data: dict)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get rental details
            cursor.execute("""
                SELECT r.rental_id, r.customer_id, r.movie_id, r.due_date, r.total_charge,
                       m.title, m.rental_rate, m.stock_quantity
                FROM rentals r
                JOIN movies m ON r.movie_id = m.movie_id
                WHERE r.rental_id = %s AND r.rental_status = 'active'
            """, (rental_id,))
            
            rental = cursor.fetchone()
            
            if not rental:
                return False, "Rental not found or already returned", None
            
            # Calculate late fees
            return_date = datetime.now().date()
            due_date = rental['due_date']
            late_days = max(0, (return_date - due_date).days)
            late_fee = late_days * self.late_fee_per_day
            total_paid = float(rental['total_charge']) + late_fee
            
            # Start transaction
            connection.autocommit = False
            
            # Update rental record
            cursor.execute("""
                UPDATE rentals 
                SET actual_return_date = %s, 
                    late_fee = %s,
                    rental_status = 'returned'
                WHERE rental_id = %s
            """, (return_date, late_fee, rental_id))
            
            # Insert return record
            cursor.execute("""
                INSERT INTO returns (rental_id, return_date, late_days, late_fee, total_paid, processed_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (rental_id, datetime.now(), late_days, late_fee, total_paid, employee_id))
            
            # Update movie stock quantity
            new_stock = rental['stock_quantity'] + 1
            cursor.execute("""
                UPDATE movies 
                SET stock_quantity = %s,
                    is_available = TRUE
                WHERE movie_id = %s
            """, (new_stock, rental['movie_id']))
            
            # Commit transaction
            connection.commit()
            
            return_data = {
                'rental_id': rental_id,
                'movie_title': rental['title'],
                'return_date': return_date,
                'late_days': late_days,
                'late_fee': late_fee,
                'original_charge': rental['total_charge'],
                'total_paid': total_paid
            }
            
            logger.info(f"Movie returned successfully: {rental['title']} (Rental ID: {rental_id})")
            
            if late_days > 0:
                message = f"Movie '{rental['title']}' returned {late_days} day(s) late. Late fee: ${late_fee:.2f}. Total: ${total_paid:.2f}"
            else:
                message = f"Movie '{rental['title']}' returned on time. Total: ${total_paid:.2f}"
            
            return True, message, return_data
            
        except Error as e:
            # Rollback transaction on error
            if connection:
                connection.rollback()
            logger.error(f"Return movie failed: {e}")
            return False, f"Failed to return movie: {str(e)}", None
        finally:
            # Reset autocommit and close connection
            if connection:
                connection.autocommit = True
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def calculate_late_fee(self, due_date, return_date=None):
        """
        Calculate late fee based on due date and return date.
        
        Args:
            due_date (datetime.date): Original due date
            return_date (datetime.date): Actual return date (defaults to today)
            
        Returns:
            tuple: (late_days: int, late_fee: float)
        """
        if return_date is None:
            return_date = datetime.now().date()
        
        late_days = max(0, (return_date - due_date).days)
        late_fee = late_days * self.late_fee_per_day
        
        return late_days, late_fee
    
    def search_rentals(self, customer_id=None, movie_id=None, status=None, 
                      start_date=None, end_date=None):
        """
        Search rentals with various filters.
        
        Args:
            customer_id (int): Filter by customer
            movie_id (int): Filter by movie
            status (str): Filter by status (active/returned/overdue)
            start_date (datetime.date): Start date for rental period
            end_date (datetime.date): End date for rental period
            
        Returns:
            tuple: (success: bool, message: str, rentals: list)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Build dynamic WHERE clause
            conditions = []
            params = []
            
            if customer_id:
                conditions.append("r.customer_id = %s")
                params.append(customer_id)
            
            if movie_id:
                conditions.append("r.movie_id = %s")
                params.append(movie_id)
            
            if status:
                conditions.append("r.rental_status = %s")
                params.append(status)
            
            if start_date:
                conditions.append("r.rental_date >= %s")
                params.append(start_date)
            
            if end_date:
                conditions.append("r.rental_date <= %s")
                params.append(end_date)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT r.rental_id, r.customer_id, r.movie_id, r.employee_id,
                       r.rental_date, r.due_date, r.actual_return_date,
                       r.total_charge, r.late_fee, r.rental_status, r.created_at,
                       c.first_name as customer_first_name, 
                       c.last_name as customer_last_name,
                       m.title as movie_title,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name
                FROM rentals r
                JOIN customers c ON r.customer_id = c.customer_id
                JOIN movies m ON r.movie_id = m.movie_id
                JOIN employees e ON r.employee_id = e.employee_id
                WHERE {where_clause}
                ORDER BY r.rental_date DESC
            """
            
            cursor.execute(query, params)
            rentals = cursor.fetchall()
            
            return True, f"Found {len(rentals)} rentals", rentals
            
        except Error as e:
            logger.error(f"Search rentals failed: {e}")
            return False, f"Search failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_active_rentals(self):
        """
        Get all active rentals (not returned).
        
        Returns:
            tuple: (success: bool, message: str, rentals: list)
        """
        return self.search_rentals(status='active')
    
    def get_overdue_rentals(self):
        """
        Get all overdue rentals.
        
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
                SELECT r.rental_id, r.customer_id, r.movie_id, r.employee_id,
                       r.rental_date, r.due_date, r.total_charge, r.late_fee,
                       c.first_name as customer_first_name, 
                       c.last_name as customer_last_name,
                       m.title as movie_title,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                       DATEDIFF(CURDATE(), r.due_date) as days_overdue
                FROM rentals r
                JOIN customers c ON r.customer_id = c.customer_id
                JOIN movies m ON r.movie_id = m.movie_id
                JOIN employees e ON r.employee_id = e.employee_id
                WHERE r.rental_status = 'active' 
                AND r.due_date < CURDATE()
                ORDER BY r.due_date ASC
            """)
            
            rentals = cursor.fetchall()
            
            return True, f"Found {len(rentals)} overdue rentals", rentals
            
        except Error as e:
            logger.error(f"Get overdue rentals failed: {e}")
            return False, f"Operation failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def update_overdue_statuses(self):
        """
        Update rental statuses from 'active' to 'overdue' for past due rentals.
        
        Returns:
            tuple: (success: bool, message: str, updated_count: int)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE rentals 
                SET rental_status = 'overdue'
                WHERE rental_status = 'active' 
                AND due_date < CURDATE()
            """)
            
            updated_count = cursor.rowcount
            connection.commit()
            
            logger.info(f"Updated {updated_count} rentals to overdue status")
            return True, f"Updated {updated_count} rentals to overdue", updated_count
            
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Update overdue statuses failed: {e}")
            return False, f"Operation failed: {str(e)}", 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()