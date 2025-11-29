"""
Test runner for all utility tests.

This script runs all tests in the tests directory and provides a summary of results.
"""

import sys
import os
import subprocess

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def run_test_script(script_name):
    """Run a test script and return the result."""
    try:
        print(f"Running {script_name}...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode == 0:
            print(f"PASS: {script_name}")
            return True
        else:
            print(f"FAIL: {script_name}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: {script_name} failed with exception: {e}")
        return False

def main():
    """Run all test scripts."""
    print("Running all utility tests...\n")
    
    # Get the directory of this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of test scripts to run
    test_scripts = [
        "test_utils.py"
    ]
    
    # Run each test script
    passed = 0
    total = len(test_scripts)
    
    for script in test_scripts:
        script_path = os.path.join(test_dir, script)
        if os.path.exists(script_path):
            if run_test_script(script_path):
                passed += 1
        else:
            print(f"WARNING: {script} not found")
    
    # Print summary
    print(f"\nTest Results: {passed}/{total} test scripts passed")
    
    if passed == total:
        print("SUCCESS: All tests passed!")
        return 0
    else:
        print("FAILURE: Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())