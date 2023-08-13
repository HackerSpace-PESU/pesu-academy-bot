import logging

import discord
from discord import app_commands
from discord.ext import commands


class DeveloperCog(commands.Cog):
    """
    This cog contains all commands and functionalities available to the bot developers
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.developer_ids = [
            543143780925177857  # rowlet
        ]
        self.developer_log_channel_id = 848634702944010252
        self.developer_log_channel = self.client.fetch_channel(self.developer_log_channel_id)

    async def check_developer_permissions(self, interaction: discord.Interaction):
        """
        Checks if the user is a developer
        """
        user_id = interaction.user.id
        return user_id in self.developer_ids

    @app_commands.command(name="sync", description="Sync commands with Discord")
    async def sync_command(self, interaction: discord.Interaction):
        if await self.check_developer_permissions(interaction):
            logging.info(f"Synchronizing commands with Discord")
            await interaction.response.defer()
            await self.client.tree.sync()
            embed = discord.Embed(
                title="Commands synced with Discord",
                description="The bot has finished syncing commands with Discord",
                color=discord.Color.blue(),
            )
            await interaction.followup.send(embed=embed)
        else:
            logging.info(f"User {interaction.user} tried to sync commands with Discord")
            embed = discord.Embed(
                title="You are not permitted to run this command",
                description="Invalid access to command. If you think this is an error, please contact the bot developers",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.developer_log_channel.send(f"User {interaction.user} tried to sync commands with Discord")

