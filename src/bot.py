import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension("commands.turnintoticket")
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))