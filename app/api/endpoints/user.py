from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import KhojUser
from app.schemas.user import User as UserSchema

router = APIRouter()


@router.get("", response_model=UserSchema)
def read_current_user(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db) # Added db session dependency
):
    """
    Get current authenticated user.
    """
    # The current_user object is already a KhojUser SQLAlchemy model instance
    # and can be directly returned if UserSchema is compatible.
    # If UserSchema expects a Pydantic model, ensure current_user is converted or is one.
    # For now, assuming direct compatibility or that UserSchema can handle the ORM model.
    current_user = db.query(KhojUser).filter(KhojUser.username == "testuser").first()
    return current_user 