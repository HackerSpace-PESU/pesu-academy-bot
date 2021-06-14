import re
import os
import time
import random
import base64
import asyncio
import discord
from itertools import cycle
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from discord.ext import commands, tasks
from utils import *


load_dotenv()
client = commands.Bot(command_prefix='pes.',
                      help_command=None, intents=discord.Intents.all())
status = cycle(["with the PRIDE of PESU", "with lives",
               "with your future", "with PESsants", "with PESts"])
greetings = ["PESsants", "PESts"]

BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_ID = int(os.environ["BOT_ID"])

ARONYABAKSY_ID = int(os.environ["ARONYA_ID"])
ADITEYABARAL_ID = int(os.environ["BARAL_ID"])
BOT_DEVS = [ARONYABAKSY_ID, ADITEYABARAL_ID]

CHANNEL_BOT_LOGS_1 = 842466762985701406
CHANNEL_BOT_LOGS_2 = 848634702944010252
DEV_SERVER_1 = 768874819474292746
DEV_SERVER_2 = 848632052059471912

BITLY_TOKEN = os.environ["BITLY_TOKEN"]
BITLY_GUID = os.environ["BITLY_GUID"]

GOOGLE_CHROME_BIN = os.environ["GOOGLE_CHROME_BIN"]
CHROMEDRIVER_PATH = os.environ["CHROMEDRIVER_PATH"]
PESU_SRN = os.environ["PESU_SRN"]
PESU_PWD = os.environ["PESU_PWD"]

REDDIT_SECRET_TOKEN = os.environ["REDDIT_SECRET_TOKEN"]
REDDIT_PERSONAL_USE_TOKEN = os.environ["REDDIT_PERSONAL_USE_TOKEN"]
REDDIT_USER_AGENT = os.environ["REDDIT_USER_AGENT"]

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = GOOGLE_CHROME_BIN
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')

COMPILER_CLIENT_ID_1 = os.environ["COMPILER_CLIENT_ID_1"]
COMPILER_CLIENT_SECRET_1 = os.environ["COMPILER_CLIENT_SECRET_1"]
COMPILER_CLIENT_ID_2 = os.environ["COMPILER_CLIENT_ID_2"]
COMPILER_CLIENT_SECRET_2 = os.environ["COMPILER_CLIENT_SECRET_2"]
COMPILER_CLIENT_ID_3 = os.environ["COMPILER_CLIENT_ID_3"]
COMPILER_CLIENT_SECRET_3 = os.environ["COMPILER_CLIENT_SECRET_3"]
COMPILER_CLIENT_ID_4 = os.environ["COMPILER_CLIENT_ID_4"]
COMPILER_CLIENT_SECRET_4 = os.environ["COMPILER_CLIENT_SECRET_4"]
COMPILER_CLIENT_ID_5 = os.environ["COMPILER_CLIENT_ID_5"]
COMPILER_CLIENT_SECRET_5 = os.environ["COMPILER_CLIENT_SECRET_5"]

compiler_keys = {
    (COMPILER_CLIENT_ID_1, COMPILER_CLIENT_SECRET_1): 0,
    (COMPILER_CLIENT_ID_2, COMPILER_CLIENT_SECRET_2): 0,
    (COMPILER_CLIENT_ID_3, COMPILER_CLIENT_SECRET_3): 0,
    (COMPILER_CLIENT_ID_4, COMPILER_CLIENT_SECRET_4): 0,
    (COMPILER_CLIENT_ID_5, COMPILER_CLIENT_SECRET_5): 0,
}

TODAY_ANNOUNCEMENTS_MADE = list()
ALL_ANNOUNCEMENTS_MADE = list()
TASK_FLAG_INSTAGRAM = False
TASK_FLAG_REDDIT = False
TASK_FLAG_PESU = True


async def checkUserIsAdminOrBotDev(ctx):
    '''
    Checks if the message author is an Administrator or is one of the Bot Developers.
    '''
    return ctx.message.author.guild_permissions.administrator or ctx.message.author.id in BOT_DEVS


async def checkUserIsBotDev(ctx):
    '''
    Checks if the message author is one of the Bot Developers.
    '''
    return ctx.message.author.id in BOT_DEVS


async def checkUserIsAdmin(ctx):
    '''
    Checks if the message author is an Administrator.
    '''
    return ctx.message.author.guild_permissions.administrator


async def checkUserEchoReplyPermissions(ctx, channel_id):
    if await checkUserIsBotDev(ctx):
        return True
    else:
        guild_id = int(ctx.guild.id)
        guild_object = client.get_guild(guild_id)
        guild_channels = guild_object.text_channels
        guild_channels_id = [gc.id for gc in guild_channels]
        if await checkUserIsAdmin(ctx) and channel_id in guild_channels_id:
            return True
        else:
            return False


async def checkUserHasManageServerPermission(ctx):
    '''
    Checks if the message author has the Manage Server permission.
    '''
    return ctx.channel.permissions_for(ctx.author).manage_guild


async def sendChannel(channel_id, content=None, embed=None, file=None):
    channel_id = int(channel_id)
    try:
        channel = client.get_channel(channel_id)
        if file != None:
            await channel.send(file=file)
        if embed == None and content != None:
            await channel.send(content)
        elif embed != None and content == None:
            await channel.send(embed=embed)
        elif embed != None and content != None:
            await channel.send(content, embed=embed)
        else:
            pass
    except:
        print(f"Error sending message to channel {channel_id}")


async def sendSpecificChannels(channels, content=None, embed=None, file=None):
    for channel_id in channels:
        await sendChannel(channel_id, content=content, embed=embed, file=file)


async def sendAllChannels(message_type, content=None, embed=None, file=None):
    db_records = getCompleteDatabase()
    for row in db_records:
        guild_id, _, channel_type, channel_id = row[1:]
        if channel_id == None:
            continue
        guild_id = int(guild_id)
        channel_id = int(channel_id)
        if channel_type == message_type:
            await sendChannel(channel_id, content=content, embed=embed, file=file)


async def subscriptionReminder():
    print("Reminding non-subscribed servers...")
    db_records = getCompleteDatabase()
    guild_info = dict()
    for row in db_records:
        guild_id, _, channel_type, channel_id = row[1:]
        guild_id = int(guild_id)
        if guild_id not in guild_info:
            guild_info[guild_id] = {
                "publish": None,
                "log": None
            }
        guild_info[guild_id][channel_type] = channel_id

    alert_embed = discord.Embed(
        color=discord.Color.blue(),
        title="PESU Academy Bot - IMPORTANT REMINDER",
        description="Your server is **not** setup for alerts. Members with the `Manage Server` permissions are requested to run `pes.alerts {CHANNEL NAME}` to setup the bot.\n You can optionally also setup a logging channel using `pes.log {CHANNEL NAME}`"
    )

    # In database and on server but not subscribed to alerts
    for guild in guild_info:
        if guild_info[guild]["publish"] == None:
            guild_object = client.get_guild(guild)
            if guild_object != None:
                for channels in guild_object.text_channels:
                    if channels.permissions_for(guild_object.me).send_messages:
                        await channels.send(embed=alert_embed)
                        break

    # On server but not in database [happens when hard sync happens and channel gets deleted - HENCE DO NOT PERFORM HARD SYNC]
    guilds_details = await client.fetch_guilds(limit=150).flatten()
    guild_id = [g.id for g in guilds_details]
    for gid in guild_id:
        if gid not in guild_info:
            guild_object = client.get_guild(gid)
            if guild_object != None:
                for channels in guild_object.text_channels:
                    if channels.permissions_for(guild_object.me).send_messages:
                        await channels.send(embed=alert_embed)
                        break


async def syncDatabase():
    print("Syncing databases...")
    db_records = getCompleteDatabase()
    guilds_details = await client.fetch_guilds(limit=150).flatten()
    guild_id = [str(g.id) for g in guilds_details]

    for row in db_records:
        db_guild_id = row[1]
        if db_guild_id not in guild_id:
            removeGuild(db_guild_id)


@client.event
async def on_ready():
    '''
    Initialising bot after boot
    '''
    print("Bot is online")
    await client.change_presence(activity=discord.Game(next(status)))
    await syncDatabase()

    for client_id, client_secret in compiler_keys.keys():
        compiler_keys[(client_id, client_secret)] = await updateCodeAPICallLimits(client_id, client_secret)

    greeting = random.choice(greetings)
    embed = discord.Embed(title=f"{greeting}, PESU Academy Bot is online",
                          description="Use `pes.` to access commands", color=discord.Color.blue())
    await sendAllChannels(message_type="log", embed=embed)
    await subscriptionReminder()

    checkNewDay.start()
    changeStatus.start()
    checkPESUAnnouncement.start()
    checkInstagramPost.start()
    checkRedditPost.start()


@client.event
async def on_guild_join(guild):
    '''
    Statements executed after bot joins a server.
    '''
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="PESU Academy Bot",
        description="Provides updates about PES University from PESU Academy and social media"
    )
    embed.add_field(
        name="\u200b",
        value="Thank you for adding the bot to your server! Use `pes.help` to view all supported commands.\n"
    )

    alert_embed = discord.Embed(
        color=discord.Color.blue(),
        title="PESU Academy Bot - IMPORTANT",
        description="Members with the `Manage Server` permissions are requested to run `pes.alerts {CHANNEL NAME}` to setup the bot.\n You can optionally also setup a logging channel using `pes.log {CHANNEL NAME}`"
    )

    for channels in guild.text_channels:
        if channels.permissions_for(guild.me).send_messages:
            await channels.send(embed=embed)
            await channels.send(embed=alert_embed)
            break

    guild_id = str(guild.id)
    guild_name = guild.name
    addGuild(guild_id, guild_name)

    server_owner = guild.owner
    try:
        await server_owner.send("Thank you for adding the PESU Academy bot to your server! run `pes.alerts {CHANNEL NAME}` to setup the bot.\n You can optionally also setup a logging channel using `pes.log {CHANNEL NAME}`\nIf you have any queries, please visit https://github.com/aditeyabaral/pesu-academy-bot")
    except:
        pass


@client.event
async def on_guild_remove(guild):
    guild_id = str(guild.id)
    removeGuild(guild_id)


@client.event
async def on_message(ctx):
    if ctx.author.bot:
        pass
    elif client.user.mentioned_in(ctx):
        if "@everyone" not in ctx.content and "@here" not in ctx.content and ctx.reference == None:
            greeting = random.choice(greetings)[:-1]
            embed = discord.Embed(
                color=discord.Color.blue(),
                title="PESU Academy Bot",
                description=f"{ctx.author.mention} don't be a {greeting} by pinging the bot. Type `pes.help` to access commands."
            )
            await ctx.channel.send(f"{ctx.author.mention}", embed=embed)
        else:
            await client.process_commands(ctx)
    else:
        await client.process_commands(ctx)


@client.event
async def on_command_error(ctx, error):
    guild_id = str(ctx.guild.id)
    author = ctx.message.author
    guild_logging_channels = getChannelFromServer(guild_id, "log")
    if guild_logging_channels:
        guild_logging_channels = [row[-1] for row in guild_logging_channels]
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="PESU Academy Bot - Command Error Log",
            description=f"{author.mention} made this error in {ctx.message.channel.mention}:\n{error}"
        )
        await sendSpecificChannels(guild_logging_channels, embed=embed)
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="PESU Academy Bot - Command Error",
        description="Incorrect command. Please type `pes.help` to view all commands."
    )
    await ctx.send(embed=embed)


@client.event
async def on_guild_channel_delete(channel):
    channel_id = str(channel.id)
    removeChannel(channel_id)


@client.command()
async def remind(ctx):
    if await checkUserIsBotDev(ctx):
        await subscriptionReminder()
        await ctx.send("Subscription reminders have been delivered.")
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def dbsync(ctx, sync_method="soft"):
    if await checkUserIsBotDev(ctx):
        db_records = getCompleteDatabase()
        guilds_details = await client.fetch_guilds(limit=150).flatten()
        guild_id = [str(g.id) for g in guilds_details]

        for row in db_records:
            db_guild_id = row[1]
            db_channel_type = row[3]
            db_channel_id = row[4]
            if db_guild_id not in guild_id:
                removeGuild(db_guild_id)

            if sync_method == "hard":
                if db_channel_id == None:
                    continue
                channel = client.get_channel(int(db_channel_id))
                client_member = ctx.guild.get_member(BOT_ID)
                client_permissions = client_member.permissions_in(channel)
                if channel == None:
                    removeChannel(db_channel_id)
                else:
                    if db_channel_type == "publish":
                        if not (client_permissions.send_messages and client_permissions.embed_links and client_permissions.attach_files and client_permissions.read_message_history):
                            removeChannelWithType(db_channel_id, "publish")
                    else:
                        if not (client_permissions.send_messages and client_permissions.embed_links and client_permissions.read_message_history):
                            removeChannelWithType(db_channel_id, "log")

        await ctx.send("Database sync completed.")
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def invite(ctx):
    embed = discord.Embed(title="Invite PESU Academy Bot to your Discord Server", url="http://bit.ly/pesu-academy-bot",
                          description="Use the following link: http://bit.ly/pesu-academy-bot", color=discord.Color.blue())
    await ctx.send(embed=embed)


@client.command(aliases=['support'])
async def contribute(ctx, *params):
    embed = discord.Embed(
        title="Contribute to PESU Academy Bot", color=discord.Color.blue())
    embed.add_field(
        name="Github repository", value="https://github.com/aditeyabaral/pesu-academy-bot", inline=False)
    embed.add_field(
        name='\u200b', value="If you wish to contribute to the bot, run these steps:", inline=False)
    rules = {
        1: "Fork this repository",
        2: "Create a new branch called `username-beta`",
        3: "Make your changes and create a pull request with the following information in the request message: `The functionality you wish to change/add | What did you change/add`. Remember to add a few screenshots of the feature working at your end",
        4: "Send a review request to `aditeyabaral` or `abaksy`",
        5: "Wait for approval for reviewers. Your PR may be directly accepted or requested for further changes"
    }
    for rule in rules:
        embed.add_field(
            name='\u200b', value=f"{rule}: {rules[rule]}", inline=False)

    guild_object = client.get_guild(DEV_SERVER_1)
    aditeyabaral = guild_object.get_member(ADITEYABARAL_ID).mention
    abaksy = guild_object.get_member(ARONYABAKSY_ID).mention
    embed.add_field(
        name="Reviewers", value=f"`aditeyabaral` - {aditeyabaral}\n`abaksy` - {abaksy}", inline=False)
    embed.add_field(
        name="Important", value="**Under no circumstances is anyone allowed to merge to the main branch.**", inline=False)
    embed.add_field(
        name="\u200b", value="You can send suggestions and feedback by raising an issue with [IMPROVEMENT] or [FEEDBACK] added to the title.")
    await ctx.send(embed=embed)


@client.command(aliases=['reachout'])
async def reachoutcommand(ctx, *, message: str = None):
    if await checkUserIsAdminOrBotDev(ctx):
        if(message == None):
            await ctx.send("Type a message to send to the developers.")
        else:

            embed = discord.Embed(
                color=discord.Color.blue(),
                title="PESU Academy Bot - Reach Out to Developer Team",
                description="Your message has been sent to the developer team. We will get back to you with a reply shortly on this channel."
            )
            await ctx.send(embed=embed)

            embed = discord.Embed(
                color=discord.Color.blue(),
                title="PESU Academy Bot - Reach Out to Developer Team",
                description=f'''**Server Name**: `{ctx.guild.name}`
**Server ID**: `{ctx.guild.id}`
**Channel ID**: `{ctx.channel.id}`\n
**Message**: {message}'''
            )
            channel = client.get_channel(CHANNEL_BOT_LOGS_2)
            await channel.send(embed=embed)

    else:
        await ctx.send("You are not authorised to run this command. Only members with administrator permissions can run this command. Contact your server administrator or anyone with a role who has administrator privileges. You can always contact us on our GitHub page: https://github.com/aditeyabaral/pesu-academy-bot")


@client.command(aliases=['reachreply'])
async def reachreplycommand(ctx, destination_channel_id: int = None, *, message: str = None):
    if await checkUserIsBotDev(ctx):
        if(destination_channel_id == None):
            await ctx.send("Enter a valid channel ID")
        elif message == None:
            await ctx.send("Enter a valid message")
        else:
            try:
                destination_channel = client.get_channel(
                    destination_channel_id)
                embed = discord.Embed(
                    color=discord.Color.blue(),
                    title="PESU Academy Bot - Message from Developer Team",
                    description=message
                )
                await destination_channel.send(embed=embed)

                embed = discord.Embed(
                    color=discord.Color.blue(),
                    title="PESU Academy Bot - Message from Developer Team",
                    description="Message has been delivered"
                )
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(
                    color=discord.Color.blue(),
                    title="PESU Academy Bot - Message from Developer Team",
                    description="Message failed to deliver to channel"
                )
                await ctx.send(embed=embed)
    else:
        await ctx.send("You do not have the permission to execute this command")


@client.command(aliases=['guilds'])
async def guildscommand(ctx):
    if await checkUserIsBotDev(ctx):
        await ctx.channel.trigger_typing()
        count = 0
        data = 'SERVER NAME,SERVER ID\n\n'
        guilds_details = await client.fetch_guilds(limit=150).flatten()
        for guild_detail in guilds_details:
            data += f"{guild_detail.name},{guild_detail.id}\n"
            count += 1
        with open('guilds.csv', 'w') as fp:
            fp.write(data)
        await ctx.send(file=discord.File('guilds.csv'))
        await ctx.send(f"Count: {count}")
        fp.close()
        os.remove('guilds.csv')
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def dbinfo(ctx):
    if await checkUserIsBotDev(ctx):
        db_records = getCompleteDatabase()
        data = "SERVER ID,SERVER NAME,CHANNEL TYPE,CHANNEL ID\n\n"
        for row in db_records:
            row_data = list(map(str, row[1:]))
            data += "{},{},{},{}\n".format(*row_data)
        with open('guilds.csv', 'w') as fp:
            fp.write(data)
        await ctx.send(file=discord.File('guilds.csv'))
        fp.close()
        os.remove('guilds.csv')
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command(aliases=['announce'])
async def announcecommand(ctx, message_type=None, *, message: str = None):
    if await checkUserIsBotDev(ctx):
        if message == None:
            await ctx.send("Please enter a valid message.")
        elif message_type == None:
            await ctx.send("Please enter a valid message type.")
        else:
            embed = discord.Embed(
                color=discord.Color.blue(),
                title="PESU Academy Bot - Message from Developer Team",
                description=message
            )
            await sendAllChannels(message_type=message_type, embed=embed)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def alerts(ctx, channel: discord.TextChannel = None):
    if channel == None:
        await ctx.send("Please mention the channel in which you would like to forward announcements.")
    else:
        if await checkUserHasManageServerPermission(ctx):
            channel_id = str(channel.id)
            guild_id = str(ctx.guild.id)
            guild_name = str(ctx.guild.name)
            if checkServerChannelAndTypeExists(guild_id, channel_id, "publish"):
                await ctx.send(f"{channel.mention} is already subscribed to PESU Academy Bot alerts.")
            else:
                client_member = ctx.guild.get_member(BOT_ID)
                client_permissions = client_member.permissions_in(channel)
                if client_permissions.send_messages and client_permissions.embed_links and client_permissions.attach_files and client_permissions.read_message_history:
                    addChannel(guild_id, guild_name, channel_id, "publish")
                    await ctx.send(f"**Success!** You will now receive PESU Academy Bot alerts on {channel.mention}. You can optionally also give the Bot permission to ping `@everyone` and `@here` roles to receive notifications.")
                else:
                    await ctx.send("I don't have enough permissions in that channel. Enable `Send Messages`, `Embed Links`, `Read History` and `Attach Files` permissions for me.")
        else:
            await ctx.send("Looks like you do not have the `Manage Server` permission to run this command.")


@client.command()
async def removealerts(ctx, channel: discord.TextChannel = None):
    if channel == None:
        await ctx.send("Please mention the channel you would like to unsubscribe from alerts.")
    else:
        if await checkUserHasManageServerPermission(ctx):
            channel_id = str(channel.id)
            guild_id = str(ctx.guild.id)
            if not checkServerChannelAndTypeExists(guild_id, channel_id, "publish"):
                await ctx.send(f"{channel.mention} is not subscribed to PESU Academy Bot alerts.")
            else:
                removeChannelWithType(channel_id, "publish")
                await ctx.send(f"**Success!** You will no longer receive PESU Academy Bot alerts on {channel.mention}.")

        else:
            await ctx.send("Looks like you do not have the `Manage Server` permission to run this command.")


@client.command(aliases=["log"])
async def logging(ctx, channel: discord.TextChannel = None):
    if channel == None:
        await ctx.send("Please mention the channel in which you would like to forward logging information.")
    else:
        if await checkUserHasManageServerPermission(ctx):
            channel_id = str(channel.id)
            guild_id = str(ctx.guild.id)
            guild_name = str(ctx.guild.name)
            if checkServerChannelAndTypeExists(guild_id, channel_id, "log"):
                await ctx.send(f"{channel.mention} is already subscribed to PESU Academy Bot logging information.")
            else:
                client_member = ctx.guild.get_member(BOT_ID)
                client_permissions = client_member.permissions_in(channel)
                if client_permissions.send_messages and client_permissions.embed_links and client_permissions.read_message_history:
                    addChannel(guild_id, guild_name, channel_id, "log")
                    await ctx.send(f"**Success!** You will now receive PESU Academy Bot logging on {channel.mention}. You can optionally also give the Bot permission to ping `@everyone` and `@here` roles to receive notifications.")
                else:
                    await ctx.send("I don't have enough permissions in that channel. Enable `Send Messages`, `Embed Links`, and `Read History` permissions for me.")
        else:
            await ctx.send("Looks like you do not have the `Manage Server` permission to run this command.")


@client.command()
async def removelog(ctx, channel: discord.TextChannel = None):
    if channel == None:
        await ctx.send("Please mention the channel you would like to unsubscribe from logging.")
    else:
        if await checkUserHasManageServerPermission(ctx):
            channel_id = str(channel.id)
            guild_id = str(ctx.guild.id)
            if not checkServerChannelAndTypeExists(guild_id, channel_id, "log"):
                await ctx.send(f"{channel.mention} is not subscribed to PESU Academy Bot logging.")
            else:
                removeChannelWithType(channel_id, "log")
                await ctx.send(f"**Success!** You will no longer receive PESU Academy Bot logging on {channel.mention}.")

        else:
            await ctx.send("Looks like you do not have the `Manage Server` permission to run this command.")


@client.command()
async def echo(ctx, *, query=None):
    await client.wait_until_ready()
    channel = query.split()[0]
    try:
        channel_id = int(channel)
        pattern = pattern = re.compile(r"^\d+")
    except ValueError:
        channel_id = int(channel[2:-1])
        pattern = pattern = re.compile(r"^<#\d+>")

    if await checkUserEchoReplyPermissions(ctx, channel_id):
        _, content = re.split(pattern, query)
        content = content.strip()
        channel = client.get_channel(channel_id)
        await channel.send(content)
    else:
        await ctx.send(f"You are not authorised to run this command.")


@client.command()
async def reply(ctx, *, query=None):
    await client.wait_until_ready()
    parent_message_url = query.split()[0]
    _, content = query.split(parent_message_url)
    parent_message_url_components = parent_message_url.split('/')
    server_id = int(parent_message_url_components[4])
    channel_id = int(parent_message_url_components[5])
    parent_message_id = int(parent_message_url_components[6])

    if await checkUserEchoReplyPermissions(ctx, channel_id):
        server = client.get_guild(server_id)
        channel = server.get_channel(channel_id)
        parent_message = await channel.fetch_message(parent_message_id)
        await parent_message.reply(content)
    else:
        await ctx.send(f"You are not authorised to run this command.")


@client.command(aliases=["vc", "pride"])
async def prideofpesu(ctx):
    greeting = random.choice(greetings)
    embed = discord.Embed(
        title=f"{greeting}, may the PRIDE of PESU be with you!", color=discord.Color.blue())
    await ctx.send(embed=embed)
    await ctx.send("https://tenor.com/view/pes-pesuniversity-pesu-may-the-pride-of-pes-may-the-pride-of-pes-be-with-you-gif-21274060")


@client.command()
async def ping(ctx):
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="PESU Academy Bot - Ping Test",
        description=f"Pong! {round(client.latency * 1000, 2)} ms"
    )
    await ctx.send(embed=embed)


@client.command(aliases=["h"])
async def help(ctx):
    content = {
        '`pes.hello`': 'Be nice to me. Say `pes.hello` once in a while 👋',
        '`pes.ping`': 'Perform a `ping` test',
        '`pes.alerts`': 'Setup a channel to receive alerts using `pes.alerts [CHANNEL]`',
        '`pes.log`': 'Setup a channel to receive logging information using `pes.log [CHANNEL]`',
        '`pes.invite`': 'Obtain the invite link for PESU Academy Bot',
        '`pes.contribute`': 'Learn how to contribute to PESU Academy Bot',
        '`pes.search`': 'To search the PESU Class and Section Database, use `pes.search [SRN | email]`',
        '`pes.pesdb`': 'Search the Student PESU Database using `pes.pesdb [search 1] & [search 2]`. String together as many filters as needed. You can also use emails and names.',
        '`pes.news`': 'Fetch PESU Announcements using `pes.news [OPTIONAL=today] [OPTIONAL=N]`. Get today\'s announcements with `pes.news today`. Fetch all announcements using `pes.news`. Specify the number of news using `N`.',
        '`pes.insta`': 'Fetch the last Instagram post from PESU Academy',
        '`pes.reddit`': 'Fetch the latest posts from r/PESU using `pes.reddit [NUMBER OF POSTS]`',
        '`pes.longrip`': 'Create a shortened long.rip link using `pes.longrip [URL]`',
        '`pes.goto`': 'Create customized redirection links using `pes.goto [LONG URL] [SHORT URL]`',
        '`pes.code`': """Use this to execute Python scripts. Attach your script within blockquotes on the next line. 
        **Example**: 
        pes.code python3
        ```
        import math
        print(math.pi)
        ```
        <inputs>""",
        '`pes.spongebob` or `pes.sb`': 'Create a SpongeBob mocking meme. `pes.sb [top text] & [bottom-text]` or `pes.sb [bottom-text]`',
        '`pes.dict`': 'Search for the meaning of word using `pes.dict [word]`'
    }
    embed = discord.Embed(title=f"Help",
                          color=discord.Color.blue())
    index = 1
    for cmd in content:
        embed.add_field(
            name=f"**{index}**", value='\t{} : {}'.format(cmd, content[cmd]), inline=False)
        index += 1
    await ctx.send(embed=embed)


@client.command(aliases=["hi"])
async def hello(ctx):
    author = ctx.message.author
    if author.id in BOT_DEVS:
        await ctx.send(f"Hello master! 👋")
    else:
        await ctx.send(f"Hello {author.mention}! 👋")


@client.command()
async def clear(ctx, amount=1):
    if await checkUserIsAdminOrBotDev(ctx):
        await ctx.channel.purge(limit=amount+1)
        await ctx.channel.send(f"Deleted {amount} messages")
        await asyncio.sleep(0.5)
        await ctx.channel.purge(limit=1)
    else:
        await ctx.send(f"You are not authorised to run this command.")


@client.command(aliases=["searchsrn", "searchpes"])
async def search(ctx, query):
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    result = await searchPESUAcademy(driver, query)
    if result == None:
        await ctx.send("No results found.")
    else:
        embed = discord.Embed(title=f"Search Results",
                              color=discord.Color.blue())
        for prn, srn, name, semester, section, cycle, department, branch, campus in result:
            embed.add_field(name=f"**{name}**", value=f'''**PRN**: {prn}
**SRN**: {srn}
**Semester**: {semester}
**Section**: {section}
**Cycle**: {cycle}
**Department**: {department}
**Branch**: {branch}
**Campus**: {campus}'''
                            )
        await ctx.send(embed=embed)
    driver.quit()


@client.command()
async def pesdb(ctx, *, query):
    result, truncated, base_url = await getPESUDBResults(query)
    if result == None:
        await ctx.send("No results found.")
    else:
        embed = discord.Embed(title=f"Search Results",
                              color=discord.Color.blue())
        for prn, srn, name, semester, section, cycle, department, branch, campus, phone, email in result:
            embed.add_field(name=f"**{name}**", value=f'''**PRN**: {prn}
**SRN**: {srn}
**Semester**: {semester}
**Section**: {section}
**Cycle**: {cycle}
**Department**: {department}
**Branch**: {branch}
**Campus**: {campus}
**Phone**: {phone}
**E-Mail**: {email}'''
                            )
        await ctx.send(embed=embed)
        if truncated and ctx is not None:
            await ctx.send(f"For more records, please visit {base_url}")


@client.command(aliases=["sb", "saas"])
async def spongebob(ctx, *, query):
    await generateSpongebobMeme(query)
    with open('meme.jpg', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
    os.remove("meme.jpg")


@client.command(aliases=["dict"])
async def dictionary(ctx, query, n=5):
    flag, result = await getDictionaryMeaning(query, n)
    if flag:
        meanings, antonyms = result
        embed = discord.Embed(title=f"Search Results",
                              color=discord.Color.blue())
        for defn, examples, form in meanings:
            if examples:
                tmp_examples = '\n'.join(examples)
                embed.add_field(name=f"**{query}** [{form}]", value=f'''**Definition**: {defn}
    **Examples**: {tmp_examples}''')
            else:
                embed.add_field(
                    name=f"**{query}** [{form}]", value=f'''**Definition**: {defn}''')
        if antonyms:
            tmp_antonyms = ', '.join(antonyms)
            embed.add_field(name=f"**Antonyms**", value=f"{tmp_antonyms}")
        await ctx.send(embed=embed)

    else:
        if result == None:
            await ctx.send(f"Your spelling is so bad that I don't even know what to suggest.")
        else:
            await ctx.send(f"Word not found. Did you mean {result}?")


@client.command(aliases=["goto"])
async def redirector(ctx, long_url, short_url):
    response = await shortenLinkRedirector(short_url, long_url)
    if response.status_code == 200:
        await ctx.send(f"{long_url} is now shortened to https://goto-link.herokuapp.com/{short_url}")
    else:
        await ctx.send("Failed to create redirected link.")


@client.command(aliases=["lr"])
async def longrip(ctx, long_url):
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    short_url = await shortenLinkLongRip(driver, long_url)
    await ctx.send(f"{long_url} is now shortened to {short_url}")
    driver.quit()


@client.command()
async def code(ctx, language, *, content=None):
    if language == "help":
        languages = ['ada', 'bash', 'bc', 'brainfuck', 'c', 'c-99', 'clisp', 'clojure', 'cobol', 'coffeescript',
                     'cpp', 'cpp17', 'csharp', 'd', 'dart', 'elixir', 'erlang', 'factor', 'falcon', 'fantom',
                     'forth', 'fortran', 'freebasic', 'fsharp', 'gccasm', 'go', 'groovy', 'hack', 'haskell',
                     'icon', 'intercal', 'java', 'jlang', 'kotlin', 'lolcode', 'lua', 'mozart', 'nasm', 'nemerle',
                     'nim', 'nodejs', 'objc', 'ocaml', 'octave', 'pascal', 'perl', 'php', 'picolisp', 'pike',
                     'prolog', 'python2', 'python3', 'r', 'racket', 'rhino', 'ruby', 'rust', 'scala', 'scheme',
                     'smalltalk', 'spidermonkey', 'sql', 'swift', 'tcl', 'unlambda', 'vbn', 'verilog',
                     'whitespace', 'yabasic']
        content = f'''`.code` uses the JDoodle code execution API which supports code compilation and execution for all major programming languages.

Supported languages: `{languages}`

To execute a script, use the following syntax for the command:

.code <language>
```
Enter code here, do not add syntax highlighting
```
<inputs for script>
'''
        await ctx.reply(content, mention_author=False)
    else:
        if content == None:
            await ctx.reply("Please enter a valid script. Use `.code help` to learn how to use the service.", mention_author=False)
        else:
            content = content.split("```")[1:]
            script, inputs = list(map(str.strip, content))
            if not inputs:
                inputs = None
            if not checkSpamCode(script, inputs):
                client_id, client_secret = max(
                    compiler_keys, key=lambda x: compiler_keys[x])
                try:
                    result = await executeCode(client_id, client_secret, script, language, inputs)
                    if not checkSpamCode(result.output.strip()):
                        await ctx.reply(f"{result.output.strip()}\nScript took {result.cpuTime} seconds to execute and consumed {result.memory} kilobyte(s)", mention_author=False)
                    else:
                        greeting = random.choice(greetings)[:-1]
                        await ctx.reply(f"Aye {greeting}, you may be smart but I am smarter. No pinging `@everyone` or `@here` with the bot.")

                except Exception as error:
                    await ctx.reply(f"**Error occured**: {error}\n\nUse `.code help` to learn how to use the service.")

            else:
                greeting = random.choice(greetings)[:-1]
                await ctx.reply(f"Aye {greeting}, you may be smart but I am smarter. No pinging `@everyone` or `@here` with the bot.")


async def getRedditEmbed(post):
    embed = discord.Embed(title="New Reddit Post",
                          url=post["url"], color=discord.Color.blue())
    if post["content"]:
        if len(post["content"]) > 1024:
            embed.add_field(
                name=post["title"], value=post["content"][:1000] + "...", inline=False)
        else:
            embed.add_field(
                name=post["title"], value=post["content"][:1000], inline=False)
    else:
        embed.add_field(name=post["title"], value="\u200b", inline=False)
    if post["images"]:
        embed.set_image(url=post["images"][0])
    return embed


@client.command(aliases=["r"])
async def reddit(ctx, subreddit="PESU", n=5):
    reddit_posts = await getRedditPosts(subreddit, REDDIT_PERSONAL_USE_TOKEN, REDDIT_SECRET_TOKEN, REDDIT_USER_AGENT, n)
    if reddit_posts:
        for p in reddit_posts:
            embed = await getRedditEmbed(p)
            await ctx.send(embed=embed)
    else:
        await ctx.send("No posts found. Please ensure that the subreddit exists and it is not NSFW.")


async def getInstagramEmbed(username):
    html = getInstagramHTML(username)
    photo_time = getLastPhotoDate(html)
    post_embed = discord.Embed(
        title=f'New Instagram Post from {username}', url=getPostLink(html), color=discord.Color.blue())
    if(checkVideo(html)):
        post_embed.set_image(url=getVideoURL(html))
    else:
        post_embed.set_image(url=getLastThumbnailURL(html))

    post_embed.add_field(name="\u200b", value=getPhotoDescription(html)[
                         :1000] + "... ", inline=False)
    post_embed.set_footer(text=datetime.fromtimestamp(photo_time))
    return post_embed, photo_time


@client.command()
async def insta(ctx, username="pesuniversity"):
    post_embed, _ = await getInstagramEmbed(username)
    await ctx.channel.send(embed=post_embed)


async def getAnnouncementEmbed(announcement):
    title = announcement["header"]
    if len(title) > 256:
        embed = discord.Embed(title=title[:253] + "...", description="..." +
                              title[253:], color=discord.Color.blue())
    else:
        embed = discord.Embed(
            title=title, color=discord.Color.blue())

    content_body = str(announcement["body"])
    if len(content_body) > 1024:
        content_bodies = content_body.split('\n')
        content_bodies = [c for c in content_bodies if c.strip() not in [
            "", " "]]
        for i, c in enumerate(content_bodies):
            if i == 0:
                embed.add_field(
                    name=str(announcement["date"]), value=c, inline=False)
            else:
                embed.add_field(name=f"\u200b", value=c, inline=False)
    else:
        embed.add_field(
            name=str(announcement["date"]), value=content_body)

    return embed


@client.command(aliases=["news"])
async def pesunews(ctx, *, query=None):
    global TODAY_ANNOUNCEMENTS_MADE
    global ALL_ANNOUNCEMENTS_MADE

    announcements = ALL_ANNOUNCEMENTS_MADE
    N = len(ALL_ANNOUNCEMENTS_MADE)
    if query != None:
        filters = query.lower().split()[:2]
        for f in filters:
            if f == "today":
                announcements = TODAY_ANNOUNCEMENTS_MADE
            else:
                try:
                    temp_limit = int(f)
                    N = temp_limit
                except ValueError:
                    pass
    announcements = announcements[:N]

    if announcements:
        for announcement in announcements:
            embed = await getAnnouncementEmbed(announcement)
            if announcement["img"] != None:
                img_base64 = announcement["img"].strip()[22:]
                imgdata = base64.b64decode(img_base64)
                filename = "announcement-img.png"
                with open(filename, 'wb') as f:
                    f.write(imgdata)
                with open(filename, 'rb') as f:
                    img_file = discord.File(f)
                    await ctx.send(file=img_file)

            await ctx.send(embed=embed)
            if announcement["attachments"]:
                for fname in announcement["attachments"]:
                    attachment_file = discord.File(fname)
                    await ctx.send(file=attachment_file)
    else:
        await ctx.send("No announcements available. Retry with another option or try again later.")


@client.command()
async def taskmanager(ctx, handle=None, mode=None):
    global TASK_FLAG_PESU
    global TASK_FLAG_REDDIT
    global TASK_FLAG_INSTAGRAM

    if await checkUserIsBotDev(ctx):
        allowed_handles = ["instagram", "reddit", "pesu"]
        allowed_modes = ["on", "off"]
        if handle == None or handle not in allowed_handles:
            await ctx.send(f"Please enter a valid handle. Allowed handles are: {allowed_handles}")
        elif mode == None or mode not in allowed_modes:
            await ctx.send(f"Please enter a valid mode. Allowed modes are: {allowed_modes}")
        else:
            value_mapping = {"on": True, "off": False}
            if handle == "instagram":
                TASK_FLAG_INSTAGRAM = value_mapping[mode]
            if handle == "reddit":
                TASK_FLAG_REDDIT = value_mapping[mode]
            if handle == "pesu":
                TASK_FLAG_PESU = value_mapping[mode]

            if mode == "pesu":
                mode = "PESU Announcement"

            embed = discord.Embed(
                color=discord.Color.blue(),
                title="PESU Academy Bot - Message from Developer Team",
                description=f"The {handle.capitalize()} feature has been turned **{mode.upper()}**"
            )

            await ctx.send(f"The {handle.capitalize()} feature has been turned **{mode.upper()}**")
            await sendAllChannels(message_type="publish", embed=embed)
            await sendAllChannels(message_type="log", embed=embed)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def taskstatus(ctx):
    global TASK_FLAG_PESU
    global TASK_FLAG_REDDIT
    global TASK_FLAG_INSTAGRAM

    if await checkUserIsBotDev(ctx):
        value_mapping = {True: "ON", False: "OFF"}
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="PESU Academy Bot - Task Status",
            description=f'''PESU Announcement Checks: **{value_mapping[TASK_FLAG_PESU]}**
Instagram Checks: **{value_mapping[TASK_FLAG_INSTAGRAM]}**
Reddit Checks: **{value_mapping[TASK_FLAG_REDDIT]}**'''
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("You are not authorised to run this command.")


@tasks.loop(minutes=26)
async def checkInstagramPost():
    await client.wait_until_ready()
    if TASK_FLAG_INSTAGRAM:
        print("Fetching Instagram posts...")
        for username in instagram_usernames:
            try:
                post_embed, photo_time = await getInstagramEmbed(username)
                curr_time = time.time()
                if (curr_time - photo_time) < 1560:
                    await sendAllChannels(message_type="publish", embed=post_embed)
            except:
                print(f"Error while fetching Instagram post from {username}")


@tasks.loop(minutes=34)
async def checkRedditPost():
    await client.wait_until_ready()
    if TASK_FLAG_REDDIT:
        print("Fetching Reddit posts...")
        reddit_posts = await getRedditPosts("PESU", REDDIT_PERSONAL_USE_TOKEN, REDDIT_SECRET_TOKEN, REDDIT_USER_AGENT)
        if reddit_posts:
            latest_reddit_post = reddit_posts[0]
            post_time = latest_reddit_post["create_time"]
            current_time = datetime.now()
            time_difference = current_time - post_time
            if time_difference.seconds < 2040 and time_difference.days == 0:
                post_embed = await getRedditEmbed(latest_reddit_post)
                await sendAllChannels(message_type="publish", embed=post_embed)


@tasks.loop(minutes=5)
async def checkPESUAnnouncement():
    global TODAY_ANNOUNCEMENTS_MADE
    global ALL_ANNOUNCEMENTS_MADE
    await client.wait_until_ready()

    if TASK_FLAG_PESU:
        print("Fetching announcements...")
        driver = webdriver.Chrome(
            executable_path=CHROMEDRIVER_PATH, options=chrome_options)
        all_announcements = getPESUAnnouncements(driver, PESU_SRN, PESU_PWD)
        # all_announcements = getPESUAnnouncements(driver, PESU_SRN, PESU_PWD)
        time.sleep(5)   # sleep so all attachments are downloaded
        print(all_announcements)

        new_announcement_count = 0
        for a in all_announcements:
            if a not in ALL_ANNOUNCEMENTS_MADE:
                ALL_ANNOUNCEMENTS_MADE.append(a)
                new_announcement_count += 1

        print(f"NEW announcements found: {new_announcement_count}")

        ALL_ANNOUNCEMENTS_MADE.sort(key=lambda x: x["date"], reverse=True)
        current_date = datetime.now().date()
        for announcement in all_announcements:
            if announcement["date"] == current_date:
                if announcement not in TODAY_ANNOUNCEMENTS_MADE:
                    embed = await getAnnouncementEmbed(announcement)
                    if announcement["img"] != None:
                        print("Image available, sending...")
                        img_base64 = announcement["img"].strip()[22:]
                        imgdata = base64.b64decode(img_base64)
                        filename = "announcement-img.png"
                        with open(filename, 'wb') as f:
                            f.write(imgdata)
                        with open(filename, 'rb') as f:
                            img_file = discord.File(f)
                            await sendAllChannels(message_type="publish", file=img_file)

                    await sendAllChannels(message_type="publish", content="@everyone", embed=embed)
                    if announcement["attachments"]:
                        print("Attachment available, sending...")
                        for fname in announcement["attachments"]:
                            attachment_file = discord.File(fname)
                            await sendAllChannels(message_type="publish", file=attachment_file)
                    TODAY_ANNOUNCEMENTS_MADE.append(announcement)
        driver.quit()


@tasks.loop(minutes=10)
async def checkNewDay():
    global TODAY_ANNOUNCEMENTS_MADE
    global ALL_ANNOUNCEMENTS_MADE
    await client.wait_until_ready()

    current_time = datetime.now()
    if current_time.hour == 0:
        TODAY_ANNOUNCEMENTS_MADE = list()
        ALL_ANNOUNCEMENTS_MADE = list()
        await cleanUp()
        await subscriptionReminder()


@tasks.loop(hours=5)
async def changeStatus():
    '''
    Changes the status of the PESU Academy bot every 4 hours.
    '''
    await client.wait_until_ready()
    await client.change_presence(activity=discord.Game(next(status)))


client.run(BOT_TOKEN)
