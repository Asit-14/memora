from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.core.jwt import decode_token
 
security = HTTPBearer()
 
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
 
    # Token invalid or expired
    if not payload or payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
 
    # Check if token was blacklisted (logged out)
    blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    if blacklisted:
        raise HTTPException(status_code=401, detail='Token has been revoked')
 
    # Get user from DB
    user_id = payload.get('sub')
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail='User not found or inactive')
 
    return user
 
 
# Role-based access control — factory function
# Usage: Depends(require_role('admin'))  or  Depends(require_role('admin', 'moderator'))
def require_role(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Access denied. Required roles: {list(allowed_roles)}'
            )
        return current_user
    return role_checker
