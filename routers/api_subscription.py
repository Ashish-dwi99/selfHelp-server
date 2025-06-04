from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import models, schemas, adapters
from database.models import get_db
from routers.auth import get_current_active_user

# Create router
router = APIRouter(prefix="/subscription", tags=["Subscription"])

@router.get("/status")
async def get_subscription_status(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    subscription = adapters.get_subscription_by_user(db, current_user.id)
    if not subscription:
        # Create default subscription if not exists
        subscription = adapters.create_subscription(
            db, 
            schemas.SubscriptionCreate(
                user_id=current_user.id,
                type="standard",
                is_recurring=False
            )
        )
    
    return {
        "type": subscription.type,
        "is_recurring": subscription.is_recurring,
        "renewal_date": subscription.renewal_date,
        "enabled_trial_at": subscription.enabled_trial_at
    }

@router.post("/enable-trial")
async def enable_trial(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    subscription = adapters.get_subscription_by_user(db, current_user.id)
    if not subscription:
        subscription = adapters.create_subscription(
            db, 
            schemas.SubscriptionCreate(
                user_id=current_user.id,
                type="standard",
                is_recurring=False
            )
        )
    
    if subscription.type == "trial":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trial already enabled"
        )
    
    # Update subscription
    subscription = adapters.update_subscription(
        db,
        current_user.id,
        schemas.SubscriptionBase(
            type="trial",
            is_recurring=False,
            enabled_trial_at=datetime.now()
        )
    )
    
    return {
        "type": subscription.type,
        "is_recurring": subscription.is_recurring,
        "renewal_date": subscription.renewal_date,
        "enabled_trial_at": subscription.enabled_trial_at
    }

@router.post("/update")
async def update_subscription(
    subscription_update: schemas.SubscriptionBase,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    subscription = adapters.get_subscription_by_user(db, current_user.id)
    if not subscription:
        subscription = adapters.create_subscription(
            db, 
            schemas.SubscriptionCreate(
                user_id=current_user.id,
                **subscription_update.dict()
            )
        )
    else:
        subscription = adapters.update_subscription(
            db,
            current_user.id,
            subscription_update
        )
    
    return {
        "type": subscription.type,
        "is_recurring": subscription.is_recurring,
        "renewal_date": subscription.renewal_date,
        "enabled_trial_at": subscription.enabled_trial_at
    }
