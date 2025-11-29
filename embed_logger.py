import sqlite3
import json
import csv
import os
import logging
from datetime import datetime
from contextlib import contextmanager
from typing import List, Optional
from logging import getLogger
import math

# Configure logging with environment variable control
# Set EMBEDCORE_LOG_LEVEL environment variable to control logging level
# Valid values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
# Default level: "INFO"
log_level_str = os.environ.get('EMBEDCORE_LOG_LEVEL', 'INFO').upper()
log_level_map = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
log_level = log_level_map.get(log_level_str, logging.INFO)  # Default to INFO if invalid

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def _validate_embedding(embedding_data: List[float], user_id: str, session_id: str, platform: str) -> bool:
    """
    Validate embedding data before saving to database.
    
    Performs strict validation to ensure embedding is valid and not an all-zero vector.
    
    Args:
        embedding_data (List[float]): Embedding data to validate
        user_id (str): User identifier for logging
        session_id (str): Session identifier for logging
        platform (str): Platform identifier for logging
        
    Returns:
        bool: True if embedding is valid, False otherwise
    """
    try:
        # Check if embedding is a list
        if not isinstance(embedding_data, list):
            logger.warning(f"Invalid embedding type for user {user_id}: expected list, got {type(embedding_data)}")
            return False
        
        # Check if embedding is empty
        if len(embedding_data) == 0:
            logger.warning(f"Empty embedding for user {user_id}")
            return False
            
        # Standard embedding dimension for sentence transformers
        expected_dimension = 384
        
        # Check dimensionality
        if len(embedding_data) != expected_dimension:
            logger.warning(f"Invalid embedding dimension for user {user_id}: expected {expected_dimension}, got {len(embedding_data)}")
            return False
        
        # Validate each element is a valid float
        for i, val in enumerate(embedding_data):
            # Check for non-numeric values
            if not isinstance(val, (int, float)):
                logger.warning(f"Non-numeric value at index {i} for user {user_id}: {type(val)}")
                return False
                
            # Check for NaN
            if math.isnan(val):
                logger.warning(f"NaN value at index {i} for user {user_id}")
                return False
                
            # Check for infinity
            if math.isinf(val):
                logger.warning(f"Infinite value at index {i} for user {user_id}")
                return False
        
        # Check for all-zero vector
        all_zero = all(abs(val) < 1e-10 for val in embedding_data)
        if all_zero:
            logger.warning(f"All-zero embedding detected for user {user_id}")
            return False
        
        # Check for uniform values (all elements are the same)
        first_val = embedding_data[0]
        uniform = all(abs(val - first_val) < 1e-10 for val in embedding_data)
        if uniform:
            logger.warning(f"Uniform embedding detected for user {user_id} (all values = {first_val})")
            return False
        
        # Check for sufficient variance (at least one value must differ meaningfully)
        mean_val = sum(embedding_data) / len(embedding_data)
        variance = sum((val - mean_val) ** 2 for val in embedding_data) / len(embedding_data)
        std_dev = variance ** 0.5
        
        if std_dev < 1e-6:
            logger.warning(f"Low variance embedding detected for user {user_id} (std dev = {std_dev})")
            return False
        
        # If we reach here, the embedding is valid
        logger.debug(f"Embedding validation passed for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error during embedding validation for user {user_id}: {e}")
        return False


def save_embedding(user_id: str, session_id: str, embedding_data: List[float], platform: str = "EmbedCore_v3", db_path: str = "assistant_core.db") -> bool:
    """
    Save embedding data to the SQLite database.
    
    This function writes embedding data to the assistant_core.db SQLite database
    in the embeddings table with full error handling and validation.
    
    Args:
        user_id (str): Unique identifier for the user
        session_id (str): Session identifier
        embedding_data (List[float]): Obfuscated embedding data
        platform (str): Platform identifier (default: "EmbedCore_v3")
        db_path (str): Path to the database file (default: "assistant_core.db")
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        TypeError: If inputs are not of expected types
        ValueError: If required fields are empty
    """
    # Input validation
    if not isinstance(user_id, str):
        raise TypeError("user_id must be a string")
    if not isinstance(session_id, str):
        raise TypeError("session_id must be a string")
    if not isinstance(embedding_data, list):
        raise TypeError("embedding_data must be a list")
    if not isinstance(platform, str):
        raise TypeError("platform must be a string")
    if not user_id:
        raise ValueError("user_id cannot be empty")
    if not session_id:
        raise ValueError("session_id cannot be empty")
    if not platform:
        raise ValueError("platform cannot be empty")
    
    # Validate embedding data
    for i, val in enumerate(embedding_data):
        if not isinstance(val, (int, float)):
            raise TypeError(f"embedding_data[{i}] must be numeric, got {type(val)}")
    
    # Perform strict embedding validation
    if not _validate_embedding(embedding_data, user_id, session_id, platform):
        logger.warning(f"Embedding validation failed for user {user_id}, session {session_id}, platform {platform}")
        return False
    
    try:
        # Convert embedding to JSON string
        embedding_json = json.dumps(embedding_data)
        
        # Get current timestamp in ISO 8601 format
        timestamp = datetime.now().isoformat()
        
        # Insert into database using context manager
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Try to create table with required schema
            try:
                cursor.execute('''
                    CREATE TABLE embeddings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        obfuscated_embedding TEXT NOT NULL
                    )
                ''')
                conn.commit()
                logger.info("Created embeddings table with required schema")
            except sqlite3.OperationalError as e:
                # Table might already exist, check if it has the right schema
                cursor.execute("PRAGMA table_info(embeddings)")
                columns = [col[1] for col in cursor.fetchall()]
                
                required_columns = ['id', 'user_id', 'session_id', 'timestamp', 'platform', 'obfuscated_embedding']
                if not all(col in columns for col in required_columns):
                    # If the schema is wrong, we need to recreate the table
                    logger.info("Recreating embeddings table with required schema")
                    cursor.execute("DROP TABLE IF EXISTS embeddings")
                    cursor.execute('''
                        CREATE TABLE embeddings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT NOT NULL,
                            session_id TEXT NOT NULL,
                            timestamp TEXT NOT NULL,
                            platform TEXT NOT NULL,
                            obfuscated_embedding TEXT NOT NULL
                        )
                    ''')
                conn.commit()
            
            # Insert data (using required schema)
            cursor.execute('''
                INSERT INTO embeddings (user_id, session_id, timestamp, platform, obfuscated_embedding)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_id, timestamp, platform, embedding_json))
            
            conn.commit()
            logger.info(f"Successfully saved embedding for user {user_id}, session {session_id}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to save embedding to database: {e}")
        return False


@contextmanager
def _get_db_connection(db_path: str):
    """
    Context manager for database connections.
    
    Args:
        db_path (str): Path to the database file
        
    Yields:
        sqlite3.Connection: Database connection object
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def log_to_db(user_id: str, session_id: str, platform: str, obf_embedding: List[float]) -> bool:
    """
    Log embedding data to the database.
    
    This is a wrapper function that calls save_embedding with proper error handling.
    
    Args:
        user_id (str): Unique identifier for the user
        session_id (str): Session identifier
        platform (str): Platform identifier
        obf_embedding (List[float]): Obfuscated embedding data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        success = save_embedding(user_id, session_id, obf_embedding, platform)
        if success:
            logger.info(f"Database logging successful for user {user_id}")
        else:
            logger.warning(f"Database logging failed for user {user_id}")
        return success
    except Exception as e:
        logger.error(f"Error in database logging for user {user_id}: {e}")
        return False


def log_to_csv(user_id: str, session_id: str, platform: str, obf_embedding: List[float]) -> bool:
    """
    Log embedding data to a CSV file.
    
    This function appends embedding data to embedding_log.csv with full error handling.
    
    Args:
        user_id (str): Unique identifier for the user
        session_id (str): Session identifier
        platform (str): Platform identifier
        obf_embedding (List[float]): Obfuscated embedding data
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Perform strict embedding validation for CSV logging as well
    if not _validate_embedding(obf_embedding, user_id, session_id, platform):
        logger.warning(f"Embedding validation failed for CSV logging for user {user_id}")
        return False
        
    try:
        # Convert embedding to JSON string
        embedding_json = json.dumps(obf_embedding)
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Define CSV file path
        csv_path = "embedding_log.csv"
        
        # Write to CSV file
        file_exists = os.path.isfile(csv_path)
        
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header if file is new
            if not file_exists:
                writer.writerow(['timestamp', 'user_id', 'session_id', 'platform', 'obfuscated_embedding'])
            
            # Write data row
            writer.writerow([timestamp, user_id, session_id, platform, embedding_json])
        
        logger.info(f"Successfully logged to CSV for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to log to CSV for user {user_id}: {e}")
        return False


def log_embedding(user_id: str, session_id: str, platform: str, obf_embedding: List[float]) -> dict:
    """
    Unified wrapper for logging embedding data to both database and CSV.
    
    This function ensures that errors in either logging mechanism don't break
    the main system by catching all exceptions and continuing execution.
    
    Args:
        user_id (str): Unique identifier for the user
        session_id (str): Session identifier
        platform (str): Platform identifier
        obf_embedding (List[float]): Obfuscated embedding data
        
    Returns:
        dict: Status dictionary with success/failure information for each logging method
    """
    # Perform strict embedding validation before proceeding
    if not _validate_embedding(obf_embedding, user_id, session_id, platform):
        logger.warning(f"Embedding validation failed for unified logging for user {user_id}")
        return {
            'db_success': False,
            'csv_success': False,
            'overall_success': False
        }
    
    # Initialize status dictionary
    status = {
        'db_success': False,
        'csv_success': False,
        'overall_success': False
    }
    
    try:
        # Log to database
        status['db_success'] = log_to_db(user_id, session_id, platform, obf_embedding)
        
        # Log to CSV
        status['csv_success'] = log_to_csv(user_id, session_id, platform, obf_embedding)
        
        # Overall success if at least one logging method succeeded
        status['overall_success'] = status['db_success'] or status['csv_success']
        
        if status['overall_success']:
            logger.info(f"Embedding logging completed for user {user_id}")
        else:
            logger.warning(f"Both logging methods failed for user {user_id}")
            
    except Exception as e:
        logger.error(f"Unexpected error in unified logging for user {user_id}: {e}")
        # Even if we get an unexpected error, we still return the status
        status['overall_success'] = status['db_success'] or status['csv_success']
    
    return status