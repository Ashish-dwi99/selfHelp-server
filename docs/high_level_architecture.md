# Khoj Backend - High Level Architecture Documentation

## Introduction

This document provides a comprehensive high-level architecture overview of the Khoj backend system. The purpose of this documentation is to help both junior developers and product managers understand the overall structure, components, and interactions within the Khoj backend system.

## System Overview

Khoj is a personal AI search assistant that helps users search through their personal knowledge base. The system is designed as a monolithic application with a clear separation between frontend interfaces and backend services. The backend is primarily built using Django and includes various components for search, processing, database management, and API endpoints.

## Core Components

### 1. API Layer (Routers)

The API layer serves as the interface between clients and the backend system. It handles HTTP requests, processes them, and returns appropriate responses. The API endpoints are organized into different modules based on functionality:

- **API Core (`api.py`)**: Handles core search and query functionality
- **API Agents (`api_agents.py`)**: Manages AI agent interactions
- **API Chat (`api_chat.py`)**: Handles chat-related functionality
- **API Content (`api_content.py`)**: Manages content indexing and retrieval
- **API Model (`api_model.py`)**: Handles AI model configurations
- **API Subscription (`api_subscription.py`)**: Manages user subscriptions
- **Authentication (`auth.py`)**: Handles user authentication and authorization
- **Helpers (`helpers.py`)**: Contains utility functions for API operations

### 2. Database Layer

The database layer manages data persistence and retrieval. It uses Django's ORM with PostgreSQL as the database backend. Key models include:

- **User Models**: `KhojUser`, `GoogleUser`, `KhojApiUser`
- **Subscription Models**: `Subscription`
- **AI Models**: `ChatModel`, `AiModelApi`
- **Agent Models**: `Agent`
- **Integration Models**: `NotionConfig`, `GithubConfig`
- **Process Management**: `ProcessLock`

The database uses PostgreSQL with pgvector extension for vector storage and similarity search capabilities.

### 3. Processing Layer

The processing layer handles the transformation, indexing, and search operations on user content:

- **Content Processors**: Process different types of content (markdown, org, PDF, etc.)
- **Search Filters**: Apply filters to search results
- **Search Types**: Implement different search algorithms and strategies

### 4. Configuration and Management

This component handles system configuration, settings management, and administrative tasks:

- **Configure (`configure.py`)**: Manages system configuration
- **Main (`main.py`)**: Application entry point
- **Manage (`manage.py`)**: Django management commands

### 5. Utilities

Utility functions and helpers that support various operations across the system:

- **Utils**: General utility functions
- **Migrations**: Database migration scripts

## Data Flow

1. **Client Request**: A client (web, mobile, or API) sends a request to the backend
2. **API Router**: The appropriate router handles the request
3. **Authentication/Authorization**: Requests are authenticated and authorized
4. **Processing**: The request is processed by the relevant components
5. **Database Operations**: Data is retrieved from or stored in the database
6. **Response**: The processed result is returned to the client

## Integration Points

The backend integrates with several external services and systems:

- **AI Models**: OpenAI, Anthropic, Google, and offline models
- **External Content Sources**: Notion, GitHub
- **Web Scrapers**: Firecrawl, Olostep, Jina
- **Authentication Providers**: Google

## Deployment Architecture

The system is designed to be deployed as a containerized application using Docker. The `docker-compose.yml` file defines the services and their configurations:

- **Web Server**: Serves the application
- **Database**: PostgreSQL for data storage
- **Vector Database**: pgvector extension for vector operations

## Security Considerations

- **Authentication**: Multiple authentication methods (token, OAuth)
- **Authorization**: Role-based access control
- **API Security**: Rate limiting, input validation
- **Data Protection**: Encryption for sensitive data

## Scalability Considerations

- **Database Scaling**: PostgreSQL can be scaled horizontally
- **Processing Scaling**: Content processing can be distributed
- **API Scaling**: API endpoints can be load balanced

## Monitoring and Logging

- **Logging**: Comprehensive logging throughout the system
- **Error Handling**: Structured error handling and reporting

## Conclusion

The Khoj backend is a comprehensive system that provides search, processing, and API capabilities for personal knowledge management. Its modular design allows for flexibility and extensibility, while its integration with various external services enhances its functionality.

This high-level architecture provides a foundation for understanding the system's components and their interactions. More detailed information about specific components and their implementations can be found in the low-level design documentation.
