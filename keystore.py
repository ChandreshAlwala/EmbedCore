"""
Encrypted KeyStore for Secure User Key Management

This module provides functions for securely storing, retrieving, and rotating
user encryption keys using Fernet symmetric encryption.
"""

import os
import json
import sqlite3
import logging
from cryptography.fernet import Fernet
from typing import Optional
import hashlib
import base64
from contextlib import contextmanager


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


class KeyStore:
    """Secure key storage using Fernet encryption."""
    
    def __init__(self, db_path: str = "keystore.db", master_key: Optional[bytes] = None):
        """
        Initialize the KeyStore.
        
        Args:
            db_path (str): Path to the key store database
            master_key (bytes, optional): Master key for encryption. If None, will be generated or loaded.
        """
        self.db_path = db_path
        self._initialize_database()
        
        if master_key is None:
            self.master_key = self._get_or_create_master_key()
        else:
            self.master_key = master_key
            
        self.fernet = Fernet(self.master_key)
        logger.info(f"KeyStore initialized with database: {db_path}")
    
    def _initialize_database(self):
        """Initialize the key store database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create table for storing encrypted user keys
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_keys (
                        user_id TEXT PRIMARY KEY,
                        encrypted_key BLOB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create table for storing the master key (in practice, this should be more secure)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS master_key (
                        id INTEGER PRIMARY KEY,
                        key_data BLOB NOT NULL
                    )
                ''')
                
                conn.commit()
                logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _get_or_create_master_key(self) -> bytes:
        """
        Get existing master key or create a new one.
        
        Returns:
            bytes: The master key for encryption
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Try to get existing master key
                cursor.execute("SELECT key_data FROM master_key WHERE id = 1")
                result = cursor.fetchone()
                
                if result:
                    # Master key exists
                    master_key = result[0]
                    logger.info("Existing master key loaded")
                else:
                    # Create new master key
                    master_key = Fernet.generate_key()
                    cursor.execute(
                        "INSERT INTO master_key (id, key_data) VALUES (?, ?)",
                        (1, master_key)
                    )
                    conn.commit()
                    logger.info("New master key generated and stored")
                
                return master_key
        except Exception as e:
            logger.error(f"Failed to get or create master key: {e}")
            raise
    
    def _derive_key_from_password(self, password: str) -> bytes:
        """
        Derive a Fernet-compatible key from a password.
        
        Args:
            password (str): Password to derive key from
            
        Returns:
            bytes: 32-byte key suitable for Fernet
        """
        # Use SHA-256 to derive a 32-byte key
        key = hashlib.sha256(password.encode()).digest()
        # Base64 encode to make it URL-safe (Fernet requirement)
        return base64.urlsafe_b64encode(key)
    
    def generate_key(self, user_id: str) -> bytes:
        """
        Generate a new random key for a user and store it encrypted.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            bytes: The generated user key
            
        Raises:
            ValueError: If user_id is empty or None
            Exception: If database operation fails
        """
        if not user_id:
            raise ValueError("user_id cannot be empty or None")
            
        try:
            # Generate a new random key for the user
            user_key = Fernet.generate_key()
            
            # Encrypt the user key with our master key
            encrypted_key = self.fernet.encrypt(user_key)
            
            # Store in database
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_keys 
                    (user_id, encrypted_key, updated_at) 
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, encrypted_key))
                
                conn.commit()
                logger.info(f"Generated and stored key for user: {user_id}")
            
            return user_key
        except Exception as e:
            logger.error(f"Failed to generate key for user {user_id}: {e}")
            raise
    
    def get_key(self, user_id: str) -> Optional[bytes]:
        """
        Retrieve and decrypt a user's key.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            bytes: The decrypted user key, or None if not found
            
        Raises:
            ValueError: If user_id is empty or None
            Exception: If decryption fails or database operation fails
        """
        if not user_id:
            raise ValueError("user_id cannot be empty or None")
            
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT encrypted_key FROM user_keys WHERE user_id = ?", 
                    (user_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"No key found for user: {user_id}")
                    return None
                    
                encrypted_key = result[0]
                
                try:
                    # Decrypt the user key with our master key
                    user_key = self.fernet.decrypt(encrypted_key)
                    logger.info(f"Retrieved key for user: {user_id}")
                    return user_key
                except Exception as decrypt_error:
                    logger.error(f"Failed to decrypt key for user {user_id}: {decrypt_error}")
                    # Decryption failed
                    return None
        except Exception as e:
            logger.error(f"Failed to retrieve key for user {user_id}: {e}")
            raise
    
    def rotate_key(self, user_id: str) -> Optional[bytes]:
        """
        Rotate a user's key by generating a new one.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            bytes: The new user key, or None if user not found
            
        Raises:
            ValueError: If user_id is empty or None
            Exception: If key generation or database operation fails
        """
        if not user_id:
            raise ValueError("user_id cannot be empty or None")
            
        try:
            # Generate a new key (this also stores it)
            new_key = self.generate_key(user_id)
            logger.info(f"Rotated key for user: {user_id}")
            return new_key
        except Exception as e:
            logger.error(f"Failed to rotate key for user {user_id}: {e}")
            raise


# Global instance for convenience
keystore = KeyStore()


# Convenience functions that match the specification
def generate_key(user_id: str) -> bytes:
    """
    Generate a new random key for a user and store it encrypted.
    
    Args:
        user_id (str): Unique identifier for the user
        
    Returns:
        bytes: The generated user key
        
    Raises:
        ValueError: If user_id is empty or None
        Exception: If key generation fails
    """
    return keystore.generate_key(user_id)


def get_key(user_id: str) -> Optional[bytes]:
    """
    Retrieve and decrypt a user's key.
    
    Args:
        user_id (str): Unique identifier for the user
        
    Returns:
        bytes: The decrypted user key, or None if not found
        
    Raises:
        ValueError: If user_id is empty or None
        Exception: If key retrieval fails
    """
    return keystore.get_key(user_id)


def rotate_key(user_id: str) -> Optional[bytes]:
    """
    Rotate a user's key by generating a new one.
    
    Args:
        user_id (str): Unique identifier for the user
        
    Returns:
        bytes: The new user key, or None if user not found
        
    Raises:
        ValueError: If user_id is empty or None
        Exception: If key rotation fails
    """
    return keystore.rotate_key(user_id)


# Test functions
def test_keystore():
    """Test the keystore functionality."""
    print("Testing keystore...")
    
    # Create a test keystore instance with a temporary database
    test_db_path = "test_keystore.db"
    test_keystore = KeyStore(test_db_path)  # Regular database for testing
    
    user_id = "test_user_123"
    
    # Test key generation
    key1 = test_keystore.generate_key(user_id)
    assert key1 is not None, "Failed to generate key"
    print("✓ Key generation works")
    
    # Test key retrieval
    retrieved_key = test_keystore.get_key(user_id)
    assert retrieved_key == key1, "Retrieved key doesn't match generated key"
    print("✓ Key retrieval works")
    
    # Test key rotation
    new_key = test_keystore.rotate_key(user_id)
    assert new_key is not None, "Failed to rotate key"
    assert new_key != key1, "New key should be different from old key"
    
    # Verify new key is stored
    latest_key = test_keystore.get_key(user_id)
    assert latest_key == new_key, "Latest key doesn't match rotated key"
    print("✓ Key rotation works")
    
    # Clean up test database
    os.remove(test_db_path)
    
    print("All keystore tests passed!")


if __name__ == "__main__":
    test_keystore()