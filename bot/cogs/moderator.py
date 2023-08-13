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
            await interaction.response.send_message(embed=embed)
        else:
            self.db.add_subscription(guild_id=interaction.guild_id, channel_id=channel.id, mode=mode.value)
            embed = discord.Embed(
                title="Subscription successful",
                description=f"You have successfully subscribed to {mode.name} on {channel.mention}",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)

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
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Not subscribed on this channel",
                description="You are not subscribed on this channel. "
                            "Please choose a valid subscribed channel",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="Clear a number of messages from a channel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(number="The number of messages to clear")
    async def clear(self, interaction: discord.Interaction, number: int):
        logging.info(f"Clearing {number} messages from {interaction.channel}")
        await interaction.response.defer()
        await interaction.channel.purge(limit=number + 1)
        embed = discord.Embed(
            title="Clear successful",
            description=f"You have successfully cleared {number} messages from {interaction.channel.mention}",
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="echo", description="Echo a message on a channel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(channel="The channel to echo on")
    @app_commands.describe(message="The message to echo")
    @app_commands.describe(embed="Whether to send the message as an embed")
    @app_commands.choices(embed=[
        app_commands.Choice(name="Yes", value=1),
        app_commands.Choice(name="No", value=0)
    ])
    async def echo(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, embed: int):
        logging.info(f"Echoing {message} on {channel}")
        await interaction.response.defer()
        if embed:
            embed = discord.Embed(
                title="Message from Admin",
                description=message,
                color=discord.Color.green(),
            )
            await channel.send(embed=embed)
        else:
            await channel.send(message)
        embed = discord.Embed(
            title="Echo successful",
            description=f"You have successfully echoed your message on {channel.mention}",
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="reply", description="Reply to a message")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(message_id="The message to reply to")
    @app_commands.describe(reply="The reply message")
    @app_commands.describe(embed="Whether to send the message as an embed")
    @app_commands.choices(embed=[
        app_commands.Choice(name="Yes", value=1),
        app_commands.Choice(name="No", value=0)
    ])
    async def reply(self, interaction: discord.Interaction, message_id: str, reply: str, embed: int):
        logging.info(f"Replying to {message_id} with {reply}")
        await interaction.response.defer()
        message = await interaction.channel.fetch_message(int(message_id))
        if embed:
            embed = discord.Embed(
                title="Message from Admin",
                description=reply,
                color=discord.Color.green(),
            )
            await message.reply(embed=embed)
        else:
            await message.reply(reply)
        embed = discord.Embed(
            title="Reply successful",
            description=f"You have successfully replied to message {message_id}",
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
