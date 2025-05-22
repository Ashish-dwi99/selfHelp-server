from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from app.core.config import settings
from app.core.security import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    get_current_user
)
from app.db.database import get_db
from app.models.user import KhojUser, KhojApiUser, Subscription
from app.schemas.user import (
    User, 
    UserCreate, 
    Token, 
    ApiTokenCreate, 
    ApiToken
)

router = APIRouter()


@router.post("/register", response_model=User)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username already exists
    db_user = db.query(KhojUser).filter(KhojUser.username == user_in.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user_in.email:
        db_user = db.query(KhojUser).filter(KhojUser.email == user_in.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = KhojUser(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_password,
        phone_number=user_in.phone_number,
        uuid=str(uuid.uuid4())
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default subscription
    subscription = Subscription(
        user_id=db_user.id,
        type="standard",
        is_recurring=False
    )
    db.add(subscription)
    db.commit()
    
    return db_user


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/api-token", response_model=ApiToken)
def create_api_token(
    token_in: ApiTokenCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API token for the current user."""
    # Generate a unique token
    token = str(uuid.uuid4())
    
    # Create new API token
    db_token = KhojApiUser(
        user_id=1,
        token=token,
        name=token_in.name
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token


@router.get("/api-tokens", response_model=list[ApiToken])
def get_api_tokens(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all API tokens for the current user."""
    tokens = db.query(KhojApiUser).filter(KhojApiUser.user_id == 1).all()
    return tokens


@router.delete("/api-token/{token_id}", response_model=ApiToken)
def delete_api_token(
    token_id: int,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API token."""
    token = db.query(KhojApiUser).filter(
        KhojApiUser.id == token_id,
        KhojApiUser.user_id == 1
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    db.delete(token)
    db.commit()
    
    return token
