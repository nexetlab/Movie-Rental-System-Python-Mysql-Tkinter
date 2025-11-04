"""
Database initialization script - creates all tables and initial data
"""
import mysql.connector
from config import DB_CONFIG
import logging
from utils.security import hash_password


logger = logging.getLogger(__name__)

class DatabaseInitializer:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            logger.info("Connected to MySQL database")
            return True
        except mysql.connector.Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS movie_rental_system")
            cursor.execute("USE movie_rental_system")
            logger.info("Database created/verified successfully")
            return True
        except mysql.connector.Error as e:
            logger.error(f"Database creation failed: {e}")
            return False
    
    def create_tables(self):
        """Execute all CREATE TABLE statements"""
        try:
            cursor = self.connection.cursor()
            
            # Employees table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    role ENUM('admin', 'manager', 'staff') NOT NULL DEFAULT 'staff',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                )
            """)
            
            # Movies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    movie_id INT PRIMARY KEY AUTO_INCREMENT,
                    title VARCHAR(255) NOT NULL,
                    director VARCHAR(255),
                    genre VARCHAR(100),
                    release_year INT,
                    duration INT,
                    description TEXT,
                    rental_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                    stock_quantity INT NOT NULL DEFAULT 0,
                    total_copies INT NOT NULL DEFAULT 0,
                    is_available BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_title (title),
                    INDEX idx_genre (genre),
                    INDEX idx_availability (is_available)
                )
            """)
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INT PRIMARY KEY AUTO_INCREMENT,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    phone VARCHAR(20),
                    address TEXT,
                    date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    INDEX idx_name (last_name, first_name),
                    INDEX idx_email (email)
                )
            """)
            
            # Rentals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rentals (
                    rental_id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_id INT NOT NULL,
                    movie_id INT NOT NULL,
                    employee_id INT NOT NULL,
                    rental_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date DATE NOT NULL,
                    actual_return_date DATE,
                    total_charge DECIMAL(8,2) DEFAULT 0.00,
                    late_fee DECIMAL(8,2) DEFAULT 0.00,
                    rental_status ENUM('active', 'returned', 'overdue') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) 
                        ON DELETE RESTRICT ON UPDATE CASCADE,
                    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) 
                        ON DELETE RESTRICT ON UPDATE CASCADE,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) 
                        ON DELETE RESTRICT ON UPDATE CASCADE,
                    INDEX idx_customer (customer_id),
                    INDEX idx_movie (movie_id),
                    INDEX idx_status (rental_status),
                    INDEX idx_due_date (due_date)
                )
            """)
            
            # Returns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS returns (
                    return_id INT PRIMARY KEY AUTO_INCREMENT,
                    rental_id INT NOT NULL,
                    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    late_days INT DEFAULT 0,
                    late_fee DECIMAL(8,2) DEFAULT 0.00,
                    total_paid DECIMAL(8,2) NOT NULL,
                    processed_by INT NOT NULL,
                    FOREIGN KEY (rental_id) REFERENCES rentals(rental_id) 
                        ON DELETE RESTRICT ON UPDATE CASCADE,
                    FOREIGN KEY (processed_by) REFERENCES employees(employee_id) 
                        ON DELETE RESTRICT ON UPDATE CASCADE,
                    INDEX idx_rental (rental_id),
                    INDEX idx_return_date (return_date)
                )
            """)
            
            self.connection.commit()
            logger.info("All tables created successfully")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Table creation failed: {e}")
            self.connection.rollback()
            return False
    
    def create_default_admin(self):
        """Create a default admin user for first-time setup"""
        try:
            cursor = self.connection.cursor()
            
            # Check if admin already exists
            cursor.execute("SELECT COUNT(*) FROM employees WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                # Create default admin (password: admin123)
                from utils.security import hash_password
                hashed_password = hash_password("admin123")
                
                cursor.execute("""
                    INSERT INTO employees (username, password_hash, first_name, last_name, email, role)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('admin', hashed_password, 'System', 'Administrator', 'admin@movierental.com', 'admin'))
                
                self.connection.commit()
                logger.info("Default admin user created (username: admin, password: admin123)")
            
            return True
        except mysql.connector.Error as e:
            logger.error(f"Admin creation failed: {e}")
            return False
    
    def initialize_database(self):
        """Main method to initialize entire database"""
        if not self.connect():
            return False
        
        try:
            if (self.create_database() and 
                self.create_tables() and 
                self.create_default_admin()):
                logger.info("Database initialization completed successfully")
                return True
            else:
                logger.error("Database initialization failed")
                return False
        finally:
            if self.connection:
                self.connection.close()

def init_db():
    """Convenience function to initialize database"""
    initializer = DatabaseInitializer()
    return initializer.initialize_database()

if __name__ == "__main__":
    # Run this script directly to initialize database
    init_db()