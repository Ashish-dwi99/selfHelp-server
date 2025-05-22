from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class FileSourceType(str, Enum):
    COMPUTER = "computer"
    NOTION = "notion"
    GITHUB = "github"


class FileType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    PLAINTEXT = "plaintext"
    MARKDOWN = "markdown"
    ORG = "org"
    NOTION = "notion"
    GITHUB = "github"
    CONVERSATION = "conversation"
    DOCX = "docx"


class FileObjectBase(BaseModel):
    file_name: Optional[str] = None
    raw_text: str


class FileObjectCreate(FileObjectBase):
    user_id: Optional[int] = None
    agent_id: Optional[int] = None


class FileObject(FileObjectBase):
    id: int
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EntryBase(BaseModel):
    embeddings: str  # Serialized vector embeddings
    raw: str
    compiled: str
    heading: Optional[str] = None
    file_source: FileSourceType = FileSourceType.COMPUTER
    file_type: FileType = FileType.PLAINTEXT
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    url: Optional[str] = None
    hashed_value: str
    corpus_id: str


class EntryCreate(EntryBase):
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    search_model_id: Optional[int] = None
    file_object_id: Optional[int] = None


class Entry(EntryBase):
    id: int
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    search_model_id: Optional[int] = None
    file_object_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    dates: List["EntryDates"] = []

    class Config:
        orm_mode = True


class EntryDatesBase(BaseModel):
    date: date


class EntryDatesCreate(EntryDatesBase):
    entry_id: int


class EntryDates(EntryDatesBase):
    id: int
    entry_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Update forward references
Entry.update_forward_refs()
