"""
Test suite for embedcore_v3.py module.

This file contains tests to verify the correctness of the embedding functions
and the reversibility of the obfuscation process.
"""

import sys
import os

# Add the parent directory to the path so we can import embedcore_v3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from embedcore_v3 import generate_embedding, obfuscate, deobfuscate


def test_obfuscation_reversibility():
    """
    Test that the obfuscation process is perfectly reversible.
    
    This test verifies that applying obfuscate() followed by deobfuscate()
    with the same user key results in the exact same embedding as the original.
    This is a critical requirement for the secure embedding system.
    """
    # Sample deterministic embedding
    original_embedding = [0.1, -0.3, 0.5, 1.0]
    
    # Sample user key
    user_key = "test-user-key"
    
    # Apply obfuscation
    obfuscated = obfuscate(original_embedding, user_key)
    
    # Apply de-obfuscation
    restored = deobfuscate(obfuscated, user_key)
    
    # Assert that the final output is exactly equal to the original embedding
    # Using a small tolerance for floating-point comparison
    tolerance = 1e-10
    assert len(restored) == len(original_embedding), "Length mismatch after de-obfuscation"
    for i in range(len(original_embedding)):
        assert abs(restored[i] - original_embedding[i]) < tolerance, \
            f"Value mismatch at index {i}: expected {original_embedding[i]}, got {restored[i]}"


def test_embedding_determinism():
    """
    Test that generate_embedding produces deterministic results.
    
    The same input text should always produce the same embedding vector.
    """
    test_text = "This is a test message for deterministic embedding generation."
    
    # Generate embedding twice
    embedding1 = generate_embedding(test_text)
    embedding2 = generate_embedding(test_text)
    
    # They should be identical
    assert embedding1 == embedding2, "generate_embedding is not deterministic"


def test_full_roundtrip():
    """
    Test the complete roundtrip process: generate -> obfuscate -> deobfuscate.
    
    This test verifies that the entire process works correctly from start to finish.
    """
    # Test text
    test_text = "This is a complete roundtrip test message."
    user_key = "roundtrip-test-key"
    
    # Generate embedding
    original_embedding = generate_embedding(test_text)
    
    # Obfuscate
    obfuscated = obfuscate(original_embedding, user_key)
    
    # De-obfuscate
    restored = deobfuscate(obfuscated, user_key)
    
    # Verify roundtrip
    tolerance = 1e-10
    assert len(restored) == len(original_embedding), "Length mismatch in full roundtrip"
    for i in range(len(original_embedding)):
        assert abs(restored[i] - original_embedding[i]) < tolerance, \
            f"Roundtrip mismatch at index {i}"


def test_same_input_same_output():
    """
    Test that same input produces same output.
    
    Same message + same key → same embedding
    Same embedding + same key → same obfuscation
    """
    # Test message
    message = "Consistency test message"
    user_key = "consistency-key"
    
    # Generate embedding twice with same input
    embedding1 = generate_embedding(message)
    embedding2 = generate_embedding(message)
    
    # They should be identical
    assert embedding1 == embedding2, "Same input should produce same embedding"
    
    # Obfuscate twice with same input
    obf_embedding1 = obfuscate(embedding1, user_key)
    obf_embedding2 = obfuscate(embedding2, user_key)
    
    # They should be identical
    assert obf_embedding1 == obf_embedding2, "Same embedding + same key should produce same obfuscation"
    
    print("✓ test_same_input_same_output passed")


def test_same_message_diff_keys():
    """
    Test that same message with different keys produces different obfuscated embeddings.
    
    Same message + different keys → different obfuscated embeddings
    """
    # Test message
    message = "Different keys test message"
    key1 = "key-one"
    key2 = "key-two"
    
    # Generate embedding
    embedding = generate_embedding(message)
    
    # Obfuscate with different keys
    obf_embedding1 = obfuscate(embedding, key1)
    obf_embedding2 = obfuscate(embedding, key2)
    
    # They should be different
    # Using a small tolerance to account for potential floating point issues
    tolerance = 1e-10
    embeddings_are_different = False
    for i in range(len(obf_embedding1)):
        if abs(obf_embedding1[i] - obf_embedding2[i]) > tolerance:
            embeddings_are_different = True
            break
    
    assert embeddings_are_different, "Different keys should produce different obfuscated embeddings"
    
    print("✓ test_same_message_diff_keys passed")


if __name__ == "__main__":
    # Run the tests
    try:
        test_obfuscation_reversibility()
        print("✓ test_obfuscation_reversibility passed")
        
        test_embedding_determinism()
        print("✓ test_embedding_determinism passed")
        
        test_full_roundtrip()
        print("✓ test_full_roundtrip passed")
        
        test_same_input_same_output()
        print("✓ test_same_input_same_output passed")
        
        test_same_message_diff_keys()
        print("✓ test_same_message_diff_keys passed")
        
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)