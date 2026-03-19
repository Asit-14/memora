from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
 

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({'exp': expire, 'type': 'access'})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
 

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({'exp': expire, 'type': 'refresh'})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
 


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
