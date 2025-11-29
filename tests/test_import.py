"""
Simple import test for utility functions.
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from tests.utils import trim, clamp, file_exists

print('trim test:', repr(trim('  hello  ')))
print('clamp test:', clamp(15, 0, 10))
print('file_exists test:', file_exists('nonexistent.txt'))
print('All imports and basic tests successful!')