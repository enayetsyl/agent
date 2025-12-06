"""
ADK Agent with MCP Toolbox for Databases 
Direct database access via Model Context Protocol for better performance.
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
import google.auth
from logging_config import setup_logging
from tools.product_tools import (
    search_products_mcp,
    get_product_details_mcp,
    get_product_by_slug_mcp,
    check_product_availability_mcp,
    get_categories_mcp
)

# Setup logging
logger = setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/agent.log")
)

# Optional: Initialize AgentOps for observability
try:
    from agentops_setup import agentops
    if agentops:
        logger.info("AgentOps observability enabled")
except ImportError:
    logger.debug("AgentOps not configured, skipping observability setup")

# Database connection configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

logger.info(f"Initializing MCP Toolbox with database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'configured'}")

# Set up credentials (supports Application Default Credentials)
try:
    credentials, project = google.auth.default()
    credentials_config = DatabaseCredentialsConfig(credentials=credentials)
    logger.info("Google credentials loaded successfully")
except Exception as e:
    logger.warning(f"Could not load Google credentials: {e}. Using default credentials.")
    credentials_config = DatabaseCredentialsConfig()

# Initialize MCP Toolbox for PostgreSQL
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


# Create tool wrappers that include mcp_toolbox
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
    """
    Search for products in the catalog.

    Args:
        query: Search query string (searches in name, description, brand)
        category: Category name or slug to filter by
        max_price: Maximum price filter
        min_price: Minimum price filter
        brand: Brand name to filter by
        in_stock: Only show products in stock (default: True)
        featured: Filter by featured status
        limit: Maximum number of results (default: 10)

    Returns:
        dict: Dictionary with status and list of matching products
    """
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
    """
    Get detailed information about a specific product.

    Args:
        product_id: The ID of the product

    Returns:
        dict: Product details or error message
    """
    return get_product_details_mcp(mcp_toolbox=mcp_toolbox, product_id=product_id)


def get_product_by_slug(slug: str) -> Dict:
    """
    Get product details by slug.

    Args:
        slug: Product slug (URL-friendly identifier)

    Returns:
        dict: Product details or error message
    """
    return get_product_by_slug_mcp(mcp_toolbox=mcp_toolbox, slug=slug)


def check_product_availability(
    product_id: int,
    size: Optional[str] = None,
    color: Optional[str] = None
) -> Dict:
    """
    Check if a product is available in specific size and/or color.

    Args:
        product_id: The ID of the product
        size: Optional size to check (e.g., "M", "10")
        color: Optional color to check (e.g., "red", "black")

    Returns:
        dict: Availability information
    """
    return check_product_availability_mcp(
        mcp_toolbox=mcp_toolbox,
        product_id=product_id,
        size=size,
        color=color
    )


def get_categories() -> Dict:
    """
    Get all available product categories.

    Returns:
        dict: List of categories
    """
    return get_categories_mcp(mcp_toolbox=mcp_toolbox)


# Create the agent
root_agent = Agent(
    name="product_catalog_agent_mcp",
    model="gemini-2.0-flash",
    description="Agent to help users search and find products using direct database access via MCP Toolbox.",
    instruction=(
        "You are a helpful product assistant. Help users find products by searching the catalog. "
        "When showing products, always include the name, price, and availability. "
        "Be conversational and friendly. If a product is not found, suggest similar items or ask for clarification. "
        "When users ask about 'this product' or 'the blue one', refer to products from recent search results stored in session state. "
        "Always check product availability before confirming it's in stock. "
        "Use the search_products tool first to find products, then use get_product_details or get_product_by_slug for more information. "
        "When checking availability for specific sizes or colors, use the check_product_availability tool."
    ),
    tools=[
        search_products,
        get_product_details,
        get_product_by_slug,
        check_product_availability,
        get_categories
    ]
)

logger.info("Agent created successfully with MCP Toolbox integration")

if __name__ == "__main__":
    logger.info("Agent module loaded. Use this agent with an ADK Runner.")
    logger.info("Example: from agent_mcp import root_agent")

