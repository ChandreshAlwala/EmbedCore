#!/usr/bin/env python3
"""
Comprehensive Embedding Test Suite

This script runs a comprehensive set of tests on the embedding generation and storage system.
"""

import sqlite3
import json
import numpy as np
from datetime import datetime
from embedcore_v3 import generate_embedding, obfuscate, deobfuscate
from keystore import KeyStore

def test_embedding_consistency():
    """Test that the same input always produces the same embedding."""
    print("Testing embedding consistency...")
    
    text = "This is a test sentence for consistency checking."
    
    # Generate embedding multiple times
    embedding1 = generate_embedding(text)
    embedding2 = generate_embedding(text)
    embedding3 = generate_embedding(text)
    
    # Check that all embeddings are identical
    assert embedding1 == embedding2 == embedding3, "Embeddings should be identical"
    print("✓ Embedding consistency test passed")

def test_obfuscation_reversibility():
    """Test that obfuscation is reversible."""
    print("Testing obfuscation reversibility...")
    
    original = [0.1, -0.2, 0.3, -0.4, 0.5]
    key = "test_key_123"
    
    # Obfuscate and then deobfuscate
    obfuscated = obfuscate(original, key)
    deobfuscated = deobfuscate(obfuscated, key)
    
    # Check that deobfuscated matches original (within floating point tolerance)
    assert len(deobfuscated) == len(original), "Length should match"
    for i in range(len(original)):
        assert abs(deobfuscated[i] - original[i]) < 1e-10, f"Value at index {i} should match"
    
    print("✓ Obfuscation reversibility test passed")

def test_key_isolation():
    """Test that different keys produce different obfuscations."""
    print("Testing key isolation...")
    
    original = [0.1, -0.2, 0.3, -0.4, 0.5]
    key1 = "test_key_alpha"
    key2 = "test_key_beta"
    
    # Obfuscate with different keys
    obfuscated1 = obfuscate(original, key1)
    obfuscated2 = obfuscate(original, key2)
    
    # Check that obfuscated values are different
    assert obfuscated1 != obfuscated2, "Different keys should produce different obfuscations"
    print("✓ Key isolation test passed")

def test_database_storage():
    """Test that embeddings can be stored and retrieved from database."""
    print("Testing database storage...")
    
    # Initialize key store
    keystore = KeyStore()
    user_id = "test_user_123"
    
    # Generate a key for the user
    user_key = keystore.generate_key(user_id)
    
    # Generate embedding
    text = "Test text for database storage"
    embedding = generate_embedding(text)
    
    # Obfuscate embedding
    obfuscated = obfuscate(embedding, user_key.decode())
    
    # Store in database
    db_path = "assistant_core.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT NOT NULL UNIQUE,
            text TEXT NOT NULL,
            vector_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Insert data
    trace_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    vector_json = json.dumps(obfuscated)
    created_at = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO embeddings (trace_id, text, vector_json, created_at)
        VALUES (?, ?, ?, ?)
    ''', (trace_id, text, vector_json, created_at))
    
    conn.commit()
    conn.close()
    
    # Retrieve from database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT vector_json FROM embeddings WHERE trace_id = ?", (trace_id,))
    row = cursor.fetchone()
    
    assert row is not None, "Should find the stored embedding"
    
    retrieved_obfuscated_json = row[0]
    retrieved_obfuscated = json.loads(retrieved_obfuscated_json)
    
    # Deobfuscate
    retrieved_deobfuscated = deobfuscate(retrieved_obfuscated, user_key.decode())
    
    # Check that retrieved embedding matches original (within floating point tolerance)
    assert len(retrieved_deobfuscated) == len(embedding), "Length should match"
    for i in range(len(embedding)):
        assert abs(retrieved_deobfuscated[i] - embedding[i]) < 1e-10, f"Value at index {i} should match"
    
    conn.close()
    print("✓ Database storage test passed")

def test_edge_cases():
    """Test edge cases."""
    print("Testing edge cases...")
    
    # Empty string
    empty_embedding = generate_embedding("")
    assert isinstance(empty_embedding, list), "Should return a list"
    assert len(empty_embedding) > 0, "Should have elements"
    
    # Very long string
    long_text = "A" * 10000
    long_embedding = generate_embedding(long_text)
    assert isinstance(long_embedding, list), "Should return a list"
    
    # Special characters
    special_text = "Test with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
    special_embedding = generate_embedding(special_text)
    assert isinstance(special_embedding, list), "Should return a list"
    
    print("✓ Edge cases test passed")

def run_all_tests():
    """Run all tests."""
    print("Running comprehensive embedding test suite...")
    print("=" * 50)
    
    try:
        test_embedding_consistency()
        test_obfuscation_reversibility()
        test_key_isolation()
        test_database_storage()
        test_edge_cases()
        
        print("=" * 50)
        print("All tests passed! 🎉")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        exit(1)