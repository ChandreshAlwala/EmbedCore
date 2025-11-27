"""
Demonstration of EmbedCore v3 and KeyStore functionality.

This script shows how to use the embedding functions and keystore together.
"""

import logging
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from embedcore_v3 import generate_embedding, obfuscate, deobfuscate
from keystore import generate_key, get_key, rotate_key


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_obfuscation_reversibility():
    """Demonstrate that the obfuscation process is perfectly reversible."""
    print("=== Demonstrating Obfuscation Reversibility ===")
    
    # Sample deterministic embedding
    original_embedding = [0.1, -0.3, 0.5, 1.0]
    
    # Sample user key
    user_key = "test-user-key"
    
    print(f"Original embedding: {original_embedding}")
    
    # Apply obfuscation
    obfuscated = obfuscate(original_embedding, user_key)
    print(f"Obfuscated embedding: {[round(x, 4) for x in obfuscated[:4]]}")
    
    # Apply de-obfuscation
    restored = deobfuscate(obfuscated, user_key)
    print(f"Restored embedding: {[round(x, 4) for x in restored[:4]]}")
    
    # Verify reversibility
    tolerance = 1e-10
    is_reversible = all(abs(restored[i] - original_embedding[i]) < tolerance 
                       for i in range(len(original_embedding)))
    
    print(f"Reversibility check: {'✓ PASSED' if is_reversible else '✗ FAILED'}")
    
    if is_reversible:
        print("The obfuscation process is perfectly reversible!\n")
    else:
        print("ERROR: The obfuscation process is not reversible!\n")
    
    return is_reversible


def main():
    """Demonstrate the usage of embedding and keystore functions."""
    print("=== EmbedCore v3 & KeyStore Demonstration ===\n")
    
    # First, demonstrate obfuscation reversibility
    if not demonstrate_obfuscation_reversibility():
        return False
    
    # User identification
    user_id = "alice_2025"
    message = "Hello, this is a secret message that needs to be embedded and protected."
    
    print(f"User: {user_id}")
    print(f"Message: {message}\n")
    
    try:
        # Step 1: Generate a secure key for the user
        print("1. Generating secure key for user...")
        user_key_bytes = generate_key(user_id)
        user_key = user_key_bytes.decode('utf-8')
        print(f"   Key generated and stored securely\n")
        
        # Step 2: Generate embedding for the message
        print("2. Generating embedding for the message...")
        embedding = generate_embedding(message)
        print(f"   Embedding generated with {len(embedding)} dimensions")
        print(f"   First 5 values: {[round(x, 4) for x in embedding[:5]]}\n")
        
        # Step 3: Obfuscate the embedding using the user's key
        print("3. Obfuscating embedding with user key...")
        obfuscated = obfuscate(embedding, user_key)
        print(f"   Embedding obfuscated")
        print(f"   First 5 obfuscated values: {[round(x, 4) for x in obfuscated[:5]]}\n")
        
        # Step 4: De-obfuscate to verify the process works
        print("4. De-obfuscating embedding to verify...")
        restored = deobfuscate(obfuscated, user_key)
        
        # Verify that the round-trip worked correctly
        is_match = all(abs(a - b) < 1e-10 for a, b in zip(embedding, restored))
        print(f"   Round-trip successful: {is_match}\n")
        
        # Step 5: Retrieve key from secure storage
        print("5. Retrieving key from secure keystore...")
        retrieved_key_bytes = get_key(user_id)
        if retrieved_key_bytes:
            retrieved_key = retrieved_key_bytes.decode('utf-8')
            keys_match = user_key == retrieved_key
            print(f"   Key retrieved successfully")
            print(f"   Keys match: {keys_match}\n")
        else:
            print("   Failed to retrieve key\n")
            return False
        
        # Step 6: Demonstrate key rotation
        print("6. Rotating user key for enhanced security...")
        new_key_bytes = rotate_key(user_id)
        if new_key_bytes:
            new_key = new_key_bytes.decode('utf-8')
            is_different = user_key != new_key
            print(f"   Key rotated successfully")
            print(f"   New key is different: {is_different}")
            
            # Verify we can get the new key
            latest_key_bytes = get_key(user_id)
            if latest_key_bytes:
                latest_key = latest_key_bytes.decode('utf-8')
                print(f"   Latest key retrieval successful: {new_key == latest_key}")
            else:
                print("   Failed to retrieve latest key")
                return False
        else:
            print("   Failed to rotate key")
            return False
        
        print("\n=== Demonstration Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)