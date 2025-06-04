from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Khoj Backend API",
    description="FastAPI backend for Khoj personal AI search assistant",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from routers import api, api_agents, api_chat, api_content, api_subscription, auth, auth_toggle

# Include routers
app.include_router(api.router)
app.include_router(api_agents.router)
app.include_router(api_chat.router)
app.include_router(api_content.router)
app.include_router(api_subscription.router)
app.include_router(auth.router)
app.include_router(auth_toggle.router)

# Create static directory for Swagger UI if it doesn't exist
os.makedirs("static", exist_ok=True)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Khoj Backend API"}

# Middleware to add authentication toggle status to response headers
@app.middleware("http")
async def add_auth_toggle_status(request: Request, call_next):
    response = await call_next(request)
    # Get auth bypass status
    auth_bypass_enabled = os.getenv("AUTH_BYPASS_ENABLED", "false").lower() == "true"
    # Add to response headers
    response.headers["X-Auth-Bypass-Enabled"] = str(auth_bypass_enabled).lower()
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
