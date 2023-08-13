import logging

import discord
from discord import app_commands
from discord.ext import commands

from pymongo import MongoClient


class DatabaseCog(commands.Cog):
    """
    This cog contains all database utilities
    """

    def __init__(self, client: commands.Bot, config: dict):
        self.client = client
        self.mongo_client = MongoClient(config["bot"]["db"])
        self.db = self.mongo_client["pesu_academy_bot_db"]
        self.subscription_collection = self.db["subscription"]
        self.task_collection = self.db["tasks"]

    def add_server(self, guild_id: str):
        record = {
            "guild_id": guild_id,
            "subscriptions": {}
        }
        self.subscription_collection.insert_one(record)

    def remove_server(self, guild_id: int):
        self.subscription_collection.delete_one({"guild_id": guild_id})

    def check_subscription(self, guild_id: int, channel_id: int):
        return self.subscription_collection.find_one({"guild_id": guild_id, f"subscriptions.{channel_id}": {"$exists": True}})

    def add_subscription(self, guild_id: int, channel_id: int, mode: str):
        if not self.check_subscription(guild_id, channel_id):
            self.subscription_collection.update_one({"guild_id": guild_id}, {"$set": {f"subscriptions.{channel_id}": mode}})
            return True
        else:
            return False

    def remove_subscription(self, guild_id: int, channel_id: int):
        self.subscription_collection.update_one({"guild_id": guild_id}, {"$unset": {f"subscriptions.{channel_id}": ""}})





