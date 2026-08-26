import hashlib

from app.core.config import settings


def hash_ip(ip: str) -> str:

    salt = settings.JWT_SECRET_KEY.get_secret_value()
    return hashlib.sha256(f"{ip}{salt}".encode()).hexdigest()