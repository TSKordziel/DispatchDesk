from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM

def create_token(*, sub: str, token_type: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,               # user id as string
        "type": token_type,       # "access" or "refresh"
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])