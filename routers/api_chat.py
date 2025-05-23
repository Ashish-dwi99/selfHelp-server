from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Union
import json
import uuid
from datetime import datetime

from database import models, schemas, adapters
from database.models import get_db
from routers.auth import get_current_active_user
from services.conversation_service import ConversationService

# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])

# Active websocket connections
active_connections: Dict[str, WebSocket] = {}

@router.post("/conversation")
async def create_conversation(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    conversation = adapters.create_conversation(db, current_user.id)
    return {
        "id": conversation.id,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "title": conversation.title,
        "user_id": current_user.id
    }

@router.get("/conversations")
async def get_conversations(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    conversations = adapters.get_conversations_by_user(db, current_user.id, skip, limit)
    return [
        {
            "id": conv.id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(), 
            "title": conv.title,
            "user_id": conv.user_id
        }
        for conv in conversations
    ]

@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with messages"""
    conversation = adapters.get_conversation(db, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages = []
    for msg in conversation.messages:
        messages.append({
            "id": msg.id,
            "user_message": msg.user_message,
            "khoj_message": msg.khoj_message,
            "created_at": msg.created_at.isoformat()
        })
    
    return {
        "id": conversation.id,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "title": conversation.title,
        "user_id": conversation.user_id,
        "messages": messages
    }

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    success = adapters.delete_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "success", "message": "Conversation deleted"}

@router.post("/conversation/{conversation_id}/message")
async def send_message(
    conversation_id: int,
    message: schemas.ChatMessage,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    agent_id: Optional[int] = Query(None)
):
    """Send a message and get streaming response"""
    
    # Get agent if specified
    agent = None
    if agent_id:
        agent = adapters.get_agent(db, agent_id)
        if not agent or not adapters.is_agent_accessible(db, agent, current_user):
            raise HTTPException(status_code=404, detail="Agent not found or not accessible")
    
    # Create conversation service
    conversation_service = ConversationService(db)
    
    # Create streaming response
    async def generate_response():
        try:
            async for chunk in conversation_service.send_message(
                conversation_id, 
                message.message, 
                current_user,
                agent
            ):
                yield f"data: {json.dumps({'message': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str
):
    await websocket.accept()
    
    # Store the connection
    if conversation_id not in active_connections:
        active_connections[conversation_id] = websocket
    
    try:
        while True:
            # Wait for messages
            data = await websocket.receive_text()
            
            # Process message (in a real implementation, this would involve more logic)
            response = {
                "type": "message",
                "content": f"Echo: {data}",
                "timestamp": datetime.now().isoformat()
            }
            
            # Send response
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        # Remove the connection when disconnected
        if conversation_id in active_connections:
            del active_connections[conversation_id]

@router.get("/models")
async def get_chat_models(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get available chat models"""
    chat_models = adapters.get_chat_models(db)
    return [
        {
            "id": model.id,
            "name": model.name,
            "model_type": model.model_type,
            "price_tier": model.price_tier,
            "vision_enabled": model.vision_enabled,
            "description": model.description
        }
        for model in chat_models
    ]

@router.get("/default-model")
async def get_default_chat_model(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the default chat model"""
    model = adapters.get_default_chat_model(db)
    if not model:
        raise HTTPException(status_code=404, detail="No default chat model configured")
        
    return {
        "id": model.id,
        "name": model.name,
        "model_type": model.model_type,
        "price_tier": model.price_tier,
        "vision_enabled": model.vision_enabled,
        "description": model.description
    }
