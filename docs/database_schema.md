# Khoj Backend - Database Schema Documentation

## Introduction

This document provides a comprehensive overview of the Khoj backend database schema. It is designed to help both junior developers understand the data structure and product managers understand the data relationships and capabilities of the system.

## Database Technology

The Khoj backend uses PostgreSQL as its primary database system with the following key technologies:

- **PostgreSQL**: A powerful, open-source object-relational database system
- **pgvector extension**: Enables vector operations for similarity search
- **Django ORM**: Provides an abstraction layer for database operations

## Core Database Models

### User Models

#### KhojUser

The central user model that extends Django's AbstractUser with additional fields.

**Fields:**
- `uuid`: UUID field for unique user identification
- `phone_number`: PhoneNumberField for user's phone number
- `verified_phone_number`: Boolean indicating if phone number is verified
- `verified_email`: Boolean indicating if email is verified
- `email_verification_code`: String for email verification
- `email_verification_code_expiry`: DateTime for verification code expiration
- Plus all fields from Django's AbstractUser (username, email, password, etc.)

**Relationships:**
- One-to-one with GoogleUser
- One-to-one with Subscription
- One-to-many with KhojApiUser
- One-to-many with Agent (as creator)
- One-to-many with NotionConfig
- One-to-many with GithubConfig

**Purpose:**
Stores core user information and authentication details.

#### GoogleUser

Stores Google OAuth user information linked to a KhojUser.

**Fields:**
- `sub`: String for Google subject identifier
- `azp`: String for authorized party
- `email`: String for user's Google email
- `name`: String for user's full name
- `given_name`: String for user's first name
- `family_name`: String for user's last name
- `picture`: String for user's profile picture URL
- `locale`: String for user's locale preference

**Relationships:**
- One-to-one with KhojUser

**Purpose:**
Enables Google OAuth authentication and stores Google-specific user information.

#### KhojApiUser

Manages API tokens for authentication.

**Fields:**
- `token`: String for API authentication token
- `name`: String for token name/description
- `accessed_at`: DateTime for last access time

**Relationships:**
- Many-to-one with KhojUser

**Purpose:**
Enables API authentication for various clients and tracks token usage.

### Subscription Models

#### Subscription

Manages user subscription status and renewal.

**Fields:**
- `type`: String choice (trial, standard)
- `is_recurring`: Boolean indicating if subscription auto-renews
- `renewal_date`: DateTime for next renewal
- `enabled_trial_at`: DateTime when trial was enabled

**Relationships:**
- One-to-one with KhojUser

**Purpose:**
Tracks user subscription status for feature access control and billing.

### AI Models

#### AiModelApi

Stores API keys and URLs for external AI services.

**Fields:**
- `name`: String for service name
- `api_key`: String for API authentication key
- `api_base_url`: URL for API endpoint

**Relationships:**
- One-to-many with ChatModel

**Purpose:**
Manages connections to external AI services like OpenAI, Anthropic, etc.

#### ChatModel

Configures available chat models with their properties.

**Fields:**
- `max_prompt_size`: Integer for maximum prompt size
- `subscribed_max_prompt_size`: Integer for subscribed user prompt size
- `tokenizer`: String for tokenizer name
- `name`: String for model name
- `model_type`: String choice (openai, offline, anthropic, google)
- `price_tier`: String choice (free, standard)
- `vision_enabled`: Boolean indicating if vision features are supported
- `description`: Text for model description
- `strengths`: Text for model strengths

**Relationships:**
- Many-to-one with AiModelApi
- One-to-many with Agent

**Purpose:**
Defines available chat models and their capabilities.

#### VoiceModelOption

Configures available voice models.

**Fields:**
- `model_id`: String for model identifier
- `name`: String for model name
- `price_tier`: String choice (free, standard)

**Purpose:**
Defines available voice models for speech synthesis.

### Agent Models

#### Agent

Defines AI agents with their personalities and capabilities.

**Fields:**
- `name`: String for agent name
- `personality`: Text for agent personality description
- `input_tools`: Array of input tool choices
- `output_modes`: Array of output mode choices
- `managed_by_admin`: Boolean indicating if admin-managed
- `slug`: String for URL-friendly identifier
- `style_color`: String choice for UI color
- `style_icon`: String choice for UI icon
- `privacy_level`: String choice (public, private, protected)
- `is_hidden`: Boolean indicating if agent is hidden

**Relationships:**
- Many-to-one with KhojUser (creator)
- Many-to-one with ChatModel

**Purpose:**
Defines AI agents that can interact with the user's knowledge base.

### Integration Models

#### NotionConfig

Stores Notion integration configuration.

**Fields:**
- `token`: String for Notion API token

**Relationships:**
- Many-to-one with KhojUser

**Purpose:**
Enables integration with Notion for content indexing.

#### GithubConfig

Stores GitHub integration configuration.

**Fields:**
- `pat_token`: String for GitHub personal access token

**Relationships:**
- Many-to-one with KhojUser
- One-to-many with GithubRepoConfig

**Purpose:**
Enables integration with GitHub for content indexing.

#### GithubRepoConfig

Stores GitHub repository configuration.

**Fields:**
- `name`: String for repository name
- `owner`: String for repository owner
- `branch`: String for repository branch

**Relationships:**
- Many-to-one with GithubConfig

**Purpose:**
Configures specific GitHub repositories for content indexing.

#### WebScraper

Configures web scraping services.

**Fields:**
- `name`: String for scraper name
- `type`: String choice (Firecrawl, Olostep, Jina, Direct)
- `api_key`: String for API key
- `api_url`: URL for API endpoint
- `priority`: Integer for scraper priority

**Purpose:**
Configures web scraping services for content retrieval.

### Process Management Models

#### ProcessLock

Manages locks for thread-safe operations.

**Fields:**
- `name`: String choice for operation name
- `started_at`: DateTime for lock start time
- `max_duration_in_seconds`: Integer for maximum lock duration

**Purpose:**
Ensures thread-safety for critical operations like content indexing.

### Base Models

#### DbBaseModel

Abstract base model with timestamp fields.

**Fields:**
- `created_at`: DateTime for record creation time
- `updated_at`: DateTime for record update time

**Purpose:**
Provides common timestamp fields for all models.

### Pydantic Models

In addition to Django models, the system uses Pydantic models for data validation:

#### ChatMessage

Defines the structure of chat messages.

**Fields:**
- `message`: String for message content
- `trainOfThought`: List of thought process steps
- `context`: List of context information
- `onlineContext`: Dictionary of online context data
- `codeContext`: Dictionary of code context data
- `created`: String for creation timestamp
- `images`: Optional list of image references
- `by`: String for message author
- `turnId`: Optional string for conversation turn ID
- `intent`: Optional intent information

**Purpose:**
Validates chat message structure for API operations.

#### Context, CodeContextFile, CodeContextResult, etc.

Various Pydantic models for structured data validation.

**Purpose:**
Ensure data consistency and validation for API operations.

## Database Relationships Diagram

```
KhojUser
├── GoogleUser (1:1)
├── Subscription (1:1)
├── KhojApiUser (1:N)
├── Agent (1:N) [as creator]
├── NotionConfig (1:N)
└── GithubConfig (1:N)
    └── GithubRepoConfig (1:N)

ChatModel
├── AiModelApi (N:1)
└── Agent (1:N)
```

## Database Indexes and Performance

The database uses several indexes to optimize performance:

- Primary key indexes on all tables
- Foreign key indexes for relationships
- Vector indexes for similarity search
- Text indexes for full-text search

## Data Flow Examples

### User Authentication Flow

1. User logs in with username/password or OAuth
2. System looks up KhojUser record
3. If OAuth, system also checks GoogleUser record
4. System validates credentials and creates session
5. User is authenticated for subsequent requests

### Search Flow

1. User submits search query
2. System authenticates user
3. System retrieves user's content entries from database
4. System performs vector similarity search
5. System returns matching results to user

### Subscription Management Flow

1. User initiates subscription change
2. System updates Subscription record
3. System adjusts feature access based on subscription type
4. User receives confirmation of subscription change

## Data Migration Strategy

The database uses Django's migration framework for schema evolution:

1. Model changes are detected by Django
2. Migration files are generated
3. Migrations are applied to update the schema
4. Data is transformed as needed during migration

## Conclusion

The Khoj database schema is designed to support a wide range of features including search, chat, agent interactions, and integrations with external services. The schema is flexible and extensible, allowing for future enhancements while maintaining data integrity and performance.

This documentation provides a comprehensive understanding of the database structure and relationships, which is essential for both development and product management. Junior developers can use this to understand data access patterns, while product managers can understand the data capabilities and limitations of the system.
