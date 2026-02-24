import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from db.database import init_db

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    await init_db()
    bot.load_extension("commands.turnintoticket")
    bot.load_extension("commands.setup")
    print(f"✅ Logged in as {bot.user}")
    print(f"✅ Serving {len(bot.guilds)} servers")

bot.run(os.getenv("DISCORD_TOKEN"))