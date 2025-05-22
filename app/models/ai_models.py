import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.db.database import Base


class AiModelApi(Base):
    """AI model API configuration."""
    __tablename__ = "ai_model_apis"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    api_key = Column(String)
    api_base_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    chat_models = relationship("ChatModel", back_populates="ai_model_api")
    text_to_image_models = relationship("TextToImageModelConfig", back_populates="ai_model_api")
    speech_to_text_models = relationship("SpeechToTextModelOptions", back_populates="ai_model_api")


class ChatModel(Base):
    """Chat model configuration."""
    __tablename__ = "chat_models"

    id = Column(Integer, primary_key=True, index=True)
    ai_model_api_id = Column(Integer, ForeignKey("ai_model_apis.id"), nullable=True)
    max_prompt_size = Column(Integer, nullable=True)
    subscribed_max_prompt_size = Column(Integer, nullable=True)
    tokenizer = Column(String, nullable=True)
    name = Column(String, default="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF")
    model_type = Column(String, default="offline")  # offline, openai, anthropic, google
    price_tier = Column(String, default="free")  # free, standard
    vision_enabled = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    strengths = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    ai_model_api = relationship("AiModelApi", back_populates="chat_models")
    agents = relationship("Agent", back_populates="chat_model")


class SearchModelConfig(Base):
    """Search model configuration."""
    __tablename__ = "search_model_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="default")
    model_type = Column(String, default="text")
    bi_encoder = Column(String, default="thenlper/gte-small")
    bi_encoder_model_config = Column(SQLiteJSON, default=dict)
    bi_encoder_query_encode_config = Column(SQLiteJSON, default=dict)
    bi_encoder_docs_encode_config = Column(SQLiteJSON, default=dict)
    cross_encoder = Column(String, default="mixedbread-ai/mxbai-rerank-xsmall-v1")
    cross_encoder_model_config = Column(SQLiteJSON, default=dict)
    embeddings_inference_endpoint = Column(String, nullable=True)
    embeddings_inference_endpoint_api_key = Column(String, nullable=True)
    embeddings_inference_endpoint_type = Column(String, default="local")
    cross_encoder_inference_endpoint = Column(String, nullable=True)
    cross_encoder_inference_endpoint_api_key = Column(String, nullable=True)
    bi_encoder_confidence_threshold = Column(Integer, default=0.18)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    entries = relationship("Entry", back_populates="search_model")


class TextToImageModelConfig(Base):
    """Text-to-image model configuration."""
    __tablename__ = "text_to_image_model_configs"

    id = Column(Integer, primary_key=True, index=True)
    ai_model_api_id = Column(Integer, ForeignKey("ai_model_apis.id"), nullable=True)
    model_name = Column(String, default="dall-e-3")
    model_type = Column(String, default="openai")  # openai, stability-ai, replicate, google
    price_tier = Column(String, default="free")  # free, standard
    api_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    ai_model_api = relationship("AiModelApi", back_populates="text_to_image_models")
    user_configs = relationship("UserTextToImageModelConfig", back_populates="setting")


class VoiceModelOption(Base):
    """Voice model option."""
    __tablename__ = "voice_model_options"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String)
    name = Column(String)
    price_tier = Column(String, default="standard")  # free, standard
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user_configs = relationship("UserVoiceModelConfig", back_populates="setting")


class SpeechToTextModelOptions(Base):
    """Speech-to-text model options."""
    __tablename__ = "speech_to_text_model_options"

    id = Column(Integer, primary_key=True, index=True)
    ai_model_api_id = Column(Integer, ForeignKey("ai_model_apis.id"), nullable=True)
    model_name = Column(String, default="base")
    model_type = Column(String, default="offline")  # openai, offline
    price_tier = Column(String, default="free")  # free, standard
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    ai_model_api = relationship("AiModelApi", back_populates="speech_to_text_models")


class ServerChatSettings(Base):
    """Server chat settings."""
    __tablename__ = "server_chat_settings"

    id = Column(Integer, primary_key=True, index=True)
    chat_default_id = Column(Integer, ForeignKey("chat_models.id"), nullable=True)
    chat_advanced_id = Column(Integer, ForeignKey("chat_models.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    chat_default = relationship("ChatModel", foreign_keys=[chat_default_id])
    chat_advanced = relationship("ChatModel", foreign_keys=[chat_advanced_id])
