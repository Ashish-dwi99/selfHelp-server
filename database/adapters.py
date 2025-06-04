from sqlalchemy.orm import Session
from typing import List, Optional
from database import models, schemas
from fastapi import HTTPException, status
import uuid
from datetime import datetime

# User adapters
def get_user(db: Session, user_id: int) -> Optional[models.KhojUser]:
    return db.query(models.KhojUser).filter(models.KhojUser.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.KhojUser]:
    return db.query(models.KhojUser).filter(models.KhojUser.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.KhojUser]:
    return db.query(models.KhojUser).filter(models.KhojUser.username == username).first()

def get_user_by_uuid(db: Session, user_uuid: uuid.UUID) -> Optional[models.KhojUser]:
    return db.query(models.KhojUser).filter(models.KhojUser.uuid == user_uuid).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.KhojUser]:
    return db.query(models.KhojUser).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.KhojUser:
    from utils.auth import get_password_hash
    
    # Check if user already exists
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.KhojUser(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        uuid=uuid.uuid4()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default subscription
    create_subscription(db, schemas.SubscriptionCreate(user_id=db_user.id))
    
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> models.KhojUser:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(db_user)
    db.commit()
    return True

def set_user_name(db: Session, user_id: int, first_name: str, last_name: str) -> models.KhojUser:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_user.first_name = first_name
    db_user.last_name = last_name
    db.commit()
    db.refresh(db_user)
    return db_user

# Google user adapters
def get_google_user_by_sub(db: Session, sub: str) -> Optional[models.GoogleUser]:
    return db.query(models.GoogleUser).filter(models.GoogleUser.sub == sub).first()

def create_google_user(db: Session, google_user: schemas.GoogleUserCreate) -> models.GoogleUser:
    db_google_user = models.GoogleUser(**google_user.dict())
    db.add(db_google_user)
    db.commit()
    db.refresh(db_google_user)
    return db_google_user

# API token adapters
def get_api_token(db: Session, token: str) -> Optional[models.KhojApiUser]:
    return db.query(models.KhojApiUser).filter(models.KhojApiUser.token == token).first()

def get_api_tokens_by_user(db: Session, user_id: int) -> List[models.KhojApiUser]:
    return db.query(models.KhojApiUser).filter(models.KhojApiUser.user_id == user_id).all()

def create_api_token(db: Session, api_token: schemas.ApiTokenCreate) -> models.KhojApiUser:
    db_api_token = models.KhojApiUser(**api_token.dict())
    db.add(db_api_token)
    db.commit()
    db.refresh(db_api_token)
    return db_api_token

def update_api_token_access(db: Session, token: str) -> models.KhojApiUser:
    db_token = get_api_token(db, token)
    if db_token:
        db_token.accessed_at = datetime.now()
        db.commit()
        db.refresh(db_token)
    return db_token

def delete_api_token(db: Session, token_id: int) -> bool:
    db_token = db.query(models.KhojApiUser).filter(models.KhojApiUser.id == token_id).first()
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    db.delete(db_token)
    db.commit()
    return True

# Subscription adapters
def get_subscription(db: Session, subscription_id: int) -> Optional[models.Subscription]:
    return db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()

def get_subscription_by_user(db: Session, user_id: int) -> Optional[models.Subscription]:
    return db.query(models.Subscription).filter(models.Subscription.user_id == user_id).first()

def create_subscription(db: Session, subscription: schemas.SubscriptionCreate) -> models.Subscription:
    db_subscription = models.Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def update_subscription(db: Session, user_id: int, subscription: schemas.SubscriptionBase) -> models.Subscription:
    db_subscription = get_subscription_by_user(db, user_id)
    if not db_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Update subscription fields
    for key, value in subscription.dict(exclude_unset=True).items():
        setattr(db_subscription, key, value)
    
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

# AI Model API adapters
def get_ai_model_api(db: Session, api_id: int) -> Optional[models.AiModelApi]:
    return db.query(models.AiModelApi).filter(models.AiModelApi.id == api_id).first()

def get_ai_model_apis(db: Session, skip: int = 0, limit: int = 100) -> List[models.AiModelApi]:
    return db.query(models.AiModelApi).offset(skip).limit(limit).all()

def create_ai_model_api(db: Session, api: schemas.AiModelApiCreate) -> models.AiModelApi:
    db_api = models.AiModelApi(**api.dict())
    db.add(db_api)
    db.commit()
    db.refresh(db_api)
    return db_api

# Chat Model adapters
def get_chat_model(db: Session, model_id: int) -> Optional[models.ChatModel]:
    return db.query(models.ChatModel).filter(models.ChatModel.id == model_id).first()

def get_chat_models(db: Session, skip: int = 0, limit: int = 100) -> List[models.ChatModel]:
    return db.query(models.ChatModel).offset(skip).limit(limit).all()

def get_default_chat_model(db: Session) -> Optional[models.ChatModel]:
    server_settings = db.query(models.ServerChatSettings).first()
    if server_settings and server_settings.chat_default:
        return server_settings.chat_default
    return db.query(models.ChatModel).filter(models.ChatModel.model_type == "offline").first()

def create_chat_model(db: Session, model: schemas.ChatModelCreate) -> models.ChatModel:
    db_model = models.ChatModel(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

# Agent adapters
def get_agent(db: Session, agent_id: int) -> Optional[models.Agent]:
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()

def get_agent_by_slug(db: Session, slug: str) -> Optional[models.Agent]:
    return db.query(models.Agent).filter(models.Agent.slug == slug).first()

def get_agents_by_creator(db: Session, creator_id: int) -> List[models.Agent]:
    return db.query(models.Agent).filter(models.Agent.creator_id == creator_id).all()

def get_public_agents(db: Session) -> List[models.Agent]:
    return db.query(models.Agent).filter(models.Agent.privacy_level == "public", models.Agent.is_hidden == False).all()

def create_agent(db: Session, agent: schemas.AgentCreate) -> models.Agent:
    db_agent = models.Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def update_agent(db: Session, agent_id: int, agent: schemas.AgentBase) -> models.Agent:
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Update agent fields
    for key, value in agent.dict(exclude_unset=True).items():
        setattr(db_agent, key, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: int) -> bool:
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    db.delete(db_agent)
    db.commit()
    return True

def is_agent_accessible(db: Session, agent: models.Agent, user: models.KhojUser) -> bool:
    if agent.privacy_level == "public":
        return True
    if agent.creator_id == user.id:
        return True
    if agent.privacy_level == "protected" and user.is_superuser:
        return True
    return False

# Notion Config adapters
def get_notion_config(db: Session, config_id: int) -> Optional[models.NotionConfig]:
    return db.query(models.NotionConfig).filter(models.NotionConfig.id == config_id).first()

def get_notion_config_by_user(db: Session, user_id: int) -> Optional[models.NotionConfig]:
    return db.query(models.NotionConfig).filter(models.NotionConfig.user_id == user_id).first()

def create_notion_config(db: Session, config: schemas.NotionConfigCreate) -> models.NotionConfig:
    db_config = models.NotionConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

# GitHub Config adapters
def get_github_config(db: Session, config_id: int) -> Optional[models.GithubConfig]:
    return db.query(models.GithubConfig).filter(models.GithubConfig.id == config_id).first()

def get_github_config_by_user(db: Session, user_id: int) -> Optional[models.GithubConfig]:
    return db.query(models.GithubConfig).filter(models.GithubConfig.user_id == user_id).first()

def create_github_config(db: Session, config: schemas.GithubConfigCreate) -> models.GithubConfig:
    db_config = models.GithubConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

# GitHub Repo Config adapters
def get_github_repo_configs(db: Session, github_config_id: int) -> List[models.GithubRepoConfig]:
    return db.query(models.GithubRepoConfig).filter(models.GithubRepoConfig.github_config_id == github_config_id).all()

def create_github_repo_config(db: Session, config: schemas.GithubRepoConfigCreate) -> models.GithubRepoConfig:
    db_config = models.GithubRepoConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

# Web Scraper adapters
def get_web_scraper(db: Session, scraper_id: int) -> Optional[models.WebScraper]:
    return db.query(models.WebScraper).filter(models.WebScraper.id == scraper_id).first()

def get_web_scrapers(db: Session) -> List[models.WebScraper]:
    return db.query(models.WebScraper).order_by(models.WebScraper.priority).all()

def create_web_scraper(db: Session, scraper: schemas.WebScraperCreate) -> models.WebScraper:
    db_scraper = models.WebScraper(**scraper.dict())
    db.add(db_scraper)
    db.commit()
    db.refresh(db_scraper)
    return db_scraper

# Process Lock adapters
def get_process_lock(db: Session, name: str) -> Optional[models.ProcessLock]:
    return db.query(models.ProcessLock).filter(models.ProcessLock.name == name).first()

def create_process_lock(db: Session, lock: schemas.ProcessLockCreate) -> models.ProcessLock:
    db_lock = models.ProcessLock(**lock.dict())
    db.add(db_lock)
    db.commit()
    db.refresh(db_lock)
    return db_lock

def delete_process_lock(db: Session, name: str) -> bool:
    db_lock = get_process_lock(db, name)
    if not db_lock:
        return False
    
    db.delete(db_lock)
    db.commit()
    return True

# Speech to Text Model Options adapters
def get_speech_to_text_config(db: Session) -> Optional[models.SpeechToTextModelOptions]:
    return db.query(models.SpeechToTextModelOptions).first()

def create_speech_to_text_config(db: Session, config: schemas.SpeechToTextModelOptionsCreate) -> models.SpeechToTextModelOptions:
    db_config = models.SpeechToTextModelOptions(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

# Server Chat Settings adapters
def get_server_chat_settings(db: Session) -> Optional[models.ServerChatSettings]:
    return db.query(models.ServerChatSettings).first()

def create_server_chat_settings(db: Session, settings: schemas.ServerChatSettingsCreate) -> models.ServerChatSettings:
    db_settings = models.ServerChatSettings(**settings.dict())
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def update_server_chat_settings(db: Session, settings: schemas.ServerChatSettingsBase) -> models.ServerChatSettings:
    db_settings = get_server_chat_settings(db)
    if not db_settings:
        return create_server_chat_settings(db, settings)
    
    # Update settings fields
    for key, value in settings.dict(exclude_unset=True).items():
        setattr(db_settings, key, value)
    
    db.commit()
    db.refresh(db_settings)
    return db_settings

# Conversation adapters
def get_conversation(db: Session, conversation_id: int) -> Optional[models.Conversation]:
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()

def get_conversations_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Conversation]:
    return db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id
    ).order_by(models.Conversation.updated_at.desc()).offset(skip).limit(limit).all()

def create_conversation(db: Session, user_id: int, title: str = None) -> models.Conversation:
    conversation = models.Conversation(
        user_id=user_id,
        title=title or "New Conversation"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def save_conversation_message(
    db: Session,
    conversation_id: int,
    user_message: str,
    khoj_message: str,
    user_message_metadata: str = None,
    khoj_message_metadata: str = None,
    compiled_references: str = None
) -> models.ConversationMessage:
    message = models.ConversationMessage(
        conversation_id=conversation_id,
        user_message=user_message,
        khoj_message=khoj_message,
        user_message_metadata=user_message_metadata,
        khoj_message_metadata=khoj_message_metadata,
        compiled_references=compiled_references
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == user_id
    ).first()
    if not conversation:
        return False
    
    db.delete(conversation)
    db.commit()
    return True
