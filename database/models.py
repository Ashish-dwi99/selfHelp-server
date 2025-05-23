from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.sql import func
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/khoj")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Helper function to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Base model with timestamp fields
class DbBaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# User model
class KhojUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    phone_number = Column(String, nullable=True)
    verified_phone_number = Column(Boolean, default=False)
    verified_email = Column(Boolean, default=False)
    email_verification_code = Column(String, nullable=True)
    email_verification_code_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    google_user = relationship("GoogleUser", back_populates="user", uselist=False)
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    api_tokens = relationship("KhojApiUser", back_populates="user")
    agents = relationship("Agent", back_populates="creator")
    notion_configs = relationship("NotionConfig", back_populates="user")
    github_configs = relationship("GithubConfig", back_populates="user")

# Google OAuth user model
class GoogleUser(Base):
    __tablename__ = "google_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    sub = Column(String)
    azp = Column(String)
    email = Column(String)
    name = Column(String, nullable=True)
    given_name = Column(String, nullable=True)
    family_name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    
    # Relationships
    user = relationship("KhojUser", back_populates="google_user")

# API token model
class KhojApiUser(DbBaseModel):
    __tablename__ = "api_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String, unique=True, index=True)
    name = Column(String)
    accessed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("KhojUser", back_populates="api_tokens")

# Subscription model
class Subscription(DbBaseModel):
    __tablename__ = "subscriptions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    type = Column(String, default="standard")  # trial, standard
    is_recurring = Column(Boolean, default=False)
    renewal_date = Column(DateTime, nullable=True)
    enabled_trial_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("KhojUser", back_populates="subscription")

# AI Model API model
class AiModelApi(DbBaseModel):
    __tablename__ = "ai_model_apis"
    
    name = Column(String)
    api_key = Column(String)
    api_base_url = Column(String, nullable=True)
    
    # Relationships
    chat_models = relationship("ChatModel", back_populates="ai_model_api")

# Chat model
class ChatModel(DbBaseModel):
    __tablename__ = "chat_models"
    
    max_prompt_size = Column(Integer, nullable=True)
    subscribed_max_prompt_size = Column(Integer, nullable=True)
    tokenizer = Column(String, nullable=True)
    name = Column(String, default="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF")
    model_type = Column(String, default="offline")  # openai, offline, anthropic, google
    price_tier = Column(String, default="free")  # free, standard
    vision_enabled = Column(Boolean, default=False)
    ai_model_api_id = Column(Integer, ForeignKey("ai_model_apis.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    
    # Relationships
    ai_model_api = relationship("AiModelApi", back_populates="chat_models")
    agents = relationship("Agent", back_populates="chat_model")

# Voice model option
class VoiceModelOption(DbBaseModel):
    __tablename__ = "voice_model_options"
    
    model_id = Column(String)
    name = Column(String)
    price_tier = Column(String, default="standard")  # free, standard

# Agent model
class Agent(DbBaseModel):
    __tablename__ = "agents"
    
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String)
    personality = Column(Text, nullable=True)
    input_tools = Column(ARRAY(String), default=list)
    output_modes = Column(ARRAY(String), default=list)
    managed_by_admin = Column(Boolean, default=False)
    chat_model_id = Column(Integer, ForeignKey("chat_models.id", ondelete="CASCADE"))
    slug = Column(String, unique=True)
    style_color = Column(String, default="orange")
    style_icon = Column(String, default="Lightbulb")
    privacy_level = Column(String, default="private")  # public, private, protected
    is_hidden = Column(Boolean, default=False)
    
    # Relationships
    creator = relationship("KhojUser", back_populates="agents")
    chat_model = relationship("ChatModel", back_populates="agents")

# Notion config model
class NotionConfig(DbBaseModel):
    __tablename__ = "notion_configs"
    
    token = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    user = relationship("KhojUser", back_populates="notion_configs")

# GitHub config model
class GithubConfig(DbBaseModel):
    __tablename__ = "github_configs"
    
    pat_token = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    user = relationship("KhojUser", back_populates="github_configs")
    repo_configs = relationship("GithubRepoConfig", back_populates="github_config")

# GitHub repo config model
class GithubRepoConfig(DbBaseModel):
    __tablename__ = "github_repo_configs"
    
    name = Column(String)
    owner = Column(String)
    branch = Column(String)
    github_config_id = Column(Integer, ForeignKey("github_configs.id", ondelete="CASCADE"))
    
    # Relationships
    github_config = relationship("GithubConfig", back_populates="repo_configs")

# Web scraper model
class WebScraper(DbBaseModel):
    __tablename__ = "web_scrapers"
    
    name = Column(String, nullable=True, unique=True)
    type = Column(String, default="Jina")  # Firecrawl, Olostep, Jina, Direct
    api_key = Column(String, nullable=True)
    api_url = Column(String, nullable=True)
    priority = Column(Integer, nullable=True, unique=True)

# Process lock model
class ProcessLock(DbBaseModel):
    __tablename__ = "process_locks"
    
    name = Column(String, unique=True)
    started_at = Column(DateTime, server_default=func.now())
    max_duration_in_seconds = Column(Integer, default=43200)  # 12 hours

# Speech to text model options
class SpeechToTextModelOptions(DbBaseModel):
    __tablename__ = "speech_to_text_model_options"
    
    class ModelType:
        OFFLINE = "offline"
        OPENAI = "openai"
    
    model_name = Column(String)
    model_type = Column(String)
    price_tier = Column(String, default="standard")  # free, standard
    ai_model_api_id = Column(Integer, ForeignKey("ai_model_apis.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    ai_model_api = relationship("AiModelApi")

# Server chat settings
class ServerChatSettings(DbBaseModel):
    __tablename__ = "server_chat_settings"
    
    chat_default_id = Column(Integer, ForeignKey("chat_models.id", ondelete="SET NULL"), nullable=True)
    chat_advanced_id = Column(Integer, ForeignKey("chat_models.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    chat_default = relationship("ChatModel", foreign_keys=[chat_default_id])
    chat_advanced = relationship("ChatModel", foreign_keys=[chat_advanced_id])

# Conversation model
class Conversation(DbBaseModel):
    __tablename__ = "conversations"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=True)
    slug = Column(String, nullable=True)
    
    # Relationships
    user = relationship("KhojUser")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")

# Conversation message model
class ConversationMessage(DbBaseModel):
    __tablename__ = "conversation_messages"
    
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    user_message = Column(Text)
    khoj_message = Column(Text)
    user_message_metadata = Column(Text, nullable=True)  # JSON
    khoj_message_metadata = Column(Text, nullable=True)  # JSON
    compiled_references = Column(Text, nullable=True)  # JSON
    
    # Relationships  
    conversation = relationship("Conversation", back_populates="messages")

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
