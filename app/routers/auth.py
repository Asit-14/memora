from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.user import UserCreate, UserLogin,UserResponse, TokenResponse,RefreshRequest

from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token,decode_token,create_refresh_token

from app.dependencies.auth import get_current_user,require_role


router =  APIRouter()
security =  HTTPBearer()

#   REGISTER ────
@router.post('/register', response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(400, 'Email already registered')

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(400, 'Username already taken')

    if not isinstance(user_data.password, str):
        raise HTTPException(400, 'Password must be a string')

    if len(user_data.password) > 72:
        raise HTTPException(400, 'Password too long (max 72 chars)')

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# ── LOGIN ───
@router.post('/login', response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
 
    # Same error for wrong email OR wrong password (prevents user enumeration)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid email or password')
 
    if not user.is_active:
        raise HTTPException(status_code=403, detail='Account is deactivated')
 
    token_data = {'sub': str(user.id), 'role': user.role}
    return {
        'access_token':  create_access_token(token_data),
        'refresh_token': create_refresh_token(token_data),
        'token_type':    'bearer'
    }


# ── GET CURRENT USER 

@router.get("/me",  response_model=UserResponse)
def get_me(current_user : User =  Depends(get_current_user)):
    return current_user

    
    
    




# ── REFRESH TOKEN ────────
@router.post('/refresh')
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
 
    if not payload or payload.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail='Invalid refresh token')
 
    user = db.query(User).filter(User.id == int(payload['sub'])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail='User not found')
 
    new_token = create_access_token({'sub': str(user.id), 'role': user.role})
    return {'access_token': new_token, 'token_type': 'bearer'}
 
 
# ── LOGOUT ────────────
@router.post('/logout')
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)   # ensures token is valid first
):
    token = credentials.credentials
    db.add(TokenBlacklist(token=token))
    db.commit()
    return {'message': 'Successfully logged out'}
 
 
# ── ADMIN ONLY ROUTE (example) ────────────────────────
@router.get('/admin/users')
def list_users(
    db: Session = Depends(get_db),
    admin = Depends(require_role('admin'))
):
    return db.query(User).all()
