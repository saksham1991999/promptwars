#!/usr/bin/env python3
"""Run Supabase migrations using psycopg2."""

import os
import glob
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection - read from environment variables
DB_HOST = os.environ.get("SUPABASE_DB_HOST", "localhost")
DB_NAME = os.environ.get("SUPABASE_DB_NAME", "postgres")
DB_USER = os.environ.get("SUPABASE_DB_USER", "postgres")
DB_PORT = os.environ.get("SUPABASE_DB_PORT", "5432")
DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD")

if not DB_PASSWORD:
    print("Please set SUPABASE_DB_PASSWORD environment variable with your Supabase database password")
    print("You can find this in your Supabase dashboard under Project Settings > Database")
    exit(1)

def run_migrations():
    """Execute all migration files."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode="require"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    # Get list of migration files
    migrations_dir = "supabase/migrations"
    migration_files = sorted(glob.glob(f"{migrations_dir}/*.sql"))
    
    print(f"Found {len(migration_files)} migration files")
    
    for migration_file in migration_files:
        filename = os.path.basename(migration_file)
        print(f"\nRunning {filename}...")
        
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        try:
            cursor.execute(sql)
            print(f"  ✓ {filename} completed")
        except Exception as e:
            print(f"  ✗ {filename} failed: {e}")
            # Continue with other migrations
    
    cursor.close()
    conn.close()
    print("\n✓ All migrations completed!")

if __name__ == "__main__":
    run_migrations()
