@echo off
REM ============================================
REM Database Setup Script for Agent 1 (Windows)
REM ============================================
REM This script sets up the PostgreSQL database
REM for the Product Catalog Query Agent.
REM ============================================

setlocal enabledelayedexpansion

REM Configuration (modify as needed)
set DB_NAME=ecommerce
set DB_USER=postgres
set DB_HOST=localhost
set DB_PORT=5432

echo ========================================
echo Agent 1: Database Setup
echo ========================================
echo.

REM Check if psql is available
where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: psql command not found. Please install PostgreSQL.
    echo Make sure PostgreSQL bin directory is in your PATH.
    pause
    exit /b 1
)

REM Get the directory where the script is located
set SCRIPT_DIR=%~dp0

REM Check if database exists
echo Checking if database exists...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -lqt 2>nul | findstr /C:"%DB_NAME%" >nul
if %ERRORLEVEL% EQU 0 (
    echo Database '%DB_NAME%' already exists.
    set /p RECREATE="Do you want to drop and recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo Dropping existing database...
        psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -c "DROP DATABASE IF EXISTS %DB_NAME%;" 2>nul
        echo Database dropped.
    ) else (
        echo Skipping database creation.
        goto :apply_schema
    )
)

REM Create database
echo Creating database '%DB_NAME%'...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -c "CREATE DATABASE %DB_NAME%;" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to create database. Check your PostgreSQL connection.
    pause
    exit /b 1
)
echo Database created successfully.

:apply_schema
REM Run schema
echo.
echo Applying database schema...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f "%SCRIPT_DIR%schema.sql" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Schema applied successfully.
) else (
    echo Error applying schema.
    pause
    exit /b 1
)

REM Ask if user wants to seed data
echo.
set /p SEED_DATA="Do you want to seed sample data? (Y/n): "
if /i not "!SEED_DATA!"=="n" (
    echo Seeding sample data...
    psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f "%SCRIPT_DIR%seed.sql" 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo Sample data seeded successfully.
    ) else (
        echo Error seeding data.
        pause
        exit /b 1
    )
) else (
    echo Skipping data seeding.
)

REM Verify setup
echo.
echo Verifying setup...
for /f "tokens=*" %%i in ('psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2^>nul') do set TABLE_COUNT=%%i
echo Found %TABLE_COUNT% tables in the database.

for /f "tokens=*" %%i in ('psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -t -c "SELECT COUNT(*) FROM products;" 2^>nul') do set PRODUCT_COUNT=%%i
if defined PRODUCT_COUNT (
    echo Found %PRODUCT_COUNT% products in the database.
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Database connection string:
echo postgresql://%DB_USER%:password@%DB_HOST%:%DB_PORT%/%DB_NAME%
echo.
echo To connect manually:
echo   psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME%
echo.
pause

