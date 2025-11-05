"""
Message Encryption Module
Provides encryption/decryption for secure message storage
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional

# Secret key from environment or generate one
SECRET_KEY = os.getenv("ENCRYPTION_SECRET_KEY", "university-secure-messages-2025")
SALT = b'university_salt_2025'  # In production, use environment variable


class MessageEncryption:
    """Handles message encryption and decryption"""
    
    def __init__(self):
        # Generate a key from the secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=SALT,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, message: str) -> str:
        """
        Encrypt a message
        
        Args:
            message: Plain text message
            
        Returns:
            Encrypted message as base64 string
        """
        if not message:
            return ""
        
        try:
            encrypted_bytes = self.cipher.encrypt(message.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"Encryption error: {e}")
            # In case of error, return original (not recommended for production)
            return message
    
    def decrypt(self, encrypted_message: str) -> str:
        """
        Decrypt a message
        
        Args:
            encrypted_message: Encrypted message as base64 string
            
        Returns:
            Decrypted plain text message
        """
        if not encrypted_message:
            return ""
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_message.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            # If decryption fails, message might not be encrypted (backward compatibility)
            return encrypted_message
    
    def is_encrypted(self, text: str) -> bool:
        """
        Check if text appears to be encrypted
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be encrypted
        """
        try:
            # Encrypted messages start with specific prefix
            return text.startswith('gAAAAA')
        except:
            return False


# Singleton instance
encryption = MessageEncryption()


def encrypt_message(message: str) -> str:
    """Encrypt a message (convenience function)"""
    return encryption.encrypt(message)


def decrypt_message(encrypted_message: str) -> str:
    """Decrypt a message (convenience function)"""
    return encryption.decrypt(encrypted_message)


def is_message_encrypted(text: str) -> bool:
    """Check if message is encrypted (convenience function)"""
    return encryption.is_encrypted(text)
