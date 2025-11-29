#!/usr/bin/env python3
"""
Debug Embedding Storage Utility

This script helps debug issues with embedding storage in the database.
"""

import sqlite3
import json
from datetime import datetime

def debug_embedding_storage(db_path: str = "assistant_core.db"):
    """Debug embedding storage issues."""
    try:
        print(f"Debugging embedding storage in {db_path}")
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
        
        # Get table schema
        cursor.execute("PRAGMA table_info(embeddings)")
        columns = cursor.fetchall()
        print(f"Table columns: {', '.join([col[1] for col in columns])}")
        
        # Count total embeddings
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        count = cursor.fetchone()[0]
        print(f"Total embeddings: {count}")
        
        # Show sample data
        if count > 0:
            print("\nSample embeddings:")
            cursor.execute("""
                SELECT trace_id, text, vector_json, created_at 
                FROM embeddings 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            samples = cursor.fetchall()
            
            for i, (trace_id, text, vector_json, created_at) in enumerate(samples, 1):
                vector = json.loads(vector_json)
                print(f"\nSample {i}:")
                print(f"  Trace ID: {trace_id}")
                print(f"  Text: {text[:50]}{'...' if len(text) > 50 else ''}")
                print(f"  Vector length: {len(vector)}")
                print(f"  Created at: {created_at}")
        
        conn.close()
        print("\n✓ Debug completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

def clear_embeddings(db_path: str = "assistant_core.db"):
    """Clear all embeddings from the database (USE WITH CAUTION)."""
    try:
        print(f"Clearing all embeddings from {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='embeddings'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Embeddings table does not exist, nothing to clear")
            conn.close()
            return True
        
        # Count before deletion
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        count_before = cursor.fetchone()[0]
        
        # Delete all records
        cursor.execute("DELETE FROM embeddings")
        conn.commit()
        
        # Count after deletion
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        count_after = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Cleared {count_before} embeddings")
        print(f"Remaining embeddings: {count_after}")
        print("✓ Clear operation completed")
        return True
        
    except Exception as e:
        print(f"❌ Clear operation failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug embedding storage")
    parser.add_argument(
        "--clear", 
        action="store_true",
        help="Clear all embeddings from database (CAUTION!)"
    )
    parser.add_argument(
        "--db-path",
        default="assistant_core.db",
        help="Path to database file"
    )
    
    args = parser.parse_args()
    
    if args.clear:
        confirm = input("Are you sure you want to clear ALL embeddings? Type 'YES' to confirm: ")
        if confirm == "YES":
            clear_embeddings(args.db_path)
        else:
            print("Operation cancelled")
    else:
        debug_embedding_storage(args.db_path)