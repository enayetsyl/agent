# Phase 1: Database Design - Quick Start Guide

## Overview

Phase 1 implements the complete database schema for the Product Catalog Query Agent. This includes:

- ✅ Database schema with all tables, indexes, and triggers
- ✅ Sample data seeding script
- ✅ Setup scripts for Windows and Linux/Mac
- ✅ Complete documentation

## Quick Start (3 Steps)

### Step 1: Install PostgreSQL

**Windows:**
```bash
# Download from: https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Run Setup Script

**Windows:**
```bash
cd database
setup.bat
```

**Linux/Mac:**
```bash
cd database
chmod +x setup.sh
./setup.sh
```

The script will:
1. Create the `ecommerce` database
2. Apply the schema (create all tables, indexes, triggers)
3. Optionally seed sample data

### Step 3: Verify Setup

```bash
psql -U postgres -d ecommerce
```

Run verification queries:
```sql
-- Check tables
\dt

-- Count records
SELECT 'Categories' as table_name, COUNT(*) as count FROM categories
UNION ALL
SELECT 'Products', COUNT(*) FROM products
UNION ALL
SELECT 'Product Variants', COUNT(*) FROM product_variants;

-- View sample products
SELECT id, name, price, brand FROM products LIMIT 5;

\q
```

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Database
```bash
psql -U postgres
```
```sql
CREATE DATABASE ecommerce;
\q
```

### 2. Apply Schema
```bash
psql -U postgres -d ecommerce -f database/schema.sql
```

### 3. Seed Data
```bash
psql -U postgres -d ecommerce -f database/seed.sql
```

## Database Structure

The database includes these main tables:

| Table | Description |
|-------|-------------|
| `categories` | Product categories (hierarchical) |
| `products` | Main product information |
| `product_variants` | Product variants (sizes, colors, etc.) |
| `variant_attributes` | Attributes for filtering variants |
| `product_images` | Product images |
| `product_tags` | Tags for search and filtering |
| `product_tag_relations` | Product-tag relationships |
| `product_reviews` | Customer reviews |

## Sample Data Included

After seeding, you'll have:
- **6 categories**: Apparel, Electronics, Footwear, Home & Garden, Sports & Outdoors, Books & Media
- **10 products**: Including t-shirts, jeans, headphones, shoes, etc.
- **30+ product variants**: Different sizes, colors, etc.
- **8 product reviews**: Sample customer reviews

## Connection String

After setup, use this connection string:

```
postgresql://postgres:your_password@localhost:5432/ecommerce
```

Replace:
- `postgres` with your PostgreSQL username
- `your_password` with your PostgreSQL password
- `localhost` with your database host (if different)
- `5432` with your PostgreSQL port (if different)

## Troubleshooting

### "psql: command not found"
- Make sure PostgreSQL is installed and `psql` is in your PATH
- On Windows, add PostgreSQL bin directory to PATH

### "database does not exist"
- Run the setup script or manually create the database first

### "permission denied"
- Ensure your PostgreSQL user has CREATE privileges
- Try running as the `postgres` superuser

### "could not connect to server"
- Make sure PostgreSQL service is running
- Check if PostgreSQL is listening on the correct port (default: 5432)

## Next Steps

After completing Phase 1:

1. ✅ Database schema created
2. ✅ Sample data loaded
3. ➡️ **Phase 2**: Set up Backend API (Express.js)
4. ➡️ **Phase 3**: Set up ADK Agent (Python)
5. ➡️ **Phase 4**: Build Frontend (Next.js)

## Files Created

```
db_search_agent/
└── database/
    ├── schema.sql          # Complete database schema
    ├── seed.sql            # Sample data seeding script
    ├── setup.sh            # Linux/Mac setup script
    ├── setup.bat           # Windows setup script
    ├── README.md           # Detailed documentation
    └── .gitignore          # Git ignore rules
```

## Need Help?

See `database/README.md` for detailed documentation and troubleshooting tips.

