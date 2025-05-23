# Khoj Backend - End-to-End UI-Backend Flow Testing Guide

## Introduction

This document provides guidance for conducting end-to-end testing between the Khoj UI and the new FastAPI backend. The purpose of these tests is to ensure that the UI and backend integrate seamlessly and that all user flows function as expected.

## Prerequisites

1. Backend server running on port 8000
2. Authentication bypass enabled for testing
3. UI code from the original repository

## Setting Up the UI for Testing

To test the UI with our new backend:

```bash
# Clone the original repository if not already done
cd /home/ubuntu/khoj-project
git clone https://github.com/khoj-ai/khoj.git ui-test

# Navigate to the web interface directory
cd ui-test/src/interface/web

# Install dependencies
npm install

# Configure the UI to point to our new backend
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local

# Start the UI development server
npm start
```

This will start the UI on port 3000, connecting to our backend on port 8000.

## Key User Flows to Test

### 1. Authentication Flow

- **User Registration**
  - Navigate to the registration page
  - Fill in user details
  - Submit the form
  - Verify successful registration and redirection

- **User Login**
  - Navigate to the login page
  - Enter credentials
  - Submit the form
  - Verify successful login and redirection to dashboard

- **Authentication Bypass**
  - Enable authentication bypass via API
  - Verify direct access to protected routes

### 2. Search Flow

- **Basic Search**
  - Enter a search query in the search box
  - Submit the search
  - Verify results are displayed correctly

- **Advanced Search with Filters**
  - Use advanced search options
  - Apply various filters
  - Verify filtered results are correct

### 3. Agent Interaction Flow

- **List Agents**
  - Navigate to agents page
  - Verify all agents are displayed

- **Create Agent**
  - Navigate to agent creation page
  - Fill in agent details
  - Submit the form
  - Verify agent is created and displayed

- **Use Agent**
  - Select an agent
  - Interact with the agent
  - Verify responses are correct

### 4. Chat Flow

- **Create Conversation**
  - Navigate to chat page
  - Start a new conversation
  - Verify conversation is created

- **Send Messages**
  - Enter a message
  - Send the message
  - Verify message is displayed and response is received

- **View Conversation History**
  - Navigate to conversation history
  - Select a previous conversation
  - Verify all messages are displayed correctly

### 5. Content Management Flow

- **Upload Content**
  - Navigate to content upload page
  - Select a file to upload
  - Submit the upload
  - Verify file is uploaded and indexed

- **View Content**
  - Navigate to content list
  - Verify all content is displayed

- **Delete Content**
  - Select content to delete
  - Confirm deletion
  - Verify content is removed

### 6. Settings Flow

- **View Settings**
  - Navigate to settings page
  - Verify all settings are displayed correctly

- **Update Settings**
  - Change various settings
  - Save changes
  - Verify settings are updated

### 7. Subscription Flow

- **View Subscription**
  - Navigate to subscription page
  - Verify subscription details are displayed

- **Update Subscription**
  - Change subscription type
  - Save changes
  - Verify subscription is updated

## Testing Methodology

For each flow:

1. **Preparation**
   - Ensure the backend server is running
   - Clear any previous test data if necessary
   - Navigate to the starting point for the flow

2. **Execution**
   - Perform each step in the flow
   - Document any unexpected behavior

3. **Verification**
   - Verify the expected outcome
   - Check for any error messages or console errors
   - Verify data persistence where applicable

## Reporting Issues

Document any issues found during testing:
- Flow name and step
- Expected behavior
- Actual behavior
- Error messages or console logs
- Screenshots if applicable

## Conclusion

Thorough end-to-end testing ensures that the new backend works seamlessly with the existing UI. Any issues found should be addressed before proceeding to process map validation and final packaging.
