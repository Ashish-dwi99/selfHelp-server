import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.db.database import Base


class Agent(Base):
    """Agent model."""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String)
    personality = Column(String, nullable=True)
    input_tools = Column(SQLiteJSON, default=list)
    output_modes = Column(SQLiteJSON, default=list)
    chat_model_id = Column(Integer, ForeignKey("chat_models.id"))
    style_color = Column(String, default="orange")
    style_icon = Column(String, default="Lightbulb")
    privacy_level = Column(String, default="private")
    is_hidden = Column(Boolean, default=False)
    managed_by_admin = Column(Boolean, default=False)
    slug = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("KhojUser", backref="created_agents")
    chat_model = relationship("ChatModel")
    conversations = relationship("Conversation", back_populates="agent")


class Conversation(Base):
    """Conversation model."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("client_applications.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    conversation_log = Column(SQLiteJSON, default=lambda: {"chat": []})
    slug = Column(String, nullable=True)
    title = Column(String, nullable=True)
    file_filters = Column(SQLiteJSON, default=list)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="conversations")
    agent = relationship("Agent", back_populates="conversations")
    client = relationship("ClientApplication", backref="conversations")


class PublicConversation(Base):
    """Public conversation model."""
    __tablename__ = "public_conversations"

    id = Column(Integer, primary_key=True, index=True)
    source_owner_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    conversation_log = Column(SQLiteJSON, default=lambda: {"chat": []})
    slug = Column(String, nullable=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    source_owner = relationship("KhojUser", backref="public_conversations")
    agent = relationship("Agent")


class UserConversationConfig(Base):
    """User conversation configuration model."""
    __tablename__ = "user_conversation_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    setting_id = Column(Integer, ForeignKey("chat_models.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="conversation_config")
    setting = relationship("ChatModel")


class UserVoiceModelConfig(Base):
    """User voice model configuration model."""
    __tablename__ = "user_voice_model_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    setting_id = Column(Integer, ForeignKey("voice_model_options.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="voice_model_config")
    setting = relationship("VoiceModelOption")


class UserTextToImageModelConfig(Base):
    """User text-to-image model configuration model."""
    __tablename__ = "user_text_to_image_model_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    setting_id = Column(Integer, ForeignKey("text_to_image_model_configs.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="text_to_image_model_config")
    setting = relationship("TextToImageModelConfig")


class ReflectiveQuestion(Base):
    """Reflective question model."""
    __tablename__ = "reflective_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("KhojUser", backref="reflective_questions")
