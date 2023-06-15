import logging

import discord
from discord import app_commands
from discord.ext import commands


class PublicCog(commands.Cog):
    """
    This cog contains all public commands
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="ping", description="Perform a ping test")
    async def ping(self, interaction: discord.Interaction):
        logging.info(f"Running ping test")
        embed = discord.Embed(
            title="Ping Test",
            description=f"{round(self.client.latency * 1000)} ms",
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)
