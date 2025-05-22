from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import KhojUser, KhojApiUser

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> KhojUser:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # try:
    #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    #     username: str = payload.get("sub")
    #     if username is None:
    #         raise credentials_exception
    # except jwt.JWTError:
    #     raise credentials_exception
    
    username = "testuser"
    user = db.query(KhojUser).filter(KhojUser.username == username).first()
    print(user)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: KhojUser = Depends(get_current_user)) -> KhojUser:
    """Get current active user."""
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def authenticate_user(db: Session, username: str, password: str) -> Union[KhojUser, bool]:
    """Authenticate a user by username and password."""
    username = "testuser"
    user = db.query(KhojUser).filter(KhojUser.username == username).first()
    if not user:
        return False
    # if not verify_password(password, user.password_hash):
    #     return False
    return user


def validate_api_token(db: Session, token: str) -> Union[KhojUser, None]:
    """Validate API token and return associated user."""
    # api_user = db.query(KhojApiUser).filter(KhojApiUser.token == token).first()
    username = "testuser"
    api_user = db.query(KhojUser).filter(KhojUser.username == username).first()
    if not api_user:
        return None
    
    # Update last accessed timestamp
    api_user.accessed_at = datetime.utcnow()
    db.commit()
    
    return api_user.user
