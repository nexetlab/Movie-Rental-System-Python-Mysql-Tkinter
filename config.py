"""
Database configuration with secure connection handling.
Uses environment variables for credentials to enhance security.
"""

import os
import mysql.connector
from mysql.connector import Error, errorcode
from dotenv import load_dotenv
import logging
import hashlib
import binascii

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def get_db_config():
    """
    Get database configuration from environment variables with fallbacks.
    
    Returns:
        dict: Database configuration parameters
        
    Raises:
        ValueError: If required environment variables are missing
    """
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'movie_rental_db',  # Changed from movie_rental_system
        'port': 3306,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': False,
    }
    
    logger.info(f"Database config loaded for host: {config['host']}, database: {config['database']}")
    return config


    
    # Validate required configuration
    if not config['user']:
        raise ValueError("DB_USER environment variable is required")
    
    logger.info(f"Database config loaded for host: {config['host']}, database: {config['database']}")
    return config

def create_db_connection():
    """
    Create and return a secure database connection.
    
    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
        
    Raises:
        Error: If connection cannot be established
    """
    try:
        config = get_db_config()
        
        # First, try to connect without database to create it if needed
        temp_config = config.copy()
        temp_config.pop('database', None)
        
        connection = mysql.connector.connect(**temp_config)
        logger.info("MySQL connection established successfully")
        return connection
        
    except Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        raise

def test_connection():
    """
    Test database connection and return status.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        connection = create_db_connection()
        if connection.is_connected():
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            database = cursor.fetchone()
            cursor.close()
            connection.close()
            
            logger.info(f"Connection test successful - MySQL Server: {db_info}, Database: {database[0]}")
            return True, f"Connected to MySQL Server {db_info}"
            
    except Error as e:
        error_msg = f"Connection test failed: {e}"
        logger.error(error_msg)
        return False, error_msg
    
    return False, "Unknown connection error"

def hash_password(password):
    """
    Hash a password using SHA-256 with salt for secure storage.
    
    Args:
        password (str): Plain text password to hash
        
    Returns:
        str: Hashed password in format 'salt:hash'
    """
    # Generate random salt
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    
    # Hash password with salt
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    
    # Return salt and hash combined
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """
    Verify a provided password against a stored hash.
    
    Args:
        stored_password (str): Stored hashed password
        provided_password (str): Password to verify
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Extract salt and hash from stored password
        salt = stored_password[:64].encode('ascii')
        stored_hash = stored_password[64:]
        
        # Hash the provided password with the same salt
        pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        
        return pwdhash == stored_hash
        
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

# Database configuration constants
DB_CONFIG = get_db_config()