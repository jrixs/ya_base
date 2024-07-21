import bcrypt
import hashlib
from core.config import settings


def hash_password(password: str) -> str:
    """Хеширует пароль с помощью bcrypt и sha256, возвращает хеш."""
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    hashed_password = bcrypt.hashpw(
        sha256_hash.encode(),
        settings.salt.encode()).decode()
    return hashed_password


def check_password(password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли введенный пароль с хешированным."""
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    hashed_password_with_salt = bcrypt.hashpw(
        sha256_hash.encode(),
        settings.salt.encode()
        ).decode()
    return hashed_password_with_salt == hashed_password
