"""
Example of how to integrate the ADK agent with Express backend.
This shows how the backend can call the Python agent.
"""
import os
import sys
from dotenv import load_dotenv
from agent_mcp import root_agent
from google.adk.runners import Runner

# Load environment variables
load_dotenv()

# Initialize runner (you'd typically do this once and reuse it)
runner = Runner(agent=root_agent)


def query_agent(user_message: str, session_id: str = None) -> dict:
    """
    Query the agent with a user message.
    
    This function can be called from your Express backend via:
    - HTTP API (if you set up a Python HTTP server)
    - Subprocess (not recommended for production)
    - gRPC (if available)
    - Shared message queue (Redis, RabbitMQ, etc.)
    
    Args:
        user_message: The user's query/question
        session_id: Optional session ID for conversation context
        
    Returns:
        dict: Agent response with status and message
    """
    try:
        # Run the agent query
        # Note: In production, you'd want to use a proper session service
        response = runner.run(user_message)
        
        return {
            "status": "success",
            "response": str(response),
            "sessionId": session_id
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "sessionId": session_id
        }


# Example: Simple HTTP server (for development/testing)
# For production, consider using FastAPI or Flask with proper async handling
if __name__ == "__main__":
    import json
    
    # Example usage
    test_queries = [
        "Find me red t-shirts",
        "What products are in stock?",
        "Show me products under $50"
    ]
    
    print("Testing agent integration...")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = query_agent(query)
        print(f"Response: {json.dumps(result, indent=2)}")
        print("-" * 60)
    
    print("\n✅ Integration test complete!")
    print("\nTo integrate with Express backend:")
    print("1. Set up a Python HTTP server (FastAPI/Flask) that calls query_agent()")
    print("2. Have Express backend make HTTP requests to the Python server")
    print("3. Or use a message queue (Redis/RabbitMQ) for async communication")
    print("4. Or use ADK's built-in HTTP server if available")



