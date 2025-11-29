# Tests

This directory contains unit tests for utility functions used in the EmbedCore v3 system.

## Test Files

- [test_utils.py](file:///c:/Users/Acer%20Aspire%203/Downloads/secure_Embeddings-main/secure_Embeddings-main/tests/test_utils.py) - Tests for string, math, and file utility functions

## Running Tests

To run all tests:

```bash
python tests/test_utils.py
```

## Test Coverage

The tests cover:

### String Utilities
- `trim()` - Remove leading and trailing whitespace
- `split()` - Split strings by delimiter
- `join()` - Join list of strings with delimiter
- `to_upper()` - Convert string to uppercase
- `to_lower()` - Convert string to lowercase
- `starts_with()` - Check if string starts with prefix
- `ends_with()` - Check if string ends with suffix

### Math Utilities
- `clamp()` - Clamp value between min and max
- `lerp()` - Linear interpolation
- `map_value()` - Map value from one range to another
- `is_nearly_equal()` - Compare floating point numbers with tolerance

### File Utilities
- `file_exists()` - Check if file exists
- `read_file()` - Read file contents
- `write_file()` - Write content to file
- `append_file()` - Append content to file

## Test Types

All tests include:
- Normal case testing
- Edge case testing
- Invalid input testing
- Boundary condition testing
- Performance-neutral testing

The tests follow the same pattern as existing tests in the project and do not require any changes to existing APIs.