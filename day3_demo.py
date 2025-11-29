#!/usr/bin/env python3
"""
Day 3 Demo Script

This script demonstrates the complete EmbedCore pipeline in action.
It shows how a message flows through the system from input to secure storage.
"""

import json
import os
from assistant_pipeline import process_message


def demo_pipeline():
    """Demonstrate the complete embedding pipeline."""
    print("=== EmbedCore Pipeline Demo ===\n")
    
    # Sample message data
    user_id = "demo_user_123"
    session_id = "session_20251129_140000"
    platform = "demo_app"
    message_text = "Hello! This is a demonstration of the EmbedCore pipeline. It shows how messages are processed, embedded, obfuscated, and securely stored."
    
    print("Input:")
    print(f"  User ID: {user_id}")
    print(f"  Session ID: {session_id}")
    print(f"  Platform: {platform}")
    print(f"  Message: {message_text}\n")
    
    # Process the message through the pipeline
    print("Processing message through EmbedCore pipeline...")
    result = process_message(user_id, session_id, platform, message_text)
    
    if result["status"] == "success":
        print("✓ Pipeline processing completed successfully!\n")
        
        # Display the deterministic embedding
        print("1. Deterministic Embedding:")
        print(f"   Dimensions: {len(result['embedding'])}")
        print(f"   First 5 values: {result['embedding'][:5]}")
        print(f"   Last 5 values: {result['embedding'][-5:]}\n")
        
        # Display the obfuscated embedding
        print("2. Obfuscated Embedding:")
        print(f"   Dimensions: {len(result['obfuscated_embedding'])}")
        print(f"   First 5 values: {result['obfuscated_embedding'][:5]}")
        print(f"   Last 5 values: {result['obfuscated_embedding'][-5:]}\n")
        
        # Display database entry
        print("3. Database Entry:")
        print("   Saved to: assistant_core.db")
        print("   Table: embeddings")
        print(f"   User ID: {result['user_id']}")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Platform: {result['platform']}")
        print(f"   Timestamp: {result['timestamp']}")
        print("   Obfuscated embedding: [stored as JSON]\n")
        
        # Display CSV entry
        print("4. CSV Entry:")
        if os.path.exists("embedding_log.csv"):
            # Read the last line of the CSV
            with open("embedding_log.csv", "r") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_line = lines[-1].strip()
                    print(f"   Appended to: embedding_log.csv")
                    print(f"   Last entry: {last_line}")
                else:
                    print("   CSV file exists but is empty")
        else:
            print("   CSV file not found")
        
        print("\n=== Demo Complete ===")
        return True
    else:
        print("✗ Pipeline processing failed!")
        print(f"   Error: {result.get('error_message', 'Unknown error')}")
        print("\n=== Demo Failed ===")
        return False


def demo_consistency():
    """Demonstrate the deterministic nature of the pipeline."""
    print("\n=== Consistency Demo ===\n")
    
    user_id = "consistency_user"
    session_id = "consistency_session"
    platform = "demo_app"
    message = "This message will be processed twice to show determinism."
    
    print("Processing the same message twice...")
    
    # Process the same message twice
    result1 = process_message(user_id, session_id + "_1", platform, message)
    result2 = process_message(user_id, session_id + "_2", platform, message)
    
    if result1["status"] == "success" and result2["status"] == "success":
        # Check if embeddings are identical
        embeddings_match = result1["embedding"] == result2["embedding"]
        obfuscated_match = result1["obfuscated_embedding"] == result2["obfuscated_embedding"]
        
        print(f"Embeddings identical: {embeddings_match}")
        print(f"Obfuscated embeddings identical: {obfuscated_match}")
        
        if embeddings_match and obfuscated_match:
            print("✓ Deterministic behavior confirmed!")
        else:
            print("✗ Deterministic behavior not working correctly!")
    else:
        print("✗ Failed to process messages")


def demo_key_isolation():
    """Demonstrate key isolation between users."""
    print("\n=== Key Isolation Demo ===\n")
    
    session_id = "isolation_session"
    platform = "demo_app"
    message = "Same message, different users."
    
    print("Processing same message for different users...")
    
    # Process with different users
    result1 = process_message("user_alpha", session_id, platform, message)
    result2 = process_message("user_beta", session_id, platform, message)
    
    if result1["status"] == "success" and result2["status"] == "success":
        # Check that embeddings are the same but obfuscated embeddings are different
        embeddings_match = result1["embedding"] == result2["embedding"]
        obfuscated_different = result1["obfuscated_embedding"] != result2["obfuscated_embedding"]
        
        print(f"Original embeddings identical: {embeddings_match}")
        print(f"Obfuscated embeddings different: {obfuscated_different}")
        
        if embeddings_match and obfuscated_different:
            print("✓ Key isolation working correctly!")
        else:
            print("✗ Key isolation not working correctly!")
    else:
        print("✗ Failed to process messages")


if __name__ == "__main__":
    try:
        # Run the main demo
        success = demo_pipeline()
        
        if success:
            # Run additional demos
            demo_consistency()
            demo_key_isolation()
        
        print("\n🎉 All demos completed!")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)