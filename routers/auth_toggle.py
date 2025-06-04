from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from database import models, schemas, adapters
from database.models import get_db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create router
router = APIRouter(prefix="/auth-toggle", tags=["Authentication Toggle"])

# Authentication bypass configuration
AUTH_BYPASS_ENABLED = os.getenv("AUTH_BYPASS_ENABLED", "false").lower() == "true"
BYPASS_USERNAME = "test_user"

@router.get("/status")
async def get_auth_toggle_status():
    """Get the current authentication bypass status"""
    return {
        "auth_bypass_enabled": AUTH_BYPASS_ENABLED,
        "bypass_username": BYPASS_USERNAME if AUTH_BYPASS_ENABLED else None
    }

@router.post("/enable")
async def enable_auth_bypass(db: Session = Depends(get_db)):
    """Enable authentication bypass for testing"""
    global AUTH_BYPASS_ENABLED
    AUTH_BYPASS_ENABLED = True
    
    # Ensure test user exists
    test_user = adapters.get_user_by_username(db, BYPASS_USERNAME)
    if not test_user:
        # Create test user
        from utils.auth import get_password_hash
        db_user = models.KhojUser(
            username=BYPASS_USERNAME,
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_superuser=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create default subscription
        subscription = models.Subscription(
            user_id=db_user.id,
            type="standard",
            is_recurring=False
        )
        db.add(subscription)
        db.commit()
    
    # Update environment variable
    os.environ["AUTH_BYPASS_ENABLED"] = "true"
    
    return {"status": "success", "auth_bypass_enabled": True, "bypass_username": BYPASS_USERNAME}

@router.post("/disable")
async def disable_auth_bypass():
    """Disable authentication bypass"""
    global AUTH_BYPASS_ENABLED
    AUTH_BYPASS_ENABLED = False
    
    # Update environment variable
    os.environ["AUTH_BYPASS_ENABLED"] = "false"
    
    return {"status": "success", "auth_bypass_enabled": False}

@router.get("/test")
async def test_auth_bypass(db: Session = Depends(get_db)):
    """Test if authentication bypass is working"""
    if not AUTH_BYPASS_ENABLED:
        return {
            "status": "disabled",
            "message": "Authentication bypass is disabled. Enable it first."
        }
    
    # Check if test user exists
    test_user = adapters.get_user_by_username(db, BYPASS_USERNAME)
    if not test_user:
        return {
            "status": "error",
            "message": f"Test user '{BYPASS_USERNAME}' not found. Enable bypass first to create it."
        }
    
    return {
        "status": "success",
        "message": "Authentication bypass is working correctly",
        "user": {
            "id": test_user.id,
            "username": test_user.username,
            "email": test_user.email
        }
    }
