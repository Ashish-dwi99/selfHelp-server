from fastapi import APIRouter

from app.api.endpoints import auth, agents, chat, search, integrations, user

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user.router, prefix="/v1/user", tags=["user"])
api_router.include_router(agents.router, prefix="/chat/options", tags=["chat-options"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(search.router, prefix="/content", tags=["content"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
