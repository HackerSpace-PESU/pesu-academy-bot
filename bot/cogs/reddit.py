import datetime
import logging
import re
import traceback
from typing import Optional

import asyncpraw
import discord
import yaml
from discord import app_commands
from discord.ext import commands, tasks


class RedditCog(commands.Cog):
    """
    This cog contains all commands and functionalities for interacting with Reddit
    """
    config = yaml.safe_load(open("config.yml"))

    reddit = app_commands.Group(name="reddit", description="Commands for interacting with Reddit")

    def __init__(self, client: commands.Bot):
        self.client = client
        self.db = client.db
        self.reddit = asyncpraw.Reddit(
            client_id=RedditCog.config["reddit"]["client_id"],
            client_secret=RedditCog.config["reddit"]["client_secret"],
            user_agent=RedditCog.config["reddit"]["user_agent"],
        )
        self.faq_url = "https://www.reddit.com/r/PESU/comments/14c1iym/faqs/"
        self.faqs = list()
        self.posts = list()

        self.update_faq_loop.start()
        self.update_posts_loop.start()
        self.update_new_posts_loop.start()

    def cog_unload(self):
        self.update_faq_loop.cancel()
        self.update_posts_loop.cancel()
        self.update_new_posts_loop.cancel()

    async def update_faqs(self):
        """
        Updates the FAQ list from the subreddit
        """
        updated_faqs = list()
        faq_post = await self.reddit.submission(url=self.faq_url)
        content = faq_post.selftext
        question_links = re.findall(r'\[(.*?)\]\((.*?)\)', content)
        for question, link in question_links:
            try:
                comment = await self.reddit.comment(url=link)
                answer = comment.body.strip()
                upvotes = comment.score
                timestamp = comment.created_utc
            except asyncpraw.exceptions.InvalidURL:
                answer = link
                upvotes = 1
                timestamp = 0
            updated_faqs.append({
                "question": question.strip(),
                "answer": answer,
                "upvotes": upvotes,
                "link": link,
                "timestamp": timestamp,
            })
        self.faqs = updated_faqs

    async def update_posts(self):
        """
        Updates all posts from the subreddit
        """
        subreddit = await self.reddit.subreddit("PESU")
        posts = subreddit.new(limit=1000)
        updated_posts = list()
        async for post in posts:
            title = post.title
            if len(title) > 100:
                title = title[0:97] + "..."
            content = post.selftext
            updated_posts.append({
                "title": title,
                "content": content,
                "upvotes": post.score,
                "link": post.url,
                "timestamp": post.created_utc,
            })
        self.posts = updated_posts

    @staticmethod
    async def format_embed_for_post(title, content, upvotes, link, timestamp):
        """
        Formats the embed for a post
        """
        embed = discord.Embed(
            title=title,
            color=0xff6314,
            url=link,
        )
        if len(content) > 4096:
            blocks = content.split("\n")
            for block in blocks:
                if not block:
                    continue
                embed.add_field(name="\u200b", value=block, inline=False)
        else:
            embed.description = content
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime("%I:%M %p, %d %B %Y")
        embed.set_footer(text=f"Upvotes: {upvotes} | Posted at {timestamp}")
        return embed

    async def handle_question(self, interaction: discord.Interaction, posts: list, question: str):
        """
        Get the answer to a frequently asked question
        """
        default_embed = discord.Embed(color=0xff6314)
        if "question" in posts[0]:
            question_key = "question"
            answer_key = "answer"
        else:
            question_key = "title"
            answer_key = "content"
        for post in posts:
            if post[question_key] == question:
                try:
                    embed = await self.format_embed_for_post(
                        post[question_key],
                        post[answer_key],
                        post["upvotes"],
                        post["link"],
                        post["timestamp"],
                    )
                    await interaction.followup.send(embed=embed)
                except Exception as e:
                    logging.error(f"Failed to send post: {e}\n{traceback.format_exc()}")
                    default_embed.title = post[question_key]
                    default_embed.description = post[answer_key][0:1020] + "..."
                    default_embed.url = post["link"]
                    timestamp = datetime.datetime.fromtimestamp(post["timestamp"]).strftime("%d %B %Y")
                    default_embed.set_footer(text=f"Upvotes: {post['upvotes']} | Posted on {timestamp}\n"
                                                  "Failed to send the full answer. Please visit the link for the full answer.")
                    await interaction.followup.send(embed=default_embed)
                break
        else:
            await interaction.followup.send("No such question found!")

    @reddit.command(name="faq", description="Get the answer to a frequently asked question")
    @app_commands.describe(question="Your question")
    async def faq(self, interaction: discord.Interaction, question: Optional[str] = None):
        """
        Get the answer to a frequently asked question
        """
        await interaction.response.defer()
        default_embed = discord.Embed(
            title="FAQ",
            color=0xff6314,
            url=self.faq_url,
            description="Visit the link for the full list of FAQs"
        )
        if question is None:
            await interaction.followup.send(embed=default_embed)
        else:
            await self.handle_question(interaction, self.faqs, question)

    @reddit.command(name="search", description="Get the answer to a previously asked question")
    @app_commands.describe(question="Your question")
    async def search(self, interaction: discord.Interaction, question: str):
        """
        Get the answer to a previously asked question
        """
        await interaction.response.defer()
        await self.handle_question(interaction, self.posts, question)

    @faq.autocomplete('question')
    async def generate_faq_question_choices(self, interaction: discord.Interaction, question: str):
        """
        Generates the choices for the question autocomplete
        """
        options = [
            app_commands.Choice(name=faq["question"], value=faq["question"]) for faq in self.faqs
            if question.lower() in faq["question"].lower()
        ]
        return options[:25]

    @search.autocomplete('question')
    async def generate_all_question_choices(self, interaction: discord.Interaction, question: str):
        """
        Generates the choices for the question autocomplete
        """
        if not question.strip():
            options = [
                app_commands.Choice(name=post["title"], value=post["title"]) for post in self.posts
            ]
        else:
            options = [
                app_commands.Choice(name=post["title"], value=post["title"]) for post in self.posts
                if question.lower() in post["title"].lower()
            ]
        return options[:25]

    @tasks.loop(hours=6)
    async def update_faq_loop(self):
        """
        Updates the FAQ list from the subreddit every 6 hours
        """
        await self.client.wait_until_ready()
        await self.update_faqs()

    @tasks.loop(hours=24)
    async def update_posts_loop(self):
        """
        Updates the posts list from the subreddit every day
        """
        await self.client.wait_until_ready()
        await self.update_posts()

    @tasks.loop(minutes=15)
    async def update_new_posts_loop(self):
        """
        Checks for new posts every 15 minutes
        """
        await self.client.wait_until_ready()
        logging.info(f"Checking for new new reddit posts")
        current_time = datetime.datetime.utcnow()
        channel_ids = self.db.get_channels_with_mode("announcements")
        subreddit = await self.reddit.subreddit("PESU")
        posts = subreddit.new(limit=10)
        async for post in posts:
            post_timestamp = datetime.datetime.fromtimestamp(post.created_utc)
            if current_time - post_timestamp <= datetime.timedelta(minutes=15):
                embed = await self.format_embed_for_post(
                    post.title,
                    post.selftext,
                    post.score,
                    post.url,
                    post.created_utc,
                )
                for channel_id in channel_ids:
                    channel = self.client.get_channel(int(channel_id))
                    if channel is None:
                        logging.warning(f"Unable to find channel with id {channel_id}")
                        continue
                    try:
                        await channel.send(embed=embed)
                    except Exception as e:
                        logging.error(f"Failed to send post: {e}\n{traceback.format_exc()}")


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(RedditCog(client))
