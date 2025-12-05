#!/bin/bash

# ============================================
# Database Setup Script for Agent 1
# ============================================
# This script sets up the PostgreSQL database
# for the Product Catalog Query Agent.
# ============================================

set -e  # Exit on error

# Configuration (modify as needed)
DB_NAME="ecommerce"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Agent 1: Database Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql command not found. Please install PostgreSQL.${NC}"
    exit 1
fi

# Check if database exists
echo -e "${YELLOW}Checking if database exists...${NC}"
if psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo -e "${YELLOW}Database '$DB_NAME' already exists.${NC}"
    read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Dropping existing database...${NC}"
        psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -c "DROP DATABASE IF EXISTS $DB_NAME;"
        echo -e "${GREEN}Database dropped.${NC}"
    else
        echo -e "${YELLOW}Skipping database creation.${NC}"
    fi
fi

# Create database if it doesn't exist
if ! psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo -e "${YELLOW}Creating database '$DB_NAME'...${NC}"
    psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -c "CREATE DATABASE $DB_NAME;"
    echo -e "${GREEN}Database created successfully.${NC}"
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run schema
echo -e "${YELLOW}Applying database schema...${NC}"
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -f "$SCRIPT_DIR/schema.sql"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Schema applied successfully.${NC}"
else
    echo -e "${RED}Error applying schema.${NC}"
    exit 1
fi

# Ask if user wants to seed data
read -p "Do you want to seed sample data? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${YELLOW}Seeding sample data...${NC}"
    psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -f "$SCRIPT_DIR/seed.sql"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Sample data seeded successfully.${NC}"
    else
        echo -e "${RED}Error seeding data.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Skipping data seeding.${NC}"
fi

# Verify setup
echo ""
echo -e "${YELLOW}Verifying setup...${NC}"
TABLE_COUNT=$(psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
echo -e "${GREEN}Found $TABLE_COUNT tables in the database.${NC}"

if psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM products;" | grep -q "[1-9]"; then
    PRODUCT_COUNT=$(psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM products;" | xargs)
    echo -e "${GREEN}Found $PRODUCT_COUNT products in the database.${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Database connection string:"
echo "postgresql://$DB_USER:password@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "To connect manually:"
echo "  psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME"
echo ""

