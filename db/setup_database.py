#!/usr/bin/env python3
"""
Database setup script for Movie Rental Management System.
Creates database, tables, and initial admin user with secure password hashing.
"""

import sys
import os
import logging
from mysql.connector import Error, errorcode

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import create_db_connection, hash_password, get_db_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database_setup.log')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Handles database creation and initialization."""
    
    def __init__(self):
        self.connection = None
        self.db_config = get_db_config()
        self.database_name = 'movie_rental_db'  # Changed from movie_rental_system
    
    def connect_to_mysql(self):
        """Connect to MySQL server without specific database."""
        try:
            temp_config = self.db_config.copy()
            temp_config.pop('database', None)
            
            self.connection = create_db_connection()
            logger.info("✅ Connected to MySQL server successfully")
            return True
            
        except Error as e:
            logger.error(f"❌ Failed to connect to MySQL: {e}")
            return False
    
    def create_database(self):
        """Create database if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            
            # Create database with UTF8MB4 encoding for full Unicode support
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {self.database_name} 
                CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Use the database
            cursor.execute(f"USE {self.database_name}")
            
            logger.info(f"✅ Database '{self.database_name}' created/verified successfully")
            cursor.close()
            return True
            
        except Error as e:
            logger.error(f"❌ Failed to create database: {e}")
            return False
    
    def create_tables(self):
        """Create all required tables with proper constraints."""
        tables = {}
        
        # Define table schemas
        tables['employees'] = """
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
                INDEX idx_email (email),
                INDEX idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        tables['movies'] = """
            CREATE TABLE IF NOT EXISTS movies (
    movie_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    director VARCHAR(255),
    genre VARCHAR(100),
    release_year INT,  -- remove CURDATE() check
    duration INT CHECK (duration > 0),
    description TEXT,
    rental_rate DECIMAL(5,2) NOT NULL DEFAULT 2.99 CHECK (rental_rate >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    total_copies INT NOT NULL DEFAULT 0 CHECK (total_copies >= 0),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_genre (genre),
    INDEX idx_release_year (release_year),
    INDEX idx_availability (is_available),
    INDEX idx_rental_rate (rental_rate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        """
        
        tables['customers'] = """
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
                INDEX idx_email (email),
                INDEX idx_phone (phone)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        tables['rentals'] = """
            CREATE TABLE IF NOT EXISTS rentals (
                rental_id INT PRIMARY KEY AUTO_INCREMENT,
                customer_id INT NOT NULL,
                movie_id INT NOT NULL,
                employee_id INT NOT NULL,
                rental_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE NOT NULL,
                actual_return_date DATE,
                total_charge DECIMAL(8,2) DEFAULT 0.00 CHECK (total_charge >= 0),
                late_fee DECIMAL(8,2) DEFAULT 0.00 CHECK (late_fee >= 0),
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
                INDEX idx_employee (employee_id),
                INDEX idx_status (rental_status),
                INDEX idx_due_date (due_date),
                INDEX idx_rental_date (rental_date),
                CHECK (due_date >= DATE(rental_date))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        tables['returns'] = """
            CREATE TABLE IF NOT EXISTS returns (
                return_id INT PRIMARY KEY AUTO_INCREMENT,
                rental_id INT NOT NULL,
                return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                late_days INT DEFAULT 0 CHECK (late_days >= 0),
                late_fee DECIMAL(8,2) DEFAULT 0.00 CHECK (late_fee >= 0),
                total_paid DECIMAL(8,2) NOT NULL CHECK (total_paid >= 0),
                processed_by INT NOT NULL,
                FOREIGN KEY (rental_id) REFERENCES rentals(rental_id) 
                    ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (processed_by) REFERENCES employees(employee_id) 
                    ON DELETE RESTRICT ON UPDATE CASCADE,
                INDEX idx_rental (rental_id),
                INDEX idx_return_date (return_date),
                INDEX idx_processed_by (processed_by)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            cursor = self.connection.cursor()
            
            # Create each table
            for table_name, ddl in tables.items():
                try:
                    cursor.execute(ddl)
                    logger.info(f"✅ Table '{table_name}' created successfully")
                except Error as e:
                    if e.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                        logger.info(f"ℹ️  Table '{table_name}' already exists")
                    else:
                        logger.error(f"❌ Failed to create table '{table_name}': {e}")
                        return False
            
            cursor.close()
            logger.info("✅ All tables created/verified successfully")
            return True
            
        except Error as e:
            logger.error(f"❌ Table creation failed: {e}")
            return False
    
    def create_default_admin(self):
        """Create default admin user with hashed password."""
        try:
            cursor = self.connection.cursor()
            
            # Check if admin user already exists
            cursor.execute("SELECT COUNT(*) FROM employees WHERE username = 'admin'")
            if cursor.fetchone()[0] > 0:
                logger.info("ℹ️  Admin user already exists")
                cursor.close()
                return True
            
            # Hash the default password
            default_password = "admin123"
            hashed_password = hash_password(default_password)
            
            # Insert admin user
            cursor.execute("""
                INSERT INTO employees (username, password_hash, first_name, last_name, email, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'admin', 
                hashed_password, 
                'System', 
                'Administrator', 
                'admin@movierental.com', 
                'admin'
            ))
            
            self.connection.commit()
            cursor.close()
            
            logger.info("✅ Default admin user created successfully")
            logger.info(f"📋 Login credentials - Username: admin, Password: {default_password}")
            logger.warning("⚠️  IMPORTANT: Change the default password after first login!")
            
            return True
            
        except Error as e:
            logger.error(f"❌ Failed to create admin user: {e}")
            self.connection.rollback()
            return False
    
    def insert_sample_data(self):
        """Insert sample data for testing."""
        try:
            cursor = self.connection.cursor()
            
            # Insert sample movies
            sample_movies = [
                ('The Shawshank Redemption', 'Frank Darabont', 'Drama', 1994, 142, 'Two imprisoned men bond over a number of years...', 2.99, 5, 5),
                ('The Godfather', 'Francis Ford Coppola', 'Crime', 1972, 175, 'The aging patriarch of an organized crime dynasty...', 3.49, 3, 3),
                ('The Dark Knight', 'Christopher Nolan', 'Action', 2008, 152, 'When the menace known as the Joker wreaks havoc...', 3.99, 4, 4),
                ('Pulp Fiction', 'Quentin Tarantino', 'Crime', 1994, 154, 'The lives of two mob hitmen, a boxer, a gangster...', 2.99, 2, 2),
                ('Forrest Gump', 'Robert Zemeckis', 'Drama', 1994, 142, 'The presidencies of Kennedy and Johnson...', 2.49, 6, 6)
            ]
            
            cursor.executemany("""
                INSERT IGNORE INTO movies (title, director, genre, release_year, duration, description, rental_rate, stock_quantity, total_copies)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, sample_movies)
            
            # Insert sample customers
            sample_customers = [
                ('John', 'Doe', 'john.doe@email.com', '+1234567890', '123 Main St, City, State'),
                ('Jane', 'Smith', 'jane.smith@email.com', '+1234567891', '456 Oak Ave, City, State'),
                ('Bob', 'Johnson', 'bob.johnson@email.com', '+1234567892', '789 Pine Rd, City, State')
            ]
            
            cursor.executemany("""
                INSERT IGNORE INTO customers (first_name, last_name, email, phone, address)
                VALUES (%s, %s, %s, %s, %s)
            """, sample_customers)
            
            self.connection.commit()
            cursor.close()
            
            logger.info("✅ Sample data inserted successfully")
            return True
            
        except Error as e:
            logger.error(f"❌ Failed to insert sample data: {e}")
            self.connection.rollback()
            return False
    
    def setup_database(self):
        """Main method to set up the entire database."""
        logger.info("🚀 Starting database setup...")
        logger.info(f"📊 Target database: {self.database_name}")
        
        try:
            # Step 1: Connect to MySQL
            if not self.connect_to_mysql():
                return False
            
            # Step 2: Create database
            if not self.create_database():
                return False
            
            # Step 3: Create tables
            if not self.create_tables():
                return False
            
            # Step 4: Create admin user
            if not self.create_default_admin():
                return False
            
            # Step 5: Insert sample data (optional)
            if len(sys.argv) > 1 and sys.argv[1] == '--with-sample-data':
                self.insert_sample_data()
            
            logger.info("🎉 Database setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"💥 Database setup failed: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("🔌 Database connection closed")

def main():
    """Main function to run database setup."""
    print("=" * 60)
    print("🎬 Movie Rental Management System - Database Setup")
    print("=" * 60)
    
    setup = DatabaseSetup()
    success = setup.setup_database()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run the main application: python main.py")
        print("2. Login with username: 'admin' and password: 'admin123'")
        print("3. Change the default password immediately!")
    else:
        print("\n❌ Setup failed! Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()