# Khoj Backend - Low Level and Feature-by-Feature Documentation

## Introduction

This document provides a detailed low-level design and feature-by-feature breakdown of the Khoj backend system. It is intended for both junior developers who need to understand the implementation details and product managers who need to understand the system capabilities and interactions.

## Core Features

### 1. Search Feature

The search functionality is the central feature of Khoj, allowing users to query their personal knowledge base.

#### API Endpoint: `/search`

**Implementation Details:**
- Located in `src/khoj/routers/api.py`
- Handles GET requests with query parameters for search text, result count, search type, and other options
- Requires authentication
- Returns a list of search results matching the query

**Process Flow:**
1. User sends a search query with parameters
2. System authenticates the request
3. Query is processed to remove filter terms
4. Query is encoded using the embeddings model
5. Search is executed across specified content types in parallel
6. Results are collated, ranked, and sorted
7. Top results are returned to the user

**Key Components:**
- `execute_search`: Core function that processes the search request
- `text_search.query`: Performs the actual search operation
- `text_search.collate_results`: Combines results from different sources
- `text_search.rerank_and_sort_results`: Ranks and sorts the search results

**Performance Considerations:**
- Uses concurrent execution for parallel searching across content types
- Implements caching to improve response time for repeated queries
- Logs execution time for performance monitoring

### 2. Content Update Feature

This feature allows users to update their indexed content, ensuring the search results remain current.

#### API Endpoint: `/update`

**Implementation Details:**
- Located in `src/khoj/routers/api.py`
- Handles GET requests with optional parameters for content type and force update
- Requires authentication
- Triggers reindexing of content

**Process Flow:**
1. User sends an update request
2. System authenticates the request
3. System validates the configuration
4. Content is reindexed based on parameters
5. Success status is returned to the user

**Key Components:**
- `initialize_content`: Core function that handles content initialization and updating

**Error Handling:**
- Checks for valid configuration before proceeding
- Catches and reports exceptions during the update process

### 3. Audio Transcription Feature

This feature converts audio input to text, supporting voice-based interaction with the system.

#### API Endpoint: `/transcribe`

**Implementation Details:**
- Located in `src/khoj/routers/api.py`
- Handles POST requests with audio file upload
- Requires authentication
- Implements rate limiting for both minute and daily usage
- Returns transcribed text

**Process Flow:**
1. User uploads an audio file
2. System authenticates the request and checks rate limits
3. Audio file size is validated
4. Audio is transcribed using configured service (OpenAI or offline)
5. Transcribed text is returned to the user

**Key Components:**
- `transcribe_audio_offline`: Handles offline transcription
- `transcribe_audio`: Handles OpenAI-based transcription

**Error Handling:**
- Validates file size with clear error messages
- Handles missing configuration gracefully
- Ensures temporary files are cleaned up

### 4. User Settings Management

This feature allows users to retrieve and update their settings.

#### API Endpoint: `/settings`

**Implementation Details:**
- Located in `src/khoj/routers/api.py`
- Handles GET requests with optional parameter for detailed information
- Requires authentication
- Returns user configuration

**Process Flow:**
1. User requests settings
2. System authenticates the request
3. User configuration is retrieved
4. Configuration is returned as JSON

**Key Components:**
- `get_user_config`: Retrieves user configuration based on authentication

### 5. User Profile Management

This feature allows users to update their profile information.

#### API Endpoint: `/user/name`

**Implementation Details:**
- Located in `src/khoj/routers/api.py`
- Handles PATCH requests with name parameter
- Requires authentication
- Updates user name

**Process Flow:**
1. User sends name update request
2. System authenticates the request
3. Name is validated and parsed
4. User record is updated
5. Success status is returned

**Key Components:**
- `adapters.set_user_name`: Updates user name in the database

**Validation:**
- Ensures name follows required format (first name, last name)
- Returns clear error messages for invalid formats

### 6. Reference and Question Extraction

This feature extracts references and questions from user queries to enhance search results.

**Implementation Details:**
- Located in `src/khoj/routers/api.py`
- Implemented as an async generator function
- Supports multiple AI models for extraction

**Process Flow:**
1. System receives user query and conversation context
2. Query is processed to extract filter terms
3. Appropriate AI model is selected based on configuration
4. AI model extracts relevant questions from the query
5. References are compiled based on extracted questions
6. Results are yielded incrementally

**Key Components:**
- `extract_questions_offline`: Extracts questions using offline models
- `extract_questions`: Extracts questions using OpenAI models
- `extract_questions_anthropic`: Extracts questions using Anthropic models
- `extract_questions_gemini`: Extracts questions using Google Gemini models

**Model Selection Logic:**
- Checks for user's configured chat model
- Falls back to appropriate defaults based on availability
- Handles different model types with specialized extraction functions

### 7. Authentication and Authorization

The system implements comprehensive authentication and authorization mechanisms.

**Implementation Details:**
- Located in `src/khoj/routers/auth.py`
- Supports multiple authentication methods (token, OAuth)
- Implements role-based access control

**Key Components:**
- `KhojUser`: Core user model with authentication fields
- `GoogleUser`: Model for Google OAuth integration
- `KhojApiUser`: Model for API token authentication

**Security Considerations:**
- Implements proper token validation
- Handles session management
- Provides clear error messages for authentication failures

### 8. Agent Management

This feature allows the creation and management of AI agents that can interact with the user's knowledge base.

**Implementation Details:**
- Located in `src/khoj/routers/api_agents.py`
- Agents are defined by personality, input tools, and output modes
- Supports public, private, and protected access levels

**Key Components:**
- `Agent`: Core model defining agent properties and behavior
- `AgentAdapters`: Provides database operations for agents

**Agent Capabilities:**
- Can access user's knowledge base
- Can have specialized personalities
- Can use different input tools and output modes

### 9. Chat Functionality

This feature provides conversational interaction with the system.

**Implementation Details:**
- Located in `src/khoj/routers/api_chat.py`
- Supports multiple chat models (OpenAI, Anthropic, Google, offline)
- Handles message history and context

**Key Components:**
- `ChatMessage`: Defines the structure of chat messages
- `ChatModel`: Configures available chat models

**Process Flow:**
1. User sends a chat message
2. System processes the message using the configured chat model
3. References are extracted from the user's knowledge base
4. Response is generated based on the message and references
5. Response is returned to the user

## Database Schema

The database uses PostgreSQL with the pgvector extension for vector operations. Key models include:

### User Models

- `KhojUser`: Extends Django's AbstractUser with additional fields for phone verification and UUID
- `GoogleUser`: Stores Google OAuth user information linked to KhojUser
- `KhojApiUser`: Manages API tokens for authentication

### Content Models

- Various models for different content types (markdown, org, PDF, etc.)
- Models include vector fields for similarity search

### AI Models

- `ChatModel`: Configures available chat models with their properties
- `AiModelApi`: Stores API keys and URLs for external AI services

### Agent Models

- `Agent`: Defines AI agents with their personalities and capabilities
- Includes fields for privacy level, style, and input/output options

### Subscription Models

- `Subscription`: Manages user subscription status and renewal
- Supports different subscription types (trial, standard)

## Integration Points

The backend integrates with several external services:

### AI Services

- OpenAI: For chat and transcription
- Anthropic: For chat
- Google: For chat
- Offline models: For local processing

### Content Sources

- Notion: For retrieving and indexing Notion content
- GitHub: For retrieving and indexing GitHub repositories

### Web Scrapers

- Firecrawl, Olostep, Jina: For web content retrieval and processing

## Error Handling

The system implements comprehensive error handling:

- Input validation with clear error messages
- Exception catching and logging
- Appropriate HTTP status codes for different error conditions

## Rate Limiting

To prevent abuse and ensure fair usage:

- API-level rate limiting for resource-intensive operations
- Different limits for trial and subscribed users
- Time-based windows (minute, day) for rate limit calculation

## Caching

The system uses caching to improve performance:

- Query results are cached for repeated searches
- Cache is user-specific to maintain privacy
- Cache is cleared when content is updated

## Conclusion

This low-level and feature-by-feature documentation provides a comprehensive understanding of the Khoj backend system. It covers the implementation details, process flows, and interactions of each major feature, as well as the database schema and integration points. This information should be valuable for both junior developers working on the codebase and product managers planning feature enhancements or changes.
