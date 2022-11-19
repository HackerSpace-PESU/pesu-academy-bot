import re
import os
import sys
import pytz
import random
import base64
import asyncio
import discord
import subprocess
from itertools import cycle
import datetime
from dotenv import load_dotenv
from selenium import webdriver
from discord.ext import commands, tasks
from utils import *
import random

load_dotenv()
client = commands.Bot(command_prefix='pes.',
                      help_command=None, intents=discord.Intents.all())
status = cycle(["with the PRIDE of PESU", "with lives",
               "with your future", "with PESsants", "with PESts"])
greetings = ["PESsants", "PESts"]

IST = pytz.timezone('Asia/Kolkata')

BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_ID = int(os.environ["BOT_ID"])

ARONYABAKSY_ID = int(os.environ["ARONYA_ID"])
ADITEYABARAL_ID = int(os.environ["BARAL_ID"])
BOT_DEVS = [ARONYABAKSY_ID, ADITEYABARAL_ID]

CHANNEL_BOT_LOGS = 975781253531983893
DEV_SERVER = 697798712184930334

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
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')

MOSS_USER_ID = os.environ.get("MOSS_USER_ID")
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

RUNTIME_ENVIRONMENT = None
TASK_FLAG_PESU = False
TASK_FLAG_REDDIT = False
TASK_FLAG_INSTAGRAM = False
TASK_FLAG_GRAMMAR = False
TASK_FLAG_TRANSLATE = False
TASK_FLAG_MAP = {"on": True, "off": False}

DEBUG_MODE = False
if len(sys.argv) > 1:
    if sys.argv[1] == "--debug":
        print("Running in test mode.")
        DEBUG_MODE = True
    else:
        print("Running in production mode.")
        DEBUG_MODE = False


async def setRuntimeEnvironment():
    global RUNTIME_ENVIRONMENT
    global chrome_options

    runtime_env_heroku_flag = await checkRuntimeEnvironmentHeroku()
    if runtime_env_heroku_flag:
        RUNTIME_ENVIRONMENT = "HEROKU"
        chrome_options.binary_location = GOOGLE_CHROME_BIN
    else:
        RUNTIME_ENVIRONMENT = "OTHER"
    print(f"Setting runtime environment as: {RUNTIME_ENVIRONMENT}")


async def getChromedriver(experimental=False):
    global chrome_options
    new_chrome_options = chrome_options
    if experimental:
        new_chrome_options.add_experimental_option(
            'prefs', {
                "download.default_directory": os.getcwd(),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True
            }
        )

    if RUNTIME_ENVIRONMENT == "HEROKU":
        driver = webdriver.Chrome(
            executable_path=CHROMEDRIVER_PATH, options=new_chrome_options)
    else:
        driver = webdriver.Chrome(options=new_chrome_options)
    tz_params = {'timezoneId': 'Asia/Kolkata'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    return driver


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


async def sendDM(recipient, mention=False, content=None, embed=None, file=None):
    if mention and content != None:
        content = f"{recipient.mention}\n{content}"
    if file != None:
        await recipient.send(file=file)
    if embed == None and content != None:
        await recipient.send(content)
    elif embed != None and content == None:
        await recipient.send(embed=embed)
    elif embed != None and content != None:
        await recipient.send(content, embed=embed)
    else:
        pass


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
    except Exception as error:
        print(f"Error sending message to channel {channel_id}: {error}")


async def sendSpecificChannels(channels, content=None, embed=None, file=None):
    for channel_id in channels:
        await sendChannel(channel_id, content=content, embed=embed, file=file)


async def sendAllChannels(message_type, content=None, embed=None, file=None):
    db_records = getCompleteGuildDatabase()
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
    db_records = getCompleteGuildDatabase()
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


async def syncGuildDatabase():
    print("Syncing databases...")
    db_records = getCompleteGuildDatabase()
    guilds_details = await client.fetch_guilds(limit=150).flatten()
    guild_id = [str(g.id) for g in guilds_details]

    for row in db_records:
        db_guild_id = row[1]
        if db_guild_id not in guild_id:
            removeGuild(db_guild_id)


async def syncTaskStatusDatabase():
    print("Syncing task status...")

    global TASK_FLAG_PESU
    global TASK_FLAG_REDDIT
    global TASK_FLAG_INSTAGRAM
    global TASK_FLAG_GRAMMAR
    global TASK_FLAG_TRANSLATE

    TASK_FLAG_PESU = TASK_FLAG_MAP[getVariableValue("pesu")]
    TASK_FLAG_REDDIT = TASK_FLAG_MAP[getVariableValue("reddit")]
    TASK_FLAG_INSTAGRAM = TASK_FLAG_MAP[getVariableValue("instagram")]
    TASK_FLAG_GRAMMAR = TASK_FLAG_MAP[getVariableValue("grammar")]
    TASK_FLAG_TRANSLATE = TASK_FLAG_MAP[getVariableValue("translate")]


async def executeDatabaseQuery(ctx, query, connection_type, send_file=False):
    try:
        result = executeQueryString(query, connection_type)
        if result:
            formatted_result = str()
            for row in result:
                row = list(map(str, row))
                row = ','.join(row)
                formatted_result += f"{row}\n"
            formatted_result = formatted_result.strip()
            if send_file:
                with open("db_query_result.csv", "w") as f:
                    f.write(formatted_result)
                await ctx.send(file=discord.File("db_query_result.csv"))
                os.remove("db_query_result.csv")
            else:
                await ctx.send(f"```csv\n{formatted_result}```")
        else:
            await ctx.send("No results returned.")
    except Exception as error_message:
        await ctx.send(f"Query failed: {error_message}")


async def syncFacultyInformation():
    print("Syncing faculty info...")
    readDataFrame()
    initialiseFacultyFilters()


async def syncCalendarInformation():
    print("Syncing calendar info...")
    loadPESUCalendar()


async def syncAPICallLimits():
    global compiler_keys
    for client_id, client_secret in compiler_keys.keys():
        compiler_keys[(client_id, client_secret)] = await updateCodeAPICallLimits(client_id, client_secret)


@client.event
async def on_ready():
    '''
    Initialising bot after boot
    '''
    print("Bot is online")
    await client.change_presence(activity=discord.Game(next(status)))

    if not DEBUG_MODE:
        await syncGuildDatabase()
        await syncTaskStatusDatabase()
        await syncFacultyInformation()
        await syncCalendarInformation()
        await setRuntimeEnvironment()
        await syncAPICallLimits()

        if not checkNewDay.is_running():
            checkNewDay.start()

        if not changeStatus.is_running():
            changeStatus.start()

        if not checkRedditPost.is_running():
            checkRedditPost.start()

        if not checkInstagramPost.is_running():
            checkInstagramPost.start()

        if not checkPESUAnnouncement.is_running():
            checkPESUAnnouncement.start()


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
        await server_owner.send("Thank you for adding the PESU Academy bot to your server! run `pes.alerts {CHANNEL NAME}` to setup the bot.\n You can optionally also setup a logging channel using `pes.log {CHANNEL NAME}`\nIf you have any queries, please visit https://github.com/HackerSpace-PESU/pesu-academy-bot")
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
    elif ctx.guild == None and ctx.content[:4].lower() != "pes.":
        bot_log_channel = client.get_channel(CHANNEL_BOT_LOGS)
        if ctx.reference == None:
            content = f'''{ctx.author.mention} sent a message on DM:\n
Message URL: {ctx.jump_url}
Message: {ctx.content}'''
        else:
            parent_message_id = ctx.reference.message_id
            parent_message_channel_id = ctx.reference.channel_id
            channel = await client.fetch_channel(parent_message_channel_id)
            parent_message = await channel.fetch_message(parent_message_id)
            parent_message_content = parent_message.content
            parent_message_url = parent_message.jump_url
            content = f'''{ctx.author.mention} replied to a message on DM\n
Original Message URL: {parent_message_url}
Original Message: {parent_message_content}\n
Reply URL: {ctx.jump_url}
Reply: {ctx.content}'''
        await bot_log_channel.send(content)
    elif client.user.mentioned_in(ctx) and "@everyone" not in ctx.content and "@here" not in ctx.content and ctx.reference == None:
        greeting = random.choice(greetings)[:-1]
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="PESU Academy Bot",
            description=f"{ctx.author.mention} don't be a {greeting} by pinging the bot. Type `pes.help` to access commands."
        )
        await ctx.channel.send(f"{ctx.author.mention}", embed=embed)
    else:
        if "pride" in ctx.content.lower() and ctx.content[:9] != "pes.pride":
            await ctx.reply("Invoking the PRIDE of PESU!", mention_author=False)
            await ctx.channel.send("https://media.discordapp.net/attachments/742995787700502565/834782280236662827/Sequence_01_1.gif")
        await client.process_commands(ctx)

    if not ctx.author.bot and ctx.content[:4].lower() != "pes.":

        cleaned_content = re.sub(r"(:[A-Za-z0-9]*:)", "", ctx.content).strip()
        if TASK_FLAG_GRAMMAR:
            corrected_message = await correctGrammar(ctx.content)
            if corrected_message != ctx.content:
                embed = discord.Embed(
                    color=discord.Color.blue(),
                    title="PESU Academy Bot - Incorrect Grammar Usage",
                    description=f"**Correct Usage**: {corrected_message}"
                )
                await ctx.reply(embed=embed)

        if cleaned_content and TASK_FLAG_TRANSLATE:
            translated_message = await translateText(cleaned_content)
            if translated_message != cleaned_content:
                embed = discord.Embed(
                    color=discord.Color.blue(),
                    title="PESU Academy Bot - Translator",
                    description=f"**Translation**: {translated_message}"
                )
                await ctx.reply(embed=embed)


@client.event
async def on_message_edit(message_before, message_after):
    edited_content = message_after.content
    if "pride" in edited_content.lower():
        await message_before.reply("You cannot escape the PRIDE of PESU!", mention_author=False)
        await message_after.channel.send("https://media.discordapp.net/attachments/742995787700502565/834782280236662827/Sequence_01_1.gif")


if not DEBUG_MODE:
    @client.event
    async def on_command_error(ctx, error):
        author = ctx.message.author
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="PESU Academy Bot - Command Error Log",
        )
        if ctx.guild != None:
            guild_id = str(ctx.guild.id)
            guild_logging_channels = getChannelFromServer(guild_id, "log")
            if guild_logging_channels:
                guild_logging_channels = [row[-1]
                                          for row in guild_logging_channels]
                embed.description = f"{author.mention} made this error in {ctx.message.channel.mention}:\n{error}"
                await sendSpecificChannels(guild_logging_channels, embed=embed)
        else:
            embed.description = f"Error occured:\n{error}"
            await ctx.send(embed=embed)

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


@client.command(aliases=["ls"])
async def files(ctx):
    if await checkUserIsBotDev(ctx):
        present_files = '\n'.join(os.listdir())
        with open("files.txt", 'w') as f:
            f.write(present_files)
        await ctx.send(f"Files in directory:", file=discord.File("files.txt"))
        os.remove("files.txt")
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command(aliases=["cleanup", "wipe"])
async def clean(ctx):
    if await checkUserIsBotDev(ctx):
        await cleanUp()
        await ctx.send(f"Directory clean-up completed.")
        await files(ctx)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def remind(ctx):
    if await checkUserIsBotDev(ctx):
        await subscriptionReminder()
        await ctx.send("Subscription reminders have been delivered.")
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def syncstatus(ctx):
    if await checkUserIsBotDev(ctx):
        await syncTaskStatusDatabase()
        await ctx.send("Task Status sync completed.")
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def syncdb(ctx, sync_method="soft"):
    if await checkUserIsBotDev(ctx):
        db_records = getCompleteGuildDatabase()
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
async def gitpull(ctx):
    if RUNTIME_ENVIRONMENT == "OTHER" and await checkUserIsBotDev(ctx):
        sys.stdout.flush()
        await ctx.send("Pulling changes from repository..")
        p = subprocess.Popen(['sudo', 'git', 'pull'], stdout=subprocess.PIPE)
        for line in iter(p.stdout.readline, ''):
            if not line:
                break
            await ctx.send(str(line.rstrip(), 'utf-8', 'ignore'))
        sys.stdout.flush()
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def restart(ctx):
    if RUNTIME_ENVIRONMENT == "OTHER" and await checkUserIsBotDev(ctx):
        await ctx.send("Restarting bot...")
        os.system("bash start.sh")
        sys.exit(0)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def shutdown(ctx):
    if RUNTIME_ENVIRONMENT == "OTHER" and await checkUserIsBotDev(ctx):
        greeting = random.choice(greetings)
        await ctx.send(f"Goodbye {greeting}! 👋")
        sys.exit(0)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command(aliases=["fixpesdb"])
async def fixdb(ctx):
    if await checkUserIsBotDev(ctx):
        await ctx.send("Fixing PESU Academy database...")
        fixPESUDB()
        await ctx.send("Database fix completed. Restart is required to activate changes.")
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
        name="Github repository", value="https://github.com/HackerSpace-PESU/pesu-academy-bot", inline=False)
    embed.add_field(
        name='\u200b', value="If you wish to contribute to the bot, run these steps:", inline=False)
    rules = {
        1: "Fork this repository",
        2: "Create a new branch called `username-beta`",
        3: "Make your changes and create a pull request with the following information in the request message: `The functionality you wish to change/add | What did you change/add`. Remember to add a few screenshots of the feature working at your end",
        4: "Send a review request to `alfadelta10010`",
        5: "Wait for approval for reviewers. Your PR may be directly accepted or requested for further changes"
    }
    for rule in rules:
        embed.add_field(
            name='\u200b', value=f"{rule}: {rules[rule]}", inline=False)

    guild_object = client.get_guild(DEV_SERVER)
    aditeyabaral = guild_object.get_member(ADITEYABARAL_ID).mention
    # abaksy = guild_object.get_member(ARONYABAKSY_ID).mention  # F for retired member
    embed.add_field(
        name="Reviewers", value=f"`alfadelta10010` - {aditeyabaral}", inline=False)
    embed.add_field(
        name="Important", value="**Under no circumstances is anyone allowed to merge to the main branch.**", inline=False)
    embed.add_field(
        name="\u200b", value="You can send suggestions and feedback by raising an issue with [IMPROVEMENT] or [FEEDBACK] added to the title.")
    await ctx.send(embed=embed)


@client.command()
async def reachout(ctx, *, message: str = None):
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
            channel = client.get_channel(CHANNEL_BOT_LOGS)
            await channel.send(embed=embed)

    else:
        await ctx.send("You are not authorised to run this command. Only members with administrator permissions can run this command. Contact your server administrator or anyone with a role who has administrator privileges. You can always contact us on our GitHub page: https://github.com/HackerSpace-PESU/pesu-academy-bot")


@client.command()
async def reachreply(ctx, destination_channel_id: int = None, *, message: str = None):
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


@client.command(aliases=['guildscommand'])
async def guilds(ctx):
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
        db_records = getCompleteGuildDatabase()
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


@client.command(aliases=['announcecommand'])
async def announce(ctx, message_type=None, *, message: str = None):
    if await checkUserIsBotDev(ctx):
        if message == None:
            await ctx.send("Please enter a valid message.")
        elif message_type == None:
            await ctx.send("Please enter a valid message type.")
        else:
            await sendAllChannels(message_type=message_type, content=message)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command(aliases=['announceembedcommand'])
async def announceembed(ctx, message_type=None, *, message: str = None):
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
        if await checkUserHasManageServerPermission(ctx) or await checkUserIsBotDev(ctx):
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
        if await checkUserHasManageServerPermission(ctx) or await checkUserIsBotDev(ctx):
            channel_id = str(channel.id)
            guild_id = str(ctx.guild.id)
            if not checkServerChannelAndTypeExists(guild_id, channel_id, "publish"):
                await ctx.send(f"{channel.mention} is not subscribed to PESU Academy Bot alerts.")
            else:
                removeChannelWithType(channel_id, "publish")
                await ctx.send(f"**Success!** You will no longer receive PESU Academy Bot alerts on {channel.mention}.")

        else:
            await ctx.send("Looks like you do not have the `Manage Server` permission to run this command.")


@client.command()
async def logs(ctx, channel: discord.TextChannel = None):
    if channel == None:
        await ctx.send("Please mention the channel in which you would like to forward logging information.")
    else:
        if await checkUserHasManageServerPermission(ctx) or await checkUserIsBotDev(ctx):
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
async def removelogs(ctx, channel: discord.TextChannel = None):
    if channel == None:
        await ctx.send("Please mention the channel you would like to unsubscribe from logging.")
    else:
        if await checkUserHasManageServerPermission(ctx) or await checkUserIsBotDev(ctx):
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
        pattern = re.compile(r"^\d+")
    except ValueError:
        channel_id = int(channel[2:-1])
        pattern = re.compile(r"^<#\d+>")

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
    channel_id = int(parent_message_url_components[5])
    parent_message_id = int(parent_message_url_components[6])

    if await checkUserEchoReplyPermissions(ctx, channel_id):
        channel = await client.fetch_channel(channel_id)
        parent_message = await channel.fetch_message(parent_message_id)
        await parent_message.reply(content)
    else:
        await ctx.send(f"You are not authorised to run this command.")


@client.command()
async def dm(ctx, recipient=None, *, message=None):
    await client.wait_until_ready()
    pattern = re.compile(r"^<@!\d+>")
    if await checkUserIsBotDev(ctx):
        if message != None and recipient != None:
            if re.match(pattern, recipient):
                recipient = recipient[3:-1]
            recipient_id = int(recipient)
            recipient = await client.fetch_user(recipient_id)
            await sendDM(recipient, content=message)
        else:
            greeting = random.choice(greetings)[:-1]
            await ctx.send(f"{greeting.capitalize()}, enter a valid message and recipient")
    else:
        await ctx.send(f"You are not authorised to run this command.")


@client.command()
async def dma(ctx, recipient, *, message=None):
    await client.wait_until_ready()
    pattern = re.compile(r"^<@!\d+>")
    if await checkUserIsBotDev(ctx):
        if message != None and recipient != None:
            if re.match(pattern, recipient):
                recipient = recipient[3:-1]
            recipient_id = int(recipient)
            recipient = await client.fetch_user(recipient_id)
            await sendDM(recipient, content=message, mention=True)
        else:
            greeting = random.choice(greetings)[:-1]
            await ctx.send(f"{greeting.capitalize()}, enter a valid message and recipient")
    else:
        await ctx.send(f"You are not authorised to run this command.")


@client.command()
async def dmr(ctx, *, query=None):
    await client.wait_until_ready()
    if await checkUserIsBotDev(ctx):
        parent_message_url = query.split()[0]
        _, content = query.split(parent_message_url)
        parent_message_url_components = parent_message_url.split('/')
        channel_id = int(parent_message_url_components[5])
        parent_message_id = int(parent_message_url_components[6])
        channel = await client.fetch_channel(channel_id)
        parent_message = await channel.fetch_message(parent_message_id)
        await parent_message.reply(content)
    else:
        await ctx.send(f"You are not authorised to run this command.")


@client.command(aliases=["vc", "prideofpesu"])
async def pride(ctx):
    greeting = random.choice(greetings)
    embed = discord.Embed(
        title=f"{greeting}, may the PRIDE of PESU be with you!", color=discord.Color.blue())
    await ctx.send(embed=embed)
    await ctx.send("https://media.discordapp.net/attachments/742995787700502565/834782280236662827/Sequence_01_1.gif")


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
        '`pes.help`': 'Invoke this help command for assistance',
        '`pes.ping`': 'Perform a `ping` test',
        '`pes.alerts`': 'Setup a channel to receive alerts using `pes.alerts [CHANNEL]`',
        '`pes.removealerts`': 'Unsubscribe a channel from alerts using `pes.removealerts [CHANNEL]`',
        '`pes.logs`': 'Setup a channel to receive logging information using `pes.logs [CHANNEL]`',
        '`pes.removelogs`': 'Unsubscribe a channel from logging information using `pes.removelogs [CHANNEL]`',
        '`pes.invite`': 'Obtain the invite link for PESU Academy Bot',
        '`pes.contribute`': 'Learn how to contribute to PESU Academy Bot',
        '`pes.reachout`': 'Send a message to the developer team',
        '`pes.hallticket`': 'Obtain your hall ticket for an upcoming ESA using `pes.hallticket [SRN | PRN] [PASSWORD]. Remember to use this command in a private DM with the bot.`',
        '`pes.calendar`': 'Obtain the calendar for the upcoming semester using `pes.calendar help`',
        '`pes.search`': 'To search the PESU Class and Section Database, use `pes.search [SRN | email]`',
        '`pes.pesdb`': 'Search the Student PESU Database using `pes.pesdb [search 1] & [search 2]`. String together as many filters as needed. You can also use emails and names.',
        '`pes.news`': 'Fetch PESU Announcements using `pes.news [OPTIONAL=today] [OPTIONAL=N]`. Get today\'s announcements with `pes.news today`. Fetch all announcements using `pes.news`. Specify the number of news using `N`.',
        '`pes.faculty`': 'Search for faculty members using `pes.faculty [filter 1] [filter 2]`. Filters can be branches `[cse|ece|me]`, courses `[ds|daa|afll]` or campus `[rr|ec]`. You can even search using a name using `pes.faculty [NAME]`',
        '`pes.ig`': 'Fetch the last Instagram post from PESU Academy or search for an account using `pes.ig [USERNAME]`',
        '`pes.reddit`': 'Fetch the latest posts from r/PESU using `pes.reddit [NUMBER OF POSTS]` or search for a subreddit using `pes.reddit [SUBREDDIT] [NUMBER OF POSTS]`',
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
        '`pes.moss`': "Compute plagiarism in inline scripts using MOSS. Use `pes.moss [LANGUAGE] ```[SCRIPT 1]``` ```[SCRIPT 2]````",
        '`pes.fmoss`': "Compute plagiarism in files using MOSS. Upload files to channel and use `pes.fmoss [LANGUAGE]`",
        '`pes.spongebob`': 'Create a SpongeBob mocking meme. `pes.sb [top text] & [bottom-text]` or `pes.sb [bottom-text]`',
        '`pes.dictionary`': 'Search for the meaning of word using `pes.dict [word]`',
        '`pes.pride`': 'Invoke the PRIDE of PESU',
        '`pes.translate`': 'Translate text using `pes.translate [LANGUAGE CODE] [TEXT]`',
        '`pes.wordle`': 'Find today\'s WORDLE solution',
        '`pes.sgpa`': 'Calculate your SGPA. Type `pes.sgpa help` for more information',
        '`pes.cgpa`': 'Calculate your CGPA. Type `pes.cgpa help` for more information',
        '`pes.devhelp`': 'Get a list of commands available to bot developers'
    }
    embed = discord.Embed(title=f"Help",
                          color=discord.Color.blue())
    index = 1
    for cmd in content:
        embed.add_field(
            name=f"**{index}**", value='\t{} : {}'.format(cmd, content[cmd]), inline=False)
        index += 1
    await ctx.send(embed=embed)


@client.command(aliases=["dh"])
async def devhelp(ctx):
    content = {
        "`pes.remind`": "Send a reminder to servers that have not setup a publish channel",
        "`pes.syncstatus`": "Sync status flags for tasks",
        "`pes.syncdb`": "Sync database containing server information. Optional [DO NOT USE WITHOUT READING DOCS]: `pes.syncdb hard`",
        "`pes.fixdb`": "Fix database transaction error",
        "`pes.syncfaculty`": "Sync database containing faculty information by fetching from the repository",
        "`pes.gitpull`": "Performs a `git pull` and fetches new code from the repository",
        "`pes.restart`": "Performs a `git pull` and reboots the bot",
        "`pes.shutdown`": "Shuts the bot down",
        "`pes.taskmanager`": "Switch individual tasks on or off using `pes.taskmanager [FEATURE] [on|off]`",
        "`pes.taskstatus`": "View all tasks and their running status",
        "`pes.nohup`": "Fetch and display the error log file",
        "`pes.guilds`": "Fetch and display the servers to which the bot has been added",
        "`pes.dbinfo`": "Fetch and display the servers and their channels which have subscribed to the bot",
        "`pes.reachreply`": "Send a message to any channel from the Developer Team using `pes.reachreply [CHANNEL ID] [MESSAGE]`",
        "`pes.announce`": "Send an announcement message to all servers using `pes.announce [publish|log] [message]`",
        "`pes.announceembed`": "Send an announcement embed to all servers using `pes.announceembed [publish|log] [message]`",
        "`pes.echo`": "Send a message on any channel using `pes.echo [CHANNEL] [MESSAGE]`",
        "`pes.reply`": "Reply to a message on any channel using `pes.reply [ORIGINAL MESSAGE URL] [MESSAGE]`",
        "`pes.clear`": "Clear messages on a channel using `pes.clear [N]`",
        "`pes.files`": "Lists all the files in the current repository directory",
        "`pes.clean`": "Cleans up unnecessary and redundant files",
        "`pes.dbquery`": "Run an SQL query on the database using `pes.dbquery [DATABASE] [QUERY]`",
        "`pes.dbqueryfile`": "Run an SQL query on the database using `pes.dbquery [DATABASE] [QUERY]` and return the results in a file",
        "`pes.synccalendar`": "Sync the semester's calendar",
        "`pes.dmr`": "Reply to a message in DMs",
        "`pes.dm`": "Send a message in DMs",
        "`pes.dma`": "Send a message in DMs and ping the recipient",
    }
    embed = discord.Embed(title=f"Developer Help",
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


@client.command()
async def sgpa(ctx, *, args):
    args = args.strip()
    if args == "" or args == "help":
        await ctx.send("The argument format is: `pes.sgpa [CREDITS][GRADE] [CREDITS][GRADE ... (for each course)`\nExample: `pes.sgpa 4A 4B 3C` indicates A grade in a 4 credit course, B grade in a 4 credit course, and C grade in a 3 credit course.")
    else:
        args = args.split(" ")
        credit_grade_pairs = list()
        for arg in args:
            if len(arg) == 2:
                credit_grade_pairs.append([int(arg[0]), arg[1]])
            else:
                await ctx.send("Incorrect argument format. Type `pes.sgpa help` for more information.")
                return
        sgpa = await calculateSGPA(credit_grade_pairs)
        sgpa = round(sgpa, 2)
        embed = discord.Embed(
            title=f"PESU Academy Bot - SGPA",
            color=discord.Color.blue(),
            description=f"Your SGPA is: **{sgpa}**"
        )
        await ctx.send(embed=embed)


@client.command()
async def cgpa(ctx, *, args):
    args = args.strip()
    if args == "" or args == "help":
        await ctx.send("The argument format is: `pes.cgpa [CREDITS IN SEMESTER],[SGPA] [CREDITS IN SEMESTER],[SGPA] ... (for each semester)`\nExample: `pes.cgpa 24,8.0 24,8.2` indicates 24 credits in the first semester and 8.0 SGPA, 24 credits in the second semester and and 8.2 SGPA.")
    else:
        args = args.split(" ")
        credits_sgpa_pairs = list()
        for arg in args:
            arg = arg.split(",")
            if len(arg) == 2:
                credits_sgpa_pairs.append([float(arg[0]), float(arg[1])])
            else:
                await ctx.send("Incorrect argument format. Type `pes.cgpa help` for more information.")
                return
        cgpa = await calculateCGPA(credits_sgpa_pairs)
        cgpa = round(cgpa, 2)
        embed = discord.Embed(
            title=f"PESU Academy Bot - CGPA",
            color=discord.Color.blue(),
            description=f"Your CGPA is: **{cgpa}**"
        )
        await ctx.send(embed=embed)


@client.command(aliases=["searchsrn", "searchpes"])
async def search(ctx, query):
    driver = await getChromedriver()
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

"""
@client.command()
async def pesdb(ctx, *, query):
    result, truncated, base_url = await getPESUDBResults(query)
    if not result:
        embed = discord.Embed(title=f"Search Results",
                              color=discord.Color.blue(),
                              description="No results found")
        await ctx.send(embed=embed)
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
"""

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


@client.command(aliases=["redirector"])
async def goto(ctx, long_url, short_url):
    response = await shortenLinkRedirector(short_url, long_url)
    if response.status_code == 200:
        await ctx.send(f"{long_url} is now shortened to https://goto-link.herokuapp.com/{short_url}")
    else:
        await ctx.send("Failed to create redirected link.")


@client.command(aliases=["lr"])
async def longrip(ctx, long_url):
    driver = await getChromedriver()
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
                    code_output = result.output.strip()
                    if not checkSpamCode(code_output):
                        if len(code_output) > 4000:
                            with open("output.txt", 'w') as f:
                                f.write(code_output)
                            await ctx.reply(f"Script took {result.cpuTime} seconds to execute and consumed {result.memory} kilobyte(s)", file=discord.File("output.txt"))
                            os.remove("output.txt")
                        else:
                            await ctx.reply(f"```\n{code_output}```\nScript took {result.cpuTime} seconds to execute and consumed {result.memory} kilobyte(s)", mention_author=False)
                    else:
                        greeting = random.choice(greetings)[:-1]
                        await ctx.reply(f"Aye {greeting}, you may be smart but I am smarter. No pinging `@everyone` or `@here` with the bot.")

                except Exception as error:
                    await ctx.reply(f"**Error occured**: {error}\n\nUse `.code help` to learn how to use the service.")

            else:
                greeting = random.choice(greetings)[:-1]
                await ctx.reply(f"Aye {greeting}, you may be smart but I am smarter. No pinging `@everyone` or `@here` with the bot.")


async def getFacultyResultEmbed(result):
    embed = discord.Embed(
        title="Faculty Lookup",
        color=discord.Color.blue()
    )
    for row in result:
        name = row["NAME"]
        email = row["EMAIL"]
        department = row["DEPARTMENT"]
        campus = row["CAMPUS"]
        courses = ""
        if not isinstance(row["COURSE"], float):
            courses = row["COURSE"].replace(',', ', ')
        content = f'''**Name**: {name}
**Email**: {email}
**Department**: {department}
**Campus**: {campus} Campus
**Courses**: {courses}'''
        embed.add_field(
            name="\u200b",
            value=content,
            inline=True
        )
    return embed


@client.command()
async def faculty(ctx, *, query):
    queries = query.split()
    result = getFacultyResults(queries)
    truncated = False
    if result:
        num_results = len(result)
        if num_results > 10:
            truncated = True
            result = result[:10]
        embed = await getFacultyResultEmbed(result)
    else:
        embed = discord.Embed(
            title="Faculty Lookup",
            description="No results found",
            color=discord.Color.blue()
        )
    await ctx.send(embed=embed)
    if truncated:
        await ctx.send("To view more results, visit https://github.com/HackerSpace-PESU/pesu-academy-bot/blob/main/data/faculty.csv")


@client.command()
async def syncfaculty(ctx):
    if await checkUserIsBotDev(ctx):
        await syncFacultyInformation()
        await ctx.send("Faculty information has been synced")
    else:
        await ctx.send(f"You are not authorised to run this command.")


@client.command()
async def synccalendar(ctx):
    if await checkUserIsBotDev(ctx):
        await syncCalendarInformation()
        await ctx.send("Calendar information has been synced")
    else:
        await ctx.send(f"You are not authorised to run this command.")


async def getCalendarResultEmbed(result):
    embed = discord.Embed(
        title="Calendar",
        color=discord.Color.blue()
    )
    for row in result:
        day = row[0]
        events = '\n'.join(row[1])
        embed.add_field(
            name=datetime.datetime.strftime(day, "%d %b %Y"),
            value=events,
            inline=True
        )

    return embed


@client.command()
async def calendar(ctx, query, num_results=1):
    possible_arguments = ["LWD", "EWD", "H", "PTM", "ASD", "CCM",
                          "FASD", "FAM", "ISA", "week", "day", "month", "dd-mm-yyyy"]
    if query == "help":
        await ctx.send(f"`calendar` supports the following arguments: `{possible_arguments}`. Add a number after the argument to specify the number of results to return.\n\nExample: `.calendar LWD 3`")
    else:
        results = getCalendarResults(query, num_results)
        if results == "file":
            await ctx.send(file=discord.File("data/calendar.docx"))
        elif results == None:
            await ctx.send(f"Invalid search. Possible arguments are {possible_arguments}")
        elif not results:
            await ctx.send("No results found")
        else:
            embed = await getCalendarResultEmbed(results)
            await ctx.send(embed=embed)

"""
@client.command(aliases=["admitcard", "ht"])
async def hallticket(ctx, srn=None, password=None):
    if ctx.guild == None or await checkUserIsBotDev(ctx):
        if srn == None or password == None:
            await ctx.send(f"Please enter a valid SRN/PRN and password.")
        else:
            srn = srn.upper()
            result, _, _ = await getPESUDBResults(srn)
            if not result:
                await ctx.send("Invalid SRN/PRN. Please verify your credentials and try again.")
            else:
                prn = result[0][1]
                name = result[0][2]
                await ctx.send(f"Looking for {name}'s hall ticket...")
                driver = await getChromedriver(experimental=True)
                try:
                    await getPESUHallTicket(driver, srn, password)
                    filename = f"AdmitCard_{prn}.pdf"
                    if filename in os.listdir():
                        await ctx.send(file=discord.File(filename))
                        os.remove(filename)
                    else:
                        await ctx.send(f"Hall ticket not found,\nYour hall ticket may not have been generated yet. Please try again later.")
                except Exception:
                    await ctx.send(f'''Error while accessing hall ticket: Please verify your credentials or try again later.''')
                driver.quit()
    else:
        await ctx.send("This command requires access to sensitive data. Please use this command in a DM with the bot.")
"""

@client.command(aliases=["mossfile", "moss-file"])
async def fmoss(ctx, language=None, *filenames):
    supported_languages = {
        "c": ".c",
        "cc": ".cc",
        "java": ".java",
        "ml": ".ml",
        "pascal": ".pas",
        "ada": ".ada",
        "lisp": ".lisp",
        "scheme": ".scm",
        "haskell": ".hs",
        "fortran": ".f",
        "ascii": ".txt",
        "vhdl": ".vhdl",
        "verilog": ".v",
        "perl": ".pl",
        "matlab": ".m",
        "python": ".py",
        "mips": ".s",
        "prolog": ".pl",
        "spice": ".sp",
        "vb": ".vb",
        "csharp": ".cs",
        "modula2": ".mod",
        "a8086": ".asm",
        "javascript": ".js",
        "plsql": ".plsql",
    }
    if language == None or language not in list(supported_languages.keys()):
        await ctx.send(f"Please enter a valid language. Supported languages are: ```{supported_languages}```")
    else:
        file_extension = supported_languages[language]
        all_attachments = list()
        async for message in ctx.history(limit=100):
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.filename.endswith(file_extension):
                        with open(attachment.filename, "wb") as f:
                            await attachment.save(f)
                        all_attachments.append(attachment.filename)

        if filenames:
            all_attachments = [
                fname for fname in all_attachments if fname in filenames]

        await ctx.send(f"Calculating plagiarism in {len(all_attachments)} files...")
        try:
            url = await evaluatePlagiarismContent(MOSS_USER_ID, all_attachments, language)
            await ctx.send(f"Plagiarism Results: {url}")
        except ConnectionRefusedError:
            await ctx.send("Connection to MOSS API refused. Try again later.")

        for fname in all_attachments:
            try:
                os.remove(fname)
            except:
                pass


@client.command(aliases=['ts'])
async def translate(ctx, language=None, *, text=None):
    supported_language_codes = ['af', 'am', 'ar', 'auto', 'az', 'be', 'bg', 'bn', 'bs', 'ca', 'ceb', 'co', 'cs', 'cy', 'da', 'de', 'el', 'en', 'en-US', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'fy', 'ga', 'gd', 'gl', 'gu', 'ha', 'haw', 'hi', 'hmn', 'hr', 'ht', 'hu', 'hy', 'id', 'ig', 'is', 'it', 'iw', 'ja', 'jw', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky',
                                'la', 'lb', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'no', 'ny', 'or', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'rw', 'sd', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tk', 'tl', 'tr', 'tt', 'ug', 'uk', 'ur', 'uz', 'vi', 'xh', 'yi', 'yo', 'zh-CN', 'zh-TW', 'zu']
    if language not in supported_language_codes or language is None:
        await ctx.send(f"Please enter a valid language. Supported languages are: ```{supported_language_codes}```")
    elif text is None:
        await ctx.send(f"Please enter some text to translate.")
    else:
        translated_text = await translateText(text, language, optimise=False)
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="PESU Academy Bot - Translator",
            description=f"**Translation**: {translated_text}"
        )
        await ctx.reply(embed=embed, mention_author=False)


@client.command()
async def moss(ctx, language=None, *, script=None):
    supported_languages = {
        "c": ".c",
        "cc": ".cc",
        "java": ".java",
        "ml": ".ml",
        "pascal": ".pas",
        "ada": ".ada",
        "lisp": ".lisp",
        "scheme": ".scm",
        "haskell": ".hs",
        "fortran": ".f",
        "ascii": ".txt",
        "vhdl": ".vhdl",
        "verilog": ".v",
        "perl": ".pl",
        "matlab": ".m",
        "python": ".py",
        "python3": ".py",
        "mips": ".s",
        "prolog": ".pl",
        "spice": ".sp",
        "vb": ".vb",
        "csharp": ".cs",
        "modula2": ".mod",
        "a8086": ".asm",
        "javascript": ".js",
        "plsql": ".plsql",
    }
    if language == None or language not in list(supported_languages.keys()):
        await ctx.send(f"Please enter a valid language. Supported languages are: ```{supported_languages}```")
    else:
        source_codes = script.split("```")
        source_codes = [source.strip()
                        for source in source_codes if source.strip() != str()]
        filenames = list()
        for i in range(len(source_codes)):
            filename = f"moss_filename_{i+1}.{supported_languages[language]}"
            with open(filename, 'w') as f:
                f.write(source_codes[i])
                filenames.append(filename)

        await ctx.send(f"Calculating plagiarism in {len(filenames)} files...")
        try:
            url = await evaluatePlagiarismContent(MOSS_USER_ID, filenames, language)
            await ctx.send(f"Plagiarism Results: {url}")
        except ConnectionRefusedError:
            await ctx.send("Connection to MOSS API refused. Try again later.")

        for fname in filenames:
            try:
                os.remove(fname)
            except:
                pass


async def getRedditEmbed(post, subreddit="PESU"):
    embed = discord.Embed(title=f"Reddit Post from r/{subreddit}",
                          url=post["url"], color=0xff6314)
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
    embed.set_footer(text=datetime.datetime.now(IST))
    return embed


@client.command(aliases=["r"])
async def reddit(ctx, subreddit="PESU", n=5):
    if TASK_FLAG_REDDIT:
        reddit_posts = await getRedditPosts(subreddit, REDDIT_PERSONAL_USE_TOKEN, REDDIT_SECRET_TOKEN, REDDIT_USER_AGENT, n)
        if reddit_posts:
            for p in reddit_posts:
                embed = await getRedditEmbed(p, subreddit)
                await ctx.send(embed=embed)
        else:
            await ctx.send("No posts found. Please ensure that the subreddit exists and it is not NSFW.")
    else:
        await ctx.send("Reddit feature has been turned off. Please contact the bot devs to enable it and continue.")


async def getInstagramEmbed(username):
    html = getInstagramHTML(username)
    photo_time = getLastPhotoDate(html)
    embed_colour = next(instagram_embed_colours)
    post_embed = discord.Embed(
        title=f'Instagram Post from {username}', url=getPostLink(html), color=embed_colour)
    post_embed.set_image(url=getLastThumbnailURL(html))
    post_caption = getPhotoDescription(html)
    if post_caption != None:
        if len(post_caption) >= 1024:
            content_bodies = post_caption.split('\n')
            content_bodies = [c for c in content_bodies if c.strip() not in [
                "", " "]]
            for c in content_bodies:
                post_embed.add_field(name=f"\u200b", value=c, inline=False)
        else:
            post_embed.add_field(
                name="\u200b", value=post_caption, inline=False)
    post_time = datetime.datetime.fromtimestamp(photo_time).astimezone(IST)
    post_embed.set_footer(text=post_time)
    return post_embed, photo_time


@client.command(aliases=["insta", "igpost"])
async def ig(ctx, username="pesuniversity"):
    if TASK_FLAG_INSTAGRAM:
        post_embed, _ = await getInstagramEmbed(username)
        await ctx.send(embed=post_embed)
    else:
        await ctx.send("Instagram feature has been turned off. Please contact the bot devs to enable it and continue.")


@client.command()
async def syncnews(ctx):
    if await checkUserIsAdminOrBotDev(ctx):
        await ctx.send("Syncing news...")
        await checkPESUAnnouncement()
        await ctx.send("Done.")
    else:
        await ctx.send("You are not authorized to use this command.")


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

    embed.set_footer(text=datetime.datetime.now(IST))
    return embed


@client.command(aliases=["pesunews"])
async def news(ctx, *, query=None):
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
                announcement_title = announcement["header"]
                img_filename = f"announcement-img-{announcement_title}.png"
                with open(img_filename, 'wb') as f:
                    f.write(imgdata)
                with open(img_filename, 'rb') as f:
                    await ctx.send(file=discord.File(img_filename))

            attachment_files = list()
            if announcement["attachments"]:
                for fname in announcement["attachments"]:
                    fname = Path(fname).name
                    if fname in os.listdir():
                        attachment_files.append(fname)
                    else:
                        embed.add_field(
                            name=f"\u200b", value=fname, inline=False)
                        if fname.startswith("http"):
                            embed.url = fname

            await ctx.send(embed=embed)

            for attachment_file in attachment_files:
                with open(attachment_file, "rb") as f:
                    await ctx.send(file=discord.File(attachment_file))

    else:
        await ctx.send("No announcements available. Retry with another option or try again later.")


@client.command()
async def taskmanager(ctx, handle=None, mode=None):
    if await checkUserIsBotDev(ctx):
        allowed_handles = ["instagram", "reddit",
                           "pesu", "grammar", "translate"]
        allowed_modes = ["on", "off"]
        if handle == None or handle not in allowed_handles:
            await ctx.send(f"Please enter a valid handle. Allowed handles are: {allowed_handles}")
        elif mode == None or mode not in allowed_modes:
            await ctx.send(f"Please enter a valid mode. Allowed modes are: {allowed_modes}")
        else:
            updateVariableValue(handle, mode)
            await syncTaskStatusDatabase()

            mode = mode.upper()
            if handle == "pesu":
                handle = "PESU Announcement"
            else:
                handle = handle.capitalize()

            embed = discord.Embed(
                color=discord.Color.blue(),
                title="PESU Academy Bot - Message from Developer Team",
                description=f"The {handle} feature has been turned **{mode}**"
            )

            await ctx.send(f"The {handle} feature has been turned **{mode}**")
            await sendAllChannels(message_type="log", embed=embed)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def taskstatus(ctx):
    if await checkUserIsBotDev(ctx):
        await syncTaskStatusDatabase()
        pesu_status_value = getVariableValue("pesu").upper()
        reddit_status_value = getVariableValue("reddit").upper()
        instagram_status_value = getVariableValue("instagram").upper()
        grammar_status_value = getVariableValue("grammar").upper()
        translation_status_value = getVariableValue("translate").upper()
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="PESU Academy Bot - Task Status",
            description=f'''PESU Announcement Checks: **{pesu_status_value}**
Instagram Checks: **{instagram_status_value}**
Reddit Checks: **{reddit_status_value}**
Grammar Checks: **{grammar_status_value}**
Translator: **{translation_status_value}**'''
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def nohup(ctx, lines=None):
    if await checkUserIsBotDev(ctx) and RUNTIME_ENVIRONMENT == "OTHER":
        if "nohup.out" in os.listdir():
            with open("nohup.out") as nohup_out_file, open("nohup.txt", "w") as nohup_write_file:
                content = nohup_out_file.readlines()
                if lines != None:
                    try:
                        lines = int(lines)
                        await ctx.send(f"Viewing last {lines} lines...")
                        content = content[-lines:]
                    except ValueError:
                        pass
                nohup_write_file.writelines(content)
            await ctx.send(file=discord.File("nohup.txt"))
            os.remove("nohup.txt")
        else:
            await ctx.send("Logging file `nohup.out` not found.")
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command(aliases=["dbf", "dbqf"])
async def dbqueryfile(ctx, connection_type, *, query):
    if await checkUserIsBotDev(ctx):
        await executeDatabaseQuery(ctx, query, connection_type, True)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command(aliases=["db", "dbq"])
async def dbquery(ctx, connection_type, *, query):
    if await checkUserIsBotDev(ctx):
        await executeDatabaseQuery(ctx, query, connection_type, False)
    else:
        await ctx.send("You are not authorised to run this command.")


@client.command()
async def wordle(ctx):
    driver = await getChromedriver()
    wordle_answer = await solveWordle(driver)
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="PESU Academy Bot - Wordle",
        description=f"Today's Wordle is: ||**{wordle_answer}**||"
    )
    await ctx.send(embed=embed)


@tasks.loop(minutes=32)
async def checkInstagramPost():
    await client.wait_until_ready()
    if TASK_FLAG_INSTAGRAM:
        print("Fetching Instagram posts...")
        for username in instagram_usernames:
            try:
                post_embed, photo_time = await getInstagramEmbed(username)
                curr_time = time.time()
                if (curr_time - photo_time) <= 1920:
                    await sendAllChannels(message_type="publish", embed=post_embed)
            except Exception as error:
                print(
                    f"Error while fetching Instagram post from {username}: {error}")
            await asyncio.sleep(1.5)


@tasks.loop(minutes=55)
async def checkRedditPost():
    await client.wait_until_ready()
    if TASK_FLAG_REDDIT:
        print("Fetching Reddit posts...")
        reddit_posts = await getRedditPosts("PESU", REDDIT_PERSONAL_USE_TOKEN, REDDIT_SECRET_TOKEN, REDDIT_USER_AGENT)
        if reddit_posts:
            latest_reddit_post = reddit_posts[0]
            post_time = latest_reddit_post["create_time"]
            current_time = datetime.datetime.now()
            time_difference = current_time - post_time
            if time_difference.seconds <= 3300 and time_difference.days == 0:
                post_embed = await getRedditEmbed(latest_reddit_post)
                await sendAllChannels(message_type="publish", embed=post_embed)


@tasks.loop(minutes=10)
async def checkPESUAnnouncement():
    global TODAY_ANNOUNCEMENTS_MADE
    global ALL_ANNOUNCEMENTS_MADE
    await client.wait_until_ready()

    if TASK_FLAG_PESU:
        print("Fetching announcements...")
        driver = await getChromedriver()
        all_announcements = await getPESUAnnouncements(driver, PESU_SRN, PESU_PWD)

        new_announcement_count = 0
        for a in all_announcements:
            if a not in ALL_ANNOUNCEMENTS_MADE:
                ALL_ANNOUNCEMENTS_MADE.append(a)
                new_announcement_count += 1

        print(f"NEW announcements found: {new_announcement_count}")

        ALL_ANNOUNCEMENTS_MADE.sort(key=lambda x: x["date"], reverse=True)
        current_date = datetime.datetime.now().date()
        db_records = getCompleteGuildDatabase()
        for announcement in all_announcements:
            if announcement["date"] == current_date:
                if announcement not in TODAY_ANNOUNCEMENTS_MADE:
                    embed = await getAnnouncementEmbed(announcement)

                    img_filename = None
                    if announcement["img"] != None:
                        img_base64 = announcement["img"].strip()[22:]
                        img_data = base64.b64decode(img_base64)
                        announcement_title = announcement["header"]
                        img_filename = f"announcement-img-{announcement_title}.png"
                        with open(img_filename, 'wb') as f:
                            f.write(img_data)

                    attachment_files = list()
                    if announcement["attachments"]:
                        for fname in announcement["attachments"]:
                            fname = Path(fname).name
                            if fname in os.listdir():
                                attachment_files.append(fname)
                            else:
                                print(f"Could not find attachment: {fname}")
                                embed.add_field(
                                    name=f"\u200b",
                                    value=fname,
                                    inline=False
                                )
                                if fname.startswith("http"):
                                    embed.url = fname

                    for row in db_records:
                        guild_id, _, channel_type, channel_id = row[1:]
                        if channel_id == None:
                            continue
                        guild_id = int(guild_id)
                        channel_id = int(channel_id)
                        if channel_type == "publish":
                            try:
                                channel = client.get_channel(channel_id)

                                if img_filename != None:
                                    with open(img_filename, "rb") as f:
                                        await channel.send(file=discord.File(img_filename))

                                await channel.send("@everyone", embed=embed)

                                for attachment_file in attachment_files:
                                    with open(attachment_file, "rb") as f:
                                        await channel.send(file=discord.File(attachment_file))

                            except Exception as error:
                                print(
                                    f"Error sending message to channel {channel_id}: {error}")

                    TODAY_ANNOUNCEMENTS_MADE.append(announcement)
        driver.quit()


@tasks.loop(minutes=35)
async def checkNewDay():
    global TODAY_ANNOUNCEMENTS_MADE
    global ALL_ANNOUNCEMENTS_MADE
    await client.wait_until_ready()

    current_time = datetime.datetime.now(IST)
    if current_time.hour == 0:
        TODAY_ANNOUNCEMENTS_MADE = list()
        ALL_ANNOUNCEMENTS_MADE = list()
        await cleanUp()
        await subscriptionReminder()


@tasks.loop(hours=5)
async def changeStatus():
    '''
    Changes the status of the PESU Academy bot every 5 hours.
    '''
    await client.wait_until_ready()
    await client.change_presence(activity=discord.Game(next(status)))


client.run(BOT_TOKEN)
