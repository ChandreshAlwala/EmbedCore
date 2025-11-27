# Secure Embeddings System

This document describes the secure embeddings system implemented in this repository, which includes deterministic embedding generation, secure obfuscation, and encrypted key storage.

## Components

### 1. EmbedCore v3 ([embedcore_v3.py](file:///c:/Users/Acer%20Aspire%203/Downloads/secure_Embeddings-main/secure_Embeddings-main/embedcore_v3.py))

Provides three core functions for secure embedding handling:

#### `generate_embedding(message_text)`
Generates a deterministic embedding vector from any text input:
- Uses a seeded random generator for deterministic output
- Produces a 384-dimensional vector (standard size)
- Normalized to unit length
- Same input always produces the same output
- Production-ready with proper error handling and logging

#### `obfuscate(embedding, user_key)`
Creates a reversible transformation of an embedding using a user key:
- Uses the user key to derive a deterministic transformation
- Transformation is completely reversible
- Does not use hashing (which is not reversible)
- Production-ready with input validation and error handling

#### `deobfuscate(obf_embedding, user_key)`
Reverses the obfuscation perfectly:
- Takes an obfuscated embedding and user key
- Restores the original embedding exactly
- Production-ready with input validation and error handling

### 2. KeyStore ([keystore.py](file:///c:/Users/Acer%20Aspire%203/Downloads/secure_Embeddings-main/secure_Embeddings-main/keystore.py))

Securely manages user encryption keys using Fernet symmetric encryption:

#### `generate_key(user_id)`
- Creates a new random key for a user
- Encrypts it with a master key
- Stores it in an encrypted database
- Production-ready with proper error handling and logging

#### `get_key(user_id)`
- Retrieves the encrypted key from database
- Decrypts it using the master key
- Returns the usable key for embedding operations
- Production-ready with proper error handling and logging

#### `rotate_key(user_id)`
- Replaces an old user key with a new one
- Updates storage securely
- Production-ready with proper error handling and logging

## Security Features

1. **Deterministic Embeddings**: Same text always produces the same embedding
2. **Reversible Obfuscation**: Embeddings can be obfuscated and de-obfuscated perfectly
3. **Encrypted Key Storage**: All user keys are encrypted at rest
4. **Key Rotation**: Keys can be rotated for enhanced security
5. **Fernet Encryption**: Industry-standard symmetric encryption for key protection
6. **Input Validation**: All functions validate inputs to prevent errors
7. **Error Handling**: Comprehensive error handling with meaningful messages
8. **Logging**: Detailed logging for monitoring and debugging

## Usage Examples

```python
from embedcore_v3 import generate_embedding, obfuscate, deobfuscate
from keystore import generate_key, get_key

# Generate a secure key for a user
user_key_bytes = generate_key("user123")
user_key = user_key_bytes.decode('utf-8')

# Create an embedding
embedding = generate_embedding("Hello, world!")

# Obfuscate it
obf_embedding = obfuscate(embedding, user_key)

# De-obfuscate it
restored_embedding = deobfuscate(obf_embedding, user_key)

# The round-trip should be perfect
assert embedding == restored_embedding
```

## Testing

Run the built-in tests to verify functionality:

```bash
python embedcore_v3.py
python keystore.py
python test_embedcore_v3.py
python test_integration.py
python demonstration.py
```

The dedicated test suite ([test_embedcore_v3.py](file:///c:/Users/Acer%20Aspire%203/Downloads/secure_Embeddings-main/secure_Embeddings-main/test_embedcore_v3.py)) includes specific tests for:
- Obfuscation reversibility (the critical requirement)
- Embedding determinism
- Full roundtrip process

## Dependencies

- `cryptography`: For Fernet encryption
- All other dependencies as listed in [requirements.txt](file:///c:/Users/Acer%20Aspire%203/Downloads/secure_Embeddings-main/secure_Embeddings-main/requirements.txt)

## Production Considerations

For production deployment, consider the following:

1. **Master Key Security**: The current implementation stores the master key in the database. 
   In production, use a more secure method such as:
   - Environment variables
   - Hardware security modules (HSM)
   - Cloud key management services (AWS KMS, Azure Key Vault, etc.)

2. **Database Security**: Ensure the keystore database file has appropriate file permissions.

3. **Monitoring**: The system includes logging for monitoring purposes.

4. **Error Handling**: All functions include proper error handling for robust operation.

5. **Scalability**: For high-volume applications, consider using a more robust database solution.