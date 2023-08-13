import logging

import discord
from discord import app_commands
from discord.ext import commands


class DeveloperCog(commands.Cog):
    """
    This cog contains all commands and functionalities available to the bot developers
    """

    def __init__(self, client: commands.Bot, config: dict):
        self.client = client
        self.config = config
        self.developer_user_ids = config["bot"]["developer_user_ids"]
        self.developer_channel_ids = config["bot"]["developer_channel_ids"]
        self.developer_log_channels = [
            self.client.get_channel(channel_id)
            for channel_id in self.developer_channel_ids
        ]

    async def check_developer_permissions(self, interaction: discord.Interaction):
        """
        Checks if the user is a developer
        """
        return interaction.user.id in self.developer_user_ids

    @app_commands.command(name="sync", description="Sync commands with Discord")
    async def sync_command(self, interaction: discord.Interaction):
        if await self.check_developer_permissions(interaction):
            logging.info(f"Synchronizing commands with Discord")
            await interaction.response.defer()
            await self.client.tree.sync()
            embed = discord.Embed(
                title="Commands synced with Discord",
                description="The bot has finished syncing commands with Discord",
                color=discord.Color.green(),
            )
            await interaction.followup.send(embed=embed)
        else:
            logging.info(f"User {interaction.user} tried to sync commands with Discord")
            embed = discord.Embed(
                title="You are not permitted to run this command",
                description="Invalid access to command. "
                            "If you think this is an error, please contact the bot developers",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)
            # TODO: Fix bug
            await self.developer_log_channel.send(f"User {interaction.user} tried to sync commands with Discord")

