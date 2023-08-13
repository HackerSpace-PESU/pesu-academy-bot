import logging

import discord
from discord import app_commands
from discord.ext import commands

from .db import DatabaseCog


class ModeratorCog(commands.Cog):
    """
    This cog contains all commands and functionalities available to server admins
    """

    def __init__(self, client: commands.Bot, db: DatabaseCog):
        self.client = client
        self.db = db

    @app_commands.command(name="subscribe", description="Subscribe to announcements or logs on a channel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(channel="The channel to subscribe on")
    @app_commands.describe(mode="The type of subscription to create")
    @app_commands.choices(mode=[
        app_commands.Choice(name="Announcements", value="announcements"),
        app_commands.Choice(name="Logging", value="logs")
    ])
    async def subscribe(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel,
            mode: app_commands.Choice[str]
    ):
        logging.info(f"Subscribing to {mode.name} on {channel}")
        if self.db.check_subscription(guild_id=interaction.guild_id, channel_id=channel.id):
            embed = discord.Embed(
                title="Already subscribed on this channel",
                description="You are already subscribed on this channel. "
                            "Please unsubscribe first or choose another channel",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            self.db.add_subscription(guild_id=interaction.guild_id, channel_id=channel.id, mode=mode.value)
            embed = discord.Embed(
                title="Subscription successful",
                description=f"You have successfully subscribed to {mode.name} on {channel.mention}",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="unsubscribe", description="Unsubscribe to announcements or logs on a channel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(channel="The channel to unsubscribe on")
    async def unsubscribe(self, interaction: discord.Interaction, channel: discord.TextChannel):
        logging.info(f"Unsubscribing from {channel}")
        if self.db.check_subscription(guild_id=interaction.guild_id, channel_id=channel.id):
            self.db.remove_subscription(guild_id=interaction.guild_id, channel_id=channel.id)
            embed = discord.Embed(
                title="Unsubscription successful",
                description=f"You have successfully unsubscribed on {channel.mention}",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Not subscribed on this channel",
                description="You are not subscribed on this channel. "
                            "Please choose a valid subscribed channel",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
