from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

from app.core.exceptions import AuthenticationError


password_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    """
    Hashes a plain text password using Argon2id.
    """
    return password_hasher.hash(plain_password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    Returns True if valid, raises AuthenticationError if invalid.
    """
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        raise AuthenticationError("Invalid credentials.")