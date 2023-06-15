import logging

from discord.ext import commands


class BaseCog(commands.Cog):
    """
    This cog contains all base functions
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.client.user.name}#{self.client.user.discriminator}")
        # TODO: Change status periodically

        # TODO: Send log to all log channels

        # TODO: Start tasks here

        await self.client.tree.sync()
