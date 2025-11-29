#!/usr/bin/env python3
"""
Debug Embeddings Utility

This script helps debug the embedding generation process.
"""

import json
from embedcore_v3 import generate_embedding, obfuscate, deobfuscate

def debug_embedding_generation(text: str, key: str = "debug_key"):
    """Debug the embedding generation process."""
    print(f"Debugging embedding generation for: '{text}'")
    print("=" * 50)
    
    try:
        # Generate embedding
        print("1. Generating embedding...")
        embedding = generate_embedding(text)
        print(f"   ✓ Generated embedding with {len(embedding)} dimensions")
        print(f"   First 5 values: {embedding[:5]}")
        
        # Obfuscate embedding
        print("\n2. Obfuscating embedding...")
        obfuscated = obfuscate(embedding, key)
        print(f"   ✓ Obfuscated embedding with {len(obfuscated)} dimensions")
        print(f"   First 5 values: {obfuscated[:5]}")
        
        # Deobfuscate embedding
        print("\n3. Deobfuscating embedding...")
        deobfuscated = deobfuscate(obfuscated, key)
        print(f"   ✓ Deobfuscated embedding with {len(deobfuscated)} dimensions")
        
        # Verify reversibility
        print("\n4. Verifying reversibility...")
        is_reversible = True
        for i in range(len(embedding)):
            if abs(embedding[i] - deobfuscated[i]) > 1e-10:
                print(f"   ❌ Mismatch at index {i}: {embedding[i]} vs {deobfuscated[i]}")
                is_reversible = False
                break
        
        if is_reversible:
            print("   ✓ Obfuscation is perfectly reversible")
        
        # Show statistics
        print("\n5. Embedding statistics:")
        print(f"   Min value: {min(embedding)}")
        print(f"   Max value: {max(embedding)}")
        print(f"   Mean value: {sum(embedding) / len(embedding)}")
        
        print("\n✓ Debug completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

def debug_multiple_texts():
    """Debug embedding generation for multiple texts."""
    test_texts = [
        "Hello world",
        "The quick brown fox jumps over the lazy dog",
        "",
        "Special chars: !@#$%^&*()",
        "Very long text: " + "A" * 1000
    ]
    
    print("Debugging multiple texts...")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        success = debug_embedding_generation(text)
        if not success:
            return False
    
    print("\n✓ All tests completed successfully")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug embedding generation")
    parser.add_argument(
        "--text",
        default="Hello, this is a debug test!",
        help="Text to generate embedding for"
    )
    parser.add_argument(
        "--multi",
        action="store_true",
        help="Run multiple test cases"
    )
    
    args = parser.parse_args()
    
    if args.multi:
        debug_multiple_texts()
    else:
        debug_embedding_generation(args.text)