from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class PrivacyLevel(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


class StyleColor(str, Enum):
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    PINK = "pink"
    TEAL = "teal"
    CYAN = "cyan"
    LIME = "lime"
    INDIGO = "indigo"
    FUCHSIA = "fuchsia"
    ROSE = "rose"
    SKY = "sky"
    AMBER = "amber"
    EMERALD = "emerald"


class StyleIcon(str, Enum):
    LIGHTBULB = "Lightbulb"
    HEALTH = "Health"
    ROBOT = "Robot"
    APERTURE = "Aperture"
    GRADUATION_CAP = "GraduationCap"
    JEEP = "Jeep"
    ISLAND = "Island"
    MATH_OPERATIONS = "MathOperations"
    ASCLEPIUS = "Asclepius"
    COUCH = "Couch"
    CODE = "Code"
    ATOM = "Atom"


class InputTool(str, Enum):
    GENERAL = "general"
    ONLINE = "online"
    NOTES = "notes"
    WEBPAGE = "webpage"
    CODE = "code"


class OutputMode(str, Enum):
    IMAGE = "image"
    DIAGRAM = "diagram"


class AgentBase(BaseModel):
    name: str
    personality: Optional[str] = None
    input_tools: List[InputTool] = Field(default_factory=list)
    output_modes: List[OutputMode] = Field(default_factory=list)
    chat_model_id: int
    style_color: StyleColor = StyleColor.ORANGE
    style_icon: StyleIcon = StyleIcon.LIGHTBULB
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE
    is_hidden: bool = False


class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id: int
    creator_id: Optional[int] = None
    managed_by_admin: bool
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Context(BaseModel):
    compiled: str
    file: str


class TrainOfThought(BaseModel):
    type: str
    data: str


class ChatMessageBase(BaseModel):
    message: str
    by: str
    created: str
    turnId: Optional[str] = None


class ChatMessage(ChatMessageBase):
    trainOfThought: List[TrainOfThought] = Field(default_factory=list)
    context: List[Context] = Field(default_factory=list)
    onlineContext: Dict[str, Any] = Field(default_factory=dict)
    codeContext: Dict[str, Any] = Field(default_factory=dict)
    images: Optional[List[str]] = None
    queryFiles: Optional[List[Dict[str, Any]]] = None
    excalidrawDiagram: Optional[List[Dict[str, Any]]] = None
    mermaidjsDiagram: Optional[str] = None
    intent: Optional[Dict[str, Any]] = None
    automationId: Optional[str] = None


class ConversationBase(BaseModel):
    conversation_log: Dict[str, Any] = Field(default_factory=lambda: {"chat": []})
    slug: Optional[str] = None
    title: Optional[str] = None
    file_filters: List[str] = Field(default_factory=list)


class ConversationCreate(ConversationBase):
    agent_id: Optional[int] = None


class Conversation(ConversationBase):
    id: str
    user_id: int
    client_id: Optional[int] = None
    agent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PublicConversationBase(BaseModel):
    conversation_log: Dict[str, Any] = Field(default_factory=lambda: {"chat": []})
    slug: Optional[str] = None
    title: Optional[str] = None


class PublicConversationCreate(PublicConversationBase):
    agent_id: Optional[int] = None


class PublicConversation(PublicConversationBase):
    id: int
    source_owner_id: int
    agent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class MessageCreate(BaseModel):
    message: str
    command: Optional[str] = None


class UserConversationConfigBase(BaseModel):
    setting_id: Optional[int] = None


class UserConversationConfigCreate(UserConversationConfigBase):
    pass


class UserConversationConfig(UserConversationConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserVoiceModelConfigBase(BaseModel):
    setting_id: Optional[int] = None


class UserVoiceModelConfigCreate(UserVoiceModelConfigBase):
    pass


class UserVoiceModelConfig(UserVoiceModelConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserTextToImageModelConfigBase(BaseModel):
    setting_id: int


class UserTextToImageModelConfigCreate(UserTextToImageModelConfigBase):
    pass


class UserTextToImageModelConfig(UserTextToImageModelConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ReflectiveQuestionBase(BaseModel):
    question: str


class ReflectiveQuestionCreate(ReflectiveQuestionBase):
    user_id: Optional[int] = None


class ReflectiveQuestion(ReflectiveQuestionBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
