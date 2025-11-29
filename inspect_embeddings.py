#!/usr/bin/env python3
"""
Inspect Embeddings Utility

This script inspects embeddings stored in the database.
"""

import sqlite3
import json

def inspect_embeddings(db_path: str = "assistant_core.db", limit: int = 10):
    """Inspect embeddings in the database."""
    try:
        print(f"Inspecting embeddings in {db_path}")
        print("=" * 50)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get embeddings
        cursor.execute("""
            SELECT trace_id, text, vector_json, created_at 
            FROM embeddings 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No embeddings found in database")
            conn.close()
            return True
        
        print(f"Found {len(rows)} embeddings:")
        
        for i, (trace_id, text, vector_json, created_at) in enumerate(rows, 1):
            vector = json.loads(vector_json)
            
            print(f"\n{i}. Trace ID: {trace_id}")
            print(f"   Text: {text[:60]}{'...' if len(text) > 60 else ''}")
            print(f"   Dimensions: {len(vector)}")
            print(f"   Created: {created_at}")
            print(f"   Sample values: {vector[:5]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error inspecting embeddings: {e}")
        return False

def inspect_embedding_by_trace_id(trace_id: str, db_path: str = "assistant_core.db"):
    """Inspect a specific embedding by trace ID."""
    try:
        print(f"Inspecting embedding with trace ID: {trace_id}")
        print("=" * 50)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get specific embedding
        cursor.execute("""
            SELECT trace_id, text, vector_json, created_at 
            FROM embeddings 
            WHERE trace_id = ?
        """, (trace_id,))
        
        row = cursor.fetchone()
        
        if not row:
            print(f"No embedding found with trace ID: {trace_id}")
            conn.close()
            return False
        
        trace_id, text, vector_json, created_at = row
        vector = json.loads(vector_json)
        
        print(f"Trace ID: {trace_id}")
        print(f"Text: {text}")
        print(f"Dimensions: {len(vector)}")
        print(f"Created: {created_at}")
        print(f"All values: {vector}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error inspecting embedding: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inspect embeddings in database")
    parser.add_argument(
        "--trace-id",
        help="Inspect specific embedding by trace ID"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of embeddings to show (default: 10)"
    )
    parser.add_argument(
        "--db-path",
        default="assistant_core.db",
        help="Path to database file"
    )
    
    args = parser.parse_args()
    
    if args.trace_id:
        inspect_embedding_by_trace_id(args.trace_id, args.db_path)
    else:
        inspect_embeddings(args.db_path, args.limit)