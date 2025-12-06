"""
HTTP Server for ADK Agent Integration.
This server exposes the agent via REST API for the Express backend to call.
"""
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

# Import agent
try:
    from agent_complete import root_agent
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
except ImportError as e:
    print(f"Error importing agent: {e}")
    print("Make sure you're in the adk-agent directory and dependencies are installed")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(title="ADK Agent Server", version="1.0.0")

# Configure CORS to allow requests from frontend
# Frontend connects directly to agent server (bypasses Express backend)
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
allowed_origins = [
    frontend_origin,
    "http://localhost:3000",  # Default Next.js dev server
    "http://127.0.0.1:3000",
]

# In production, you should set FRONTEND_ORIGIN to your actual frontend URL
if os.getenv("NODE_ENV") != "production":
    allowed_origins.append("*")  # Allow all in development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize session service (in-memory for now, can be replaced with persistent storage)
session_service = InMemorySessionService()

# Initialize runner (reused for all requests)
runner = Runner(
    app_name="product-catalog-agent",
    agent=root_agent,
    session_service=session_service,
)


# Request/Response models
class AgentQueryRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None


class AgentQueryResponse(BaseModel):
    status: str
    response: str
    sessionId: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "adk-agent-server"}


@app.post("/query", response_model=AgentQueryResponse)
async def query_agent(request: AgentQueryRequest):
    """
    Query the agent with a user message.
    
    Args:
        request: AgentQueryRequest with message and optional sessionId
        
    Returns:
        AgentQueryResponse with agent's response
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get or create session
        session_id = request.sessionId
        user_id = f"user-{session_id}" if session_id else f"user-{os.urandom(8).hex()}"
        
        # Get or create session for this user
        try:
            if session_id:
                session = await session_service.get_session(
                    app_name="product-catalog-agent",
                    session_id=session_id
                )
            else:
                # Create a new session
                session = await session_service.create_session(
                    app_name="product-catalog-agent",
                    user_id=user_id,
                )
                session_id = session.id
        except Exception:
            # Session doesn't exist, create a new one
            session = await session_service.create_session(
                app_name="product-catalog-agent",
                user_id=user_id,
            )
            session_id = session.id
        
        # Create message content
        new_message = types.Content(parts=[types.Part(text=request.message)])
        
        # Run the agent query with the session
        # Note: runner.run() returns a generator, so we need to collect the response
        response_generator = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
        )
        
        # Collect response from generator
        response_parts = []
        for event in response_generator:
            if hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_parts.append(part.text)
        
        response_text = " ".join(response_parts) if response_parts else "No response received"
        
        return AgentQueryResponse(
            status="success",
            response=response_text,
            sessionId=session_id
        )
    except Exception as e:
        error_message = str(e)
        print(f"Error querying agent: {error_message}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return AgentQueryResponse(
            status="error",
            response="",
            sessionId=request.sessionId,
            error=error_message
        )


if __name__ == "__main__":
    port = int(os.getenv("AGENT_SERVER_PORT", "8000"))
    host = os.getenv("AGENT_SERVER_HOST", "0.0.0.0")
    
    print(f"Starting ADK Agent Server on {host}:{port}")
    print(f"Agent: {root_agent.name}")
    print(f"Model: {root_agent.model}")
    print(f"Tools: {len(root_agent.tools)}")
    
    uvicorn.run(app, host=host, port=port)

