import time
import logging
from typing import List, Dict, Any, Optional, Union
import math
from enum import Enum

logger = logging.getLogger(__name__)

def timer(message, logger=None):
    """Context manager for timing code execution"""
    class TimerContext:
        def __init__(self, message, logger=None):
            self.message = message
            self.logger = logger
            
        def __enter__(self):
            self.start_time = time.time()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            end_time = time.time()
            duration = end_time - self.start_time
            log_message = f"{self.message}: {duration:.3f} seconds"
            if self.logger:
                self.logger.debug(log_message)
            else:
                print(log_message)
    
    return TimerContext(message, logger)

def is_none_or_empty(value):
    """Check if a value is None or empty"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if hasattr(value, "__len__") and len(value) == 0:
        return True
    return False

class ConversationCommand(str, Enum):
    Default = "default"
    Notes = "notes"
    Online = "online"
    Webpage = "webpage"
    Code = "code"
    Image = "image"
    Diagram = "diagram"

def get_gemini_client(api_key: str, api_base_url: str = None):
    """Get Gemini client"""
    from google import genai
    client = genai.Client(api_key=api_key)
    return client

def get_chat_usage_metrics(model_name: str, input_tokens: int, output_tokens: int, thought_tokens: int = 0, usage: dict = None):
    """Get chat usage metrics"""
    if usage is None:
        usage = {}
    
    return {
        "input_tokens": usage.get("input_tokens", 0) + input_tokens,
        "output_tokens": usage.get("output_tokens", 0) + output_tokens,
        "thought_tokens": usage.get("thought_tokens", 0) + thought_tokens,
        "model_name": model_name
    }

def is_promptrace_enabled():
    """Check if prompt tracing is enabled"""
    import os
    return os.getenv("KHOJ_PROMPTRACE_ENABLED", "false").lower() == "true"
