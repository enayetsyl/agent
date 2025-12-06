"""
Example usage of the ADK agent with MCP Toolbox.
This demonstrates how to use the agent in your application.
"""
import os
import asyncio
from dotenv import load_dotenv
from agent_mcp import root_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

# Load environment variables
load_dotenv()

async def main():
    """Example usage of the product catalog agent."""
    
    # Create session service
    session_service = InMemorySessionService()
    
    # Create a runner with the agent
    runner = Runner(
        app_name="product-catalog-agent",
        agent=root_agent,
        session_service=session_service,
    )
    
    # Example queries
    queries = [
        "Find me red t-shirts under $50",
        "What products are available in the electronics category?",
        "Show me featured products",
        "Check if product ID 1 is available in size M and color red",
        "What categories do you have?",
    ]
    
    print("=" * 60)
    print("Product Catalog Agent - Example Usage")
    print("=" * 60)
    print()
    
    # Create a session for the user
    user_id = "test_user"
    session = await session_service.create_session(
        app_name="product-catalog-agent",
        user_id=user_id,
    )
    
    from google.genai import types
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 60)
        
        try:
            # Create message content
            new_message = types.Content(parts=[types.Part(text=query)])
            
            # Run the query
            response_generator = runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=new_message,
            )
            
            # Collect response
            response_parts = []
            for event in response_generator:
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_parts.append(part.text)
            
            response = " ".join(response_parts) if response_parts else "No response received"
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print("=" * 60)
        print()


if __name__ == "__main__":
    asyncio.run(main())

