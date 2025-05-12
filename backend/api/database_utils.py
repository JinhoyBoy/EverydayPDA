import sys
import os
from fastapi import HTTPException
from typing import Dict, List, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.database import get_db_connection
from api.models import User, UserUpdate

# Initialize User Preferences
#
# Parameters:
#   - user (User): User object containing preferences, e.g., {"username": "john_doe", "city": "Stuttgart"}
#
# Returns:
#   - dict: Confirmation of successful initialization, including the user ID
async def init_user_preferences(user: User):
    """
    Initialize user preferences by inserting user data into the database.
    """
    conn = await get_db_connection()
    async with conn.transaction():
        check_query = "SELECT COUNT(*) FROM users WHERE username = $1"
        existing = await conn.fetchval(check_query, user.username)

        if existing > 0:
            raise HTTPException(status_code=400, detail="User already exists")

        insert_user_query = """
        INSERT INTO users (username, course, cafeteria, city, preferred_transport_medium)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING u_id
        """
        user_id = await conn.fetchval(insert_user_query, user.username, user.course, user.cafeteria, user.city, user.preferred_transport_medium)

        if user.stocks:
            for stock_name in user.stocks:
                stock_id = await conn.fetchval("SELECT s_id FROM stocks WHERE stock_name = $1", stock_name)
                if not stock_id:
                    stock_id = await conn.fetchval("INSERT INTO stocks (stock_name) VALUES ($1) RETURNING s_id", stock_name)
                await conn.execute("INSERT INTO user_stocks (u_id, s_id) VALUES ($1, $2)", user_id, stock_id)

        if user.news:
            for news_name in user.news:
                news_id = await conn.fetchval("SELECT n_id FROM news WHERE news_name = $1", news_name)
                if not news_id:
                    news_id = await conn.fetchval("INSERT INTO news (news_name) VALUES ($1) RETURNING n_id", news_name)
                await conn.execute("INSERT INTO user_news (u_id, n_id) VALUES ($1, $2)", user_id, news_id)

    await conn.close()
    return {"message": "User created successfully", "user_id": user_id}

# Retrieve User Preferences
#
# Parameters:
#   - username (str): The username of the user, e.g., "john_doe"
#
# Returns:
#   - User: User object containing preferences, or raises HTTPException if the user is not found
async def get_user_preferences(username: str) -> Optional[User]:
    """
    Retrieve user preferences from the database.
    """
    conn = await get_db_connection()
    
    query = """
        SELECT 
            u.username, 
            u.course, 
            u.cafeteria, 
            u.city, 
            u.preferred_transport_medium,
            (SELECT STRING_AGG(s.stock_name, ',') 
            FROM user_stocks us
            JOIN stocks s ON us.s_id = s.s_id
            WHERE us.u_id = u.u_id) AS stocks,
            (SELECT STRING_AGG(n.news_name, ',') 
            FROM user_news un
            JOIN news n ON un.n_id = n.n_id
            WHERE un.u_id = u.u_id) AS news
        FROM users u
        WHERE u.username = $1;
    """

    result = await conn.fetchrow(query, username)
    await conn.close()
    
    if result:
        return User(
            username=result["username"],
            course=result["course"],
            cafeteria=result["cafeteria"],
            city=result["city"],
            preferred_transport_medium=result["preferred_transport_medium"],
            stocks=result["stocks"].split(",") if result["stocks"] else [],
            news=result["news"].split(",") if result["news"] else [],
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Update List Preferences
#
# Parameters:
#   - conn: Database connection object
#   - user_id (int): The ID of the user in the database
#   - items (dict): Dictionary containing "add" and "delete" lists for preferences
#   - table (str): The name of the table to update, e.g., "stocks"
#   - id_column (str): The ID column in the table, e.g., "s_id"
#   - name_column (str): The name column in the table, e.g., "stock_name"
#   - link_table (str): The linking table for user preferences, e.g., "user_stocks"
#   - link_column (str): The column in the linking table, e.g., "s_id"
#
# Returns:
#   - None
async def __update_list_preferences(conn, user_id, items, table, id_column, name_column, link_table, link_column):
    """
    Add or remove items in the user's preferences list.
    """
    add_items = items.get("add", [])
    delete_items = items.get("delete", [])
    
    if add_items:
        for item_name in add_items:
            item_id = await conn.fetchval(f"SELECT {id_column} FROM {table} WHERE {name_column} = $1", item_name)
            if not item_id:
                item_id = await conn.fetchval(f"INSERT INTO {table} ({name_column}) VALUES ($1) RETURNING {id_column}", item_name)
            await conn.execute(f"INSERT INTO {link_table} (u_id, {link_column}) VALUES ($1, $2) ON CONFLICT DO NOTHING", user_id, item_id)
    
    if delete_items:
        for item_name in delete_items:
            await conn.execute(f"DELETE FROM {link_table} WHERE u_id = $1 AND {link_column} = (SELECT {id_column} FROM {table} WHERE {name_column} = $2)", user_id, item_name)

# Update User Preferences
#
# Parameters:
#   - username (str): The username of the user, e.g., "john_doe"
#   - user (UserUpdate): Object containing updated preferences, e.g., {"city": "Berlin"}
#
# Returns:
#   - dict: Confirmation of successful update
async def update_user_preferences(username: str, user: UserUpdate):
    """
    Update user preferences in the database.
    """
    conn = await get_db_connection()
    try:
        async with conn.transaction():
            check_query = "SELECT u_id FROM users WHERE username = $1"
            user_id = await conn.fetchval(check_query, username)

            if not user_id:
                raise HTTPException(status_code=404, detail="User not found")

            update_fields = []
            update_values = []

            if user.course:
                update_fields.append("course = $1")
                update_values.append(user.course)
            if user.cafeteria:
                update_fields.append("cafeteria = $2")
                update_values.append(user.cafeteria)
            if user.city:
                update_fields.append("city = $3")
                update_values.append(user.city)
            if user.preferred_transport_medium:
                update_fields.append("preferred_transport_medium = $4")
                update_values.append(user.preferred_transport_medium)

            if update_fields:
                update_query = f"""
                    UPDATE users
                    SET {', '.join(update_fields)}
                    WHERE u_id = $5
                """
                await conn.execute(update_query, *update_values, user_id)

            await __update_list_preferences(conn, user_id, {"add": user.add_stocks, "delete": user.delete_stocks}, "stocks", "s_id", "stock_name", "user_stocks", "s_id")
            await __update_list_preferences(conn, user_id, {"add": user.add_news, "delete": user.delete_news}, "news", "n_id", "news_name", "user_news", "n_id")

        return {"message": "User preferences updated successfully"}
    finally:
        await conn.close()

# Get All Users
#
# Parameters:
#   - None
#
# Returns:
#   - list: List of all usernames in the database, e.g., ["john_doe", "jane_doe"]
async def get_all_users():
    """
    Retrieve all usernames from the database.
    """
    conn = await get_db_connection()
    try:
        return await conn.fetch("SELECT username FROM users")
    finally:
        await conn.close()