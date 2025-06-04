from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import models, schemas, adapters
from database.models import get_db
from routers.auth import get_current_active_user

# Create router
router = APIRouter(prefix="/content", tags=["Content"])

@router.get("/sources")
async def get_content_sources(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # In a real implementation, we would get content sources from the database
    # For now, we'll just return a placeholder response
    return {
        "markdown": True,
        "org": True,
        "pdf": True,
        "notion": bool(adapters.get_notion_config_by_user(db, current_user.id)),
        "github": bool(adapters.get_github_config_by_user(db, current_user.id))
    }

@router.post("/upload")
async def upload_content(
    request: Request,
    file: UploadFile = File(...),
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # In a real implementation, we would process and store the uploaded file
    # For now, we'll just return a success message
    return {
        "status": "success",
        "message": f"File {file.filename} uploaded successfully",
        "file_id": str(uuid.uuid4())
    }

@router.get("/files")
async def get_files(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # In a real implementation, we would get files from the database
    # For now, we'll just return a placeholder response
    return []

@router.delete("/file/{file_id}")
async def delete_file(
    file_id: str,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # In a real implementation, we would delete the file from the database
    # For now, we'll just return a success message
    return {"status": "success", "message": "File deleted"}

@router.post("/notion/config")
async def set_notion_config(
    config: schemas.NotionConfigBase,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if config already exists
    existing_config = adapters.get_notion_config_by_user(db, current_user.id)
    
    if existing_config:
        # Update existing config
        existing_config.token = config.token
        db.commit()
        db.refresh(existing_config)
        return existing_config
    else:
        # Create new config
        notion_config = schemas.NotionConfigCreate(
            token=config.token,
            user_id=current_user.id
        )
        return adapters.create_notion_config(db, notion_config)

@router.get("/notion/config")
async def get_notion_config(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    config = adapters.get_notion_config_by_user(db, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notion configuration not found"
        )
    return config

@router.delete("/notion/config")
async def delete_notion_config(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    config = adapters.get_notion_config_by_user(db, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notion configuration not found"
        )
    
    db.delete(config)
    db.commit()
    return {"status": "success", "message": "Notion configuration deleted"}

@router.post("/github/config")
async def set_github_config(
    config: schemas.GithubConfigBase,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if config already exists
    existing_config = adapters.get_github_config_by_user(db, current_user.id)
    
    if existing_config:
        # Update existing config
        existing_config.pat_token = config.pat_token
        db.commit()
        db.refresh(existing_config)
        return existing_config
    else:
        # Create new config
        github_config = schemas.GithubConfigCreate(
            pat_token=config.pat_token,
            user_id=current_user.id
        )
        return adapters.create_github_config(db, github_config)

@router.get("/github/config")
async def get_github_config(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    config = adapters.get_github_config_by_user(db, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    return config

@router.delete("/github/config")
async def delete_github_config(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    config = adapters.get_github_config_by_user(db, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    
    db.delete(config)
    db.commit()
    return {"status": "success", "message": "GitHub configuration deleted"}

@router.post("/github/repos")
async def add_github_repo(
    repo: schemas.GithubRepoConfigBase,
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get GitHub config
    github_config = adapters.get_github_config_by_user(db, current_user.id)
    if not github_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    
    # Create repo config
    repo_config = schemas.GithubRepoConfigCreate(
        **repo.dict(),
        github_config_id=github_config.id
    )
    return adapters.create_github_repo_config(db, repo_config)

@router.get("/github/repos")
async def get_github_repos(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get GitHub config
    github_config = adapters.get_github_config_by_user(db, current_user.id)
    if not github_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    
    # Get repos
    return adapters.get_github_repo_configs(db, github_config.id)
