from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ModelType(str, Enum):
    OPENAI = "openai"
    OFFLINE = "offline"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class PriceTier(str, Enum):
    FREE = "free"
    STANDARD = "standard"


class AiModelApiBase(BaseModel):
    name: str
    api_key: str
    api_base_url: Optional[str] = None


class AiModelApiCreate(AiModelApiBase):
    pass


class AiModelApi(AiModelApiBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ChatModelBase(BaseModel):
    max_prompt_size: Optional[int] = None
    subscribed_max_prompt_size: Optional[int] = None
    tokenizer: Optional[str] = None
    name: str = "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF"
    model_type: ModelType = ModelType.OFFLINE
    price_tier: PriceTier = PriceTier.FREE
    vision_enabled: bool = False
    description: Optional[str] = None
    strengths: Optional[str] = None


class ChatModelCreate(ChatModelBase):
    ai_model_api_id: Optional[int] = None


class ChatModel(ChatModelBase):
    id: int
    ai_model_api_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SearchModelConfigBase(BaseModel):
    name: str = "default"
    model_type: str = "text"
    bi_encoder: str = "thenlper/gte-small"
    bi_encoder_model_config: Dict[str, Any] = Field(default_factory=dict)
    bi_encoder_query_encode_config: Dict[str, Any] = Field(default_factory=dict)
    bi_encoder_docs_encode_config: Dict[str, Any] = Field(default_factory=dict)
    cross_encoder: str = "mixedbread-ai/mxbai-rerank-xsmall-v1"
    cross_encoder_model_config: Dict[str, Any] = Field(default_factory=dict)
    embeddings_inference_endpoint: Optional[str] = None
    embeddings_inference_endpoint_api_key: Optional[str] = None
    embeddings_inference_endpoint_type: str = "local"
    cross_encoder_inference_endpoint: Optional[str] = None
    cross_encoder_inference_endpoint_api_key: Optional[str] = None
    bi_encoder_confidence_threshold: float = 0.18


class SearchModelConfigCreate(SearchModelConfigBase):
    pass


class SearchModelConfig(SearchModelConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TextToImageModelConfigBase(BaseModel):
    model_name: str = "dall-e-3"
    model_type: str = "openai"  # openai, stability-ai, replicate, google
    price_tier: PriceTier = PriceTier.FREE
    api_key: Optional[str] = None


class TextToImageModelConfigCreate(TextToImageModelConfigBase):
    ai_model_api_id: Optional[int] = None


class TextToImageModelConfig(TextToImageModelConfigBase):
    id: int
    ai_model_api_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class VoiceModelOptionBase(BaseModel):
    model_id: str
    name: str
    price_tier: PriceTier = PriceTier.STANDARD


class VoiceModelOptionCreate(VoiceModelOptionBase):
    pass


class VoiceModelOption(VoiceModelOptionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SpeechToTextModelOptionsBase(BaseModel):
    model_name: str = "base"
    model_type: str = "offline"  # openai, offline
    price_tier: PriceTier = PriceTier.FREE


class SpeechToTextModelOptionsCreate(SpeechToTextModelOptionsBase):
    ai_model_api_id: Optional[int] = None


class SpeechToTextModelOptions(SpeechToTextModelOptionsBase):
    id: int
    ai_model_api_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ServerChatSettingsBase(BaseModel):
    chat_default_id: Optional[int] = None
    chat_advanced_id: Optional[int] = None


class ServerChatSettingsCreate(ServerChatSettingsBase):
    pass


class ServerChatSettings(ServerChatSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
