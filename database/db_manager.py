"""
Database manager module for handling MySQL operations.
Provides methods for CRUD operations on anode tracking data.
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

import mysql.connector
from mysql.connector import Error, pooling

from config import DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations for anode tracking."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database manager with configuration.
        
        Args:
            config: Database configuration object
        """
        self.config = config
        self._connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Initialize connection pool for better performance."""
        try:
            self._connection_pool = pooling.MySQLConnectionPool(
                pool_name="anode_pool",
                pool_size=5,
                **self.config.connection_params
            )
            logger.info("Database connection pool initialized successfully")
        except Error as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def _get_connection(self):
        """Get a connection from the pool."""
        try:
            return self._connection_pool.get_connection()
        except Error as e:
            logger.error(f"Failed to get connection from pool: {e}")
            raise
    
    def check_anode_exists_today(
        self, pot_number: str, date_entry: str
    ) -> Optional[Tuple]:
        """Check if an anode entry exists for today.
        
        Args:
            pot_number: The anode/pot number to check
            date_entry: The date to check against
            
        Returns:
            Tuple of existing record if found, None otherwise
        """
        query = """
            SELECT * FROM stem_analysis 
            WHERE pot_number = %s AND date_entry = %s
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (pot_number, date_entry))
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error checking anode existence: {e}")
            raise
    
    def insert_anode_entry(
        self, pot_number: str, date_entry: str, time_in: str
    ) -> bool:
        """Insert a new anode entry record.
        
        Args:
            pot_number: The anode/pot number
            date_entry: Entry date (YYYY-MM-DD)
            time_in: Entry time (HH:MM:SS)
            
        Returns:
            True if insertion successful, False otherwise
        """
        query = """
            INSERT INTO stem_analysis (date_entry, time_in, pot_number) 
            VALUES (%s, %s, %s)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (date_entry, time_in, pot_number))
                conn.commit()
                logger.info(f"Inserted new anode entry: {pot_number}")
                return True
        except Error as e:
            logger.error(f"Error inserting anode entry: {e}")
            return False
    
    def update_anode_exit(
        self, pot_number: str, date_entry: str, date_out: str, time_out: str
    ) -> bool:
        """Update an existing anode entry with exit information.
        
        Args:
            pot_number: The anode/pot number
            date_entry: Original entry date
            date_out: Exit date (YYYY-MM-DD)
            time_out: Exit time (HH:MM:SS)
            
        Returns:
            True if update successful, False otherwise
        """
        query = """
            UPDATE stem_analysis 
            SET date_out = %s, time_out = %s 
            WHERE pot_number = %s AND date_entry = %s
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (date_out, time_out, pot_number, date_entry))
                conn.commit()
                logger.info(f"Updated anode exit: {pot_number}")
                return True
        except Error as e:
            logger.error(f"Error updating anode exit: {e}")
            return False
    
    def get_all_records(self) -> List[Tuple]:
        """Retrieve all anode tracking records.
        
        Returns:
            List of tuples containing all records
        """
        query = """
            SELECT pot_number, date_entry, time_in, date_out, time_out 
            FROM stem_analysis 
            ORDER BY date_entry DESC, time_in DESC
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Error retrieving records: {e}")
            raise
    
    def save_or_update_anode(self, pot_number: str) -> Tuple[bool, str]:
        """Save new anode entry or update existing entry with exit time.
        
        Args:
            pot_number: The anode/pot number to save/update
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not pot_number:
            return False, "No anode number provided"
        
        current_datetime = datetime.now()
        current_date = current_datetime.strftime("%Y-%m-%d")
        current_time = current_datetime.strftime("%H:%M:%S")
        
        try:
            existing = self.check_anode_exists_today(pot_number, current_date)
            
            if existing:
                success = self.update_anode_exit(
                    pot_number, current_date, current_date, current_time
                )
                if success:
                    return True, "Existing Anode entry updated with Date Out and Time Out."
                return False, "Failed to update anode entry"
            else:
                success = self.insert_anode_entry(
                    pot_number, current_date, current_time
                )
                if success:
                    return True, "Anode saved to the database"
                return False, "Failed to save anode entry"
                
        except Error as e:
            return False, f"Database error: {e}"
    
    def close(self) -> None:
        """Close all database connections."""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Database connection pool closed")