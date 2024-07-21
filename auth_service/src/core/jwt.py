import jwt
from datetime import datetime, timedelta


def create_token(payload, secret_key, expires_in=15 * 60):
    """Создает access токен"""
    now = datetime.utcnow()
    exp = now + timedelta(seconds=expires_in)
    payload["iat"] = now
    payload["exp"] = exp
    return jwt.encode(payload, secret_key, algorithm='HS256')


def verify_token(token, secret_key):
    """Проверяет токен"""

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        # Проверяем время истечения
        if datetime.utcnow() >= datetime.fromtimestamp(decoded_token['exp']):
            return None  # Токен истек
        return decoded_token
    except jwt.exceptions.InvalidTokenError:
        return None


def get_secret_key(key):
    return f"{key}_Yandex" * 2
