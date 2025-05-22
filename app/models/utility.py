from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.db.database import Base


class ClientApplication(Base):
    """Client application model."""
    __tablename__ = "client_applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    client_id = Column(String, unique=True)
    client_secret = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ProcessLock(Base):
    """Process lock model."""
    __tablename__ = "process_locks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    max_duration_in_seconds = Column(Integer, default=43200)  # 12 hours
    started_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserRequests(Base):
    """User requests model."""
    __tablename__ = "user_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    slug = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="requests")


class RateLimitRecord(Base):
    """Rate limit record model."""
    __tablename__ = "rate_limit_records"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String)
    slug = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class DataStore(Base):
    """Data store model."""
    __tablename__ = "data_stores"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    key = Column(String)
    value = Column(SQLiteJSON, default=dict)
    private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("KhojUser", backref="data_stores")
