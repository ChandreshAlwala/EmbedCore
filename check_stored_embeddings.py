import sqlite3
import json

def check_stored_embeddings(db_path: str = "assistant_core.db"):
    """Check and display stored embeddings in the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all embeddings
        cursor.execute("SELECT trace_id, text, vector_json, created_at FROM embeddings")
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} stored embeddings:")
        print("-" * 50)
        
        for row in rows:
            trace_id, text, vector_json, created_at = row
            vector = json.loads(vector_json)
            print(f"Trace ID: {trace_id}")
            print(f"Text: {text}")
            print(f"Vector length: {len(vector)}")
            print(f"Created at: {created_at}")
            print("-" * 30)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error checking stored embeddings: {e}")
        return False

if __name__ == "__main__":
    check_stored_embeddings()