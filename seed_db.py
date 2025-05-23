#!/usr/bin/env python3

import os
import sys
from sqlalchemy.orm import Session

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import get_db
from database import adapters, schemas, models

def update_gemini_model():
    """Update the existing Gemini Pro model to use Gemini 2.0 Flash"""
    
    db: Session = next(get_db())
    
    try:
        print("🔍 Current Models in Database:")
        print("=" * 50)
        
        # Show all current models
        all_models = db.query(models.ChatModel).all()
        for model in all_models:
            print(f"  ID: {model.id} | Name: {model.name} | Type: {model.model_type}")
        
        # Find the model with ID 2 (the one your agent is using)
        target_model = db.query(models.ChatModel).filter_by(id=2).first()
        
        if target_model:
            print(f"\n🎯 Found target model:")
            print(f"  ID: {target_model.id}")
            print(f"  Current Name: {target_model.name}")
            print(f"  Type: {target_model.model_type}")
            
            # Update the model to use Gemini 2.0 Flash
            print(f"\n🔧 Updating model to use Gemini 2.0 Flash...")
            target_model.name = "gemini-2.0-flash"
            target_model.description = "Google's Gemini 2.0 Flash - Latest fast AI model"
            target_model.model_type = "google"
            target_model.vision_enabled = True
            
            db.commit()
            
            print("✅ Model updated successfully!")
            print(f"  New Name: {target_model.name}")
            print(f"  Type: {target_model.model_type}")
            print(f"  Vision: {target_model.vision_enabled}")
            
            # Verify the mapping will work
            from services.conversation_service import ConversationService
            service = ConversationService(db)
            mapped_name = service._get_gemini_model_name(target_model)
            print(f"  API Model Name: {mapped_name}")
            
            if mapped_name == "gemini-2.0-flash":
                print("✅ Model name mapping is correct!")
            else:
                print(f"⚠️ Warning: Model maps to {mapped_name}, not gemini-2.0-flash")
            
        else:
            print("❌ Model with ID 2 not found!")
            
        print(f"\n📋 Updated Models:")
        print("=" * 30)
        updated_models = db.query(models.ChatModel).all()
        for model in updated_models:
            print(f"  ID: {model.id} | Name: {model.name} | Type: {model.model_type}")
            
    except Exception as e:
        print(f"❌ Error updating model: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_gemini_model()