# Phase 1: Database Setup Guide

This directory contains the database schema and seed data for Agent 1: Product Catalog Query Agent.

## Files

- `schema.sql` - Complete database schema with all tables, indexes, and triggers
- `seed.sql` - Sample data for testing and development
- `setup.sh` - Setup script for Linux/Mac
- `setup.bat` - Setup script for Windows

## Prerequisites

1. **PostgreSQL 14+** installed and running
2. **psql** command-line tool (usually comes with PostgreSQL)
3. Database user with CREATE privileges

### Installing PostgreSQL

**Windows:**

- Download from: https://www.postgresql.org/download/windows/
- Or use Chocolatey: `choco install postgresql`

**macOS:**

- Using Homebrew: `brew install postgresql@14`
- Start service: `brew services start postgresql@14`

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Step-by-Step Setup

### Step 1: Create Database

Connect to PostgreSQL and create a new database:

```bash
# Connect to PostgreSQL (default user is usually 'postgres')
psql -U postgres

# Or if you have a different user:
psql -U your_username
```

In the PostgreSQL prompt, create the database:

```sql
CREATE DATABASE ecommerce;
\q
```

### Step 2: Run Schema

Apply the database schema:

```bash
# Using psql command line
psql -U postgres -d ecommerce -f schema.sql

# Or if using a different user:
psql -U your_username -d ecommerce -f schema.sql
```

**Alternative:** Connect interactively and run the file:

```bash
psql -U postgres -d ecommerce
\i schema.sql
\q
```

### Step 3: Seed Sample Data

Load the sample data:

```bash
psql -U postgres -d ecommerce -f seed.sql
```

**Alternative:** Connect interactively:

```bash
psql -U postgres -d ecommerce
\i seed.sql
\q
```

### Step 4: Verify Setup

Verify that everything was created correctly:

```bash
psql -U postgres -d ecommerce
```

Run these verification queries:

```sql
-- Check tables exist
\dt

-- Count records
SELECT 'Categories' as table_name, COUNT(*) as count FROM categories
UNION ALL
SELECT 'Products', COUNT(*) FROM products
UNION ALL
SELECT 'Product Variants', COUNT(*) FROM product_variants
UNION ALL
SELECT 'Product Reviews', COUNT(*) FROM product_reviews;

-- View sample products
SELECT id, name, price, brand FROM products LIMIT 5;

-- Exit
\q
```

## Using Helper Scripts

### Windows (setup.bat)

1. Edit `setup.bat` and update the database connection details if needed
2. Run: `setup.bat`

### Linux/Mac (setup.sh)

1. Make the script executable:

   ```bash
   chmod +x setup.sh
   ```

2. Edit `setup.sh` and update the database connection details if needed

3. Run:
   ```bash
   ./setup.sh
   ```

## Database Connection String

After setup, you can connect to the database using:

```
postgresql://username:password@localhost:5432/ecommerce
```

For example:

- Username: `postgres`
- Password: `your_password`
- Host: `localhost`
- Port: `5432`
- Database: `ecommerce`

Full connection string:

```
postgresql://postgres:your_password@localhost:5432/ecommerce
```

## Troubleshooting

### Error: "database does not exist"

- Make sure you created the database first (Step 1)

### Error: "permission denied"

- Ensure your PostgreSQL user has CREATE privileges
- You may need to run as the `postgres` superuser

### Error: "relation already exists"

- The tables already exist. Drop them first if you want to start fresh:
  ```sql
  DROP SCHEMA public CASCADE;
  CREATE SCHEMA public;
  GRANT ALL ON SCHEMA public TO postgres;
  GRANT ALL ON SCHEMA public TO public;
  ```

### Error: "could not connect to server"

- Make sure PostgreSQL is running:
  - Windows: Check Services (services.msc) for "postgresql"
  - Mac: `brew services list`
  - Linux: `sudo systemctl status postgresql`

## Next Steps

After completing Phase 1, you can proceed to:

- **Phase 2**: Backend API (Express.js) setup
- The backend will use Prisma ORM to connect to this database

## Schema Overview

The database includes:

- **categories** - Product categories with hierarchical support
- **products** - Main product information
- **product_variants** - Product variants (sizes, colors, etc.)
- **variant_attributes** - Attributes for filtering variants
- **product_images** - Product images
- **product_tags** - Tags for search and filtering
- **product_tag_relations** - Many-to-many relationship between products and tags
- **product_reviews** - Customer reviews

All tables include proper indexes for performance optimization.
