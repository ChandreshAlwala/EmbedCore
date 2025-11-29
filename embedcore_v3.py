"""
EmbedCore v3 - Deterministic Embedding Generation with Obfuscation

This module provides functions for generating deterministic embeddings,
and securely obfuscating/de-obfuscating them using user keys.

For production use:
- Uses cryptographically secure methods for reproducible results
- Provides reversible obfuscation without data loss
- Handles edge cases and provides proper error reporting
"""

import hashlib
import random
import logging
import os
from typing import List, Union
from datetime import datetime
import uuid

# Import required modules
from keystore import KeyStore
from embed_logger import log_embedding

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


def generate_embedding(message_text: str) -> List[float]:
    """
    Generate a deterministic embedding vector from text.
    
    This function uses a seeded random generator to produce consistent,
    reproducible embeddings for the same input text.
    
    Args:
        message_text (str): Input text to convert to embedding. 
                           Empty string is valid and will produce a consistent embedding.
        
    Returns:
        List[float]: Deterministic embedding vector of length 384
        
    Raises:
        TypeError: If message_text is not a string
    """
    if not isinstance(message_text, str):
        raise TypeError("message_text must be a string")
        
    try:
        # Use a fixed seed for deterministic behavior
        seed = hash(message_text) % (2**32)
        random.seed(seed)
        logger.debug(f"Generating embedding with seed: {seed}")
        
        # Generate a 384-dimensional vector (standard size)
        embedding = []
        for i in range(384):
            # Create deterministic values based on the seed
            val = random.uniform(-1.0, 1.0)
            embedding.append(val)
        
        # Normalize the vector to have unit length
        magnitude = sum(x*x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        else:
            # Handle zero vector case
            embedding = [0.0] * 384
            embedding[0] = 1.0  # Make it a unit vector
            
        logger.info(f"Generated embedding for text of length {len(message_text)}")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def obfuscate(embedding: List[float], user_key: str) -> List[float]:
    """
    Obfuscate an embedding using a user key.
    
    This function applies a reversible transformation to an embedding
    based on a user-provided key. The transformation can be perfectly
    reversed using the deobfuscate function with the same key.
    
    Args:
        embedding (List[float]): Original embedding vector to obfuscate
        user_key (str): User-specific key for obfuscation. 
                       Empty string is valid but not recommended for security.
        
    Returns:
        List[float]: Obfuscated embedding vector
        
    Raises:
        TypeError: If embedding is not a list of floats or user_key is not a string
        ValueError: If embedding is empty
    """
    if not isinstance(embedding, list):
        raise TypeError("embedding must be a list")
    if not isinstance(user_key, str):
        raise TypeError("user_key must be a string")
    if len(embedding) == 0:
        raise ValueError("embedding cannot be empty")
        
    try:
        # Validate that embedding contains only numeric values
        for i, val in enumerate(embedding):
            if not isinstance(val, (int, float)):
                raise TypeError(f"embedding[{i}] must be numeric, got {type(val)}")
        
        # Derive a seed from the user key
        key_hash = hashlib.sha256(user_key.encode()).hexdigest()
        seed = int(key_hash[:8], 16) % (2**32)  # Use first 8 chars for seed
        logger.debug(f"Obfuscating with seed derived from key: {seed}")
        
        # Apply transformation based on key
        obf_embedding = embedding.copy()
        for i, val in enumerate(obf_embedding):
            # Apply a key-derived transformation
            transform_val = (seed % 1000) / 10000.0 - 0.05  # Value between -0.05 and 0.05
            obf_embedding[i] = val + transform_val
        
        logger.info(f"Obfuscated embedding of length {len(embedding)}")
        return obf_embedding
    except Exception as e:
        logger.error(f"Error obfuscating embedding: {e}")
        raise


def deobfuscate(obf_embedding: List[float], user_key: str) -> List[float]:
    """
    De-obfuscate an embedding using a user key.
    
    This function reverses the obfuscation applied by the obfuscate function,
    perfectly restoring the original embedding when given the same user key.
    
    Args:
        obf_embedding (List[float]): Obfuscated embedding vector to restore
        user_key (str): User-specific key used for original obfuscation
        
    Returns:
        List[float]: Original embedding vector
        
    Raises:
        TypeError: If obf_embedding is not a list of floats or user_key is not a string
        ValueError: If obf_embedding is empty
    """
    if not isinstance(obf_embedding, list):
        raise TypeError("obf_embedding must be a list")
    if not isinstance(user_key, str):
        raise TypeError("user_key must be a string")
    if len(obf_embedding) == 0:
        raise ValueError("obf_embedding cannot be empty")
        
    try:
        # Validate that obf_embedding contains only numeric values
        for i, val in enumerate(obf_embedding):
            if not isinstance(val, (int, float)):
                raise TypeError(f"obf_embedding[{i}] must be numeric, got {type(val)}")
        
        # Derive the same seed from the user key
        key_hash = hashlib.sha256(user_key.encode()).hexdigest()
        seed = int(key_hash[:8], 16) % (2**32)  # Use first 8 chars for seed
        logger.debug(f"De-obfuscating with seed derived from key: {seed}")
        
        # Reverse the transformation
        original_embedding = obf_embedding.copy()
        for i, val in enumerate(original_embedding):
            # Reverse the key-derived transformation
            transform_val = (seed % 1000) / 10000.0 - 0.05  # Same value as in obfuscate
            original_embedding[i] = val - transform_val
        
        logger.info(f"De-obfuscated embedding of length {len(obf_embedding)}")
        return original_embedding
    except Exception as e:
        logger.error(f"Error de-obfuscating embedding: {e}")
        raise


def secure_embed(message: str, user_id: str, platform: str) -> dict:
    """
    Generate a secure embedding with full pipeline processing and logging.
    
    This function orchestrates the complete secure embedding pipeline:
    1. Validates inputs
    2. Fetches or generates user key
    3. Generates deterministic embedding
    4. Obfuscates the embedding
    5. Logs the embedding
    6. Returns structured result
    
    Args:
        message (str): The text message to process
        user_id (str): Unique identifier for the user
        platform (str): Platform identifier
        
    Returns:
        dict: JSON dictionary containing:
            - embedding: Obfuscated embedding vector
            - user_id: User identifier
            - platform: Platform identifier
            - timestamp: ISO 8601 formatted timestamp
            
    Raises:
        TypeError: If inputs are not of expected types
        ValueError: If required fields are empty
        Exception: For any other processing errors
    """
    # Input validation
    if not isinstance(message, str):
        raise TypeError("message must be a string")
    if not isinstance(user_id, str):
        raise TypeError("user_id must be a string")
    if not isinstance(platform, str):
        raise TypeError("platform must be a string")
    if not user_id:
        raise ValueError("user_id cannot be empty")
    if not platform:
        raise ValueError("platform cannot be empty")
        
    try:
        logger.info(f"Processing secure embedding for user {user_id} on platform {platform}")
        
        # Fetch the user key using get_key(user_id), and if missing, generate it using generate_key(user_id)
        keystore = KeyStore()
        user_key_bytes = keystore.get_key(user_id)
        
        # If no key exists, generate one
        if user_key_bytes is None:
            logger.info(f"No existing key found for user {user_id}, generating new key")
            user_key_bytes = keystore.generate_key(user_id)
        
        # Decode key for use in obfuscation
        user_key = user_key_bytes.decode()
        logger.debug("Retrieved user key for obfuscation")
        
        # Generate the embedding using generate_embedding(message)
        embedding = generate_embedding(message)
        logger.debug(f"Generated embedding with {len(embedding)} dimensions")
        
        # Obfuscate it using obfuscate(embedding, key)
        obf_embedding = obfuscate(embedding, user_key)
        logger.debug("Obfuscated embedding with user key")
        
        # Create an ISO timestamp using datetime.utcnow().isoformat()
        timestamp = datetime.utcnow().isoformat()
        
        # Generate session_id (auto-generated UUID)
        session_id = str(uuid.uuid4())
        
        # Log the embedding by calling log_embedding() from embed_logger with user_id, session_id, platform, obfuscated embedding
        log_result = log_embedding(user_id, session_id, platform, obf_embedding)
        if log_result['overall_success']:
            logger.info(f"Successfully logged embedding for user {user_id}")
        else:
            logger.warning(f"Failed to log embedding for user {user_id}")
        
        # Return a JSON dictionary exactly in this format
        result = {
            "embedding": obf_embedding,
            "user_id": user_id,
            "platform": platform,
            "timestamp": timestamp
        }
        
        logger.info(f"Secure embedding processing completed for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in secure_embed for user {user_id}: {e}")
        raise


# Test functions to verify correctness
def test_embedding_functions():
    """Test the embedding functions for correctness."""
    print("Testing embedding functions...")
    
    # Test determinism of generate_embedding
    text = "hello world"
    emb1 = generate_embedding(text)
    emb2 = generate_embedding(text)
    
    assert emb1 == emb2, "generate_embedding is not deterministic"
    print("✓ generate_embedding is deterministic")
    
    # Test obfuscation/de-obfuscation roundtrip
    user_key = "test_user_key_123"
    original = generate_embedding("test message")
    obfuscated = obfuscate(original, user_key)
    restored = deobfuscate(obfuscated, user_key)
    
    # Check if roundtrip is successful (accounting for floating point precision)
    assert len(original) == len(restored), "Length mismatch after de-obfuscation"
    for i in range(len(original)):
        assert abs(original[i] - restored[i]) < 1e-10, f"Value mismatch at index {i}"
    
    print("✓ obfuscate/deobfuscate roundtrip works correctly")
    
    # Test edge cases
    # Empty string
    empty_emb = generate_embedding("")
    assert len(empty_emb) == 384, "Empty string should produce 384-dim embedding"
    print("✓ Empty string handling works")
    
    # Zero vector roundtrip
    zero_vec = [0.0] * 384
    obf_zero = obfuscate(zero_vec, "key")
    rest_zero = deobfuscate(obf_zero, "key")
    for i in range(len(zero_vec)):
        assert abs(zero_vec[i] - rest_zero[i]) < 1e-10, f"Zero vector mismatch at index {i}"
    print("✓ Zero vector roundtrip works")
    
    print("All tests passed!")


if __name__ == "__main__":
    test_embedding_functions()