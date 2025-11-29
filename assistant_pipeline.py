"""
Assistant Pipeline Module

High-level entrypoint for all embedding operations in the EmbedCore system.
This module orchestrates the complete pipeline from message input to secure storage.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import required modules
from embedcore_v3 import generate_embedding, obfuscate, deobfuscate
from keystore import KeyStore
from embed_logger import save_embedding, log_to_csv

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


def process_message(user_id: str, session_id: str, platform: str, message_text: str) -> Dict[str, Any]:
    """
    Process a message through the complete embedding pipeline.
    
    This function orchestrates the full pipeline:
    1. Generate deterministic embedding from message text
    2. Fetch or create user-specific encryption key
    3. Obfuscate embedding with user key
    4. Save to database and CSV
    
    Args:
        user_id (str): Unique identifier for the user
        session_id (str): Session identifier
        platform (str): Platform identifier (e.g., "whatsapp", "web", "mobile")
        message_text (str): The text message to process
        
    Returns:
        Dict[str, Any]: Structured response containing:
            - status: "success" or "error"
            - embedding: Original embedding vector
            - obfuscated_embedding: Obfuscated embedding vector
            - user_id: User identifier
            - session_id: Session identifier
            - platform: Platform identifier
            - timestamp: ISO 8601 formatted timestamp
            
    Raises:
        TypeError: If inputs are not of expected types
        ValueError: If required fields are empty
        Exception: For any other processing errors
    """
    # Input validation
    if not isinstance(user_id, str):
        raise TypeError("user_id must be a string")
    if not isinstance(session_id, str):
        raise TypeError("session_id must be a string")
    if not isinstance(platform, str):
        raise TypeError("platform must be a string")
    if not isinstance(message_text, str):
        raise TypeError("message_text must be a string")
    if not user_id:
        raise ValueError("user_id cannot be empty")
    if not session_id:
        raise ValueError("session_id cannot be empty")
    if not platform:
        raise ValueError("platform cannot be empty")
    
    try:
        logger.info(f"Processing message for user {user_id}, session {session_id}")
        
        # Step 1: Generate deterministic embedding
        embedding = generate_embedding(message_text)
        logger.debug(f"Generated embedding with {len(embedding)} dimensions")
        
        # Step 2: Fetch or create user-specific encryption key
        keystore = KeyStore()
        user_key_bytes = keystore.get_key(user_id)
        
        # If no key exists, generate one
        if user_key_bytes is None:
            logger.info(f"No existing key found for user {user_id}, generating new key")
            user_key_bytes = keystore.generate_key(user_id)
        
        # Decode key for use in obfuscation
        user_key = user_key_bytes.decode()
        logger.debug("Retrieved user key for obfuscation")
        
        # Step 3: Obfuscate embedding with user key
        obfuscated_embedding = obfuscate(embedding, user_key)
        logger.debug("Obfuscated embedding with user key")
        
        # Step 4: Save to database
        db_success = save_embedding(user_id, session_id, obfuscated_embedding, platform)
        if not db_success:
            logger.warning(f"Failed to save embedding to database for user {user_id}")
        
        # Step 5: Save to CSV
        csv_success = log_to_csv(user_id, session_id, platform, obfuscated_embedding)
        if not csv_success:
            logger.warning(f"Failed to save embedding to CSV for user {user_id}")
        
        # Step 6: Create response
        timestamp = datetime.now().isoformat()
        
        response = {
            "status": "success",
            "embedding": embedding,
            "obfuscated_embedding": obfuscated_embedding,
            "user_id": user_id,
            "session_id": session_id,
            "platform": platform,
            "timestamp": timestamp
        }
        
        logger.info(f"Successfully processed message for user {user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing message for user {user_id}: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "user_id": user_id,
            "session_id": session_id,
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        }


# Example usage (commented out)
if __name__ == "__main__":
    # Example of how to use the pipeline
    # result = process_message("user123", "session456", "web", "Hello, this is a test message!")
    # print(result)
    pass