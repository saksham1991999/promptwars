#!/usr/bin/env python3
"""Run a single migration file."""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_HOST = "db.inhvcajyddrnbexgpbxy.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PORT = "5432"
DB_PASSWORD = "DoorstepDelhi@123"

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
