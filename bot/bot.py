import asyncio
import logging

import discord
import yaml
from discord.ext import commands

from cogs.db import DatabaseCog


logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(threadName)s:%(lineno)d - %(message)s",
    filemode="w",
)


async def setup():
    """
    Adds all cogs to the bot and starts the bot
    """
    logging.info(f"Adding cogs to bot")
    database_cog = DatabaseCog(client)
    client.db = database_cog
    client.extns = ['cogs.base', 'cogs.developer', 'cogs.moderator', 'cogs.pesu_academy', 'cogs.public']
    for extn in client.extns:
        await client.load_extension(extn)
    logging.info(f"Successfully added all cogs. Starting bot now")
    await client.start(config["bot"]["token"])


if __name__ == "__main__":
    config = yaml.safe_load(open("config.yml"))
    bot_prefix = config["bot"].get("prefix", "pes.")
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    client = commands.Bot(command_prefix=bot_prefix, help_command=None, intents=intents)
    client.config = config
    asyncio.run(setup())
