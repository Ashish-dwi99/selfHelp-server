from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.db.database import Base


class NotionConfig(Base):
    """Notion configuration model."""
    __tablename__ = "notion_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="notion_config")


class GithubConfig(Base):
    """GitHub configuration model."""
    __tablename__ = "github_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pat_token = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="github_config")
    repos = relationship("GithubRepoConfig", back_populates="github_config", cascade="all, delete-orphan")


class GithubRepoConfig(Base):
    """GitHub repository configuration model."""
    __tablename__ = "github_repo_configs"

    id = Column(Integer, primary_key=True, index=True)
    github_config_id = Column(Integer, ForeignKey("github_configs.id"))
    name = Column(String)
    owner = Column(String)
    branch = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    github_config = relationship("GithubConfig", back_populates="repos")


class WebScraper(Base):
    """Web scraper model."""
    __tablename__ = "web_scrapers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    type = Column(String, default="Jina")  # Jina, Firecrawl, Olostep, Direct
    api_key = Column(String, nullable=True)
    api_url = Column(String, nullable=True)
    priority = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
