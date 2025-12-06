"""
Test script for the ADK agent with MCP Toolbox.
Run this to verify the setup is working correctly.
"""
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding for emoji characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

# Verify required environment variables
required_vars = ["DATABASE_URL", "GOOGLE_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set them in your .env file or environment.")
    sys.exit(1)

print("✅ Environment variables loaded")

# Test imports
try:
    from agent_mcp import root_agent, mcp_toolbox, search_products, get_categories
    print("✅ Agent imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you've installed all dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Test database connection
print("\n🔍 Testing database connection...")
try:
    result = mcp_toolbox.execute_sql(
        query="SELECT COUNT(*) FROM products",
        parameters={}
    )
    product_count = result.rows[0][0] if result.rows else 0
    print(f"✅ Database connection successful")
    print(f"   Found {product_count} products in database")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("   Check your DATABASE_URL and ensure PostgreSQL is running")
    sys.exit(1)

# Test search function
print("\n🔍 Testing product search...")
try:
    result = search_products(limit=3)
    if result.get("status") == "success":
        print(f"✅ Product search successful")
        print(f"   Found {result.get('count', 0)} products")
        if result.get("products"):
            print(f"   First product: {result['products'][0].get('name', 'N/A')}")
    else:
        print(f"⚠️  Search returned error: {result.get('error_message', 'Unknown error')}")
except Exception as e:
    print(f"❌ Product search failed: {e}")
    import traceback
    traceback.print_exc()

# Test categories
print("\n🔍 Testing category retrieval...")
try:
    result = get_categories()
    if result.get("status") == "success":
        print(f"✅ Category retrieval successful")
        print(f"   Found {len(result.get('categories', []))} categories")
    else:
        print(f"⚠️  Categories returned error: {result.get('error_message', 'Unknown error')}")
except Exception as e:
    print(f"❌ Category retrieval failed: {e}")

# Test agent
print("\n🔍 Testing agent initialization...")
try:
    if root_agent:
        print(f"✅ Agent initialized successfully")
        print(f"   Agent name: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        print(f"   Tools available: {len(root_agent.tools)}")
    else:
        print("❌ Agent is None")
except Exception as e:
    print(f"❌ Agent initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("✅ All tests completed!")
print("="*50)
print("\nNext steps:")
print("1. Test the agent with a query:")
print("   from agent_mcp import root_agent")
print("   from google.adk.runners import Runner")
print("   runner = Runner(agent=root_agent)")
print("   response = runner.run('Find me red t-shirts')")
print("2. Integrate with your Express backend")
print("3. Set up AgentOps for production monitoring (optional)")

