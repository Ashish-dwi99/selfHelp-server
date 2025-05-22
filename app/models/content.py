import uuid
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.db.database import Base


class FileObject(Base):
    """File object model."""
    __tablename__ = "file_objects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    file_name = Column(String, nullable=True)
    raw_text = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="file_objects")
    agent = relationship("Agent", backref="file_objects")
    entries = relationship("Entry", back_populates="file_object")


class Entry(Base):
    """Entry model for search index."""
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    search_model_id = Column(Integer, ForeignKey("search_model_configs.id"), nullable=True)
    file_object_id = Column(Integer, ForeignKey("file_objects.id"), nullable=True)
    embeddings = Column(Text)  # Serialized vector embeddings
    raw = Column(Text)
    compiled = Column(Text)
    heading = Column(String, nullable=True)
    file_source = Column(String, default="computer")
    file_type = Column(String, default="plaintext")
    file_path = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    url = Column(String, nullable=True)
    hashed_value = Column(String)
    corpus_id = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="entries")
    agent = relationship("Agent", backref="entries")
    search_model = relationship("SearchModelConfig", back_populates="entries")
    file_object = relationship("FileObject", back_populates="entries")
    dates = relationship("EntryDates", back_populates="entry", cascade="all, delete-orphan")


class EntryDates(Base):
    """Entry dates model."""
    __tablename__ = "entry_dates"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"))
    date = Column(Date)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    entry = relationship("Entry", back_populates="dates")
