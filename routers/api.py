from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union
import math
import time
import uuid
import concurrent.futures
from datetime import datetime

from database import models, schemas, adapters
from database.models import get_db
from routers.auth import get_current_active_user
from utils.search import text_search
from utils.state import SearchType, query_cache
from utils.helpers import timer, is_none_or_empty

# Create router
router = APIRouter(tags=["API"])

@router.delete("/self")
async def delete_self(
    request: Request,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    adapters.delete_user(db, current_user.id)
    return {"status": "ok"}

@router.get("/search", response_model=List[schemas.SearchResponse])
async def search(
    q: str,
    request: Request,
    n: Optional[int] = 5,
    t: Optional[SearchType] = SearchType.All,
    r: Optional[bool] = False,
    max_distance: Optional[Union[float, None]] = None,
    dedupe: Optional[bool] = True,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    results = await execute_search(
        user=current_user,
        q=q,
        n=n,
        t=t,
        r=r,
        max_distance=max_distance or math.inf,
        dedupe=dedupe,
        db=db
    )
    
    return results

async def execute_search(
    user: models.KhojUser,
    q: str,
    n: Optional[int] = 5,
    t: Optional[SearchType] = SearchType.All,
    r: Optional[bool] = False,
    max_distance: Optional[Union[float, None]] = None,
    dedupe: Optional[bool] = True,
    agent: Optional[models.Agent] = None,
    db: Session = None
):
    # Run validation checks
    results = []

    start_time = time.time()

    # Ensure the agent, if present, is accessible by the user
    if user and agent and not adapters.is_agent_accessible(db, agent, user):
        return results

    if q is None or q == "":
        return results

    # initialize variables
    user_query = q.strip()
    results_count = n or 5
    search_futures = []

    # return cached results, if available
    query_cache_key = f"{user_query}-{n}-{t}-{r}-{max_distance}-{dedupe}"
    if user.uuid in query_cache and query_cache_key in query_cache[user.uuid]:
        return query_cache[user.uuid][query_cache_key]

    # Encode query with filter terms removed
    defiltered_query = user_query
    # In a real implementation, we would apply filters here
    # For now, we'll use the query as is

    encoded_asymmetric_query = None
    if t != SearchType.Image:
        with timer("Encoding query took"):
            search_model = adapters.get_default_chat_model(db)
            # In a real implementation, we would encode the query here
            # For now, we'll use a placeholder
            encoded_asymmetric_query = defiltered_query

    with concurrent.futures.ThreadPoolExecutor() as executor:
        if t in [
            SearchType.All,
            SearchType.Org,
            SearchType.Markdown,
            SearchType.Github,
            SearchType.Notion,
            SearchType.Plaintext,
            SearchType.Pdf,
        ]:
            # query text content
            search_futures += [
                executor.submit(
                    text_search.query,
                    user_query,
                    user,
                    t,
                    question_embedding=encoded_asymmetric_query,
                    max_distance=max_distance,
                    agent=agent,
                    db=db
                )
            ]

        # Query across each requested content types in parallel
        with timer("Query took"):
            for search_future in concurrent.futures.as_completed(search_futures):
                hits = await search_future.result()
                # Collate results
                results += text_search.collate_results(hits, dedupe=dedupe)

                # Sort results across all content types and take top results
                results = text_search.rerank_and_sort_results(
                    results, query=defiltered_query, rank_results=r
                )[:results_count]

    # Cache results
    if user.uuid not in query_cache:
        query_cache[user.uuid] = {}
    query_cache[user.uuid][query_cache_key] = results

    end_time = time.time()
    print(f"🔍 Search took: {end_time - start_time:.3f} seconds")

    return results

@router.get("/update")
async def update(
    request: Request,
    t: Optional[SearchType] = None,
    force: Optional[bool] = False,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # In a real implementation, we would initialize content here
    # For now, we'll just return a success message
    return {"status": "ok", "message": "khoj reloaded"}

@router.post("/transcribe")
async def transcribe(
    request: Request,
    file: bytes,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # In a real implementation, we would transcribe audio here
    # For now, we'll just return a placeholder response
    return {"text": "This is a placeholder transcription"}

@router.get("/settings")
async def get_settings(
    request: Request,
    detailed: Optional[bool] = False,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # In a real implementation, we would get user settings here
    # For now, we'll just return a placeholder response
    user_config = {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name
        },
        "subscription": {
            "type": "standard",
            "is_recurring": False
        },
        "detailed": detailed
    }
    
    return user_config

@router.patch("/user/name")
async def set_user_name(
    request: Request,
    name: str,
    client: Optional[str] = None,
    current_user: models.KhojUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    split_name = name.split(" ")

    if len(split_name) > 2:
        raise HTTPException(status_code=400, detail="Name must be in the format: Firstname Lastname")

    if len(split_name) == 1:
        first_name = split_name[0]
        last_name = ""
    else:
        first_name, last_name = split_name[0], split_name[-1]

    adapters.set_user_name(db, current_user.id, first_name, last_name)

    return {"status": "ok"}
