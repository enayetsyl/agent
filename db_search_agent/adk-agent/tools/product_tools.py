"""
Product query tools using MCP Toolbox for direct database access.
"""
import logging
import sys
import os
from typing import Optional, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_wrapper import MCPToolboxForDatabases

logger = logging.getLogger(__name__)


def search_products_mcp(
    mcp_toolbox: MCPToolboxForDatabases,
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
    Search for products using MCP database tools.

    Args:
        mcp_toolbox: MCP Toolbox instance for database access
        query: Search query string (searches in name, description, brand)
        category: Category slug or name to filter by
        max_price: Maximum price filter
        min_price: Minimum price filter
        brand: Brand name to filter by
        in_stock: Only show products in stock (default: True)
        featured: Filter by featured status
        limit: Maximum number of results (default: 10)

    Returns:
        dict: Dictionary with status and list of matching products
    """
    try:
        logger.info(f"Searching products with query: {query}, category: {category}, max_price: {max_price}")

        # Build SQL query dynamically
        sql_query = """
        SELECT
            p.id, p.name, p.slug, p.description, p.short_description,
            p.price, p.compare_at_price, p.brand, p.featured,
            c.id as category_id, c.name as category_name, c.slug as category_slug,
            COUNT(DISTINCT v.id) FILTER (WHERE v.stock_quantity > 0) as in_stock_variants,
            COALESCE(SUM(v.stock_quantity), 0) as total_stock_quantity,
            COUNT(DISTINCT v.id) as total_variants,
            (
                SELECT url FROM product_images pi
                WHERE pi.product_id = p.id AND pi.is_primary = true
                LIMIT 1
            ) as primary_image_url
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN product_variants v ON p.id = v.product_id
        WHERE p.status = 'active'
        """

        conditions = []
        params = {}

        if query:
            # Improved search: handle hyphens/spaces, partial matches, and category names
            # This helps match "T shirt" with "T-Shirt", "red t shirt" with "Red Cotton T-Shirt", etc.
            # Normalize query: remove hyphens and normalize spaces for better matching
            query_normalized = query.lower().replace('-', ' ').strip()
            query_words = [w for w in query_normalized.split() if len(w) > 1]  # Filter out single characters
            
            # Build search conditions - try multiple matching strategies
            search_conditions = [
                "p.name ILIKE :query",
                "p.description ILIKE :query",
                "p.short_description ILIKE :query",
                "p.brand ILIKE :query",
                "REPLACE(LOWER(p.name), '-', ' ') LIKE :query_normalized",
                "REPLACE(LOWER(p.name), ' ', '-') LIKE REPLACE(:query_normalized, ' ', '-')",
                "REPLACE(LOWER(p.description), '-', ' ') LIKE :query_normalized",
                "REPLACE(LOWER(p.short_description), '-', ' ') LIKE :query_normalized",
                "c.name ILIKE :query",
                "c.slug ILIKE :query"
            ]
            
            # Add word-by-word matching: if all important words appear in product name
            # This helps "red t shirt" match "Red Cotton T-Shirt"
            if len(query_words) > 1:
                word_like_conditions = []
                for i, word in enumerate(query_words):
                    param_name = f'word_{i}'
                    word_like_conditions.append(f"LOWER(p.name) LIKE :{param_name}")
                    params[param_name] = f'%{word}%'
                
                if word_like_conditions:
                    # Match if all words appear in the name
                    search_conditions.append(f"({' AND '.join(word_like_conditions)})")
            
            conditions.append(f"({' OR '.join(search_conditions)})")
            params['query'] = f'%{query}%'
            params['query_normalized'] = f'%{query_normalized}%'

        if category:
            conditions.append("(c.slug = :category OR c.name ILIKE :category)")
            params['category'] = category

        if max_price:
            conditions.append("p.price <= :max_price")
            params['max_price'] = float(max_price)

        if min_price:
            conditions.append("p.price >= :min_price")
            params['min_price'] = float(min_price)

        if brand:
            conditions.append("p.brand ILIKE :brand")
            params['brand'] = f'%{brand}%'

        if featured is not None:
            conditions.append("p.featured = :featured")
            params['featured'] = featured

        if conditions:
            sql_query += " AND " + " AND ".join(conditions)

        sql_query += """
        GROUP BY p.id, p.name, p.slug, p.description, p.short_description,
                 p.price, p.compare_at_price, p.brand, p.featured,
                 c.id, c.name, c.slug
        """
        

        # Filter by stock availability
        if in_stock:
            sql_query += " HAVING COUNT(DISTINCT v.id) FILTER (WHERE v.stock_quantity > 0) > 0"

        sql_query += """
        ORDER BY p.featured DESC, p.created_at DESC
        LIMIT :limit
        """
        params['limit'] = limit

        # Execute query using MCP toolbox
        result = mcp_toolbox.execute_sql(
            query=sql_query,
            parameters=params
        )

        logger.info(f"Found {len(result.rows)} products")

        products = []
        for row in result.rows:
            # Column order: id, name, slug, desc, short_desc, price, compare_price, brand, featured,
            #               cat_id, cat_name, cat_slug, in_stock_variants, total_stock_quantity, total_variants, image
            products.append({
                "id": row[0],
                "name": row[1],
                "slug": row[2],
                "description": row[3],
                "shortDescription": row[4],
                "price": float(row[5]) if row[5] else None,
                "compareAtPrice": float(row[6]) if row[6] else None,
                "brand": row[7],
                "featured": row[8],
                "category": {
                    "id": row[9],
                    "name": row[10],
                    "slug": row[11]
                } if row[9] else None,
                "inStock": row[12] > 0 if row[12] is not None else False,
                "stockQuantity": int(row[13]) if len(row) > 13 and row[13] is not None else 0,
                "totalVariants": row[14] if len(row) > 14 and row[14] is not None else 0,
                "image": row[15] if len(row) > 15 and row[15] else None
            })

        return {
            "status": "success",
            "count": len(products),
            "products": products
        }
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to search products: {str(e)}"
        }


def get_product_details_mcp(
    mcp_toolbox: MCPToolboxForDatabases,
    product_id: int
) -> Dict:
    """
    Get detailed information about a specific product using MCP database tools.

    Args:
        mcp_toolbox: MCP Toolbox instance for database access
        product_id: The ID of the product

    Returns:
        dict: Product details or error message
    """
    try:
        logger.info(f"Fetching product details for ID: {product_id}")

        # Get product with variants and images
        sql_query = """
        SELECT
            p.id, p.name, p.slug, p.description, p.short_description,
            p.sku, p.price, p.compare_at_price, p.cost_price,
            p.brand, p.status, p.featured,
            c.id as category_id, c.name as category_name, c.slug as category_slug,
            json_agg(
                DISTINCT jsonb_build_object(
                    'id', v.id,
                    'name', v.name,
                    'sku', v.sku,
                    'price', v.price,
                    'compareAtPrice', v.compare_at_price,
                    'stockQuantity', v.stock_quantity,
                    'trackInventory', v.track_inventory,
                    'weight', v.weight,
                    'dimensions', v.dimensions
                )
            ) FILTER (WHERE v.id IS NOT NULL) as variants
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN product_variants v ON p.id = v.product_id
        WHERE p.id = :product_id AND p.status = 'active'
        GROUP BY p.id, p.name, p.slug, p.description, p.short_description,
                 p.sku, p.price, p.compare_at_price, p.cost_price,
                 p.brand, p.status, p.featured,
                 c.id, c.name, c.slug
        """

        result = mcp_toolbox.execute_sql(
            query=sql_query,
            parameters={'product_id': product_id}
        )

        if not result.rows:
            return {
                "status": "error",
                "error_message": f"Product with ID {product_id} not found."
            }

        row = result.rows[0]

        # Get variant attributes
        variant_ids = []
        if row[15]:  # variants JSON
            import json
            variants_data = json.loads(row[15]) if isinstance(row[15], str) else row[15]
            variant_ids = [v.get('id') for v in variants_data if v.get('id')]

        attributes_query = """
        SELECT va.variant_id, va.attribute_name, va.attribute_value
        FROM variant_attributes va
        WHERE va.variant_id = ANY(:variant_ids)
        ORDER BY va.variant_id, va.attribute_name
        """
        attributes_result = mcp_toolbox.execute_sql(
            query=attributes_query,
            parameters={'variant_ids': variant_ids}
        ) if variant_ids else None

        # Get product images
        images_query = """
        SELECT id, url, alt_text, sort_order, is_primary
        FROM product_images
        WHERE product_id = :product_id
        ORDER BY is_primary DESC, sort_order ASC
        """
        images_result = mcp_toolbox.execute_sql(
            query=images_query,
            parameters={'product_id': product_id}
        )

        # Get product tags
        tags_query = """
        SELECT t.id, t.name, t.slug
        FROM product_tags t
        JOIN product_tag_relations ptr ON t.id = ptr.tag_id
        WHERE ptr.product_id = :product_id
        """
        tags_result = mcp_toolbox.execute_sql(
            query=tags_query,
            parameters={'product_id': product_id}
        )

        # Get reviews summary
        reviews_query = """
        SELECT 
            COUNT(*) as review_count,
            AVG(rating) as average_rating
        FROM product_reviews
        WHERE product_id = :product_id
        """
        reviews_result = mcp_toolbox.execute_sql(
            query=reviews_query,
            parameters={'product_id': product_id}
        )

        # Process variants with attributes
        variants = []
        if row[15]:
            import json
            variants_data = json.loads(row[15]) if isinstance(row[15], str) else row[15]
            variant_attrs = {}
            if attributes_result:
                for attr_row in attributes_result.rows:
                    vid = attr_row[0]
                    if vid not in variant_attrs:
                        variant_attrs[vid] = {}
                    variant_attrs[vid][attr_row[1]] = attr_row[2]

            for variant in variants_data:
                variant['attributes'] = variant_attrs.get(variant.get('id'), {})
                variants.append(variant)

        # Process images
        images = []
        if images_result:
            for img_row in images_result.rows:
                images.append({
                    "id": img_row[0],
                    "url": img_row[1],
                    "altText": img_row[2],
                    "sortOrder": img_row[3],
                    "isPrimary": img_row[4]
                })

        # Process tags
        tags = []
        if tags_result:
            for tag_row in tags_result.rows:
                tags.append({
                    "id": tag_row[0],
                    "name": tag_row[1],
                    "slug": tag_row[2]
                })

        # Process reviews summary
        review_count = 0
        average_rating = None
        if reviews_result and reviews_result.rows:
            review_row = reviews_result.rows[0]
            review_count = review_row[0] or 0
            average_rating = float(review_row[1]) if review_row[1] else None

        product = {
            "id": row[0],
            "name": row[1],
            "slug": row[2],
            "description": row[3],
            "shortDescription": row[4],
            "sku": row[5],
            "price": float(row[6]) if row[6] else None,
            "compareAtPrice": float(row[7]) if row[7] else None,
            "costPrice": float(row[8]) if row[8] else None,
            "brand": row[7],
            "status": row[10],
            "featured": row[11],
            "category": {
                "id": row[12],
                "name": row[13],
                "slug": row[14]
            } if row[12] else None,
            "variants": variants,
            "images": images,
            "tags": tags,
            "reviewCount": review_count,
            "averageRating": average_rating,
            "inStock": any(v.get('stockQuantity', 0) > 0 for v in variants) if variants else False
        }

        return {
            "status": "success",
            "product": product
        }
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to get product: {str(e)}"
        }


def get_product_by_slug_mcp(
    mcp_toolbox: MCPToolboxForDatabases,
    slug: str
) -> Dict:
    """
    Get product details by slug using MCP database tools.

    Args:
        mcp_toolbox: MCP Toolbox instance for database access
        slug: Product slug (URL-friendly identifier)

    Returns:
        dict: Product details or error message
    """
    try:
        logger.info(f"Fetching product by slug: {slug}")

        # First get product ID by slug
        id_query = "SELECT id FROM products WHERE slug = :slug AND status = 'active'"
        id_result = mcp_toolbox.execute_sql(
            query=id_query,
            parameters={'slug': slug}
        )

        if not id_result.rows:
            return {
                "status": "error",
                "error_message": f"Product with slug '{slug}' not found."
            }

        product_id = id_result.rows[0][0]

        # Use the get_product_details_mcp function
        return get_product_details_mcp(mcp_toolbox, product_id)
    except Exception as e:
        logger.error(f"Error fetching product by slug: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to get product: {str(e)}"
        }


def check_product_availability_mcp(
    mcp_toolbox: MCPToolboxForDatabases,
    product_id: int,
    size: Optional[str] = None,
    color: Optional[str] = None
) -> Dict:
    """
    Check if a product is available in specific size and/or color using MCP database tools.

    Args:
        mcp_toolbox: MCP Toolbox instance for database access
        product_id: The ID of the product
        size: Optional size to check (e.g., "M", "10")
        color: Optional color to check (e.g., "red", "black")

    Returns:
        dict: Availability information
    """
    try:
        logger.info(f"Checking availability for product {product_id}, size: {size}, color: {color}")

        sql_query = """
        SELECT
            v.id, v.name, v.sku, v.price, v.compare_at_price,
            v.stock_quantity, v.track_inventory,
            json_object_agg(va.attribute_name, va.attribute_value) as attributes
        FROM product_variants v
        JOIN variant_attributes va ON v.id = va.variant_id
        WHERE v.product_id = :product_id
        """

        params = {'product_id': product_id}

        if size:
            sql_query += """
            AND EXISTS (
                SELECT 1 FROM variant_attributes va2
                WHERE va2.variant_id = v.id
                AND va2.attribute_name = 'size'
                AND LOWER(va2.attribute_value) = LOWER(:size)
            )
            """
            params['size'] = size

        if color:
            sql_query += """
            AND EXISTS (
                SELECT 1 FROM variant_attributes va3
                WHERE va3.variant_id = v.id
                AND va3.attribute_name = 'color'
                AND LOWER(va3.attribute_value) = LOWER(:color)
            )
            """
            params['color'] = color

        sql_query += """
        GROUP BY v.id, v.name, v.sku, v.price, v.compare_at_price,
                 v.stock_quantity, v.track_inventory
        HAVING v.stock_quantity > 0 OR v.track_inventory = false
        ORDER BY v.stock_quantity DESC
        """

        result = mcp_toolbox.execute_sql(query=sql_query, parameters=params)

        variants = []
        total_stock = 0
        for row in result.rows:
            import json
            attributes = json.loads(row[7]) if isinstance(row[7], str) else row[7] if row[7] else {}
            
            variant = {
                "id": row[0],
                "name": row[1],
                "sku": row[2],
                "price": float(row[3]) if row[3] else None,
                "compareAtPrice": float(row[4]) if row[4] else None,
                "stockQuantity": row[5],
                "trackInventory": row[6],
                "attributes": attributes
            }
            variants.append(variant)
            total_stock += row[5] if row[5] else 0

        return {
            "status": "success",
            "available": len(variants) > 0,
            "variants": variants,
            "totalStock": total_stock
        }
    except Exception as e:
        logger.error(f"Error checking availability: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to check availability: {str(e)}"
        }


def get_product_variants_mcp(
    mcp_toolbox: MCPToolboxForDatabases,
    product_id: Optional[int] = None,
    product_name: Optional[str] = None
) -> Dict:
    """
    Get all variants (sizes, colors, etc.) for a product using MCP database tools.
    This is useful when users ask about available sizes or colors.

    Args:
        mcp_toolbox: MCP Toolbox instance for database access
        product_id: The ID of the product (preferred)
        product_name: Product name to search for if ID not provided

    Returns:
        dict: Product variants with attributes (sizes, colors, etc.)
    """
    try:
        # If product_name provided but not product_id, find the product first
        if product_name and not product_id:
            logger.info(f"Searching for product by name: {product_name}")
            search_result = search_products_mcp(
                mcp_toolbox=mcp_toolbox,
                query=product_name,
                limit=1
            )
            if search_result.get("status") == "success" and search_result.get("products"):
                product_id = search_result["products"][0]["id"]
            else:
                return {
                    "status": "error",
                    "error_message": f"Product '{product_name}' not found"
                }

        if not product_id:
            return {
                "status": "error",
                "error_message": "Product ID or name is required"
            }

        logger.info(f"Fetching variants for product ID: {product_id}")

        # Get all variants with their attributes
        sql_query = """
        SELECT
            v.id, v.name, v.sku, v.price, v.compare_at_price,
            v.stock_quantity, v.track_inventory,
            json_object_agg(va.attribute_name, va.attribute_value) as attributes
        FROM product_variants v
        LEFT JOIN variant_attributes va ON v.id = va.variant_id
        WHERE v.product_id = :product_id
        GROUP BY v.id, v.name, v.sku, v.price, v.compare_at_price,
                 v.stock_quantity, v.track_inventory
        ORDER BY v.stock_quantity DESC
        """

        result = mcp_toolbox.execute_sql(
            query=sql_query,
            parameters={'product_id': product_id}
        )

        variants = []
        sizes = set()
        colors = set()
        
        for row in result.rows:
            import json
            attributes = json.loads(row[7]) if isinstance(row[7], str) else row[7] if row[7] else {}
            
            variant = {
                "id": row[0],
                "name": row[1],
                "sku": row[2],
                "price": float(row[3]) if row[3] else None,
                "compareAtPrice": float(row[4]) if row[4] else None,
                "stockQuantity": row[5],
                "trackInventory": row[6],
                "attributes": attributes
            }
            variants.append(variant)
            
            # Extract sizes and colors
            if 'size' in attributes:
                sizes.add(attributes['size'])
            if 'color' in attributes:
                colors.add(attributes['color'])

        return {
            "status": "success",
            "productId": product_id,
            "variants": variants,
            "availableSizes": sorted(list(sizes)) if sizes else [],
            "availableColors": sorted(list(colors)) if colors else [],
            "totalVariants": len(variants)
        }
    except Exception as e:
        logger.error(f"Error fetching product variants: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to get product variants: {str(e)}"
        }


def get_categories_mcp(
    mcp_toolbox: MCPToolboxForDatabases
) -> Dict:
    """
    Get all available product categories using MCP database tools.

    Args:
        mcp_toolbox: MCP Toolbox instance for database access

    Returns:
        dict: List of categories
    """
    try:
        logger.info("Fetching all categories")

        sql_query = """
        SELECT
            c.id, c.name, c.slug, c.description, c.parent_id,
            (
                SELECT json_agg(json_build_object('id', child.id, 'name', child.name, 'slug', child.slug))
                FROM categories child
                WHERE child.parent_id = c.id
            ) as children
        FROM categories c
        WHERE c.parent_id IS NULL
        ORDER BY c.name ASC
        """

        result = mcp_toolbox.execute_sql(query=sql_query)

        categories = []
        for row in result.rows:
            import json
            children = json.loads(row[5]) if isinstance(row[5], str) else row[5] if row[5] else []
            
            category = {
                "id": row[0],
                "name": row[1],
                "slug": row[2],
                "description": row[3],
                "parentId": row[4],
                "children": children
            }
            categories.append(category)

        return {
            "status": "success",
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to get categories: {str(e)}"
        }

