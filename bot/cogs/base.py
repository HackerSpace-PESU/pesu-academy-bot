import logging

from discord.ext import commands

from .db import DatabaseCog


class BaseCog(commands.Cog):
    """
    This cog contains all base functions
    """

    def __init__(self, client: commands.Bot, db: DatabaseCog):
        self.client = client
        self.db = db

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.client.user.name}#{self.client.user.discriminator}")
        # TODO: Change status periodically

        # TODO: Send log to all log channels

        # TODO: Start tasks here

        await self.client.tree.sync()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        logging.info(f"Joined server {guild.name}")
        self.db.add_server(guild.id)
        # TODO: Send subscription reminder message

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logging.info(f"Left server {guild.name}")
        self.db.remove_server(guild.id)
