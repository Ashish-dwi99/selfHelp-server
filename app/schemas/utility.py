from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ClientApplicationBase(BaseModel):
    name: str
    client_id: str
    client_secret: str


class ClientApplicationCreate(ClientApplicationBase):
    pass


class ClientApplication(ClientApplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProcessLockBase(BaseModel):
    name: str
    max_duration_in_seconds: int = 43200  # 12 hours


class ProcessLockCreate(ProcessLockBase):
    pass


class ProcessLock(ProcessLockBase):
    id: int
    started_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserRequestsBase(BaseModel):
    slug: str


class UserRequestsCreate(UserRequestsBase):
    user_id: int


class UserRequests(UserRequestsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RateLimitRecordBase(BaseModel):
    identifier: str
    slug: str


class RateLimitRecordCreate(RateLimitRecordBase):
    pass


class RateLimitRecord(RateLimitRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DataStoreBase(BaseModel):
    key: str
    value: dict = Field(default_factory=dict)
    private: bool = False


class DataStoreCreate(DataStoreBase):
    owner_id: Optional[int] = None


class DataStore(DataStoreBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
