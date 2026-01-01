"""
Database module for storing chat history using PostgreSQL.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor, Json


# Database connection pool
connection_pool = None


def get_db_config():
    """Get database configuration from environment variables."""
    return {
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'database': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }


def init_database():
    """Initialize the database connection pool and create tables if they don't exist."""
    global connection_pool
    
    try:
        db_config = get_db_config()
        
        # Create connection pool
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **db_config
        )
        
        # Get a connection from pool to create tables
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        # Read and execute SQL from db.sql file
        sql_file_path = os.path.join(os.path.dirname(__file__), 'db.sql')
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        
        # Execute the SQL script
        cursor.execute(sql_script)
        
        conn.commit()
        cursor.close()
        connection_pool.putconn(conn)
        
        print(f"PostgreSQL database initialized: {db_config['database']} at {db_config['host']}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def save_conversation(
    session_id: str,
    user_query: str,
    assistant_output: dict,
    timestamp: Optional[str] = None
) -> str:
    """
    Save a conversation to the database.
    Updates both conversation table and session_chat.history in a transaction.
    
    Args:
        session_id: Session ID (must already exist in session_chat)
        user_query: User's query
        assistant_output: AssistantOutput dict with tools_responses and final_assistant_response
        timestamp: Optional timestamp (defaults to now)
        
    Returns:
        str: The generated conversation ID (UUID)
    """
    if connection_pool is None:
        print("Error: Database not initialized")
        raise Exception("Database not initialized")
    
    try:
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("BEGIN")
        
        # Insert into conversation table and get the generated conv_id
        cursor.execute("""
            INSERT INTO conversation (session_id, timestamp, user_query, assistant_output)
            VALUES (%s, %s, %s, %s)
            RETURNING conv_id
        """, (session_id, timestamp, user_query, Json(assistant_output)))
        
        conv_id = cursor.fetchone()[0]
        conv_id_str = str(conv_id)
        
        # Update session_chat.history with the new conversation
        conversation_data = {
            "timestamp": timestamp,
            "user_query": user_query,
            "assistant_output": assistant_output
        }
        
        cursor.execute("""
            UPDATE session_chat
            SET history = history || %s::jsonb,
                updated_at = %s
            WHERE session_id = %s
        """, (Json({conv_id_str: conversation_data}), timestamp, session_id))
        
        # Commit transaction
        conn.commit()
        cursor.close()
        connection_pool.putconn(conn)
        
        return conv_id_str
        
    except Exception as e:
        print(f"Error saving conversation: {e}")
        if conn:
            conn.rollback()
            connection_pool.putconn(conn)
        raise


def get_conversations_by_session(session_id: str, limit: int = 50) -> List[Dict]:
    """
    Get conversations for a specific session from the conversation table.
    
    Args:
        session_id: Session ID to query
        limit: Maximum number of conversations to return
        
    Returns:
        List[ConversationEntry]: List of conversation entries
    """
    if connection_pool is None:
        print("Error: Database not initialized")
        return []
    
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                conv_id::text as conv_id,
                session_id,
                timestamp,
                user_query,
                assistant_output
            FROM conversation
            WHERE session_id = %s
            ORDER BY timestamp ASC
            LIMIT %s
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        cursor.close()
        connection_pool.putconn(conn)
        
        # Convert to list of dicts with proper formatting
        conversations = []
        for row in rows:
            conversations.append({
                "conv_id": row['conv_id'],
                "session_id": row['session_id'],
                "timestamp": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                "user_query": row['user_query'],
                "assistant_output": row['assistant_output']
            })
        
        return conversations
        
    except Exception as e:
        print(f"Error retrieving conversations: {e}")
        if conn:
            connection_pool.putconn(conn)
        return []


def get_session_history(session_id: str) -> Dict:
    """
    Get the complete conversation history from session_chat.history JSONB column.
    This is faster than querying the conversation table.
    
    Args:
        session_id: Session ID to query
        
    Returns:
        Dict: History dictionary with conv_id as keys
    """
    if connection_pool is None:
        print("Error: Database not initialized")
        return {}
    
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT history
            FROM session_chat
            WHERE session_id = %s
        """, (session_id,))
        
        row = cursor.fetchone()
        cursor.close()
        connection_pool.putconn(conn)
        
        if row and row['history']:
            return row['history']
        return {}
        
    except Exception as e:
        print(f"Error retrieving session history: {e}")
        if conn:
            connection_pool.putconn(conn)
        return {}


def get_session_info(session_id: str) -> Optional[Dict]:
    """
    Get session metadata (without full history).
    
    Args:
        session_id: Session ID to query
        
    Returns:
        Optional[Dict]: Session info or None if not found
    """
    if connection_pool is None:
        print("Error: Database not initialized")
        return None
    
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT session_id, username, created_at, updated_at
            FROM session_chat
            WHERE session_id = %s
        """, (session_id,))
        
        row = cursor.fetchone()
        cursor.close()
        connection_pool.putconn(conn)
        
        if row:
            return {
                "session_id": row['session_id'],
                "username": row['username'],
                "created_at": row['created_at'].isoformat() if hasattr(row['created_at'], 'isoformat') else str(row['created_at']),
                "updated_at": row['updated_at'].isoformat() if hasattr(row['updated_at'], 'isoformat') else str(row['updated_at'])
            }
        return None
        
    except Exception as e:
        print(f"Error retrieving session info: {e}")
        if conn:
            connection_pool.putconn(conn)
        return None


def create_session(session_id: str, username: str) -> bool:
    """
    Create a new session in the session_chat table.
    
    Args:
        session_id: Unique session identifier
        username: GitHub username
        
    Returns:
        bool: True if successful, False otherwise
    """
    if connection_pool is None:
        print("Error: Database not initialized")
        return False
    
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO session_chat (session_id, username)
            VALUES (%s, %s)
            ON CONFLICT (session_id) DO NOTHING
        """, (session_id, username))
        
        conn.commit()
        cursor.close()
        connection_pool.putconn(conn)
        return True
        
    except Exception as e:
        print(f"Error creating session: {e}")
        if conn:
            connection_pool.putconn(conn)
        return False


def close_database():
    """Close all database connections in the pool."""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("Database connection pool closed")


