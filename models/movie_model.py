"""
Movie Management Model
Handles CRUD operations for movies with business logic constraints.
"""

import mysql.connector
from mysql.connector import Error
from config import get_db_config
import logging

logger = logging.getLogger(__name__)

class MovieModel:
    """Handles all movie-related database operations."""
    
    def __init__(self):
        self.db_config = get_db_config()
    
    def _get_connection(self):
        """Get database connection."""
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def add_movie(self, title, director, genre, release_year, duration, description, 
                  rental_rate, total_copies):
        """
        Add a new movie to the database.
        
        Args:
            title (str): Movie title
            director (str): Movie director
            genre (str): Movie genre
            release_year (int): Release year
            duration (int): Duration in minutes
            description (str): Movie description
            rental_rate (float): Daily rental rate
            total_copies (int): Total copies available
            
        Returns:
            tuple: (success: bool, message: str, movie_id: int)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Check if movie with same title and director already exists
            cursor.execute(
                "SELECT movie_id FROM movies WHERE title = %s AND director = %s",
                (title, director)
            )
            if cursor.fetchone():
                return False, "Movie with same title and director already exists", None
            
            # Insert new movie
            cursor.execute("""
                INSERT INTO movies (title, director, genre, release_year, duration, 
                                  description, rental_rate, stock_quantity, total_copies)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, director, genre, release_year, duration, description, 
                  rental_rate, total_copies, total_copies))
            
            movie_id = cursor.lastrowid
            connection.commit()
            
            logger.info(f"Movie added successfully: {title} (ID: {movie_id})")
            return True, "Movie added successfully", movie_id
            
        except Error as e:
            connection.rollback()
            logger.error(f"Add movie failed: {e}")
            return False, f"Failed to add movie: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def update_movie(self, movie_id, **kwargs):
        """
        Update movie details.
        
        Args:
            movie_id (int): Movie ID to update
            **kwargs: Fields to update (title, director, genre, release_year, duration, 
                     description, rental_rate, total_copies)
        
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
            
            # Build dynamic update query
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(movie_id)
            
            query = f"UPDATE movies SET {set_clause} WHERE movie_id = %s"
            
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                return False, "Movie not found"
            
            connection.commit()
            logger.info(f"Movie updated successfully: ID {movie_id}")
            return True, "Movie updated successfully"
            
        except Error as e:
            connection.rollback()
            logger.error(f"Update movie failed: {e}")
            return False, f"Failed to update movie: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def delete_movie(self, movie_id):
        """
        Delete a movie if it's not currently rented.
        
        Args:
            movie_id (int): Movie ID to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed"
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Check if movie has active rentals
            cursor.execute("""
                SELECT COUNT(*) FROM rentals 
                WHERE movie_id = %s AND rental_status IN ('active', 'overdue')
            """, (movie_id,))
            
            active_rentals = cursor.fetchone()[0]
            
            if active_rentals > 0:
                return False, f"Cannot delete movie. It has {active_rentals} active rental(s)."
            
            # Delete movie
            cursor.execute("DELETE FROM movies WHERE movie_id = %s", (movie_id,))
            
            if cursor.rowcount == 0:
                return False, "Movie not found"
            
            connection.commit()
            logger.info(f"Movie deleted successfully: ID {movie_id}")
            return True, "Movie deleted successfully"
            
        except Error as e:
            connection.rollback()
            logger.error(f"Delete movie failed: {e}")
            return False, f"Failed to delete movie: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def get_movie_by_id(self, movie_id):
        """
        Get movie details by ID.
        
        Args:
            movie_id (int): Movie ID
            
        Returns:
            tuple: (success: bool, message: str, movie_data: dict)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed", None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM movies WHERE movie_id = %s", (movie_id,))
            movie = cursor.fetchone()
            
            if not movie:
                return False, "Movie not found", None
            
            return True, "Movie found", movie
            
        except Error as e:
            logger.error(f"Get movie failed: {e}")
            return False, f"Operation failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def search_movies(self, title=None, genre=None, director=None, release_year=None, 
                     min_price=None, max_price=None, available_only=False):
        """
        Search movies with various filters.
        
        Args:
            title (str): Partial title match
            genre (str): Exact genre match
            director (str): Partial director match
            release_year (int): Exact release year
            min_price (float): Minimum rental rate
            max_price (float): Maximum rental rate
            available_only (bool): Only show available movies
            
        Returns:
            tuple: (success: bool, message: str, movies: list)
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
            
            if title:
                conditions.append("title LIKE %s")
                params.append(f"%{title}%")
            
            if genre:
                conditions.append("genre = %s")
                params.append(genre)
            
            if director:
                conditions.append("director LIKE %s")
                params.append(f"%{director}%")
            
            if release_year:
                conditions.append("release_year = %s")
                params.append(release_year)
            
            if min_price is not None:
                conditions.append("rental_rate >= %s")
                params.append(min_price)
            
            if max_price is not None:
                conditions.append("rental_rate <= %s")
                params.append(max_price)
            
            if available_only:
                conditions.append("is_available = TRUE AND stock_quantity > 0")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT movie_id, title, director, genre, release_year, duration,
                       description, rental_rate, stock_quantity, total_copies, 
                       is_available, created_at
                FROM movies 
                WHERE {where_clause}
                ORDER BY title
            """
            
            cursor.execute(query, params)
            movies = cursor.fetchall()
            
            return True, f"Found {len(movies)} movies", movies
            
        except Error as e:
            logger.error(f"Search movies failed: {e}")
            return False, f"Search failed: {str(e)}", None
        finally:
            if cursor:
                cursor.close()
            connection.close()
    
    def get_all_movies(self):
        """
        Get all movies.
        
        Returns:
            tuple: (success: bool, message: str, movies: list)
        """
        return self.search_movies()
    
    def update_stock_quantity(self, movie_id, new_quantity):
        """
        Update movie stock quantity and availability.
        
        Args:
            movie_id (int): Movie ID
            new_quantity (int): New stock quantity
            
        Returns:
            tuple: (success: bool, message: str)
        """
        connection = self._get_connection()
        if not connection:
            return False, "Database connection failed"
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE movies 
                SET stock_quantity = %s, 
                    is_available = CASE WHEN %s > 0 THEN TRUE ELSE FALSE END
                WHERE movie_id = %s
            """, (new_quantity, new_quantity, movie_id))
            
            if cursor.rowcount == 0:
                return False, "Movie not found"
            
            connection.commit()
            return True, "Stock quantity updated successfully"
            
        except Error as e:
            connection.rollback()
            logger.error(f"Update stock quantity failed: {e}")
            return False, f"Failed to update stock: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            connection.close()