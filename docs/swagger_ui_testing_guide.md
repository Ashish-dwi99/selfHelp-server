# Khoj Backend - Swagger UI Testing Guide

## Introduction

This document provides guidance for testing the Khoj backend API using Swagger UI. It outlines the key endpoints to test, expected behaviors, and special considerations for authentication bypass testing.

## Starting the Server

To start the backend server for Swagger UI testing:

```bash
cd /home/ubuntu/khoj-project/khoj-backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Once started, access the Swagger UI at: http://localhost:8000/docs

## Authentication Testing

### Normal Authentication Flow

1. Use the `/auth/token` endpoint to obtain an access token
   - Provide username and password in the request body
   - Verify that a valid token is returned

2. Use the token for authenticated endpoints
   - Click the "Authorize" button in Swagger UI
   - Enter the token in the format: `Bearer {token}`
   - Verify that authenticated endpoints now work

### Authentication Bypass Testing

1. Check current bypass status
   - Use the `/auth-toggle/status` endpoint
   - Verify that it returns the current status

2. Enable authentication bypass
   - Use the `/auth-toggle/enable` endpoint
   - Verify that it returns success and creates a test user

3. Test the bypass
   - Use the `/auth-toggle/test` endpoint
   - Verify that it confirms the bypass is working

4. Access authenticated endpoints without a token
   - Try various authenticated endpoints
   - Verify they work without providing a token

5. Disable authentication bypass
   - Use the `/auth-toggle/disable` endpoint
   - Verify that authenticated endpoints now require a token again

## Key Endpoints to Test

### User Management

- `/auth/register`: Create a new user
- `/auth/me`: Get current user information
- `/auth/api-token`: Create API token
- `/auth/api-tokens`: List API tokens
- `/auth/api-token/{token_id}`: Delete API token

### Core API

- `/search`: Test search functionality with various parameters
- `/update`: Test content update
- `/transcribe`: Test audio transcription (if applicable)
- `/settings`: Get user settings
- `/user/name`: Update user name

### Agents

- `/agents/`: List agents
- `/agents/{slug}`: Get agent by slug
- `/agents/`: Create agent
- `/agents/{agent_id}`: Update agent
- `/agents/{agent_id}`: Delete agent

### Chat

- `/chat/conversation`: Create conversation
- `/chat/conversations`: List conversations
- `/chat/conversation/{conversation_id}`: Get conversation
- `/chat/conversation/{conversation_id}`: Delete conversation
- `/chat/conversation/{conversation_id}/message`: Create message
- `/chat/models`: List chat models
- `/chat/default-model`: Get default chat model

### Content

- `/content/sources`: Get content sources
- `/content/upload`: Upload content
- `/content/files`: List files
- `/content/file/{file_id}`: Delete file
- `/content/notion/config`: Set/get/delete Notion config
- `/content/github/config`: Set/get/delete GitHub config
- `/content/github/repos`: Add/list GitHub repos

### Subscription

- `/subscription/status`: Get subscription status
- `/subscription/enable-trial`: Enable trial
- `/subscription/update`: Update subscription

## Expected Behaviors

1. All endpoints should return appropriate status codes:
   - 200/201 for successful operations
   - 400 for bad requests
   - 401 for unauthorized access
   - 404 for not found resources
   - 500 for server errors

2. Authentication should work as expected:
   - Endpoints should require authentication when bypass is disabled
   - Endpoints should work without authentication when bypass is enabled

3. Response formats should match the expected schemas

## Reporting Issues

Document any issues found during testing:
- Endpoint URL
- Request method and parameters
- Expected behavior
- Actual behavior
- Error messages or status codes

## Conclusion

Thorough testing via Swagger UI ensures that the API is compatible with the existing UI and behaves as expected. Any issues found should be addressed before proceeding to end-to-end UI-backend flow testing.
