"""
Optional AgentOps integration for production observability.
Uncomment and configure if you want to enable AgentOps monitoring.
"""
import os
import logging

logger = logging.getLogger(__name__)

# Check if AgentOps is enabled
AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")

if AGENTOPS_API_KEY:
    try:
        from agentops import AgentOps
        
        # Initialize AgentOps
        agentops = AgentOps(
            api_key=AGENTOPS_API_KEY,
            tags=["ecommerce", "product-catalog", "mcp"],
            max_wait_time=5  # seconds
        )
        logger.info("AgentOps initialized successfully")
        
        # AgentOps will automatically instrument the agent when it's created
        # No additional code needed - it tracks:
        # - Tool calls and responses
        # - Agent responses
        # - Errors and exceptions
        # - Latency metrics
        
    except ImportError:
        logger.warning("AgentOps package not installed. Install with: pip install agentops")
        agentops = None
    except Exception as e:
        logger.error(f"Failed to initialize AgentOps: {str(e)}")
        agentops = None
else:
    logger.info("AgentOps API key not found, observability disabled")
    agentops = None


def wrap_agent_with_observability(agent):
    """
    Wrap agent with AgentOps observability.
    
    Args:
        agent: ADK Agent instance
        
    Returns:
        Agent instance (AgentOps automatically instruments it)
    """
    if agentops:
        logger.info("Agent wrapped with AgentOps observability")
        # AgentOps automatically instruments the agent
        # No explicit wrapping needed - it hooks into ADK internals
    else:
        logger.info("AgentOps not available, skipping observability setup")
    
    return agent

