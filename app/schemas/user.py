from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: int
    uuid: str
    verified_email: bool
    verified_phone_number: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password_hash: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None


class ApiTokenCreate(BaseModel):
    name: str


class ApiToken(BaseModel):
    id: int
    token: str
    name: str
    accessed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class GoogleUserCreate(BaseModel):
    sub: str
    azp: str
    email: EmailStr
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None


class GoogleUser(GoogleUserCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class SubscriptionBase(BaseModel):
    type: str = Field(..., description="Subscription type: trial or standard")
    is_recurring: bool = False
    renewal_date: Optional[datetime] = None
    enabled_trial_at: Optional[datetime] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class Subscription(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
