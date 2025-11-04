"""
Database connection handler - manages DB connections throughout the application
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            logger.info("Database connection established")
            return True
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_connection(self):
        """Get database connection, reconnect if necessary"""
        if self.connection is None or not self.connection.is_connected():
            self.connect()
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.lastrowid
            
            cursor.close()
            return result
        except Error as e:
            logger.error(f"Query execution failed: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def execute_many(self, query, params_list):
        """Execute multiple queries"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.executemany(query, params_list)
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Batch execution failed: {e}")
            if self.connection:
                self.connection.rollback()
            raise

# Global database instance
db = DatabaseConnection()