import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/djira.db')

async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_config (
                user_id TEXT PRIMARY KEY,
                jira_base_url TEXT,
                jira_email TEXT,
                jira_api_token TEXT,
                jira_project_key TEXT,
                jira_project_name TEXT
            )
        ''')
        await db.commit()