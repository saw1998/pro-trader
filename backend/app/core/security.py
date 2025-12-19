"""
Security Service Module

This module provides cryptographic utilities for the trading platform,
including password hashing, verification, and secure session ID generation.

Security Features:
- bcrypt password hashing with automatic salt generation
- Cryptographically secure session ID generation
- Protection against timing attacks
- Automatic handling of deprecated hash schemes

The module uses industry-standard security practices:
- bcrypt for password hashing (resistant to rainbow table attacks)
- secrets module for cryptographically secure random generation
- Passlib for hash scheme management and migration
"""

import secrets
from passlib.context import CryptContext

# Configure password hashing context with bcrypt
# bcrypt is chosen for its adaptive nature - it can be made slower as hardware improves
# 'deprecated="auto"' allows automatic migration from older hash schemes if needed
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


class SecurityService:
    """
    Provides cryptographic security utilities for the application.
    
    This service handles all security-related operations including:
    - Password hashing and verification
    - Session ID generation
    - Future: JWT token generation and validation
    
    All methods are static as they don't require instance state.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password using bcrypt.
        
        This method generates a cryptographically secure hash of the password
        with an automatically generated salt. The resulting hash is safe to
        store in the database.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            str: bcrypt hash string (includes salt and hash)
            
        Security Features:
            - Automatic salt generation (unique per password)
            - Configurable work factor (can be increased as hardware improves)
            - Resistant to rainbow table attacks
            - Timing attack resistant
            
        Example:
            hash = SecurityService.hash_password("mypassword123")
            # Returns: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Erfu8W"
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a stored hash.
        
        This method safely compares a plain text password with its stored
        bcrypt hash. It's designed to be resistant to timing attacks.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored bcrypt hash from database
            
        Returns:
            bool: True if password matches, False otherwise
            
        Security Features:
            - Constant-time comparison (timing attack resistant)
            - Automatic handling of different bcrypt variants
            - Safe against hash length extension attacks
            
        Example:
            is_valid = SecurityService.verify_password(
                "mypassword123", 
                "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Erfu8W"
            )
            # Returns: True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a cryptographically secure session ID.
        
        This method creates a URL-safe, base64-encoded random string
        suitable for use as a session identifier. The session ID is
        stored in Redis and used for user authentication.
        
        Returns:
            str: 32-byte random string, base64-encoded (43 characters)
            
        Security Features:
            - Cryptographically secure random number generation
            - URL-safe base64 encoding (no padding characters)
            - 256 bits of entropy (2^256 possible values)
            - Suitable for use in URLs and HTTP headers
            
        Example:
            session_id = SecurityService.generate_session_id()
            # Returns: "dGhpcyBpcyBhIHNlY3VyZSBzZXNzaW9uIGlkZW50aWZpZXI"
            
        Note:
            The session ID should be treated as a secret and transmitted
            only over HTTPS connections. It should be stored securely
            and have an appropriate expiration time.
        """
        # Generate 32 bytes (256 bits) of cryptographically secure random data
        # Convert to URL-safe base64 string (no padding, safe for URLs)
        return secrets.token_urlsafe(32)