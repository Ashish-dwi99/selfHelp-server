from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import KhojUser
from app.models.integration import NotionConfig, GithubConfig, GithubRepoConfig, WebScraper
from app.schemas.integration import (
    NotionConfig as NotionConfigSchema,
    NotionConfigCreate,
    GithubConfig as GithubConfigSchema,
    GithubConfigCreate,
    GithubRepoConfig as GithubRepoConfigSchema,
    GithubRepoConfigCreate,
    WebScraper as WebScraperSchema
)

router = APIRouter()


@router.post("/notion", response_model=NotionConfigSchema)
def configure_notion(
    config_in: NotionConfigCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure Notion integration."""
    # Check if config already exists
    existing_config = db.query(NotionConfig).filter(
        NotionConfig.user_id == 1
    ).first()
    
    if existing_config:
        # Update existing config
        existing_config.token = config_in.token
        db.commit()
        db.refresh(existing_config)
        return existing_config
    
    # Create new config
    db_config = NotionConfig(
        token=config_in.token,
        user_id=1
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/notion", response_model=NotionConfigSchema)
def get_notion_config(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Notion integration configuration."""
    config = db.query(NotionConfig).filter(
        NotionConfig.user_id == 1
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notion configuration not found"
        )
    
    return config


@router.delete("/notion", status_code=status.HTTP_204_NO_CONTENT)
def delete_notion_config(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete Notion integration configuration."""
    config = db.query(NotionConfig).filter(
        NotionConfig.user_id == 1
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notion configuration not found"
        )
    
    db.delete(config)
    db.commit()
    
    return None


@router.post("/github", response_model=GithubConfigSchema)
def configure_github(
    config_in: GithubConfigCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure GitHub integration."""
    # Check if config already exists
    existing_config = db.query(GithubConfig).filter(
        GithubConfig.user_id == 1
    ).first()
    
    if existing_config:
        # Update existing config
        existing_config.pat_token = config_in.pat_token
        db.commit()
        db.refresh(existing_config)
        return existing_config
    
    # Create new config
    db_config = GithubConfig(
        pat_token=config_in.pat_token,
        user_id=1
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/github", response_model=GithubConfigSchema)
def get_github_config(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get GitHub integration configuration."""
    config = db.query(GithubConfig).filter(
        GithubConfig.user_id == 1
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    
    return config


@router.delete("/github", status_code=status.HTTP_204_NO_CONTENT)
def delete_github_config(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete GitHub integration configuration."""
    config = db.query(GithubConfig).filter(
        GithubConfig.user_id == 1
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    
    db.delete(config)
    db.commit()
    
    return None


@router.post("/github/repo", response_model=GithubRepoConfigSchema)
def add_github_repo(
    repo_in: GithubRepoConfigCreate,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add GitHub repository configuration."""
    # Check if GitHub config exists
    github_config = db.query(GithubConfig).filter(
        GithubConfig.id == repo_in.github_config_id,
        GithubConfig.user_id == 1
    ).first()
    
    if not github_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    
    # Create new repo config
    db_repo = GithubRepoConfig(
        name=repo_in.name,
        owner=repo_in.owner,
        branch=repo_in.branch,
        github_config_id=repo_in.github_config_id
    )
    db.add(db_repo)
    db.commit()
    db.refresh(db_repo)
    
    return db_repo


@router.get("/github/repos", response_model=List[GithubRepoConfigSchema])
def get_github_repos(
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all GitHub repository configurations."""
    # Get user's GitHub config
    github_config = db.query(GithubConfig).filter(
        GithubConfig.user_id == 1
    ).first()
    
    if not github_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    
    # Get repos for this config
    repos = db.query(GithubRepoConfig).filter(
        GithubRepoConfig.github_config_id == github_config.id
    ).all()
    
    return repos


@router.delete("/github/repo/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_github_repo(
    repo_id: int,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete GitHub repository configuration."""
    # Get user's GitHub config
    github_config = db.query(GithubConfig).filter(
        GithubConfig.user_id == 1
    ).first()
    
    if not github_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub configuration not found"
        )
    
    # Get repo
    repo = db.query(GithubRepoConfig).filter(
        GithubRepoConfig.id == repo_id,
        GithubRepoConfig.github_config_id == github_config.id
    ).first()
    
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub repository configuration not found"
        )
    
    db.delete(repo)
    db.commit()
    
    return None
