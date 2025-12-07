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
    get_product_variants_mcp,
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
    """
    Search for products in the catalog.
    
    Use this when users are searching for NEW products or browsing.
    DO NOT use this when users are asking about attributes (sizes/colors) of a product 
    they've already been discussing - use get_product_variants() instead.
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


def get_product_variants(
    product_id: Optional[int] = None,
    product_name: Optional[str] = None
) -> Dict:
    """
    Get all variants (sizes, colors, etc.) for a product.
    
    CRITICAL: Use this when users ask about sizes, colors, or variants.
    
    CONTEXT HANDLING:
    - If user asks about colors/sizes WITHOUT specifying a product, check conversation history for the most recently mentioned product.
    - Common product names to look for: 'jeans', 'Blue Denim Jeans', 't shirt', 'red cotton t shirt', 'Red Cotton T-Shirt', etc.
    - If you see 'jeans' in recent messages, use product_name='jeans' or product_name='Blue Denim Jeans'.
    - If you see 't shirt' or 'red cotton t shirt', use product_name='red cotton t shirt' or product_name='Red Cotton T-Shirt'.
    
    EXAMPLES:
    - User: "jeans" → You show jeans → User: "do you have alternative color" → Use product_name="jeans" (from context!)
    - User: "red cotton t shirt" → You show product → User: "do you have blue color" → Use product_name="red cotton t shirt" (from context!)
    - User: "what colors are available?" after discussing jeans → Use product_name="jeans" (from context!)
    
    You can provide either product_id or product_name. If product_name is provided, the tool will find the product first.
    If product_name is None but you know the product from conversation context, extract it from the recent messages.
    """
    return get_product_variants_mcp(
        mcp_toolbox=mcp_toolbox,
        product_id=product_id,
        product_name=product_name
    )


def get_categories() -> Dict:
    """Get all available product categories."""
    return get_categories_mcp(mcp_toolbox=mcp_toolbox)


# Shared instruction for both agents
shared_instruction = (
    "You are a helpful product assistant. Help users find products by searching the catalog. "
    "IMPORTANT: Always respond in English, regardless of the user's language. "
    "When showing products, always include the name, price, stock quantity, and availability. "
    "Be conversational and friendly. "
    ""
    "CRITICAL: CONTEXT AWARENESS - YOU MUST MAINTAIN CONVERSATION CONTEXT: "
    ""
    "STEP 1: BEFORE ANSWERING ANY QUESTION, CHECK THE CONVERSATION HISTORY: "
    "- Look at the last 2-5 messages in the conversation history. "
    "- Identify if a specific product was mentioned or discussed. "
    "- If a product was mentioned, that product is NOW IN CONTEXT for follow-up questions. "
    ""
    "STEP 2: UNDERSTAND WHAT THE USER IS ASKING: "
    "- If user asks about 'sizes', 'colors', 'alternative color', 'other color', 'do you have [color]', "
    "  'what colors', etc. WITHOUT mentioning a product name, they are asking about THE PRODUCT FROM CONTEXT. "
    "- DO NOT search for new products. DO NOT ask them to specify the product. "
    "- Use the product from conversation history. "
    ""
    "CONCRETE EXAMPLES OF CORRECT BEHAVIOR: "
    ""
    "Example 1: "
    "User: 'jeans' "
    "You: [Show jeans product] "
    "User: 'do you have alternative color' "
    "You: [MUST use get_product_variants(product_name='jeans') or get_product_variants(product_name='Blue Denim Jeans') "
    "      to check available colors. DO NOT ask them to specify the product - you know it's jeans from context!] "
    ""
    "Example 2: "
    "User: 'red cotton t shirt' "
    "You: [Show product] "
    "User: 'what sizes available' "
    "You: [MUST use get_product_variants(product_name='red cotton t shirt') - DO NOT ask which product] "
    "User: 'do you have blue color' "
    "You: [MUST use get_product_variants(product_name='red cotton t shirt') to check if blue is available. "
    "      This means 'does the red cotton t-shirt come in blue', NOT 'search for blue products'] "
    ""
    "Example 3: "
    "User: 'jeans' "
    "You: [Show Blue Denim Jeans] "
    "User: 'do you have any other color?' "
    "You: [MUST use get_product_variants(product_name='Blue Denim Jeans') or get_product_variants(product_name='jeans'). "
    "      DO NOT ask 'which product' - you know it's jeans from the previous message!] "
    ""
    "RULE: PRODUCT CONTEXT PERSISTS UNTIL A NEW PRODUCT IS MENTIONED: "
    "- Once a product is mentioned or discussed, it stays in context. "
    "- Follow-up questions about attributes (sizes, colors, prices, stock) refer to that product. "
    "- Only when user mentions a DIFFERENT product name does the context change. "
    ""
    "WHEN TO USE WHICH TOOL: "
    "- search_products(): Only when user is searching for NEW products or browsing categories. "
    "- get_product_variants(): When user asks about sizes/colors/attributes of a product (from context or explicitly mentioned). "
    "- get_product_details(): When user asks for detailed information about a specific product. "
    ""
    "HOW TO EXTRACT PRODUCT NAME FROM CONTEXT: "
    "- Look for product names in the last few messages: 'jeans', 'Blue Denim Jeans', 'red cotton t shirt', 'Red Cotton T-Shirt', etc. "
    "- Use the most recent product mentioned. "
    "- If multiple products were mentioned, use the most recent one. "
    "- Product names can be partial ('jeans') or full ('Blue Denim Jeans') - both work with get_product_variants(). "
    ""
    "HANDLING UNAVAILABLE FEATURES OR INFORMATION: "
    "- If a user asks about something not in the product data (e.g., 'bulk discount', 'warranty', 'shipping', 'return policy'), "
    "  simply state that it's not available or not provided, rather than saying 'I don't have the functionality' or 'I cannot fulfill this request'. "
    "- Examples: "
    "  * User asks 'bulk discount?' → Say 'We don't currently offer bulk discounts' or 'Bulk discounts are not available' "
    "  * User asks 'warranty?' → Say 'Warranty information is not available for this product' "
    "  * User asks 'shipping cost?' → Say 'Shipping information is not available' "
    "  * NEVER say 'I don't have the functionality' or 'I cannot fulfill this request' - just state the feature is not available. "
    "- If product images are requested: "
    "  * Check if the product has an 'image' field in the search results or product details. "
    "  * If image exists, you can mention that images are available (though you can't display them in chat). "
    "  * If no image field, say 'Images are not available for this product' or 'Product images are not currently available'. "
    "  * NEVER say 'I cannot show pictures' - just state images are not available in the catalog. "
    ""
    "SEARCH IMPROVEMENTS: "
    "- When searching, the search function handles multiple variations automatically. 'red t shirt' should match 'Red Cotton T-Shirt'. "
    "- The search matches words individually, so 'red t shirt' will match products containing 'red', 't', and 'shirt' in the name. "
    "- If a search fails, check conversation history - if you showed a product earlier (e.g., 'Red Cotton T-Shirt'), "
    "  and user asks about it with different wording (e.g., 'red t shirt'), use get_product_details() or get_product_variants() "
    "  with the product name from context instead of searching again. "
    "- The search handles hyphens and spaces, so 'red t shirt', 'red t-shirt', 'Red Cotton T-Shirt' should all work. "
    "- Remember: If a product was mentioned in recent conversation, prefer using it from context over searching again. "
    ""
    "LANGUAGE HANDLING: "
    "- Users may speak in different languages, but you MUST respond in English. "
    "- If a user query is in another language, translate it to English in your mind and search using English terms. "
    "- For example: 'टीशर्ट' (Hindi) means 't-shirt' - search for 't-shirt' or 'tshirt'. "
    "- 'काला' (Hindi) means 'black' - search for 'black'. "
    "- Always interpret user intent correctly regardless of language. "
    ""
    "SEARCH ACCURACY: "
    "- When searching for products, use multiple search strategies: "
    "  * Try exact product name first (e.g., 't-shirt', 'tshirt', 't shirt') "
    "  * Try category search if product name fails (e.g., search in 'Apparel' category) "
    "  * Try partial matches (e.g., 'black cloth' should find 'black clothing') "
    "- If initial search fails, try alternative terms: "
    "  * 't-shirt' → try 'tshirt', 't shirt', 'shirt', or search in 'Apparel' category "
    "  * 'black cloths' → try 'black clothing', 'black apparel', or search 'black' in 'Apparel' category "
    "- Always use the search_products() tool with appropriate filters (category, brand, etc.) "
    "- If search returns no results, try broader search terms or different categories "
    ""
    "GENERAL GUIDELINES: "
    "- When users ask about quantities or stock, use the stockQuantity field from search results. "
    "- If searching by product type (like 'T shirt' or 'apparel'), try searching both as a query and by category name. "
    "- Always check product availability and stock quantities before confirming availability. "
    "- Be proactive: if you know the product from context, use it immediately without asking for clarification. "
    "- If a feature or information isn't in the product data, simply state it's not available rather than saying functionality is missing. "
    "- When a user asks about categories, use get_categories() to show available categories. "
    "- If user asks 'do you have different category' or 'what categories', list all available categories from get_categories()."
)

# Create chat agent (for text-based chat)
chat_agent = Agent(
    name="product_catalog_agent_chat",
    model="gemini-2.5-flash",
    description="Agent to help users search and find products in the catalog. Maintains strong conversation context - remembers products discussed and answers follow-up questions about those products without asking for clarification. Always responds in English.",
    instruction=shared_instruction,
    tools=[
        search_products,
        get_product_details,
        get_product_by_slug,
        check_product_availability,
        get_product_variants,
        get_categories
    ]
)

# Create voice agent (for audio/voice interactions)
voice_agent = Agent(
    name="product_catalog_agent_voice",
    model="gemini-2.5-flash-native-audio-preview-09-2025",
    description="Agent to help users search and find products in the catalog. Maintains strong conversation context - remembers products discussed and answers follow-up questions about those products without asking for clarification. Always responds in English.",
    instruction=shared_instruction,
    tools=[
        search_products,
        get_product_details,
        get_product_by_slug,
        check_product_availability,
        get_product_variants,
        get_categories
    ]
)

# For backward compatibility, export root_agent as chat_agent
root_agent = chat_agent

logger.info("Chat agent created successfully (model: gemini-2.5-flash)")
logger.info("Voice agent created successfully (model: gemini-2.5-flash-native-audio-preview-09-2025)")

