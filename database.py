import aiosqlite
from config import DB_NAME


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE,
                title TEXT,
                username TEXT,
                invite_link TEXT,
                chat_type TEXT
            )
        """)
        await db.commit()


# ---------- FOYDALANUVCHILAR ----------

async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def users_count() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]


# ---------- KANAL / GURUHLAR ----------

async def add_channel(chat_id: int, title: str, username: str, invite_link: str, chat_type: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """INSERT OR REPLACE INTO channels (chat_id, title, username, invite_link, chat_type)
               VALUES (?, ?, ?, ?, ?)""",
            (chat_id, title, username, invite_link, chat_type)
        )
        await db.commit()


async def remove_channel(chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM channels WHERE chat_id = ?", (chat_id,))
        await db.commit()


async def get_channels():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT chat_id, title, username, invite_link, chat_type FROM channels"
        )
        rows = await cursor.fetchall()
        return rows


async def channels_count() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM channels")
        row = await cursor.fetchone()
        return row[0]
