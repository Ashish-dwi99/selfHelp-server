from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import KhojUser
from app.models.conversation import Conversation, Agent
from app.schemas.conversation import (
    Conversation as ConversationSchema,
    ConversationCreate,
    MessageCreate,
    ChatMessage
)

router = APIRouter()


@router.get("/sessions", response_model=List[ConversationSchema])
def get_conversations(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user."""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == 1
    ).all()
    
    return conversations


@router.get("/sessions/{conversation_id}", response_model=ConversationSchema)
def get_conversation(
    conversation_id: str,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation by ID."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == 1
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.post("/sessions", response_model=ConversationSchema)
def create_conversation(
    conversation_in: ConversationCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    # Check if agent exists if agent_id is provided
    if conversation_in.agent_id:
        agent = db.query(Agent).filter(Agent.id == conversation_in.agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check if user has access to this agent
        if agent.privacy_level != "public" and agent.creator_id != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to use this agent"
            )
    
    # Create new conversation
    db_conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=1,
        conversation_log=conversation_in.conversation_log,
        slug=conversation_in.slug or f"conversation-{uuid.uuid4().hex[:8]}",
        title=conversation_in.title,
        agent_id=conversation_in.agent_id,
        file_filters=conversation_in.file_filters
    )
    
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    
    return db_conversation


@router.put("/sessions/{conversation_id}", response_model=ConversationSchema)
def update_conversation(
    conversation_id: str,
    conversation_in: ConversationCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing conversation."""
    # Get the conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == 1
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check if agent exists if agent_id is provided
    if conversation_in.agent_id:
        agent = db.query(Agent).filter(Agent.id == conversation_in.agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check if user has access to this agent
        if agent.privacy_level != "public" and agent.creator_id != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to use this agent"
            )
    
    # Update conversation
    conversation.conversation_log = conversation_in.conversation_log
    conversation.slug = conversation_in.slug or conversation.slug
    conversation.title = conversation_in.title
    conversation.agent_id = conversation_in.agent_id
    conversation.file_filters = conversation_in.file_filters
    
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.delete("/sessions/{conversation_id}", response_model=ConversationSchema)
def delete_conversation(
    conversation_id: str,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation."""
    # Get the conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == 1
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    db.delete(conversation)
    db.commit()
    
    return conversation


@router.post("/sessions/{conversation_id}/message", response_model=ChatMessage)
async def send_message(
    conversation_id: str,
    message_in: MessageCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a conversation and get AI response."""
    # Get the conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == 1
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Initialize conversation_log.chat if it doesn't exist
    if "chat" not in conversation.conversation_log:
        conversation.conversation_log["chat"] = []
    
    # Create user message
    import datetime
    current_time = datetime.datetime.utcnow().isoformat()
    turn_id = str(uuid.uuid4())
    
    user_message = {
        "message": message_in.message,
        "by": "user",
        "created": current_time,
        "turnId": turn_id
    }
    
    # Add user message to conversation
    conversation.conversation_log["chat"].append(user_message)
    
    # Get agent if specified
    agent_personality = None
    if conversation.agent_id:
        agent = db.query(Agent).filter(Agent.id == conversation.agent_id).first()
        if agent:
            agent_personality = agent.personality
    
    # Process command if specified
    command = message_in.command or "default"
    
    # Create AI message (simplified for lightweight version)
    ai_response = "This is a lightweight version of Khoj. For full AI chat functionality, please install the complete version with Gemini API integration."
    
    if agent_personality:
        ai_response = f"Agent ({agent.name}): {ai_response}"
    
    # Create AI message
    ai_message = {
        "message": ai_response,
        "by": "assistant",
        "created": datetime.datetime.utcnow().isoformat(),
        "turnId": turn_id,
        "trainOfThought": [{"type": "thinking", "data": "Lightweight mode - no AI processing"}],
        "context": []
    }
    
    # Add AI message to conversation
    conversation.conversation_log["chat"].append(ai_message)
    
    # Update conversation in database
    db.commit()
    
    return ai_message
