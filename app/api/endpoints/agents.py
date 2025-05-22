from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import KhojUser
from app.models.conversation import Agent
from app.schemas.conversation import Agent as AgentSchema, AgentCreate
from app.models.ai_models import ChatModel

router = APIRouter()


@router.get("", response_model=List[AgentSchema])
def get_agents(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all agents available to the current user."""
    # Get public agents
    public_agents = db.query(Agent).filter(
        Agent.privacy_level == "public",
        Agent.is_hidden == False
    ).all()
    
    # Get user's private agents
    private_agents = db.query(Agent).filter(
        Agent.creator_id == 1,
        Agent.is_hidden == False
    ).all()
    
    # Combine and return
    return public_agents + private_agents


@router.get("/{agent_id}", response_model=AgentSchema)
def get_agent(
    agent_id: int,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific agent by ID."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user has access to this agent
    if agent.privacy_level != "public" and agent.creator_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this agent"
        )
    
    return agent


@router.post("", response_model=AgentSchema)
def create_agent(
    agent_in: AgentCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new agent."""
    # Verify chat model exists
    chat_model = db.query(ChatModel).filter(ChatModel.id == agent_in.chat_model_id).first()
    if not chat_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat model not found"
        )
    
    # Create new agent
    db_agent = Agent(
        creator_id=1,
        name=agent_in.name,
        personality=agent_in.personality,
        input_tools=agent_in.input_tools,
        output_modes=agent_in.output_modes,
        chat_model_id=agent_in.chat_model_id,
        style_color=agent_in.style_color,
        style_icon=agent_in.style_icon,
        privacy_level=agent_in.privacy_level,
        is_hidden=agent_in.is_hidden,
        managed_by_admin=False,
        slug=f"{agent_in.name.lower().replace(' ', '-')}-{1}"
    )
    
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    return db_agent


@router.put("/{agent_id}", response_model=AgentSchema)
def update_agent(
    agent_id: int,
    agent_in: AgentCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing agent."""
    # Get the agent
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user has permission to update
    if agent.creator_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this agent"
        )
    
    # Verify chat model exists
    chat_model = db.query(ChatModel).filter(ChatModel.id == agent_in.chat_model_id).first()
    if not chat_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat model not found"
        )
    
    # Update agent
    agent.name = agent_in.name
    agent.personality = agent_in.personality
    agent.input_tools = agent_in.input_tools
    agent.output_modes = agent_in.output_modes
    agent.chat_model_id = agent_in.chat_model_id
    agent.style_color = agent_in.style_color
    agent.style_icon = agent_in.style_icon
    agent.privacy_level = agent_in.privacy_level
    agent.is_hidden = agent_in.is_hidden
    
    db.commit()
    db.refresh(agent)
    
    return agent


@router.delete("/{agent_id}", response_model=AgentSchema)
def delete_agent(
    agent_id: int,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an agent."""
    # Get the agent
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user has permission to delete
    if agent.creator_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this agent"
        )
    
    db.delete(agent)
    db.commit()
    
    return agent
