from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
import uuid

# Base Pydantic model
class BaseModelSchema(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

# User schemas
class UserBase(BaseModelSchema):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModelSchema):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    verified_phone_number: Optional[bool] = None
    verified_email: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    uuid: uuid.UUID
    is_active: bool
    is_superuser: bool
    verified_phone_number: bool
    verified_email: bool
    created_at: datetime
    updated_at: datetime

class User(UserBase):
    id: int
    uuid: uuid.UUID
    is_active: bool
    is_superuser: bool
    verified_phone_number: bool
    verified_email: bool

# Google User schemas
class GoogleUserBase(BaseModelSchema):
    sub: str
    azp: str
    email: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None

class GoogleUserCreate(GoogleUserBase):
    user_id: int

class GoogleUserInDB(GoogleUserBase):
    id: int
    user_id: int

# API Token schemas
class ApiTokenBase(BaseModelSchema):
    name: str
    token: str

class ApiTokenCreate(ApiTokenBase):
    user_id: int

class ApiTokenInDB(ApiTokenBase):
    id: int
    user_id: int
    accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ApiToken(ApiTokenBase):
    id: int
    accessed_at: Optional[datetime] = None

# Subscription schemas
class SubscriptionBase(BaseModelSchema):
    type: str = "standard"
    is_recurring: bool = False
    renewal_date: Optional[datetime] = None
    enabled_trial_at: Optional[datetime] = None

class SubscriptionCreate(SubscriptionBase):
    user_id: int

class SubscriptionInDB(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class Subscription(SubscriptionBase):
    id: int

# AI Model API schemas
class AiModelApiBase(BaseModelSchema):
    name: str
    api_key: str
    api_base_url: Optional[str] = None

class AiModelApiCreate(AiModelApiBase):
    pass

class AiModelApiInDB(AiModelApiBase):
    id: int
    created_at: datetime
    updated_at: datetime

class AiModelApi(AiModelApiBase):
    id: int

# Chat Model schemas
class ChatModelBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: str
    model_type: str = "offline"
    price_tier: str = "free"
    vision_enabled: bool = False
    description: Optional[str] = None

class ChatModelCreate(ChatModelBase):
    ai_model_api_id: Optional[int] = None

class ChatModelInDB(ChatModelBase):
    id: int
    ai_model_api_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class ChatModel(ChatModelBase):
    id: int
    ai_model_api_id: Optional[int] = None
    ai_model_api: Optional[AiModelApi] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

# Voice Model Option schemas
class VoiceModelOptionBase(BaseModelSchema):
    model_id: str
    name: str
    price_tier: str = "standard"

class VoiceModelOptionCreate(VoiceModelOptionBase):
    pass

class VoiceModelOptionInDB(VoiceModelOptionBase):
    id: int
    created_at: datetime
    updated_at: datetime

class VoiceModelOption(VoiceModelOptionBase):
    id: int

# Agent schemas
class AgentBase(BaseModelSchema):
    name: str
    personality: Optional[str] = None
    input_tools: List[str] = []
    output_modes: List[str] = []
    managed_by_admin: bool = False
    slug: str
    style_color: str = "orange"
    style_icon: str = "Lightbulb"
    privacy_level: str = "private"
    is_hidden: bool = False

class AgentCreate(AgentBase):
    creator_id: Optional[int] = None
    chat_model_id: int

class AgentInDB(AgentBase):
    id: int
    creator_id: Optional[int] = None
    chat_model_id: int
    created_at: datetime
    updated_at: datetime

class Agent(AgentBase):
    id: int
    creator_id: Optional[int] = None
    chat_model_id: int
    chat_model: Optional[ChatModel] = None

# Notion Config schemas
class NotionConfigBase(BaseModelSchema):
    token: str

class NotionConfigCreate(NotionConfigBase):
    user_id: int

class NotionConfigInDB(NotionConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class NotionConfig(NotionConfigBase):
    id: int
    user_id: int

# GitHub Config schemas
class GithubConfigBase(BaseModelSchema):
    pat_token: str

class GithubConfigCreate(GithubConfigBase):
    user_id: int

class GithubConfigInDB(GithubConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class GithubConfig(GithubConfigBase):
    id: int
    user_id: int

# GitHub Repo Config schemas
class GithubRepoConfigBase(BaseModelSchema):
    name: str
    owner: str
    branch: str

class GithubRepoConfigCreate(GithubRepoConfigBase):
    github_config_id: int

class GithubRepoConfigInDB(GithubRepoConfigBase):
    id: int
    github_config_id: int
    created_at: datetime
    updated_at: datetime

class GithubRepoConfig(GithubRepoConfigBase):
    id: int
    github_config_id: int

# Web Scraper schemas
class WebScraperBase(BaseModelSchema):
    name: Optional[str] = None
    type: str = "Jina"
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    priority: Optional[int] = None

class WebScraperCreate(WebScraperBase):
    pass

class WebScraperInDB(WebScraperBase):
    id: int
    created_at: datetime
    updated_at: datetime

class WebScraper(WebScraperBase):
    id: int

# Process Lock schemas
class ProcessLockBase(BaseModelSchema):
    name: str
    max_duration_in_seconds: int = 43200  # 12 hours

class ProcessLockCreate(ProcessLockBase):
    pass

class ProcessLockInDB(ProcessLockBase):
    id: int
    started_at: datetime
    created_at: datetime
    updated_at: datetime

class ProcessLock(ProcessLockBase):
    id: int
    started_at: datetime

# Speech to Text Model Options schemas
class SpeechToTextModelOptionsBase(BaseModelSchema):
    model_name: str
    model_type: str
    price_tier: str = "standard"

class SpeechToTextModelOptionsCreate(SpeechToTextModelOptionsBase):
    ai_model_api_id: Optional[int] = None

class SpeechToTextModelOptionsInDB(SpeechToTextModelOptionsBase):
    id: int
    ai_model_api_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class SpeechToTextModelOptions(SpeechToTextModelOptionsBase):
    id: int
    ai_model_api_id: Optional[int] = None
    ai_model_api: Optional[AiModelApi] = None

# Server Chat Settings schemas
class ServerChatSettingsBase(BaseModelSchema):
    chat_default_id: Optional[int] = None
    chat_advanced_id: Optional[int] = None

class ServerChatSettingsCreate(ServerChatSettingsBase):
    pass

class ServerChatSettingsInDB(ServerChatSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ServerChatSettings(ServerChatSettingsBase):
    id: int
    chat_default: Optional[ChatModel] = None
    chat_advanced: Optional[ChatModel] = None

# Token schemas
class Token(BaseModelSchema):
    access_token: str
    token_type: str

class TokenData(BaseModelSchema):
    username: Optional[str] = None

# Search response schemas
class SearchResult(BaseModelSchema):
    entry_id: str
    content: str
    score: float
    source: str
    additional_metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModelSchema):
    results: List[SearchResult]
    query: str
    total_results: int

# Chat message schemas
class Context(BaseModelSchema):
    compiled: str
    file: str

class CodeContextFile(BaseModelSchema):
    filename: str
    b64_data: str

class CodeContextResult(BaseModelSchema):
    success: bool
    output_files: List[CodeContextFile]
    std_out: str
    std_err: str
    code_runtime: int

class CodeContextData(BaseModelSchema):
    code: str
    result: Optional[CodeContextResult] = None

class WebPage(BaseModelSchema):
    link: str
    query: Optional[str] = None
    snippet: str

class AnswerBox(BaseModelSchema):
    link: Optional[str] = None
    snippet: Optional[str] = None
    title: str
    snippetHighlighted: Optional[List[str]] = None

class PeopleAlsoAsk(BaseModelSchema):
    link: Optional[str] = None
    question: Optional[str] = None
    snippet: Optional[str] = None
    title: Optional[str] = None

class KnowledgeGraph(BaseModelSchema):
    attributes: Optional[Dict[str, str]] = None
    description: Optional[str] = None
    descriptionLink: Optional[str] = None
    descriptionSource: Optional[str] = None
    imageUrl: Optional[str] = None
    title: str
    type: Optional[str] = None

class OrganicContext(BaseModelSchema):
    snippet: str
    title: str
    link: str

class OnlineContext(BaseModelSchema):
    webpages: Optional[Union[WebPage, List[WebPage]]] = None
    answerBox: Optional[AnswerBox] = None
    peopleAlsoAsk: Optional[List[PeopleAlsoAsk]] = None
    knowledgeGraph: Optional[KnowledgeGraph] = None
    organicContext: Optional[List[OrganicContext]] = None

class Intent(BaseModelSchema):
    type: str
    query: str
    memory_type: str = Field(alias="memory-type")
    inferred_queries: Optional[List[str]] = Field(default=None, alias="inferred-queries")

class TrainOfThought(BaseModelSchema):
    type: str
    data: str

class ChatMessage(BaseModelSchema):
    message: str
    trainOfThought: List[TrainOfThought] = []
    context: List[Context] = []
    onlineContext: Dict[str, OnlineContext] = {}
    codeContext: Dict[str, CodeContextData] = {}
    created: str
    images: Optional[List[str]] = None
    queryFiles: Optional[List[Dict[str, Any]]] = None
    excalidrawDiagram: Optional[List[Dict[str, Any]]] = None
    mermaidjsDiagram: Optional[str] = None
    by: str
    turnId: Optional[str] = None
    intent: Optional[Intent] = None
    automationId: Optional[str] = None

# Location data schema
class LocationData(BaseModelSchema):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    altitudeAccuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
