import logging
from itertools import cycle

import discord
from discord.ext import commands, tasks

from .db import DatabaseCog


class BaseCog(commands.Cog):
    """
    This cog contains all base functions
    """

    def __init__(self, client: commands.Bot, db: DatabaseCog):
        self.client = client
        self.db = db
        self.statuses = cycle([
            "with the PRIDE of PESU",
            "with lives",
            "with your future",
            "with PESsants",
            "with PESts"
        ])

        self.change_status_loop.start()

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.client.user.name}#{self.client.user.discriminator}")
        # TODO: Change status periodically

        # TODO: Send log to all log channels

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

    @tasks.loop(hours=5)
    async def change_status_loop(self):
        await self.client.wait_until_ready()
        logging.info("Changing bot status")
        await self.client.change_presence(activity=discord.Game(next(self.statuses)))
