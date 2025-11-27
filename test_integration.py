"""
Integration test for EmbedCore v3 and KeyStore functionality.
"""

import logging
from embedcore_v3 import generate_embedding, obfuscate, deobfuscate
from keystore import generate_key, get_key


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_full_integration():
    """Test the full integration of embedding generation and key management."""
    print("Testing full integration...")
    
    # Test data
    user_id = "user_123"
    message = "This is a test message for embedding"
    
    try:
        # Step 1: Generate user key
        user_key_bytes = generate_key(user_id)
        user_key = user_key_bytes.decode('utf-8')  # Convert to string for our implementation
        print(f"✓ Generated user key for {user_id}")
        
        # Step 2: Generate embedding
        original_embedding = generate_embedding(message)
        print(f"✓ Generated embedding with {len(original_embedding)} dimensions")
        
        # Step 3: Obfuscate embedding
        obfuscated_embedding = obfuscate(original_embedding, user_key)
        print("✓ Obfuscated embedding")
        
        # Step 4: De-obfuscate embedding
        restored_embedding = deobfuscate(obfuscated_embedding, user_key)
        print("✓ De-obfuscated embedding")
        
        # Step 5: Verify round-trip
        for i in range(len(original_embedding)):
            assert abs(original_embedding[i] - restored_embedding[i]) < 1e-10, f"Mismatch at index {i}"
        print("✓ Round-trip verification successful")
        
        # Step 6: Retrieve key from keystore
        retrieved_key_bytes = get_key(user_id)
        if retrieved_key_bytes is not None:
            retrieved_key = retrieved_key_bytes.decode('utf-8')
            assert user_key == retrieved_key, "Retrieved key doesn't match original"
            print("✓ Key retrieval from keystore successful")
        else:
            print("✗ Failed to retrieve key from keystore")
            return
        
        print("All integration tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_full_integration()
    if not success:
        exit(1)