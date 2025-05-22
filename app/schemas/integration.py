from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class NotionConfigBase(BaseModel):
    token: str


class NotionConfigCreate(NotionConfigBase):
    user_id: int


class NotionConfig(NotionConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class GithubConfigBase(BaseModel):
    pat_token: str


class GithubConfigCreate(GithubConfigBase):
    user_id: int


class GithubConfig(GithubConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class GithubRepoConfigBase(BaseModel):
    name: str
    owner: str
    branch: str


class GithubRepoConfigCreate(GithubRepoConfigBase):
    github_config_id: int


class GithubRepoConfig(GithubRepoConfigBase):
    id: int
    github_config_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WebScraperType(str):
    FIRECRAWL = "Firecrawl"
    OLOSTEP = "Olostep"
    JINA = "Jina"
    DIRECT = "Direct"


class WebScraperBase(BaseModel):
    name: Optional[str] = None
    type: str = "Jina"
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    priority: Optional[int] = None


class WebScraperCreate(WebScraperBase):
    pass


class WebScraper(WebScraperBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
