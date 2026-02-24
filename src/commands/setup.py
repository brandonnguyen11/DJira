import nextcord
from nextcord.ext import commands
import requests
from requests.auth import HTTPBasicAuth
from db.user_config import save_user_config, get_user_config, delete_user_config

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="setup", description="Connect your personal Jira account to the bot")
    async def setup(
        self,
        interaction: nextcord.Interaction,
        jira_url: str = nextcord.SlashOption(description="Your Jira base URL e.g. https://yourname.atlassian.net", required=True),
        jira_email: str = nextcord.SlashOption(description="Your Atlassian email", required=True),
        jira_api_token: str = nextcord.SlashOption(description="Your Jira API token", required=True),
    ):
        # Always ephemeral so credentials are only visible to the user
        await interaction.response.defer(ephemeral=True)

        # Validate credentials by fetching their projects
        try:
            response = requests.get(
                f"{jira_url.rstrip('/')}/rest/api/3/project",
                auth=HTTPBasicAuth(jira_email, jira_api_token),
                headers={"Accept": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            projects = response.json()
        except Exception as e:
            await interaction.followup.send(
                f"❌ Could not connect to Jira. Check your URL, email, and API token.\nError: `{str(e)}`",
                ephemeral=True
            )
            return

        if not projects:
            await interaction.followup.send("❌ No Jira projects found on this account.", ephemeral=True)
            return

        # Build dropdown of their projects
        options = [
            nextcord.SelectOption(label=p['name'], description=p['key'], value=f"{p['key']}||{p['name']}")
            for p in projects[:25]
        ]

        class ProjectSelect(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

            @nextcord.ui.select(placeholder="Choose your Jira project...", options=options)
            async def select_project(self, select: nextcord.ui.Select, inter: nextcord.Interaction):
                if inter.user.id != interaction.user.id:
                    await inter.response.send_message("❌ This setup menu isn't for you.", ephemeral=True)
                    return

                selected_key, selected_name = select.values[0].split("||")

                await save_user_config(
                    user_id=str(inter.user.id),
                    jira_base_url=jira_url.rstrip('/'),
                    jira_email=jira_email,
                    jira_api_token=jira_api_token,
                    jira_project_key=selected_key,
                    jira_project_name=selected_name
                )

                await inter.response.edit_message(
                    content=(
                        f"✅ Your Jira account is connected!\n"
                        f"**Project:** {selected_name} (`{selected_key}`)\n"
                        f"**URL:** {jira_url}\n\n"
                        f"You can now use `/turnintoticket` anywhere this bot is present."
                    ),
                    view=None
                )
                self.stop()

        await interaction.followup.send(
            "✅ Credentials verified! Choose which Jira project to use:",
            view=ProjectSelect(),
            ephemeral=True
        )

    @nextcord.slash_command(name="myconfig", description="View your current Jira configuration")
    async def myconfig(self, interaction: nextcord.Interaction):
        config = await get_user_config(str(interaction.user.id))
        if not config:
            await interaction.response.send_message(
                "⚠️ You haven't connected Jira yet. Run `/setup` to get started.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"**Your Jira Config:**\n"
            f"🔗 URL: `{config['jira_base_url']}`\n"
            f"📋 Project: {config['jira_project_name']} (`{config['jira_project_key']}`)\n"
            f"📧 Email: `{config['jira_email']}`",
            ephemeral=True
        )

    @nextcord.slash_command(name="disconnect", description="Disconnect your Jira account from the bot")
    async def disconnect(self, interaction: nextcord.Interaction):
        await delete_user_config(str(interaction.user.id))
        await interaction.response.send_message(
            "✅ Your Jira account has been disconnected.",
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(Setup(bot))