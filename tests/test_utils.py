"""
Unit tests for utility functions.

This file contains tests for string, math, and file utility functions.
All tests follow the same pattern as existing tests in the project.
"""

import sys
import os
import tempfile
import shutil

# Add the parent directory to the path so we can import utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from tests.utils import (
    trim, split, join, to_upper, to_lower, starts_with, ends_with,
    clamp, lerp, map_value, is_nearly_equal,
    file_exists, read_file, write_file, append_file
)


def test_string_utilities():
    """Test all string utility functions."""
    print("Testing string utilities...")
    
    # Test trim
    assert trim("  hello world  ") == "hello world"
    assert trim("no_spaces") == "no_spaces"
    assert trim("  ") == ""
    assert trim("") == ""
    
    # Test trim with invalid input
    try:
        trim(123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    # Test split
    assert split("a,b,c", ",") == ["a", "b", "c"]
    assert split("hello world") == ["hello", "world"]
    assert split("") == [""]
    assert split("a,,b", ",") == ["a", "", "b"]
    
    # Test split with invalid inputs
    try:
        split(123, ",")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        split("test", 123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    # Test join
    assert join(["a", "b", "c"], ",") == "a,b,c"
    assert join(["hello", "world"]) == "hello world"
    assert join([]) == ""
    assert join(["single"]) == "single"
    
    # Test join with invalid inputs
    try:
        join("not a list", ",")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        join(["a", "b"], 123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        join(["a", 123], ",")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    # Test to_upper
    assert to_upper("hello") == "HELLO"
    assert to_upper("Hello World") == "HELLO WORLD"
    assert to_upper("") == ""
    assert to_upper("ALREADY UPPER") == "ALREADY UPPER"
    
    # Test to_upper with invalid input
    try:
        to_upper(123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    # Test to_lower
    assert to_lower("HELLO") == "hello"
    assert to_lower("Hello World") == "hello world"
    assert to_lower("") == ""
    assert to_lower("already lower") == "already lower"
    
    # Test to_lower with invalid input
    try:
        to_lower(123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    # Test starts_with
    assert starts_with("hello world", "hello") == True
    assert starts_with("hello world", "world") == False
    assert starts_with("", "") == True
    assert starts_with("test", "") == True
    assert starts_with("test", "test") == True
    assert starts_with("test", "testing") == False
    
    # Test starts_with with invalid inputs
    try:
        starts_with(123, "test")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        starts_with("test", 123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    # Test ends_with
    assert ends_with("hello world", "world") == True
    assert ends_with("hello world", "hello") == False
    assert ends_with("", "") == True
    assert ends_with("test", "") == True
    assert ends_with("test", "test") == True
    assert ends_with("test", "testing") == False
    
    # Test ends_with with invalid inputs
    try:
        ends_with(123, "test")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        ends_with("test", 123)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    print("PASS: String utilities tests passed")


def test_math_utilities():
    """Test all math utility functions."""
    print("Testing math utilities...")
    
    # Test clamp
    assert clamp(5, 0, 10) == 5
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10
    assert clamp(5.5, 0.0, 10.0) == 5.5
    
    # Test clamp with invalid inputs
    try:
        clamp("not a number", 0, 10)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        clamp(5, "not a number", 10)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        clamp(5, 0, "not a number")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        clamp(5, 10, 0)  # min > max
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    # Test lerp
    assert lerp(0, 10, 0.5) == 5.0
    assert lerp(1, 5, 0.0) == 1
    assert lerp(1, 5, 1.0) == 5
    assert lerp(0, 0, 0.5) == 0
    assert lerp(-1, 1, 0.5) == 0.0
    assert lerp(1.5, 2.5, 0.5) == 2.0
    
    # Test lerp with invalid inputs
    try:
        lerp("not a number", 10, 0.5)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        lerp(0, "not a number", 0.5)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        lerp(0, 10, "not a number")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    # Test map_value
    assert map_value(5, 0, 10, 0, 100) == 50.0
    assert map_value(0, 0, 10, 0, 100) == 0.0
    assert map_value(10, 0, 10, 0, 100) == 100.0
    assert map_value(5, 0, 10, 100, 0) == 50.0  # reversed output range
    assert map_value(2.5, 0, 5, 0, 10) == 5.0
    assert map_value(-5, -10, 0, 0, 10) == 5.0
    
    # Test map_value with invalid inputs
    try:
        map_value("not a number", 0, 10, 0, 100)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        map_value(5, "not a number", 10, 0, 100)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        map_value(5, 0, 10, "not a number", 100)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        map_value(5, 0, 0, 0, 100)  # in_min == in_max
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    # Test is_nearly_equal
    assert is_nearly_equal(0.1 + 0.2, 0.3) == True
    assert is_nearly_equal(1.0, 1.0000000001, 1e-9) == True  # Within default epsilon
    assert is_nearly_equal(1.0, 2.0) == False
    assert is_nearly_equal(0, 0) == True
    assert is_nearly_equal(-1.0, -1.0) == True
    assert is_nearly_equal(1.0, 1.0, 0.0) == True  # exact comparison
    
    # Test is_nearly_equal with invalid inputs
    try:
        is_nearly_equal("not a number", 0.3)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        is_nearly_equal(0.1, "not a number")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        is_nearly_equal(0.1, 0.2, "not a number")  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
    
    try:
        is_nearly_equal(0.1, 0.2, -0.1)  # negative epsilon
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    print("PASS: Math utilities tests passed")


def test_file_utilities():
    """Test all file utility functions."""
    print("Testing file utilities...")
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.txt")
    test_content = "This is a test file.\nWith multiple lines."
    
    try:
        # Test file_exists on non-existent file
        assert file_exists(test_file) == False
        
        # Test write_file
        assert write_file(test_file, test_content) == True
        assert file_exists(test_file) == True
        
        # Test read_file
        content = read_file(test_file)
        assert content == test_content
        
        # Test read_file with non-existent file
        try:
            read_file(os.path.join(temp_dir, "nonexistent.txt"))
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected
        
        # Test read_file with invalid input
        try:
            read_file(123)  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected
        
        # Test write_file with invalid inputs
        try:
            write_file(123, "content")  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected
        
        try:
            write_file(test_file, 123)  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected
        
        # Test append_file
        additional_content = "\nAppended content."
        assert append_file(test_file, additional_content) == True
        
        # Check that content was appended
        content = read_file(test_file)
        assert content == test_content + additional_content
        
        # Test append_file with invalid inputs
        try:
            append_file(123, "content")  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected
        
        try:
            append_file(test_file, 123)  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected
        
        # Test file_exists with invalid input
        try:
            file_exists(123)  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected
        
        print("PASS: File utilities tests passed")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)


def test_edge_cases():
    """Test edge cases for all utility functions."""
    print("Testing edge cases...")
    
    # String utilities edge cases
    assert trim("") == ""
    assert trim("   ") == ""
    assert trim("\t\n hello \r\n") == "hello"  # whitespace characters
    
    assert split("", ",") == [""]
    assert split(",,,", ",") == ["", "", "", ""]  # empty parts
    assert split("no_delimiter", ",") == ["no_delimiter"]
    
    assert join([], ",") == ""
    assert join([""], ",") == ""
    assert join(["", "", ""], ",") == ",,"  # empty strings
    
    assert to_upper("") == ""
    assert to_upper("123!@#") == "123!@#"  # non-alphabetic characters
    
    assert to_lower("") == ""
    assert to_lower("123!@#") == "123!@#"  # non-alphabetic characters
    
    assert starts_with("", "") == True
    assert starts_with("test", "") == True  # empty prefix
    assert starts_with("", "test") == False  # empty string with non-empty prefix
    
    assert ends_with("", "") == True
    assert ends_with("test", "") == True  # empty suffix
    assert ends_with("", "test") == False  # empty string with non-empty suffix
    
    # Math utilities edge cases
    assert clamp(0, 0, 0) == 0  # all same values
    assert clamp(float('inf'), 0, 10) == 10  # infinity
    assert clamp(float('-inf'), 0, 10) == 0  # negative infinity
    
    assert lerp(0, 0, 0.5) == 0  # same start and end
    assert lerp(1, 5, -0.5) == -1.0  # negative t
    assert lerp(1, 5, 1.5) == 7.0  # t > 1.0
    
    assert map_value(0, 0, 1, 0, 1) == 0  # identity mapping
    assert map_value(1, 0, 1, 0, 1) == 1  # identity mapping
    
    assert is_nearly_equal(0.0, -0.0) == True  # positive and negative zero
    # Note: float('inf') == float('inf') is True, but float('nan') == float('nan') is False
    
    print("PASS: Edge cases tests passed")


def test_boundary_conditions():
    """Test boundary conditions for all utility functions."""
    print("Testing boundary conditions...")
    
    # Test with very large strings
    large_string = "a" * 10000
    assert trim(large_string) == large_string  # already trimmed
    assert len(split(large_string, "b")) == 1  # no delimiter
    assert join([large_string, large_string], "|") == large_string + "|" + large_string
    
    # Test with very large numbers
    large_num = 1e308
    assert clamp(large_num, 0, 1e307) == 1e307  # clamped to max
    assert lerp(0, large_num, 0.5) == large_num / 2
    assert map_value(large_num, 0, large_num, 0, 1) == 1.0
    
    # Test with very small numbers
    small_num = 1e-308
    assert is_nearly_equal(small_num, 0.0, 1e-300) == True  # within tolerance
    
    # Test with special float values
    # Note: NaN comparisons always return False
    assert is_nearly_equal(float('nan'), float('nan')) == False  # nan is not equal to itself
    
    print("PASS: Boundary conditions tests passed")


if __name__ == "__main__":
    # Run all tests
    try:
        test_string_utilities()
        test_math_utilities()
        test_file_utilities()
        test_edge_cases()
        test_boundary_conditions()
        print("\nAll utility tests passed! SUCCESS")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)