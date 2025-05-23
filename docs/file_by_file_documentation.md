# Khoj Backend - File-by-File Documentation

## Introduction

This document provides a comprehensive file-by-file breakdown of the Khoj backend system. It is designed to help both junior developers understand the codebase structure and product managers understand the system components and their relationships.

## Core Backend Files

### 1. Main Application Files

#### `src/khoj/main.py`

**Purpose:** Serves as the entry point for the Khoj backend application.

**Key Functions:**
- Initializes the FastAPI application
- Sets up middleware for authentication, CORS, and other services
- Configures API routers
- Handles startup and shutdown events

**Dependencies:**
- FastAPI framework
- Khoj configuration module
- API routers

**Usage Context:**
This file is the starting point when the application is launched. It orchestrates the initialization of all components and ensures they are properly connected.

#### `src/khoj/configure.py`

**Purpose:** Manages the configuration of the Khoj system.

**Key Functions:**
- Loads configuration from files and environment variables
- Initializes content processors and search models
- Sets up database connections
- Configures external services

**Dependencies:**
- Configuration files
- Environment variables
- Database models

**Usage Context:**
This file is used during system startup to ensure all components are properly configured. It is also used when configuration changes are made through the API.

#### `src/khoj/manage.py`

**Purpose:** Provides Django management commands for database operations.

**Key Functions:**
- Handles database migrations
- Provides command-line interface for administrative tasks
- Manages database schema updates

**Dependencies:**
- Django framework
- Database models

**Usage Context:**
This file is used primarily during development and deployment for database management tasks.

### 2. API Router Files

#### `src/khoj/routers/api.py`

**Purpose:** Implements core API endpoints for search and system management.

**Key Endpoints:**
- `/search`: Performs search operations across user content
- `/update`: Updates indexed content
- `/transcribe`: Transcribes audio to text
- `/settings`: Retrieves user settings
- `/user/name`: Updates user name

**Dependencies:**
- FastAPI framework
- Authentication middleware
- Search processors
- Database adapters

**Usage Context:**
This file handles the primary interaction points for clients accessing the Khoj system's core functionality.

#### `src/khoj/routers/api_agents.py`

**Purpose:** Implements API endpoints for managing AI agents.

**Key Endpoints:**
- Agent creation, retrieval, update, and deletion
- Agent configuration management
- Agent access control

**Dependencies:**
- FastAPI framework
- Authentication middleware
- Agent models and adapters

**Usage Context:**
This file handles all operations related to AI agents that can interact with the user's knowledge base.

#### `src/khoj/routers/api_chat.py`

**Purpose:** Implements API endpoints for chat functionality.

**Key Endpoints:**
- Chat message handling
- Conversation management
- Chat model configuration

**Dependencies:**
- FastAPI framework
- Authentication middleware
- Chat models and processors
- Reference extraction

**Usage Context:**
This file handles conversational interactions between users and the Khoj system.

#### `src/khoj/routers/api_content.py`

**Purpose:** Implements API endpoints for content management.

**Key Endpoints:**
- Content indexing
- Content retrieval
- Content source configuration

**Dependencies:**
- FastAPI framework
- Authentication middleware
- Content processors
- Database adapters

**Usage Context:**
This file handles operations related to managing the content that Khoj indexes and searches.

#### `src/khoj/routers/api_subscription.py`

**Purpose:** Implements API endpoints for subscription management.

**Key Endpoints:**
- Subscription status retrieval
- Subscription updates
- Payment processing

**Dependencies:**
- FastAPI framework
- Authentication middleware
- Subscription models and adapters

**Usage Context:**
This file handles user subscription management for premium features.

#### `src/khoj/routers/auth.py`

**Purpose:** Implements authentication and authorization endpoints.

**Key Endpoints:**
- User registration
- Login and logout
- Token management
- OAuth integration

**Dependencies:**
- FastAPI framework
- Authentication middleware
- User models and adapters

**Usage Context:**
This file handles user authentication and authorization for accessing the Khoj system.

#### `src/khoj/routers/helpers.py`

**Purpose:** Provides utility functions for API routers.

**Key Functions:**
- Rate limiting
- Common query parameter handling
- Telemetry tracking
- User configuration retrieval

**Dependencies:**
- FastAPI framework
- Database models and adapters

**Usage Context:**
This file contains shared functionality used across multiple API routers.

### 3. Database Files

#### `src/khoj/database/models/__init__.py`

**Purpose:** Defines the database schema using Django models.

**Key Models:**
- User models (`KhojUser`, `GoogleUser`, `KhojApiUser`)
- Content models
- AI models (`ChatModel`, `AiModelApi`)
- Agent models (`Agent`)
- Subscription models (`Subscription`)

**Dependencies:**
- Django ORM
- PostgreSQL with pgvector extension

**Usage Context:**
This file defines the structure of the database and the relationships between different entities.

#### `src/khoj/database/adapters.py`

**Purpose:** Provides database access functions for the application.

**Key Functions:**
- User management
- Content management
- Agent management
- Subscription management

**Dependencies:**
- Database models
- Django ORM

**Usage Context:**
This file abstracts database operations for the rest of the application, providing a clean interface for data access.

#### `src/khoj/database/migrations/`

**Purpose:** Contains database migration files for schema evolution.

**Key Components:**
- Migration scripts for each schema change
- Migration history tracking

**Dependencies:**
- Django migrations framework
- Database models

**Usage Context:**
These files are used to update the database schema when models change, ensuring data integrity during upgrades.

### 4. Processor Files

#### `src/khoj/processor/conversation/`

**Purpose:** Implements conversation processing logic for different AI models.

**Key Components:**
- Model-specific chat implementations (OpenAI, Anthropic, Google, offline)
- Prompt templates
- Response processing

**Dependencies:**
- AI model APIs
- Prompt templates
- Database models

**Usage Context:**
These files handle the interaction with various AI models for generating responses in conversations.

#### `src/khoj/processor/content/`

**Purpose:** Implements content processing logic for different content types.

**Key Components:**
- Content type-specific processors (markdown, org, PDF, etc.)
- Content extraction
- Content indexing

**Dependencies:**
- Content parsers
- Embedding models
- Database models

**Usage Context:**
These files handle the processing of different content types for indexing and searching.

### 5. Search Files

#### `src/khoj/search_type/text_search.py`

**Purpose:** Implements text search functionality.

**Key Functions:**
- Query processing
- Vector similarity search
- Result ranking and sorting

**Dependencies:**
- Embedding models
- Database models
- Search filters

**Usage Context:**
This file handles the core search functionality for finding relevant content based on user queries.

#### `src/khoj/search_filter/`

**Purpose:** Implements search filters for refining search results.

**Key Components:**
- Date filter
- Word filter
- File filter

**Dependencies:**
- Query parsing logic
- Database models

**Usage Context:**
These files handle the filtering of search results based on specific criteria.

### 6. Utility Files

#### `src/khoj/utils/state.py`

**Purpose:** Manages application state.

**Key Components:**
- Configuration state
- Model state
- Cache state

**Dependencies:**
- Configuration module
- Database models

**Usage Context:**
This file provides access to shared state across the application.

#### `src/khoj/utils/helpers.py`

**Purpose:** Provides utility functions for the application.

**Key Functions:**
- Timing functions
- String processing
- Enumeration definitions

**Dependencies:**
- Standard libraries

**Usage Context:**
This file contains general utility functions used throughout the application.

#### `src/khoj/utils/rawconfig.py`

**Purpose:** Defines configuration data structures.

**Key Components:**
- Configuration classes
- Response models
- Data validation

**Dependencies:**
- Pydantic models

**Usage Context:**
This file defines the structure of configuration data and API responses.

## Interface Files

### `src/interface/web/`

**Purpose:** Implements the web interface for Khoj.

**Key Components:**
- React frontend
- API client
- User interface components

**Dependencies:**
- React framework
- Backend API

**Usage Context:**
These files provide the web-based user interface for interacting with the Khoj system.

## Conclusion

This file-by-file documentation provides a comprehensive understanding of the Khoj backend system's structure. Each file has a specific purpose and role in the overall architecture, and understanding these roles is essential for both development and product management. The documentation should help junior developers navigate the codebase and product managers understand the system components and their relationships.
