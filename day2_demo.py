"""
Day-2 Demo for EmbedCore v3

This script demonstrates the new Day-2 functionality including:
- Database integration
- Embedding logging (DB + CSV)
- Consistency and reversibility tests
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from embedcore_v3 import generate_embedding, obfuscate, deobfuscate
from keystore import generate_key, get_key
from embed_logger import log_embedding, save_embedding


def demo_day2_functionality():
    """Demonstrate all Day-2 functionality."""
    print("=== EmbedCore v3 Day-2 Demo ===\n")
    
    # Test data
    user_id = "demo_user_123"
    session_id = "session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    platform = "demo_app"
    message = "This is a demonstration message for EmbedCore v3 Day-2 features."
    
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")
    print(f"Platform: {platform}")
    print(f"Message: {message}\n")
    
    try:
        # Step 1: Generate user key
        print("1. Generating user key...")
        user_key_bytes = generate_key(user_id)
        user_key = user_key_bytes.decode('utf-8')
        print(f"   ✓ User key generated and stored\n")
        
        # Step 2: Generate embedding
        print("2. Generating embedding...")
        embedding = generate_embedding(message)
        print(f"   ✓ Embedding generated ({len(embedding)} dimensions)\n")
        
        # Step 3: Obfuscate embedding
        print("3. Obfuscating embedding...")
        obf_embedding = obfuscate(embedding, user_key)
        print(f"   ✓ Embedding obfuscated\n")
        
        # Step 4: Log embedding (Day-2 feature)
        print("4. Logging embedding to DB and CSV...")
        log_result = log_embedding(user_id, session_id, platform, obf_embedding)
        print(f"   ✓ Logging completed:")
        print(f"     Database success: {log_result['db_success']}")
        print(f"     CSV success: {log_result['csv_success']}")
        print(f"     Overall success: {log_result['overall_success']}\n")
        
        # Step 5: Direct database save (alternative method)
        print("5. Direct database save...")
        direct_save_success = save_embedding(
            user_id=user_id,
            session_id=session_id + "_direct",
            embedding_data=obf_embedding,
            platform=platform + "_direct"
        )
        print(f"   ✓ Direct database save: {'Success' if direct_save_success else 'Failed'}\n")
        
        # Step 6: Verify reversibility
        print("6. Verifying obfuscation reversibility...")
        restored_embedding = deobfuscate(obf_embedding, user_key)
        
        # Check if roundtrip is successful
        tolerance = 1e-10
        is_reversible = all(abs(a - b) < tolerance for a, b in zip(embedding, restored_embedding))
        print(f"   ✓ Obfuscation reversibility: {'PASS' if is_reversible else 'FAIL'}\n")
        
        # Step 7: Show logged data
        print("7. Checking logged data...")
        
        # Check CSV
        if os.path.exists("embedding_log.csv"):
            with open("embedding_log.csv", "r") as f:
                lines = f.readlines()
                print(f"   ✓ CSV entries: {len(lines) - 1}")  # Subtract 1 for header
        
        # Check database
        import sqlite3
        try:
            conn = sqlite3.connect("assistant_core.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            db_count = cursor.fetchone()[0]
            print(f"   ✓ Database entries: {db_count}")
            conn.close()
        except Exception as e:
            print(f"   ✗ Database check failed: {e}")
        
        print("\n=== Demo Complete ===")
        return True
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return False


if __name__ == "__main__":
    success = demo_day2_functionality()
    if not success:
        sys.exit(1)