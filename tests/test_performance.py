"""
Performance test suite for EmbedCore v3.

This file contains performance benchmarks for the embedding generation and obfuscation functions.
"""

import sys
import os
import time
import platform
import subprocess

# Add the parent directory to the path so we can import embedcore_v3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embedcore_v3 import generate_embedding, obfuscate


def test_embedding_performance_1000():
    """
    Performance test for generating and obfuscating 1000 embeddings.
    
    This test measures the performance of the EmbedCore v3 system by generating
    1000 embeddings and obfuscating them with a deterministic user key.
    
    The test measures:
    - Total time for 1000 operations
    - Average time per operation
    
    Results are written to perf_results.md in the project root.
    """
    # Fixed message for testing
    test_message = "performance test message"
    
    # Deterministic user key for testing
    user_key = "perf-key"
    
    # Start timing
    start_time = time.perf_counter()
    
    # Generate and obfuscate 1000 embeddings
    for i in range(1000):
        # Generate embedding
        embedding = generate_embedding(test_message)
        
        # Obfuscate embedding
        obfuscated = obfuscate(embedding, user_key)
    
    # End timing
    end_time = time.perf_counter()
    
    # Calculate total time in milliseconds
    total_time_ms = (end_time - start_time) * 1000
    
    # Calculate average time per embedding in milliseconds
    avg_time_ms = total_time_ms / 1000
    
    # Get system information
    python_version = sys.version.split()[0]
    os_info = platform.platform()
    cpu_info = platform.processor() or "Unknown CPU"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    
    # Create perf_results.md content
    perf_results_content = f"""# EmbedCore v3 Performance Benchmark

Total embeddings: 1000
Total time: {total_time_ms:.2f} ms
Average per embedding: {avg_time_ms:.4f} ms

Environment:
- Python version: {python_version}
- OS: {os_info}
- CPU info: {cpu_info}
- Timestamp: {timestamp}
"""
    
    # Write results to perf_results.md in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    perf_results_path = os.path.join(project_root, "perf_results.md")
    
    try:
        with open(perf_results_path, "w") as f:
            f.write(perf_results_content)
        print(f"Performance results written to {perf_results_path}")
    except Exception as e:
        print(f"Failed to write performance results: {e}")
        # Still pass the test even if we can't write the file
        pass
    
    # Print summary to console
    print(f"Performance Test Results:")
    print(f"  Total time: {total_time_ms:.2f} ms")
    print(f"  Average per embedding: {avg_time_ms:.4f} ms")


if __name__ == "__main__":
    # Run the performance test
    try:
        test_embedding_performance_1000()
        print("Performance test completed successfully!")
    except Exception as e:
        print(f"Performance test failed: {e}")
        sys.exit(1)