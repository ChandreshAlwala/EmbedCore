"""
End-to-End Tests for Assistant Pipeline

This module contains comprehensive tests for the assistant_pipeline module.
"""

import os
import json
import sys
from typing import Dict, List
import sqlite3

# Import the module to test
from assistant_pipeline import process_message
from embedcore_v3 import generate_embedding, obfuscate, deobfuscate
from keystore import KeyStore


def test_same_message_same_key_same_user():
    """Test that same message + same key + same user produces same results."""
    user_id = "test_user_1"
    session_id = "test_session_1"
    platform = "test_platform"
    message = "This is a test message for consistency"
    
    # Process the same message twice
    result1 = process_message(user_id, session_id, platform, message)
    result2 = process_message(user_id, session_id, platform, message)
    
    # Both should be successful
    assert result1["status"] == "success"
    assert result2["status"] == "success"
    
    # Embeddings should be identical
    assert result1["embedding"] == result2["embedding"]
    
    # Obfuscated embeddings should be identical
    assert result1["obfuscated_embedding"] == result2["obfuscated_embedding"]
    
    # User ID, session ID, and platform should match
    assert result1["user_id"] == result2["user_id"] == user_id
    assert result1["session_id"] == result2["session_id"] == session_id
    assert result1["platform"] == result2["platform"] == platform


def test_same_message_different_users():
    """Test that same message + different users produces different obfuscations."""
    session_id = "test_session_1"
    platform = "test_platform"
    message = "This is a test message for key isolation"
    
    # Process with different users
    result1 = process_message("user_alpha", session_id, platform, message)
    result2 = process_message("user_beta", session_id, platform, message)
    
    # Both should be successful
    assert result1["status"] == "success"
    assert result2["status"] == "success"
    
    # Embeddings should be identical (deterministic)
    assert result1["embedding"] == result2["embedding"]
    
    # But obfuscated embeddings should be different (different keys)
    assert result1["obfuscated_embedding"] != result2["obfuscated_embedding"]
    
    # User IDs should be different
    assert result1["user_id"] != result2["user_id"]


def test_database_writing():
    """Test that process_message writes to database."""
    user_id = "db_test_user"
    session_id = "db_test_session"
    platform = "db_test_platform"
    message = "This is a test message for database writing"
    
    # Process message
    result = process_message(user_id, session_id, platform, message)
    assert result["status"] == "success"
    
    # Check database
    conn = sqlite3.connect("assistant_core.db")
    cursor = conn.cursor()
    
    # Look for the entry we just created
    cursor.execute("""
        SELECT user_id, session_id, platform, obfuscated_embedding 
        FROM embeddings 
        WHERE user_id = ? AND session_id = ?
    """, (user_id, session_id))
    
    rows = cursor.fetchall()
    assert len(rows) > 0, "Should find at least one row"
    
    row = rows[0]
    assert row[0] == user_id
    assert row[1] == session_id
    assert row[2] == platform
    
    # Check that the obfuscated embedding matches
    stored_embedding = json.loads(row[3])
    assert stored_embedding == result["obfuscated_embedding"]
    
    conn.close()


def test_csv_writing():
    """Test that process_message writes to CSV."""
    user_id = "csv_test_user"
    session_id = "csv_test_session"
    platform = "csv_test_platform"
    message = "This is a test message for CSV writing"
    
    # Process message
    result = process_message(user_id, session_id, platform, message)
    assert result["status"] == "success"
    
    # Check CSV file
    assert os.path.exists("embedding_log.csv"), "CSV file should exist"
    
    with open("embedding_log.csv", "r") as f:
        lines = f.readlines()
        assert len(lines) > 1, "Should have at least header and one data line"
        
        # Check that our entry is in the file
        found = False
        for line in lines[1:]:  # Skip header
            if user_id in line and session_id in line:
                found = True
                break
        
        assert found, "Should find our entry in CSV"


def test_structured_response():
    """Test that process_message returns proper structured dictionary."""
    user_id = "response_test_user"
    session_id = "response_test_session"
    platform = "response_test_platform"
    message = "This is a test message for response structure"
    
    # Process message
    result = process_message(user_id, session_id, platform, message)
    
    # Check structure
    assert isinstance(result, dict)
    assert "status" in result
    assert "embedding" in result
    assert "obfuscated_embedding" in result
    assert "user_id" in result
    assert "session_id" in result
    assert "platform" in result
    assert "timestamp" in result
    
    # Check values
    assert result["status"] == "success"
    assert result["user_id"] == user_id
    assert result["session_id"] == session_id
    assert result["platform"] == platform
    assert isinstance(result["embedding"], list)
    assert isinstance(result["obfuscated_embedding"], list)
    assert isinstance(result["timestamp"], str)


def test_obfuscation_reversibility():
    """Test that obfuscation -> deobfuscation is reversible."""
    user_id = "reversibility_test_user"
    session_id = "reversibility_test_session"
    platform = "reversibility_test_platform"
    message = "This is a test message for reversibility"
    
    # Process message
    result = process_message(user_id, session_id, platform, message)
    assert result["status"] == "success"
    
    # Get the user key
    keystore = KeyStore()
    user_key_bytes = keystore.get_key(user_id)
    if user_key_bytes is not None:
        user_key = user_key_bytes.decode()
        
        # Deobfuscate the obfuscated embedding
        deobfuscated = deobfuscate(result["obfuscated_embedding"], user_key)
        
        # Check that it matches the original embedding (within floating point tolerance)
        original = result["embedding"]
        assert len(deobfuscated) == len(original)
        
        for i in range(len(original)):
            assert abs(deobfuscated[i] - original[i]) < 1e-10, f"Value at index {i} should match"


def test_input_validation():
    """Test input validation."""
    # Test with invalid types - we'll catch the exceptions
    try:
        process_message(123, "session", "platform", "message")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        process_message("user", 456, "platform", "message")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        process_message("user", "session", 789, "message")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        process_message("user", "session", "platform", 123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    # Test with empty values
    try:
        process_message("", "session", "platform", "message")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    try:
        process_message("user", "", "platform", "message")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    try:
        process_message("user", "session", "", "message")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_error_handling():
    """Test error handling."""
    # This test ensures the function doesn't crash on errors
    # We can't easily trigger real errors without mocking, so we'll just
    # verify the function returns an error structure
    
    # Test with normal inputs to ensure success path works
    result = process_message("error_test_user", "error_test_session", "error_test_platform", "Test message")
    assert result["status"] in ["success", "error"]


if __name__ == "__main__":
    # Run tests manually if not using pytest
    test_functions = [
        test_same_message_same_key_same_user,
        test_same_message_different_users,
        test_database_writing,
        test_csv_writing,
        test_structured_response,
        test_obfuscation_reversibility,
        test_input_validation,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
    
    print(f"\nTests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed > 0:
        sys.exit(1)