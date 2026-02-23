import discord
from discord import app_commands
from discord.ext import commands
from utils.message_extractor import extract_message_context
from services.gemini_service import generate_ticket_data
from services.jira_service import create_jira_issue
import os

class TurnIntoTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="turnintoticket", description="Turn a replied-to message into a Jira ticket")
    @app_commands.describe(context="Any extra context to include (optional)")
    async def turnintoticket(self, interaction: discord.Interaction, context: str = ""):
        await interaction.response.defer()

        # Fetch recent messages to find the one to reference
        messages = [m async for m in interaction.channel.history(limit=10) if not m.author.bot]
        if not messages:
            await interaction.followup.send("⚠️ Could not find a message to reference. Send or reply to a message first.")
            return

        target_message = messages[0]

        # 1. Extract context
        msg_context = await extract_message_context(target_message, interaction.channel)

        # 2. Generate ticket with Gemini
        await interaction.followup.send("🤖 Generating ticket with Gemini...")
        ticket_data = generate_ticket_data(msg_context, context)

        # 3. Create Jira issue
        await interaction.edit_original_response(content="📋 Creating Jira issue...")
        issue = create_jira_issue(ticket_data)

        # 4. Return the link
        url = f"{os.getenv('JIRA_BASE_URL')}/browse/{issue['key']}"
        await interaction.edit_original_response(
            content=f"✅ **Jira ticket created!**\n**[{issue['key']}]** {ticket_data['summary']}\n🔗 <{url}>"
        )

async def setup(bot):
    await bot.add_cog(TurnIntoTicket(bot))