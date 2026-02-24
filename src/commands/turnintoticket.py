import nextcord
from nextcord.ext import commands
from utils.message_extractor import extract_message_context
from services.groq_service import generate_ticket_data
from services.jira_service import create_jira_issue
from db.user_config import get_user_config

class TurnIntoTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="turnintoticket", description="Turn a message into a Jira ticket in your connected project")
    async def turnintoticket(
        self,
        interaction: nextcord.Interaction,
        context: str = nextcord.SlashOption(description="Any extra context to include", required=False, default="")
    ):
        await interaction.response.defer()

        # Pull this specific user's Jira config
        config = await get_user_config(str(interaction.user.id))
        if not config:
            await interaction.followup.send(
                "⚠️ You haven't connected your Jira account yet. Run `/setup` first.",
                ephemeral=True
            )
            return

        messages = [m async for m in interaction.channel.history(limit=10) if not m.author.bot]
        if not messages:
            await interaction.followup.send("⚠️ Could not find a message to reference.")
            return

        target_message = messages[0]
        msg_context = await extract_message_context(target_message, interaction.channel)

        await interaction.followup.send("🤖 Generating ticket with Groq...")
        ticket_data = generate_ticket_data(msg_context, context)

        await interaction.edit_original_message(content="📋 Creating Jira issue...")
        issue = create_jira_issue(ticket_data, config)

        url = f"{config['jira_base_url']}/browse/{issue['key']}"
        await interaction.edit_original_message(
            content=(
                f"✅ **Jira ticket created!**\n"
                f"**[{issue['key']}]** {ticket_data['summary']}\n"
                f"🔗 <{url}>"
            )
        )

def setup(bot):
    bot.add_cog(TurnIntoTicket(bot))