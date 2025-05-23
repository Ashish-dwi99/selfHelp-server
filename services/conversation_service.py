import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, AsyncGenerator, Optional
from sqlalchemy.orm import Session

from database import models, adapters

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self, db: Session):
        self.db = db
    
    def _get_gemini_model_name(self, chat_model: models.ChatModel) -> str:
        """Map database model name to proper Gemini model name"""
        model_name = chat_model.name.lower()
        
        # Map common variations to correct Gemini model names
        if "gemini" in model_name:
            if "2.5" in model_name:
                if "flash" in model_name:
                    return "gemini-2.5-flash-preview-05-20"
                else:
                    return "gemini-2.5-pro-preview-05-06"
            elif "2.0" in model_name or "flash-2" in model_name or model_name == "gemini-2.0-flash":
                return "gemini-2.0-flash"
            elif "1.5" in model_name:
                if "flash" in model_name:
                    return "gemini-1.5-flash"
                else:
                    return "gemini-1.5-pro"
            elif "pro" in model_name:
                # Default "pro" to 2.0 flash instead of 1.5 pro (which is deprecated)
                return "gemini-2.0-flash"
            else:
                return "gemini-2.0-flash"  # Default to latest stable
        else:
            # Default fallback for any non-gemini model names
            return "gemini-2.0-flash"
    
    async def send_message(
        self,
        conversation_id: int,
        user_message: str,
        user: models.KhojUser,
        agent: Optional[models.Agent] = None
    ) -> AsyncGenerator[str, None]:
        """Send a message to a conversation and get streaming response"""
        
        # Get or create conversation
        conversation = adapters.get_conversation(self.db, conversation_id)
        if not conversation:
            conversation = adapters.create_conversation(self.db, user.id)
            conversation_id = conversation.id
            
        # Get default chat model
        chat_model = adapters.get_default_chat_model(self.db)
        if not chat_model:
            yield "Error: No default chat model configured"
            return
            
        # Use agent's chat model if agent is provided
        if agent and agent.chat_model:
            chat_model = agent.chat_model
            
        # Get API key
        api_key = None
        if chat_model.ai_model_api:
            api_key = chat_model.ai_model_api.api_key
            
        if not api_key:
            yield "Error: No API key configured for chat model"
            return
        
        # Get proper Gemini model name
        gemini_model_name = self._get_gemini_model_name(chat_model)
        
        # Generate response using Gemini directly
        response_text = ""
        try:
            async for chunk in self._generate_gemini_response(
                user_message=user_message,
                conversation_id=conversation_id,
                api_key=api_key,
                model_name=gemini_model_name,
                agent=agent
            ):
                response_text += chunk
                yield chunk
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            response_text = error_response
            yield error_response
            
        # Save the conversation
        try:
            adapters.save_conversation_message(
                self.db,
                conversation_id=conversation_id,
                user_message=user_message,
                khoj_message=response_text,
                user_message_metadata=json.dumps({"timestamp": datetime.now().isoformat()}),
                khoj_message_metadata=json.dumps({
                    "agent_id": agent.id if agent else None,
                    "chat_model_id": chat_model.id,
                    "timestamp": datetime.now().isoformat()
                })
            )
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    async def _generate_gemini_response(
        self,
        user_message: str,
        conversation_id: int,
        api_key: str,
        model_name: str,
        agent: Optional[models.Agent] = None
    ) -> AsyncGenerator[str, None]:
        """Generate response using Gemini API directly"""
        
        try:
            import google.generativeai as genai
        except ImportError:
            yield "Error: Google GenerativeAI library not available. Please install google-generativeai."
            return
        
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Get conversation history
            conversation_history = self._get_conversation_history(conversation_id)
            
            # Build system prompt
            system_prompt = self._build_system_prompt(agent)
            
            # Build conversation for Gemini
            history = self._build_gemini_history(conversation_history)
            
            # Create the model with retry logic for quota issues
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt
            )
            
            # Start a chat session with history
            chat = model.start_chat(history=history)
            
            # Generate streaming response with error handling
            try:
                response = await chat.send_message_async(
                    user_message,
                    stream=True
                )
                
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text
                        
            except Exception as api_error:
                error_str = str(api_error)
                if "429" in error_str or "quota" in error_str.lower():
                    yield f"⚠️ Rate limit exceeded. The free tier has daily/minute limits. Please try again in a few minutes or consider upgrading to a paid plan. Model used: {model_name}"
                elif "404" in error_str:
                    yield f"❌ Model '{model_name}' not found. Please check if the model name is correct."
                else:
                    yield f"❌ API Error: {error_str}"
                    
        except Exception as e:
            logger.error(f"Error with Gemini API: {e}")
            yield f"Error communicating with AI model: {str(e)}"
    
    def _build_system_prompt(self, agent: Optional[models.Agent] = None) -> str:
        """Build system prompt for the conversation"""
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        day_of_week = datetime.now().strftime("%A")
        
        if agent and agent.personality:
            return f"""You are {agent.name}, a personal agent.
{agent.personality}

Use your general knowledge and past conversation with the user as context to inform your responses.

Today is {day_of_week}, {current_date}.

Instructions:
- Be helpful, informative, and engaging
- Provide clear and accurate responses
- Ask follow-up questions when needed for clarification
- Be concise but thorough in your explanations
"""
        else:
            return f"""You are Khoj, a smart, inquisitive and helpful personal assistant.
Use your general knowledge and past conversation with the user as context to inform your responses.

Today is {day_of_week}, {current_date}.

Instructions:
- Be helpful, informative, and engaging
- Provide clear and accurate responses  
- Ask follow-up questions when needed for clarification
- Be concise but thorough in your explanations
"""
    
    def _build_gemini_history(self, conversation_history: dict) -> list:
        """Build conversation history for Gemini chat session"""
        
        history = []
        chat_messages = conversation_history.get("chat", [])
        
        # Take last 10 messages for context (5 exchanges)
        recent_messages = chat_messages[-10:]
        
        for i in range(0, len(recent_messages), 2):
            if i + 1 < len(recent_messages):
                user_msg = recent_messages[i]
                assistant_msg = recent_messages[i + 1]
                
                if user_msg["by"] == "you" and assistant_msg["by"] == "khoj":
                    history.append({
                        "role": "user",
                        "parts": [user_msg["message"]]
                    })
                    history.append({
                        "role": "model", 
                        "parts": [assistant_msg["message"]]
                    })
        
        return history
    
    def _get_conversation_history(self, conversation_id: int) -> dict:
        """Get conversation history in simple format"""
        conversation = adapters.get_conversation(self.db, conversation_id)
        if not conversation:
            return {"chat": []}
            
        chat_history = []
        for message in conversation.messages:
            # Add user message
            chat_history.append({
                "by": "you",
                "message": message.user_message,
                "created": message.created_at.isoformat()
            })
            
            # Add khoj message  
            chat_history.append({
                "by": "khoj", 
                "message": message.khoj_message,
                "created": message.created_at.isoformat()
            })
            
        return {"chat": chat_history} 