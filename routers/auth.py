from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

from database import models, schemas, adapters
from database.models import get_db
from utils.auth import authenticate_user, create_access_token, get_current_user, get_password_hash

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# Toggle for authentication bypass
AUTH_BYPASS_ENABLED = os.getenv("AUTH_BYPASS_ENABLED", "false").lower() == "true"

# Authentication bypass user
BYPASS_USER_ID = 1
BYPASS_USERNAME = "test_user"

# Helper function to get current active user with bypass option
async def get_current_active_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # Check if authentication bypass is enabled
    if AUTH_BYPASS_ENABLED:
        # Return a default test user
        db_user = adapters.get_user_by_username(db, BYPASS_USERNAME)
        if not db_user:
            # Create test user if it doesn't exist
            test_user = schemas.UserCreate(
                username=BYPASS_USERNAME,
                email="test@example.com",
                password="password123"
            )
            db_user = adapters.create_user(db, test_user)
        return db_user
    
    # Normal authentication flow
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = adapters.get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = adapters.create_user(db, user)
    return db_user

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.KhojUser = Depends(get_current_active_user)):
    return current_user

@router.post("/api-token", response_model=schemas.ApiToken)
async def create_api_token(
    token_data: schemas.ApiTokenBase,
    db: Session = Depends(get_db),
    current_user: models.KhojUser = Depends(get_current_active_user)
):
    api_token = schemas.ApiTokenCreate(
        name=token_data.name,
        token=token_data.token,
        user_id=current_user.id
    )
    return adapters.create_api_token(db, api_token)

@router.get("/api-tokens", response_model=List[schemas.ApiToken])
async def get_api_tokens(
    db: Session = Depends(get_db),
    current_user: models.KhojUser = Depends(get_current_active_user)
):
    return adapters.get_api_tokens_by_user(db, current_user.id)

@router.delete("/api-token/{token_id}")
async def delete_api_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: models.KhojUser = Depends(get_current_active_user)
):
    token = db.query(models.KhojApiUser).filter(
        models.KhojApiUser.id == token_id,
        models.KhojApiUser.user_id == current_user.id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found or not owned by user"
        )
    
    adapters.delete_api_token(db, token_id)
    return {"status": "success", "message": "Token deleted"}

@router.get("/status")
async def auth_status():
    """Get the current authentication status and configuration"""
    return {
        "auth_bypass_enabled": AUTH_BYPASS_ENABLED,
        "bypass_username": BYPASS_USERNAME if AUTH_BYPASS_ENABLED else None
    }

@router.post("/toggle-bypass")
async def toggle_auth_bypass(enable: bool):
    """Toggle authentication bypass (for development and testing only)"""
    global AUTH_BYPASS_ENABLED
    AUTH_BYPASS_ENABLED = enable
    return {"auth_bypass_enabled": AUTH_BYPASS_ENABLED}
