"""
Utility functions for string, math, and file operations.

This module provides common utility functions that are used throughout the project.
All functions are designed to be robust, handle edge cases, and provide clear error messages.
"""

import os
from typing import List, Union, Any


# String utilities
def trim(s: str) -> str:
    """
    Remove leading and trailing whitespace from a string.
    
    Args:
        s (str): Input string to trim
        
    Returns:
        str: String with leading and trailing whitespace removed
        
    Examples:
        >>> trim("  hello world  ")
        'hello world'
        >>> trim("no_spaces")
        'no_spaces'
        >>> trim("  ")
        ''
    """
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s.strip()


def split(s: str, delimiter: str = " ") -> List[str]:
    """
    Split a string into a list of substrings using the specified delimiter.
    
    Args:
        s (str): Input string to split
        delimiter (str): Delimiter to split on (default: space)
        
    Returns:
        List[str]: List of substrings
        
    Examples:
        >>> split("a,b,c", ",")
        ['a', 'b', 'c']
        >>> split("hello world")
        ['hello', 'world']
        >>> split("")
        ['']
    """
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    if not isinstance(delimiter, str):
        raise TypeError("Delimiter must be a string")
    return s.split(delimiter)


def join(strings: List[str], delimiter: str = " ") -> str:
    """
    Join a list of strings into a single string using the specified delimiter.
    
    Args:
        strings (List[str]): List of strings to join
        delimiter (str): Delimiter to use between strings (default: space)
        
    Returns:
        str: Joined string
        
    Examples:
        >>> join(["a", "b", "c"], ",")
        'a,b,c'
        >>> join(["hello", "world"])
        'hello world'
        >>> join([])
        ''
    """
    if not isinstance(strings, list):
        raise TypeError("Input must be a list")
    if not isinstance(delimiter, str):
        raise TypeError("Delimiter must be a string")
    # Validate that all elements are strings
    for i, item in enumerate(strings):
        if not isinstance(item, str):
            raise TypeError(f"All list elements must be strings, got {type(item)} at index {i}")
    return delimiter.join(strings)


def to_upper(s: str) -> str:
    """
    Convert a string to uppercase.
    
    Args:
        s (str): Input string to convert
        
    Returns:
        str: Uppercase string
        
    Examples:
        >>> to_upper("hello")
        'HELLO'
        >>> to_upper("Hello World")
        'HELLO WORLD'
        >>> to_upper("")
        ''
    """
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s.upper()


def to_lower(s: str) -> str:
    """
    Convert a string to lowercase.
    
    Args:
        s (str): Input string to convert
        
    Returns:
        str: Lowercase string
        
    Examples:
        >>> to_lower("HELLO")
        'hello'
        >>> to_lower("Hello World")
        'hello world'
        >>> to_lower("")
        ''
    """
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s.lower()


def starts_with(s: str, prefix: str) -> bool:
    """
    Check if a string starts with the specified prefix.
    
    Args:
        s (str): Input string to check
        prefix (str): Prefix to check for
        
    Returns:
        bool: True if string starts with prefix, False otherwise
        
    Examples:
        >>> starts_with("hello world", "hello")
        True
        >>> starts_with("hello world", "world")
        False
        >>> starts_with("", "")
        True
    """
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    if not isinstance(prefix, str):
        raise TypeError("Prefix must be a string")
    return s.startswith(prefix)


def ends_with(s: str, suffix: str) -> bool:
    """
    Check if a string ends with the specified suffix.
    
    Args:
        s (str): Input string to check
        suffix (str): Suffix to check for
        
    Returns:
        bool: True if string ends with suffix, False otherwise
        
    Examples:
        >>> ends_with("hello world", "world")
        True
        >>> ends_with("hello world", "hello")
        False
        >>> ends_with("", "")
        True
    """
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    if not isinstance(suffix, str):
        raise TypeError("Suffix must be a string")
    return s.endswith(suffix)


# Math utilities
def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """
    Clamp a value between a minimum and maximum value.
    
    Args:
        value (Union[int, float]): Value to clamp
        min_val (Union[int, float]): Minimum allowed value
        max_val (Union[int, float]): Maximum allowed value
        
    Returns:
        Union[int, float]: Clamped value
        
    Examples:
        >>> clamp(5, 0, 10)
        5
        >>> clamp(-5, 0, 10)
        0
        >>> clamp(15, 0, 10)
        10
    """
    if not isinstance(value, (int, float)):
        raise TypeError("Value must be a number")
    if not isinstance(min_val, (int, float)):
        raise TypeError("Min value must be a number")
    if not isinstance(max_val, (int, float)):
        raise TypeError("Max value must be a number")
    if min_val > max_val:
        raise ValueError("Min value cannot be greater than max value")
    return max(min_val, min(value, max_val))


def lerp(a: Union[int, float], b: Union[int, float], t: Union[int, float]) -> Union[int, float]:
    """
    Linear interpolation between two values.
    
    Args:
        a (Union[int, float]): Start value
        b (Union[int, float]): End value
        t (Union[int, float]): Interpolation factor (0.0 to 1.0)
        
    Returns:
        Union[int, float]: Interpolated value
        
    Examples:
        >>> lerp(0, 10, 0.5)
        5.0
        >>> lerp(1, 5, 0.0)
        1
        >>> lerp(1, 5, 1.0)
        5
    """
    if not isinstance(a, (int, float)):
        raise TypeError("Start value must be a number")
    if not isinstance(b, (int, float)):
        raise TypeError("End value must be a number")
    if not isinstance(t, (int, float)):
        raise TypeError("Interpolation factor must be a number")
    return a + (b - a) * t


def map_value(value: Union[int, float], in_min: Union[int, float], in_max: Union[int, float], 
              out_min: Union[int, float], out_max: Union[int, float]) -> Union[int, float]:
    """
    Map a value from one range to another.
    
    Args:
        value (Union[int, float]): Value to map
        in_min (Union[int, float]): Input range minimum
        in_max (Union[int, float]): Input range maximum
        out_min (Union[int, float]): Output range minimum
        out_max (Union[int, float]): Output range maximum
        
    Returns:
        Union[int, float]: Mapped value
        
    Examples:
        >>> map_value(5, 0, 10, 0, 100)
        50.0
        >>> map_value(0, 0, 10, 0, 100)
        0.0
        >>> map_value(10, 0, 10, 0, 100)
        100.0
    """
    if not isinstance(value, (int, float)):
        raise TypeError("Value must be a number")
    if not isinstance(in_min, (int, float)):
        raise TypeError("Input min must be a number")
    if not isinstance(in_max, (int, float)):
        raise TypeError("Input max must be a number")
    if not isinstance(out_min, (int, float)):
        raise TypeError("Output min must be a number")
    if not isinstance(out_max, (int, float)):
        raise TypeError("Output max must be a number")
    if in_min == in_max:
        raise ValueError("Input min and max cannot be equal")
        
    # Map value from input range to output range
    return out_min + (out_max - out_min) * (value - in_min) / (in_max - in_min)


def is_nearly_equal(a: Union[int, float], b: Union[int, float], epsilon: float = 1e-9) -> bool:
    """
    Check if two floating point numbers are nearly equal within a tolerance.
    
    Args:
        a (Union[int, float]): First number
        b (Union[int, float]): Second number
        epsilon (float): Tolerance for comparison (default: 1e-9)
        
    Returns:
        bool: True if numbers are nearly equal, False otherwise
        
    Examples:
        >>> is_nearly_equal(0.1 + 0.2, 0.3)
        True
        >>> is_nearly_equal(1.0, 1.000000001)
        True
        >>> is_nearly_equal(1.0, 2.0)
        False
    """
    if not isinstance(a, (int, float)):
        raise TypeError("First value must be a number")
    if not isinstance(b, (int, float)):
        raise TypeError("Second value must be a number")
    if not isinstance(epsilon, (int, float)):
        raise TypeError("Epsilon must be a number")
    if epsilon < 0:
        raise ValueError("Epsilon must be non-negative")
    return abs(a - b) <= epsilon


# File utilities
def file_exists(path: str) -> bool:
    """
    Check if a file exists at the specified path.
    
    Args:
        path (str): Path to check
        
    Returns:
        bool: True if file exists, False otherwise
        
    Examples:
        >>> file_exists("nonexistent.txt")
        False
        >>> file_exists(__file__)
        True
    """
    if not isinstance(path, str):
        raise TypeError("Path must be a string")
    return os.path.isfile(path)


def read_file(path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        path (str): Path to the file to read
        
    Returns:
        str: Contents of the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    if not isinstance(path, str):
        raise TypeError("Path must be a string")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except Exception as e:
        raise IOError(f"Error reading file {path}: {e}")


def write_file(path: str, content: str) -> bool:
    """
    Write content to a file, overwriting if it exists.
    
    Args:
        path (str): Path to the file to write
        content (str): Content to write to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not isinstance(path, str):
        raise TypeError("Path must be a string")
    if not isinstance(content, str):
        raise TypeError("Content must be a string")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file {path}: {e}")
        return False


def append_file(path: str, content: str) -> bool:
    """
    Append content to a file.
    
    Args:
        path (str): Path to the file to append to
        content (str): Content to append to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not isinstance(path, str):
        raise TypeError("Path must be a string")
    if not isinstance(content, str):
        raise TypeError("Content must be a string")
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error appending to file {path}: {e}")
        return False


# Example usage (for doctest)
if __name__ == "__main__":
    import doctest
    doctest.testmod()