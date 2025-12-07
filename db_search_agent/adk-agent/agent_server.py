"""
HTTP Server for ADK Agent Integration.
This server exposes the agent via REST API for the Express backend to call.
Also supports WebSocket for voice/audio streaming.
"""
import os
import sys
import json
import asyncio
import base64
import warnings
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
import uvicorn

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Load environment variables
load_dotenv()

# Import agents
try:
    from agent_complete import chat_agent, voice_agent, root_agent
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.agents import LiveRequestQueue
    from google.adk.agents.run_config import RunConfig, StreamingMode
    from google.genai import types
    from google.genai.types import Part, Content, Blob
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

# Initialize runners for different agent types
APP_NAME = "product-catalog-agent"

# Chat runner (for text-based chat)
chat_runner = Runner(
    app_name=APP_NAME,
    agent=chat_agent,
    session_service=session_service,
)

# Voice runner (for audio/voice interactions)
voice_runner = Runner(
    app_name=APP_NAME,
    agent=voice_agent,
    session_service=session_service,
)

# For backward compatibility
runner = chat_runner
root_agent = chat_agent


# WebSocket helper functions
async def start_agent_session(user_id: str, is_audio: bool = False):
    """Starts an agent session for WebSocket streaming"""
    print(f"[SESSION]: Starting agent session for user_id={user_id}, is_audio={is_audio}")
    
    # Select the appropriate agent and runner based on audio mode
    if is_audio:
        agent = voice_agent
        runner_to_use = voice_runner
        print(f"[SESSION]: Using VOICE agent (model: {voice_agent.model})")
    else:
        agent = chat_agent
        runner_to_use = chat_runner
        print(f"[SESSION]: Using CHAT agent (model: {chat_agent.model})")
    
    # Get or create session
    session_id = f"{APP_NAME}_{user_id}"
    session = await runner_to_use.session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if not session:
        print(f"[SESSION]: Creating new session: {session_id}")
        session = await runner_to_use.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
    else:
        print(f"[SESSION]: Using existing session: {session_id}")

    # Configure response format based on client preference
    # Check if model supports native audio
    model_name = agent.model if isinstance(agent.model, str) else agent.model.model
    is_native_audio = "native-audio" in model_name.lower() if model_name else False
    print(f"[SESSION]: Model: {model_name}, Native audio: {is_native_audio}")
    
    # IMPORTANT: gemini-2.0-flash doesn't support AUDIO modality for bidiGenerateContent
    # For non-native audio models, we use TEXT modality but still accept audio input
    # ADK will automatically convert audio input to text (speech-to-text)
    if is_native_audio:
        # Native audio models can use AUDIO modality
        modality = "AUDIO"
        print(f"[SESSION]: Using native audio model with AUDIO modality")
    elif is_audio:
        # For non-native models with audio input, use TEXT modality
        # Audio input will be converted to text automatically
        modality = "TEXT"
        print(f"[SESSION]: WARNING: Model {model_name} doesn't support AUDIO output")
        print(f"[SESSION]: Using TEXT modality - audio input will be converted to text")
        print(f"[SESSION]: For full audio streaming, use a native audio model (see AUDIO_MODEL_SETUP.md)")
    else:
        modality = "TEXT"
    
    print(f"[SESSION]: Final modality: {modality}")

    # Enable session resumption and output transcription for audio
    # Only enable audio transcription for native audio models
    # Note: Language configuration may be available in future ADK versions
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=[modality],
        session_resumption=types.SessionResumptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig() if (is_native_audio and is_audio) else None,
    )
    print(f"[SESSION]: RunConfig created: streaming_mode={run_config.streaming_mode}, modalities={run_config.response_modalities}")

    # Create LiveRequestQueue
    live_request_queue = LiveRequestQueue()
    print(f"[SESSION]: LiveRequestQueue created")

    # Start streaming session
    print(f"[SESSION]: Calling runner.run_live...")
    live_events = runner_to_use.run_live(
        user_id=user_id,
        session_id=session.id,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    print(f"[SESSION]: runner.run_live returned, live_events iterator created")
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket: WebSocket, live_events):
    """Agent to client communication via WebSocket"""
    try:
        print("[AGENT TO CLIENT]: Starting to listen for events...")
        event_count = 0
        async for event in live_events:
            event_count += 1
            # Reduced logging for performance - only log important events
            if event_count % 10 == 0 or hasattr(event, 'turn_complete') and event.turn_complete:
                print(f"[AGENT TO CLIENT]: Received event #{event_count}, type: {type(event).__name__}")
            
            # Handle input audio transcription (user's speech)
            # Only send when turn is complete to avoid fragmentation
            if hasattr(event, 'input_transcription') and event.input_transcription and event.input_transcription.text:
                # Check if this is a final transcription (turn complete) or partial
                is_final = hasattr(event, 'turn_complete') and event.turn_complete
                transcript_text = event.input_transcription.text
                
                # Only send if it's a meaningful chunk (not just single characters)
                if transcript_text.strip() and (is_final or len(transcript_text.strip()) > 1):
                    message = {
                        "mime_type": "text/plain",
                        "data": transcript_text,
                        "is_user_transcript": True,  # Mark as user transcript
                        "role": "user",
                        "turn_complete": is_final  # Indicate if this is the final chunk
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: user input transcript: {transcript_text} (final: {is_final})")
            
            # Handle output audio transcription (agent's speech)
            if hasattr(event, 'output_transcription') and event.output_transcription and event.output_transcription.text:
                transcript_text = event.output_transcription.text
                message = {
                    "mime_type": "text/plain",
                    "data": transcript_text,
                    "is_transcript": True,  # Mark as agent transcript
                    "role": "agent"
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: agent output transcript: {transcript_text}")

            # Read the Content and its first Part
            part: Part = None
            if event.content and event.content.parts and len(event.content.parts) > 0:
                part = event.content.parts[0]
                print(f"[AGENT TO CLIENT]: Part type: {type(part).__name__}")
            
            if part:
                # Audio data must be Base64-encoded for JSON transport
                is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
                if is_audio:
                    audio_data = part.inline_data and part.inline_data.data
                    if audio_data:
                        message = {
                            "mime_type": "audio/pcm",
                            "data": base64.b64encode(audio_data).decode("ascii")
                        }
                        await websocket.send_text(json.dumps(message))
                        print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")

                # If it's text, send it (only send meaningful chunks to reduce fragmentation)
                if hasattr(part, 'text') and part.text:
                    # Only send if it's a meaningful chunk (not just single characters)
                    if len(part.text.strip()) > 0:
                        message = {
                            "mime_type": "text/plain",
                            "data": part.text
                        }
                        await websocket.send_text(json.dumps(message))
                        # Reduced logging
                        if len(part.text) > 50:
                            print(f"[AGENT TO CLIENT]: text/plain: {part.text[:50]}...")

            # If the turn complete or interrupted, send it
            if hasattr(event, 'turn_complete') and event.turn_complete:
                message = {
                    "turn_complete": True,
                    "interrupted": False,
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: turn_complete")
            
            if hasattr(event, 'interrupted') and event.interrupted:
                message = {
                    "turn_complete": False,
                    "interrupted": True,
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: interrupted")
                
        print(f"[AGENT TO CLIENT]: Event loop ended. Total events: {event_count}")
    except WebSocketDisconnect:
        print("Client disconnected from agent_to_client_messaging")
    except Exception as e:
        print(f"Error in agent_to_client_messaging: {e}")
        import traceback
        traceback.print_exc()


async def client_to_agent_messaging(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    """Client to agent communication via WebSocket"""
    try:
        while True:
            message_json = await websocket.receive_text()
            message = json.loads(message_json)
            mime_type = message.get("mime_type")
            
            # Handle interrupt/stop signal
            if mime_type == "interrupt" or message.get("action") == "interrupt":
                live_request_queue.interrupt()
                print(f"[CLIENT TO AGENT]: Interrupt signal received")
                continue
            
            data = message.get("data")

            if mime_type == "text/plain":
                # send_content() sends text in "turn-by-turn mode"
                content = Content(role="user", parts=[Part.from_text(text=data)])
                live_request_queue.send_content(content=content)
                print(f"[CLIENT TO AGENT]: {data}")
            elif mime_type == "audio/pcm":
                # send_realtime() sends audio in "realtime mode"
                decoded_data = base64.b64decode(data)
                live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
                print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
            else:
                raise ValueError(f"Mime type not supported: {mime_type}")
    except WebSocketDisconnect:
        print("Client disconnected from client_to_agent_messaging")
    except Exception as e:
        print(f"Error in client_to_agent_messaging: {e}")
        import traceback
        traceback.print_exc()


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
        
        # Get or create session for this user (using chat runner's session service)
        try:
            if session_id:
                session = await chat_runner.session_service.get_session(
                    app_name="product-catalog-agent",
                    session_id=session_id
                )
            else:
                # Create a new session
                session = await chat_runner.session_service.create_session(
                    app_name="product-catalog-agent",
                    user_id=user_id,
                )
                session_id = session.id
        except Exception:
            # Session doesn't exist, create a new one
            session = await chat_runner.session_service.create_session(
                app_name="product-catalog-agent",
                user_id=user_id,
            )
            session_id = session.id
        
        # Create message content
        new_message = types.Content(parts=[types.Part(text=request.message)])
        
        # Run the agent query with the session using CHAT agent
        # Note: runner.run() returns a generator, so we need to collect the response
        response_generator = chat_runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
        )
        
        # Collect response from generator
        response_parts = []
        generator_error = None
        try:
            # Try to get at least one event from the generator
            event_count = 0
            for event in response_generator:
                event_count += 1
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_parts.append(part.text)
            
            # If generator completed without yielding any events, it might have failed silently
            if event_count == 0 and not response_parts:
                # Check if there's a rate limit issue by checking recent logs or error state
                # For now, assume it's a rate limit if no events were yielded
                generator_error = "Rate limit exceeded - no response from API"
                
        except Exception as gen_error:
            # Handle errors from the generator (e.g., rate limits)
            generator_error = gen_error
            error_str = str(gen_error)
            print(f"Error in response generator: {error_str}", file=sys.stderr)
            import traceback
            traceback.print_exc()
        
        # Handle generator errors (including silent failures)
        if generator_error:
            error_str = str(generator_error)
            
            # Check for rate limit errors
            if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str or 
                "quota" in error_str.lower() or "Rate limit" in error_str):
                user_message = (
                    "I'm sorry, but I've reached the API rate limit for today. "
                    "The free tier allows 20 requests per day. Please try again later, "
                    "or check your usage at https://ai.dev/usage?tab=rate-limit"
                )
                return AgentQueryResponse(
                    status="error",
                    response=user_message,
                    sessionId=session_id,
                    error="Rate limit exceeded"
                )
            else:
                # Other errors
                return AgentQueryResponse(
                    status="error",
                    response=f"I encountered an error: {error_str}",
                    sessionId=session_id,
                    error=error_str
                )
        
        # If no response parts and no error, it might be a silent failure
        if not response_parts:
            # Check if this might be a rate limit issue
            user_message = (
                "I'm sorry, but I couldn't get a response. This might be due to API rate limits. "
                "The free tier allows 20 requests per day. Please try again later, "
                "or check your usage at https://ai.dev/usage?tab=rate-limit"
            )
            return AgentQueryResponse(
                status="error",
                response=user_message,
                sessionId=session_id,
                error="No response received - possible rate limit"
            )
        
        response_text = " ".join(response_parts)
        
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
        
        # Check for rate limit errors
        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message or "quota" in error_message.lower():
            user_message = (
                "I'm sorry, but I've reached the API rate limit for today. "
                "The free tier allows 20 requests per day. Please try again later, "
                "or check your usage at https://ai.dev/usage?tab=rate-limit"
            )
            return AgentQueryResponse(
                status="error",
                response=user_message,
                sessionId=request.sessionId,
                error="Rate limit exceeded"
            )
        
        return AgentQueryResponse(
            status="error",
            response=f"I encountered an error: {error_message}",
            sessionId=request.sessionId,
            error=error_message
        )


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for voice/audio streaming.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID or session ID for session management (string)
    """
    try:
        # Accept the WebSocket connection first
        await websocket.accept()
        
        # Get is_audio from query parameters
        is_audio = websocket.query_params.get("is_audio", "false")
        print(f"Client {user_id} connected, audio mode: {is_audio}")

        live_events, live_request_queue = await start_agent_session(user_id, is_audio == "true")
    except Exception as e:
        print(f"Error accepting WebSocket connection for {user_id}: {e}")
        import traceback
        traceback.print_exc()
        # Try to close the connection if it was partially established
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
        return

    # Run bidirectional messaging concurrently
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    try:
        # Wait for either task to complete (connection close or error)
        tasks = [agent_to_client_task, client_to_agent_task]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        # Check for errors in completed tasks
        for task in done:
            if task.exception() is not None:
                print(f"Task error for client {user_id}: {task.exception()}")
                import traceback
                traceback.print_exception(
                    type(task.exception()),
                    task.exception(),
                    task.exception().__traceback__
                )
    finally:
        # Clean up resources
        live_request_queue.close()
        print(f"Client {user_id} disconnected")


if __name__ == "__main__":
    port = int(os.getenv("AGENT_SERVER_PORT", "8000"))
    host = os.getenv("AGENT_SERVER_HOST", "0.0.0.0")
    
    print(f"Starting ADK Agent Server on {host}:{port}")
    print(f"Chat Agent: {chat_agent.name} (Model: {chat_agent.model})")
    print(f"Voice Agent: {voice_agent.name} (Model: {voice_agent.model})")
    print(f"Tools: {len(chat_agent.tools)}")
    
    uvicorn.run(app, host=host, port=port)

