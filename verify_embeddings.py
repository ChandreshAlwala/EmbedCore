#!/usr/bin/env python3
"""
Verify Embeddings Utility

This script verifies the integrity of embeddings stored in the database.
"""

import sqlite3
import json
import numpy as np

def verify_embeddings(db_path: str = "assistant_core.db"):
    """Verify the integrity of embeddings in the database."""
    try:
        print(f"Verifying embeddings in {db_path}")
        print("=" * 50)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if embeddings table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='embeddings'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Embeddings table does not exist")
            conn.close()
            return False
        
        print("✓ Embeddings table exists")
        
        # Get all embeddings
        cursor.execute("SELECT id, trace_id, vector_json FROM embeddings")
        rows = cursor.fetchall()
        
        if not rows:
            print("No embeddings found to verify")
            conn.close()
            return True
        
        print(f"Verifying {len(rows)} embeddings...")
        
        valid_count = 0
        invalid_count = 0
        
        for id, trace_id, vector_json in rows:
            try:
                # Parse JSON
                vector = json.loads(vector_json)
                
                # Check if it's a list
                if not isinstance(vector, list):
                    print(f"❌ Invalid format in record {id} (trace_id: {trace_id})")
                    invalid_count += 1
                    continue
                
                # Check if all elements are numbers
                valid_vector = True
                for i, val in enumerate(vector):
                    if not isinstance(val, (int, float)):
                        print(f"❌ Non-numeric value at index {i} in record {id} (trace_id: {trace_id})")
                        valid_vector = False
                        break
                
                if valid_vector:
                    # Check for reasonable values (not all zeros, not NaN, not infinite)
                    vector_array = np.array(vector)
                    if np.isnan(vector_array).any():
                        print(f"❌ NaN values found in record {id} (trace_id: {trace_id})")
                        invalid_count += 1
                    elif np.isinf(vector_array).any():
                        print(f"❌ Infinite values found in record {id} (trace_id: {trace_id})")
                        invalid_count += 1
                    elif np.all(vector_array == 0):
                        print(f"⚠️  All-zero vector in record {id} (trace_id: {trace_id})")
                        # Not necessarily invalid, but worth noting
                        valid_count += 1
                    else:
                        valid_count += 1
                else:
                    invalid_count += 1
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in record {id} (trace_id: {trace_id})")
                invalid_count += 1
            except Exception as e:
                print(f"❌ Error processing record {id} (trace_id: {trace_id}): {e}")
                invalid_count += 1
        
        conn.close()
        
        print(f"\nVerification Results:")
        print(f"  Valid embeddings: {valid_count}")
        print(f"  Invalid embeddings: {invalid_count}")
        print(f"  Total embeddings: {len(rows)}")
        
        if invalid_count == 0:
            print("✓ All embeddings are valid!")
            return True
        else:
            print(f"⚠️  Found {invalid_count} invalid embeddings")
            return False
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def verify_embedding_dimensions(db_path: str = "assistant_core.db", expected_dim: int = 384):
    """Verify that all embeddings have the expected dimension."""
    try:
        print(f"Verifying embedding dimensions in {db_path}")
        print(f"Expected dimension: {expected_dim}")
        print("=" * 50)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all embeddings
        cursor.execute("SELECT id, trace_id, vector_json FROM embeddings")
        rows = cursor.fetchall()
        
        if not rows:
            print("No embeddings found to verify")
            conn.close()
            return True
        
        print(f"Checking dimensions of {len(rows)} embeddings...")
        
        correct_dim_count = 0
        incorrect_dim_count = 0
        
        for id, trace_id, vector_json in rows:
            try:
                vector = json.loads(vector_json)
                
                if len(vector) == expected_dim:
                    correct_dim_count += 1
                else:
                    print(f"❌ Wrong dimension in record {id} (trace_id: {trace_id}): {len(vector)} (expected {expected_dim})")
                    incorrect_dim_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing record {id} (trace_id: {trace_id}): {e}")
                incorrect_dim_count += 1
        
        conn.close()
        
        print(f"\nDimension Verification Results:")
        print(f"  Correct dimension: {correct_dim_count}")
        print(f"  Incorrect dimension: {incorrect_dim_count}")
        print(f"  Total embeddings: {len(rows)}")
        
        if incorrect_dim_count == 0:
            print("✓ All embeddings have correct dimensions!")
            return True
        else:
            print(f"⚠️  Found {incorrect_dim_count} embeddings with incorrect dimensions")
            return False
        
    except Exception as e:
        print(f"❌ Dimension verification failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify embeddings in database")
    parser.add_argument(
        "--dimensions",
        type=int,
        help="Verify that all embeddings have this dimension"
    )
    parser.add_argument(
        "--db-path",
        default="assistant_core.db",
        help="Path to database file"
    )
    
    args = parser.parse_args()
    
    # Run basic verification
    basic_success = verify_embeddings(args.db_path)
    
    # Run dimension verification if requested
    dim_success = True
    if args.dimensions:
        dim_success = verify_embedding_dimensions(args.db_path, args.dimensions)
    
    if basic_success and dim_success:
        print("\n🎉 All verifications passed!")
        exit(0)
    else:
        print("\n❌ Some verifications failed!")
        exit(1)