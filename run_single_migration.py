#!/usr/bin/env python3
"""Run a single migration file."""

import os

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_HOST = os.environ.get("SUPABASE_DB_HOST", "localhost")
DB_NAME = os.environ.get("SUPABASE_DB_NAME", "postgres")
DB_USER = os.environ.get("SUPABASE_DB_USER", "postgres")
DB_PORT = os.environ.get("SUPABASE_DB_PORT", "5432")
DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD", "")

def run_migration():
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

    with open("supabase/migrations/011_alter_black_player_id.sql", "r") as f:
        sql = f.read()

    print("Running migration 011...")
    cursor.execute(sql)
    print("✓ Migration completed!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_migration()
