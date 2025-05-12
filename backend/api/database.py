import asyncpg

DATABASE_URL = "postgresql://user:password@preferences_db:5432/preferences_db"

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)
