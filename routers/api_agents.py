from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from database import models, schemas, adapters
from database.models import get_db
from routers.auth import get_current_active_user

# Create router
router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("/", response_model=List[schemas.Agent])
async def get_agents(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get user's agents
    user_agents = adapters.get_agents_by_creator(db, current_user.id)
    
    # Get public agents
    public_agents = adapters.get_public_agents(db)
    
    # Combine and deduplicate
    all_agents = user_agents + [agent for agent in public_agents if agent.id not in [ua.id for ua in user_agents]]
    
    # Apply pagination
    return all_agents[skip:skip+limit]

@router.get("/{slug}", response_model=schemas.Agent)
async def get_agent(
    slug: str,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agent = adapters.get_agent_by_slug(db, slug)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    if not adapters.is_agent_accessible(db, agent, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this agent"
        )
    
    return agent

@router.post("/", response_model=schemas.Agent)
async def create_agent(
    agent: schemas.AgentBase,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if agent with same name already exists for this user
    existing_agents = adapters.get_agents_by_creator(db, current_user.id)
    if any(a.name == agent.name for a in existing_agents):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An agent with the name {agent.name} already exists"
        )
    
    # Check if public agent with same name exists
    if agent.privacy_level == "public":
        public_agents = adapters.get_public_agents(db)
        if any(a.name == agent.name for a in public_agents):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A public agent with the name {agent.name} already exists"
            )
    
    # Generate a slug if not provided
    if not agent.slug:
        import random
        random_sequence = ''.join(random.choice("0123456789") for i in range(6))
        agent.slug = f"{agent.name.lower().replace(' ', '-')}-{random_sequence}"
    
    # Get the first available chat model (preferably Gemini)
    default_model = adapters.get_default_chat_model(db)
    if not default_model:
        # If no default model, get the first available model
        available_models = adapters.get_chat_models(db, limit=1)
        if not available_models:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No chat models available. Please set up at least one chat model."
            )
        default_model = available_models[0]
    
    # Create agent
    agent_create = schemas.AgentCreate(
        **agent.dict(),
        creator_id=current_user.id,
        chat_model_id=default_model.id
    )
    
    return adapters.create_agent(db, agent_create)

@router.put("/{agent_id}", response_model=schemas.Agent)
async def update_agent(
    agent_id: int,
    agent_update: schemas.AgentBase,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get agent
    agent = adapters.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user owns the agent
    if agent.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this agent"
        )
    
    # Update agent
    return adapters.update_agent(db, agent_id, agent_update)

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get agent
    agent = adapters.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user owns the agent
    if agent.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this agent"
        )
    
    # Delete agent
    adapters.delete_agent(db, agent_id)
    return {"status": "success", "message": "Agent deleted"}
