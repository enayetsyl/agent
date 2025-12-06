# ADK Agent with MCP Toolbox (Option B)

This is the ADK agent implementation using **MCP Toolbox for Databases** (Option B - Recommended) for direct database access. This approach provides better performance and direct SQL query capabilities compared to the HTTP API approach.

## Architecture

```
ADK Agent (Python)
    ↓ Direct PostgreSQL Connection
PostgreSQL Database
```

The agent uses the MCP Toolbox to directly query the PostgreSQL database, eliminating the need for HTTP API calls and reducing latency.

## Features

- ✅ **Direct Database Access**: Uses MCP Toolbox for efficient database queries
- ✅ **Comprehensive Logging**: Structured logging with configurable levels
- ✅ **Product Search**: Full-text search with filters (category, price, brand, etc.)
- ✅ **Product Details**: Get complete product information with variants, images, tags
- ✅ **Availability Checking**: Check stock availability for specific sizes/colors
- ✅ **Category Management**: Retrieve product categories with hierarchy
- ✅ **Optional AgentOps**: Production-ready observability (optional)

## Prerequisites

1. **Python 3.9+**
2. **PostgreSQL Database** (already set up in the backend)
3. **Google API Key** for ADK
4. **Google Cloud Credentials** (for MCP Toolbox)

## Setup

### 1. Install Dependencies

```bash
cd db_search_agent/adk-agent
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` and set:

- `DATABASE_URL`: Your PostgreSQL connection string (same as backend)
- `GOOGLE_API_KEY`: Your Google API key for ADK
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_FILE`: Path to log file (default: `logs/agent.log`)

### 3. Google Cloud Credentials

The MCP Toolbox requires Google Cloud credentials for authentication. You have two options:

**Option A: Application Default Credentials (Recommended for Development)**

This is the easiest method for local development:

1. **Install Google Cloud SDK** (if not already installed):

   **Windows Installation Options:**

   **Option 1: Using the Official Installer (Recommended)**

   - Download the installer from: https://cloud.google.com/sdk/docs/install
   - Run the installer and follow the prompts
   - The installer will add `gcloud` to your PATH automatically

   **Option 2: Using Chocolatey** (if you have Chocolatey installed):

   ```bash
   choco install gcloudsdk
   ```

   **Option 3: Using PowerShell** (Windows 10/11):

   ```powershell
   (New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
   & $env:Temp\GoogleCloudSDKInstaller.exe
   ```

   **macOS:**

   ```bash
   brew install --cask google-cloud-sdk
   ```

   **Linux:**

   ```bash
   curl https://sdk.cloud.google.com | bash
   ```

   **Verify Installation:**

   ```bash
   gcloud --version
   ```

   This should display the Google Cloud SDK version, components, and Python version if installed correctly.

2. **Authenticate and set up Application Default Credentials**:

   ```bash
   gcloud auth application-default login
   ```

   This command will:

   - Open your browser for Google account authentication
   - Request necessary permissions
   - Store credentials locally for your application to use

3. **Verify the setup**:
   ```bash
   gcloud auth application-default print-access-token
   ```
   If this returns a token, your credentials are configured correctly.

**Option B: Service Account JSON (Recommended for Production)**

For production environments or when you need more control:

1. **Create a Google Cloud Project** (if you don't have one):

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Create Project" or select an existing project
   - Note your Project ID

2. **Create a Service Account**:

   - Navigate to **IAM & Admin** > **Service Accounts**
   - Click **Create Service Account**
   - Enter a name (e.g., "adk-mcp-toolbox")
   - Add a description (optional)
   - Click **Create and Continue**

3. **Grant Permissions** (if needed):

   - For basic database access, you typically don't need special roles
   - The service account is mainly used for authentication
   - Click **Continue** and then **Done**

4. **Create and Download a Key**:

   - Click on your newly created service account
   - Go to the **Keys** tab
   - Click **Add Key** > **Create New Key**
   - Select **JSON** as the key type
   - Click **Create**
   - A JSON file will be downloaded (e.g., `your-project-xxxxx.json`)

5. **Set the Environment Variable**:
   - Store the JSON file securely (e.g., in your project directory)
   - Add to your `.env` file:
     ```
     GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account-key.json
     ```
   - **Important**: Never commit this JSON file to version control!

**Note**: For local development with a local PostgreSQL database, you may not need extensive Google Cloud permissions. The credentials are primarily used for authentication purposes by the MCP Toolbox library.

### 4. Verify Database Connection

Make sure your `DATABASE_URL` matches the one used in the backend. The format should be:

```
postgresql://user:password@host:port/database
```

## Pricing & Costs

### MCP Toolbox Costs

**Good News**: The MCP Toolbox itself is **free** - it's a library/tool provided by Google ADK that facilitates database connections. There are no charges for using the MCP Toolbox library.

### What You May Be Charged For

However, you may incur costs from the underlying services:

1. **Google API Key (Gemini API)**:

   - Used by the ADK agent for LLM interactions
   - Check [Google AI Studio Pricing](https://aistudio.google.com/pricing) for current rates
   - Gemini models typically have free tiers with usage limits

2. **PostgreSQL Database**:

   - If using **Cloud SQL** (Google Cloud's managed PostgreSQL), you'll be charged for the database instance
   - If using a **local PostgreSQL** database, there are no cloud charges
   - If using **other cloud providers** (AWS RDS, Azure Database, etc.), check their pricing

3. **Google Cloud Project**:
   - Creating a Google Cloud project is **free**
   - You only pay for services you use
   - For MCP Toolbox authentication, you typically don't need any paid services

### Cost Optimization Tips

- Use **local PostgreSQL** for development (free)
- Use **Application Default Credentials** for local development (no service account needed)
- Monitor your **Gemini API usage** to stay within free tier limits
- Only use **Cloud SQL** if you need managed database services

### Free Tier Eligibility

- Google Cloud projects include a **$300 free credit** for new users
- Gemini API has **free tier limits** (check current limits on Google AI Studio)
- Local development with local databases is **completely free**

## Usage

### Basic Usage

```python
from agent_mcp import root_agent
from google.adk.runners import Runner

# Create a runner with the agent
runner = Runner(agent=root_agent)

# Query the agent
response = runner.run("Find me red t-shirts under $50")
print(response)
```

### Using with Express Backend

The agent can be integrated with your Express backend through the agent service. See `backend/src/services/agent.service.ts` for integration examples.

### Available Tools

The agent provides the following tools:

1. **search_products**: Search products with filters
   - Parameters: query, category, max_price, min_price, brand, in_stock, featured, limit
2. **get_product_details**: Get detailed product information
   - Parameters: product_id
3. **get_product_by_slug**: Get product by slug
   - Parameters: slug
4. **check_product_availability**: Check stock availability
   - Parameters: product_id, size (optional), color (optional)
5. **get_categories**: Get all product categories

   - No parameters

6. **MCP Toolbox**: Direct SQL execution (for advanced queries)
   - The agent also has access to the MCP Toolbox for custom SQL queries

## Logging

Logs are written to both console and file (if `LOG_FILE` is set). Log levels:

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages

Log files are stored in the `logs/` directory.

## Optional: AgentOps Integration

To enable AgentOps observability:

1. Sign up at [AgentOps](https://agentops.ai)
2. Get your API key
3. Add to `.env`:
   ```
   AGENTOPS_API_KEY=your-agentops-api-key
   ```
4. Uncomment `agentops` in `requirements.txt` and install:
   ```bash
   pip install agentops
   ```

AgentOps will automatically track:

- Tool calls and responses
- Agent responses
- Errors and exceptions
- Latency metrics

## Testing

### Test Database Connection

```python
from agent_mcp import mcp_toolbox

# Test connection
result = mcp_toolbox.execute_sql(
    query="SELECT COUNT(*) FROM products",
    parameters={}
)
print(f"Total products: {result.rows[0][0]}")
```

### Test Agent Tools

```python
from agent_mcp import root_agent, search_products

# Test search
result = search_products(query="t-shirt", limit=5)
print(result)
```

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is correct
- Check PostgreSQL is running and accessible
- Ensure database user has proper permissions

### Google Cloud Credentials Issues

- Run `gcloud auth application-default login`
- Or set `GOOGLE_APPLICATION_CREDENTIALS` to a valid service account JSON path
- Verify the service account has necessary permissions

### MCP Toolbox Initialization Errors

- Check Google Cloud credentials are properly configured
- Verify `DATABASE_URL` format is correct
- Check logs for detailed error messages

## File Structure

```
adk-agent/
├── agent_mcp.py           # Main agent with MCP Toolbox integration
├── logging_config.py      # Logging configuration
├── tools/
│   ├── __init__.py
│   └── product_tools.py  # Product query tools using MCP
├── logs/                  # Log files directory
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Next Steps

1. Test the agent with sample queries
2. Integrate with Express backend (if needed)
3. Set up AgentOps for production monitoring
4. Move to Agent 2: Cart Management

## References

- [ADK Documentation](https://google.github.io/adk-docs/)
- [MCP Toolbox for Databases](https://google.github.io/adk-docs/tools/google-cloud/mcp-toolbox-for-databases/)
- [ADK Logging](https://google.github.io/adk-docs/observability/logging/)
- [AgentOps Integration](https://google.github.io/adk-docs/observability/agentops/)
