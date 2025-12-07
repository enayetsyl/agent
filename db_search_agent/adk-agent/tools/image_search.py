"""
Image search tool - prioritizes database images, falls back to Unsplash API.
"""
import os
import sys
import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Unsplash API endpoint (public access, no auth required for basic searches)
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

# MCP toolbox will be passed as parameter to avoid circular imports
# Type hint for Optional MCPToolboxForDatabases
try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from db_wrapper import MCPToolboxForDatabases
except ImportError:
    pass


def _normalize_query(query: str) -> str:
    """
    Normalize product query to better match Unsplash search terms.
    """
    query_lower = query.lower().strip()
    
    # Map product-specific terms to better search queries
    query_mappings = {
        "t-shirt": "t-shirt clothing",
        "tshirt": "t-shirt clothing",
        "t shirt": "t-shirt clothing",
        "red cotton t-shirt": "red t-shirt clothing",
        "red cotton t shirt": "red t-shirt clothing",
        "blue denim jeans": "blue jeans",
        "jeans": "jeans clothing",
        "pants": "pants clothing",
        "yoga mat": "yoga mat",
    }
    
    # Check for exact matches first
    for key, mapped_query in query_mappings.items():
        if key in query_lower:
            return mapped_query
    
    # If no mapping found, clean up the query
    # Remove brand names and extra descriptive words that might confuse search
    words_to_remove = ["cotton", "denim", "leather", "basicwear", "sportswear"]
    query_words = query_lower.split()
    cleaned_words = [w for w in query_words if w not in words_to_remove]
    
    # Add "clothing" if it's a clothing item
    clothing_keywords = ["shirt", "pants", "jeans", "jacket", "dress", "shoes", "boots"]
    if any(keyword in query_lower for keyword in clothing_keywords):
        if "clothing" not in cleaned_words:
            cleaned_words.append("clothing")
    
    return " ".join(cleaned_words) if cleaned_words else query_lower


def get_product_images_from_db(
    mcp_toolbox,
    product_query: str,
    count: int = 3
) -> Dict:
    """
    Get product images from the database first.
    
    Args:
        mcp_toolbox: MCP Toolbox instance for database access
        product_query: Product name or query to search for
        count: Maximum number of images to return
    
    Returns:
        Dict with 'images' list if found, empty dict if not found
    """
    if not mcp_toolbox:
        return {}
    
    try:
        logger.info(f"Searching database for product images: '{product_query}'")
        
        # Import here to avoid circular imports
        from tools.product_tools import search_products_mcp, get_product_details_mcp
        
        # Search for products matching the query
        search_result = search_products_mcp(
            mcp_toolbox=mcp_toolbox,
            query=product_query,
            limit=1  # Get the first matching product
        )
        
        logger.info(f"Database search result status: {search_result.get('status')}, products found: {len(search_result.get('products', []))}")
        
        if search_result.get("status") != "success" or not search_result.get("products"):
            logger.info(f"No products found in database for query: '{product_query}'")
            return {}
        
        product = search_result["products"][0]
        product_id = product.get("id")
        product_name = product.get("name", product_query)
        
        logger.info(f"Found product in database: ID={product_id}, Name='{product_name}'")
        
        if not product_id:
            logger.warning(f"Product found but no ID: {product}")
            return {}
        
        # Get product details which includes images
        product_details = get_product_details_mcp(mcp_toolbox, product_id)
        
        if product_details.get("status") != "success":
            logger.warning(f"Failed to get product details for ID {product_id}: {product_details.get('error_message')}")
            return {}
        
        product_data = product_details.get("product", {})
        images = product_data.get("images", [])
        
        logger.info(f"Product '{product_name}' has {len(images)} images in database")
        
        if not images:
            logger.info(f"No images found in database for product ID: {product_id} (Product: {product_name})")
            return {}
        
        # Format images for response
        image_list = []
        for img in images[:count]:
            if img.get("url"):
                image_list.append({
                    "url": img["url"],
                    "description": img.get("altText") or product_data.get("name") or product_query,
                    "author": "Product Catalog",
                    "unsplash_url": "",
                    "from_database": True
                })
        
        if image_list:
            logger.info(f"Found {len(image_list)} images from database for product: '{product_data.get('name', product_query)}'")
            return {
                "success": True,
                "query": product_query,
                "images": image_list,
                "count": len(image_list),
                "from_database": True
            }
        
        return {}
        
    except Exception as e:
        logger.error(f"Error getting images from database: {str(e)}")
        return {}


def search_images(query: str, count: int = 3, mcp_toolbox = None) -> Dict:
    """
    Search for product images - FIRST checks database, then falls back to Unsplash API.
    
    Args:
        query: Product name or query (e.g., "t-shirt", "Red Cotton T-Shirt", "jeans")
        count: Number of images to return (default: 3, max: 10)
        mcp_toolbox: Optional MCP Toolbox for database access
    
    Returns:
        Dict with 'images' list containing image URLs and metadata
    """
    try:
        # FIRST: Try to get images from database
        if mcp_toolbox:
            logger.info(f"Attempting database search for images with query: '{query}'")
            db_result = get_product_images_from_db(mcp_toolbox, query, count)
            if db_result.get("images"):
                logger.info(f"✓ Found {len(db_result['images'])} images from database for query: '{query}'")
                return db_result
            else:
                logger.info(f"✗ No database images found for query: '{query}', will try Unsplash")
        else:
            logger.warning("No mcp_toolbox provided, skipping database search")
        
        # If no database images found, fall back to Unsplash
        logger.info(f"Falling back to Unsplash search for: '{query}'")
        
        # Normalize the query for better search results
        normalized_query = _normalize_query(query)
        logger.info(f"Image search: original='{query}', normalized='{normalized_query}'")
        
        # Limit count to reasonable range
        count = min(max(1, count), 10)
        
        # Prepare headers
        headers = {}
        if UNSPLASH_ACCESS_KEY:
            headers["Authorization"] = f"Client-ID {UNSPLASH_ACCESS_KEY}"
        else:
            # Without API key, Unsplash API has limited access
            # We'll use fallback for better results
            logger.warning("No UNSPLASH_ACCESS_KEY found, using fallback images")
            return _get_fallback_images(query, count)
        
        # Make request to Unsplash API
        params = {
            "query": normalized_query,
            "per_page": count,
        }
        
        response = requests.get(UNSPLASH_API_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            images = []
            for result in results[:count]:
                # Extract image URL - prefer regular, then small, then raw
                image_url = (
                    result.get("urls", {}).get("regular") or 
                    result.get("urls", {}).get("small") or 
                    result.get("urls", {}).get("raw")
                )
                
                # Build optimized URL similar to the examples provided
                # Format: https://images.unsplash.com/photo-{id}?w=600&auto=format&fit=crop&q=60
                if image_url:
                    # Use regular URL with optimization parameters
                    # Unsplash URLs already include the photo ID
                    if "unsplash.com" in image_url:
                        # Add optimization parameters if not already present
                        if "?" not in image_url:
                            optimized_url = f"{image_url}?w=600&auto=format&fit=crop&q=60"
                        elif "w=" not in image_url:
                            optimized_url = f"{image_url}&w=600&auto=format&fit=crop&q=60"
                        else:
                            optimized_url = image_url
                    else:
                        optimized_url = image_url
                    
                    images.append({
                        "url": optimized_url,
                        "description": result.get("description") or result.get("alt_description") or query,
                        "author": result.get("user", {}).get("name", "Unknown"),
                        "unsplash_url": result.get("links", {}).get("html", "")
                    })
            
            return {
                "success": True,
                "query": query,
                "images": images,
                "count": len(images)
            }
        else:
            # If API fails, return example URLs based on query
            logger.warning(f"Unsplash API returned status {response.status_code}, using fallback")
            return _get_fallback_images(query, count)
            
    except Exception as e:
        logger.error(f"Error searching images: {str(e)}")
        return _get_fallback_images(query, count)


def _get_fallback_images(query: str, count: int) -> Dict:
    """
    Fallback function that returns example Unsplash image URLs.
    This is used when the API is unavailable or rate-limited.
    """
    logger.info(f"Using fallback images for query: '{query}', count: {count}")
    
    # Map common queries to example image URLs
    # These are actual Unsplash t-shirt image URLs
    fallback_urls = {
        "pants": [
            "https://images.unsplash.com/photo-1605518216938-7c31b7b14ad0?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8cGFudHxlbnwwfHwwfHx8MA%3D%3D",
            "https://plus.unsplash.com/premium_photo-1674828600712-7d0caab39109?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8cGFudHxlbnwwfHwwfHx8MA%3D%3D"
        ],
        "jeans": [
            "https://images.unsplash.com/photo-1605518216938-7c31b7b14ad0?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8cGFudHxlbnwwfHwwfHx8MA%3D%3D"
        ],
        # T-shirt specific images - using actual t-shirt images from Unsplash
        "t-shirt": [
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
            "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
            "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0"
        ],
        "tshirt": [
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
            "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
            "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0"
        ],
        "shirt": [
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
            "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0"
        ],
        "t shirt": [
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
            "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
            "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0"
        ],
        "red": [
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0"
        ]
    }
    
    # Find matching fallback URLs - check for most specific matches first
    query_lower = query.lower().strip()
    urls = []
    matched_key = None
    
    # Check for exact matches first (more specific)
    # Check in order of specificity
    for key in ["t-shirt", "tshirt", "t shirt", "shirt", "red", "jeans", "pants"]:
        if key in query_lower:
            matched_key = key
            urls.extend(fallback_urls[key])
            logger.info(f"Matched fallback key: '{key}' for query: '{query}'")
            break
    
    # If no match, use default t-shirt images (most common request)
    if not urls:
        matched_key = "t-shirt"
        urls = fallback_urls["t-shirt"]
        logger.info(f"No specific match found, using default t-shirt images for query: '{query}'")
    
    # Limit to requested count
    urls = urls[:count]
    
    images = [{
        "url": url,
        "description": f"{query} image",
        "author": "Unsplash",
        "unsplash_url": ""
    } for url in urls]
    
    logger.info(f"Returning {len(images)} fallback images for query: '{query}'")
    
    return {
        "success": True,
        "query": query,
        "images": images,
        "count": len(images),
        "fallback": True
    }

