"""
Complete ADK Agent combining MCP Toolbox + Logging + AgentOps.
This is the production-ready version with all features integrated.
"""
import os
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from google.adk.agents import Agent
from db_wrapper import (
    MCPToolboxForDatabases,
    DatabaseCredentialsConfig
)
from logging_config import setup_logging
import google.auth

# Setup logging
logger = setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/agent.log")
)

# Initialize AgentOps
agentops = None
if os.getenv("AGENTOPS_API_KEY"):
    try:
        from agentops import AgentOps
        agentops = AgentOps(
            api_key=os.getenv("AGENTOPS_API_KEY"),
            tags=["ecommerce", "product-catalog", "mcp"],
            max_wait_time=5
        )
        logger.info("AgentOps initialized")
    except ImportError:
        logger.warning("AgentOps package not installed. Install with: pip install agentops")
    except Exception as e:
        logger.warning(f"Failed to initialize AgentOps: {str(e)}")
else:
    logger.info("AgentOps API key not found, observability disabled")

# Setup MCP Toolbox
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

try:
    credentials, project = google.auth.default()
    credentials_config = DatabaseCredentialsConfig(credentials=credentials)
    logger.info("Google credentials loaded successfully")
except Exception as e:
    logger.warning(f"Could not load Google credentials: {e}. Using default credentials.")
    credentials_config = DatabaseCredentialsConfig()

try:
    mcp_toolbox = MCPToolboxForDatabases(
        database_type="postgresql",
        connection_string=DATABASE_URL,
        credentials_config=credentials_config
    )
    logger.info("MCP Toolbox initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MCP Toolbox: {str(e)}", exc_info=True)
    raise

# Import custom tools
from tools.product_tools import (
    search_products_mcp,
    get_product_details_mcp,
    get_product_by_slug_mcp,
    check_product_availability_mcp,
    get_categories_mcp
)

# Create tool wrappers
def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    brand: Optional[str] = None,
    in_stock: bool = True,
    featured: Optional[bool] = None,
    limit: int = 10
) -> Dict:
    """Search for products in the catalog."""
    return search_products_mcp(
        mcp_toolbox=mcp_toolbox,
        query=query,
        category=category,
        max_price=max_price,
        min_price=min_price,
        brand=brand,
        in_stock=in_stock,
        featured=featured,
        limit=limit
    )


def get_product_details(product_id: int) -> Dict:
    """Get detailed information about a specific product."""
    return get_product_details_mcp(mcp_toolbox=mcp_toolbox, product_id=product_id)


def get_product_by_slug(slug: str) -> Dict:
    """Get product details by slug."""
    return get_product_by_slug_mcp(mcp_toolbox=mcp_toolbox, slug=slug)


def check_product_availability(
    product_id: int,
    size: Optional[str] = None,
    color: Optional[str] = None
) -> Dict:
    """Check if a product is available in specific size and/or color."""
    return check_product_availability_mcp(
        mcp_toolbox=mcp_toolbox,
        product_id=product_id,
        size=size,
        color=color
    )


def get_categories() -> Dict:
    """Get all available product categories."""
    return get_categories_mcp(mcp_toolbox=mcp_toolbox)


# Create agent
root_agent = Agent(
    name="product_catalog_agent",
    model="gemini-2.0-flash",
    description="Agent to help users search and find products in the catalog.",
    instruction=(
        "You are a helpful product assistant. Help users find products by searching the catalog. "
        "When showing products, always include the name, price, and availability. "
        "Be conversational and friendly. If a product is not found, suggest similar items or ask for clarification. "
        "When users ask about 'this product' or 'the blue one', refer to products from recent search results stored in session state. "
        "Always check product availability before confirming it's in stock."
    ),
    tools=[
        search_products,
        get_product_details,
        get_product_by_slug,
        check_product_availability,
        get_categories
    ]
)

logger.info("Agent created successfully")

