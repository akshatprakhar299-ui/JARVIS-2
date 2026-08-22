import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "jarvis.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()


    # Conversation messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            created_at TEXT NOT NULL
        )
    """)


    # Long-term memories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            key TEXT NOT NULL UNIQUE,

            value TEXT NOT NULL,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL
        )
    """)


    connection.commit()

    connection.close()


# ============================================================
# SAVE CHAT MESSAGE
# ============================================================

def save_message(role, content):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages
        (
            role,
            content,
            created_at
        )

        VALUES (?, ?, ?)
        """,

        (
            role,
            content,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# GET RECENT MESSAGES
# ============================================================

def get_messages(limit=20):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role, content

        FROM messages

        ORDER BY id DESC

        LIMIT ?
        """,

        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()


    # Oldest → newest
    rows.reverse()


    return [
        {
            "role": row["role"],
            "content": row["content"]
        }

        for row in rows
    ]


# ============================================================
# CLEAR CHAT
# ============================================================

def clear_messages():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM messages"
    )

    connection.commit()

    connection.close()


# ============================================================
# SAVE LONG-TERM MEMORY
# ============================================================

def save_memory(key, value):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()


    cursor.execute(
        """
        INSERT INTO memories
        (
            key,
            value,
            created_at,
            updated_at
        )

        VALUES (?, ?, ?, ?)

        ON CONFLICT(key)

        DO UPDATE SET

            value = excluded.value,

            updated_at = excluded.updated_at
        """,

        (
            key,
            value,
            now,
            now
        )
    )


    connection.commit()

    connection.close()


# ============================================================
# GET ALL MEMORIES
# ============================================================

def get_memories():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT key, value

        FROM memories

        ORDER BY updated_at DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()


    return [
        {
            "key": row["key"],
            "value": row["value"]
        }

        for row in rows
    ]


# ============================================================
# DELETE MEMORY
# ============================================================

def delete_memory(key):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM memories

        WHERE key = ?
        """,

        (key,)
    )

    connection.commit()

    connection.close()


# ============================================================
# CLEAR ALL MEMORIES
# ============================================================

def clear_memories():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM memories"
    )

    connection.commit()

    connection.close()