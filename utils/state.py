from enum import Enum
from typing import Dict, List, Set

# Define search types
class SearchType(str, Enum):
    All = "all"
    Org = "org"
    Markdown = "markdown"
    Pdf = "pdf"
    Github = "github"
    Notion = "notion"
    Plaintext = "plaintext"
    Image = "image"

# Global state variables
embeddings_model = {}
search_models = {}
query_cache: Dict[str, Dict[str, List]] = {}
config = None
config_file = "config.yaml"
openai_client = None
offline_chat_processor_config = None
