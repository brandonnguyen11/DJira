import aiosqlite
from db.database import DB_PATH

async def save_user_config(user_id, jira_base_url, jira_email, jira_api_token, jira_project_key, jira_project_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO user_config (user_id, jira_base_url, jira_email, jira_api_token, jira_project_key, jira_project_name)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                jira_base_url=excluded.jira_base_url,
                jira_email=excluded.jira_email,
                jira_api_token=excluded.jira_api_token,
                jira_project_key=excluded.jira_project_key,
                jira_project_name=excluded.jira_project_name
        ''', (user_id, jira_base_url, jira_email, jira_api_token, jira_project_key, jira_project_name))
        await db.commit()

async def get_user_config(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT jira_base_url, jira_email, jira_api_token, jira_project_key, jira_project_name FROM user_config WHERE user_id = ?',
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    'jira_base_url': row[0],
                    'jira_email': row[1],
                    'jira_api_token': row[2],
                    'jira_project_key': row[3],
                    'jira_project_name': row[4],
                }
            return None

async def delete_user_config(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM user_config WHERE user_id = ?', (user_id,))
        await db.commit()