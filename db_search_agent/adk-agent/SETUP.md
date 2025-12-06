# Quick Setup Guide

## Step 1: Install Dependencies

```bash
cd db_search_agent/adk-agent
pip install -r requirements.txt
```

## Step 2: Configure Environment

Create a `.env` file (copy from `.env.example` if it exists, or create manually):

```bash
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
GOOGLE_API_KEY=your-google-api-key-here

# Optional
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log
```

**Important**: Use the same `DATABASE_URL` as your backend!

## Step 3: Set Up Google Cloud Credentials

Choose one option:

### Option A: Application Default Credentials (Easiest)

```bash
gcloud auth application-default login
```

### Option B: Service Account JSON

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Add to `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   ```

## Step 4: Test the Setup

Run the test script:

```bash
python test_agent.py
```

You should see:

- ✅ Environment variables loaded
- ✅ Agent imports successful
- ✅ Database connection successful
- ✅ Product search successful
- ✅ Category retrieval successful
- ✅ Agent initialized successfully

## Step 5: Try It Out

Run the example usage:

```bash
python example_usage.py
```

Or use in your code:

```python
from agent_mcp import root_agent
from google.adk.runners import Runner

runner = Runner(agent=root_agent)
response = runner.run("Find me red t-shirts")
print(response)
```

## Troubleshooting

### "DATABASE_URL is required"

- Make sure `.env` file exists and contains `DATABASE_URL`
- Check the connection string format: `postgresql://user:password@host:port/database`

### "Failed to initialize MCP Toolbox"

- Verify Google Cloud credentials are set up (run `gcloud auth application-default login`)
- Check that PostgreSQL is running and accessible
- Verify database user has proper permissions

### "Import error: No module named 'google.adk'"

- Install dependencies: `pip install -r requirements.txt`
- Make sure you're using Python 3.9+

### Database connection fails

- Verify PostgreSQL is running: `pg_isready` or check your database service
- Test connection manually: `psql -h localhost -U user -d ecommerce`
- Check firewall/network settings

## Next Steps

1. ✅ Test the agent with various queries
2. ✅ Integrate with Express backend (see `backend/src/services/agent.service.ts`)
3. ✅ Set up AgentOps for production monitoring (optional)
4. ✅ Move to Agent 2: Cart Management

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review the [comprehensive plan](../../requirements/AGENT_1_COMPREHENSIVE_PLAN.md)
- Check ADK documentation: https://google.github.io/adk-docs/
