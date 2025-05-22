from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib
import json
import os
import tempfile
import uuid

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import KhojUser
from app.models.content import Entry, FileObject, EntryDates
from app.models.ai_models import SearchModelConfig
from app.schemas.content import Entry as EntrySchema, EntryCreate

router = APIRouter()


@router.post("/search")
def search_content(
    query: str,
    limit: int = 10,
    file_type: Optional[str] = None,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for content (lightweight version without vector search)."""
    # Get all entries for the user
    query_obj = db.query(Entry).filter(Entry.user_id == 1)
    
    # Filter by file type if specified
    if file_type:
        query_obj = query_obj.filter(Entry.file_type == file_type)
    
    entries = query_obj.all()
    
    # Simple keyword search (for lightweight version)
    results = []
    for entry in entries:
        if query.lower() in entry.raw.lower() or query.lower() in entry.compiled.lower():
            results.append(entry)
    
    # Return top results
    return results[:limit]


@router.post("/index", response_model=List[EntrySchema])
async def index_content(
    files: List[UploadFile] = File(...),
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Index content from uploaded files (lightweight version without embeddings)."""
    indexed_entries = []
    
    # Get default search model
    search_model = db.query(SearchModelConfig).filter(SearchModelConfig.name == "default").first()
    if not search_model:
        # Create default search model if it doesn't exist
        search_model = SearchModelConfig(name="default")
        db.add(search_model)
        db.commit()
        db.refresh(search_model)
    
    for file in files:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write uploaded file content to temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process file based on type
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            if file_extension in ['.txt', '.md', '.org']:
                # Process text file
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                # Create file object
                file_object = FileObject(
                    file_name=file.filename,
                    raw_text=text_content,
                    user_id=1
                )
                db.add(file_object)
                db.commit()
                db.refresh(file_object)
                
                # Split content into chunks (simple implementation)
                chunks = [text_content[i:i+1000] for i in range(0, len(text_content), 1000)]
                
                for i, chunk in enumerate(chunks):
                    # Create hash for deduplication
                    chunk_hash = hashlib.sha256(chunk.encode()).hexdigest()
                    
                    # Create entry (with placeholder for embeddings)
                    entry = Entry(
                        user_id=1,
                        embeddings=json.dumps([0.0] * 10),  # Placeholder embeddings
                        raw=chunk,
                        compiled=chunk,
                        heading=f"{file.filename} - Chunk {i+1}",
                        file_source="computer",
                        file_type="plaintext" if file_extension == '.txt' else 
                                 "markdown" if file_extension == '.md' else "org",
                        file_path=file.filename,
                        file_name=file.filename,
                        hashed_value=chunk_hash,
                        corpus_id=str(uuid.uuid4()),
                        search_model_id=search_model.id,
                        file_object_id=file_object.id
                    )
                    db.add(entry)
                    indexed_entries.append(entry)
            
            # Add support for other file types (PDF, DOCX, etc.) here
            
            db.commit()
            for entry in indexed_entries:
                db.refresh(entry)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    return indexed_entries


@router.delete("/index", status_code=status.HTTP_204_NO_CONTENT)
def delete_index(
    file_name: Optional[str] = None,
    file_type: Optional[str] = None,
    #current_user: KhojUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete indexed content."""
    query = db.query(Entry).filter(Entry.user_id == 1)
    
    if file_name:
        query = query.filter(Entry.file_name == file_name)
    
    if file_type:
        query = query.filter(Entry.file_type == file_type)
    
    entries = query.all()
    
    # Delete associated file objects
    file_object_ids = set(entry.file_object_id for entry in entries if entry.file_object_id)
    for file_object_id in file_object_ids:
        file_object = db.query(FileObject).filter(FileObject.id == file_object_id).first()
        if file_object:
            db.delete(file_object)
    
    # Delete entries
    for entry in entries:
        db.delete(entry)
    
    db.commit()
    
    return None
