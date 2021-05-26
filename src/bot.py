import re
import os
import sys
import time
import random
import base64
import asyncio
import signal
from io import StringIO
import contextlib
from itertools import cycle
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
import discord
from discord.ext import commands, tasks
from utils import *


load_dotenv()
client = commands.Bot(command_prefix='pes.', help_command=None)
status = cycle(["with the PRIDE of PESU", "with lives",
               "with your future", "with PESsants", "with PESts"])

BOT_TOKEN = os.environ["BOT_TOKEN"]

CHANNEL_BOT_LOGS = None
CHANNEL_PESU_ANNOUNCEMENT = None

ARONYABAKSY_ID = int(os.environ["ARONYA_ID"])
ADITEYABARAL_ID = int(os.environ["BARAL_ID"])
BOT_DEVS = [ARONYABAKSY_ID, ADITEYABARAL_ID]

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

TODAY_ANNOUNCEMENTS_MADE = list()
ALL_ANNOUNCEMENTS_MADE = list()
greetings_1 = ["PESsants", "PESts"]
greetings_2 = ["PESsant", "PESt"]


async def checkUserIsAdminOrBotDev(ctx):
    '''
    Checks if the message author is an Admin or is one of the Bot Developers.
    '''
    return ctx.message.author.guild_permissions.administrator or ctx.message.author.id in BOT_DEVS

async def checkUserIsBotDev(ctx):
    '''
    Checks if the message author is one of the Bot Developers.
    '''
    return ctx.message.author.id in BOT_DEVS


@tasks.loop(hours=4)
async def changeStatus():
    '''
    Changes the status of the PESU Academy bot every 4 hours.
    '''
    await client.wait_until_ready()
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_ready():
    '''
    Initialising bot after boot
    '''
    await client.change_presence(activity=discord.Game(next(status)))

    if CHANNEL_BOT_LOGS is not None:
        channel = client.get_channel(id=CHANNEL_BOT_LOGS)
        greeting = random.choice(greetings_1)
        embed = discord.Embed(title=f"{greeting}, PESU Academy Bot is online",
                              description="Use `pes.` to access commands", color=0x03f8fc)
        await channel.send(embed=embed)


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
        value="Thank you for adding the bot to your server! Use `.help` to view all supported commands.\n"
    )

    alert_embed = discord.Embed(
        color=discord.Color.blue(),
        title="PESU Academy Bot - IMPORTANT",
    )
    alert_embed.add_field(
        name="\u200b",
        value="Members with the `Manage Server` permissions are requested to run `pes.alerts {CHANNEL NAME}` to setup the bot.\n You can optionally also setup a logging channel using `pes.log {CHANNEL NAME}`"
    )

    for channel in guild.text_channels:
        if channel.permission_for(guild.me).send_messages:
            await channel.send(embed=embed)
            await channel.send(embed=alert_embed)
            break

    server_owner = guild.owner
    try:
        await server_owner.send("Thank you for adding the PESU Academy bot to your server! run `pes.alerts {CHANNEL NAME}` to setup the bot.\n You can optionally also setup a logging channel using `pes.log {CHANNEL NAME}`\nIf you have any queries, please visit https://github.com/aditeyabaral/pesu-academy-bot")
    except:
        pass


@client.event
async def on_message(ctx):
    if ctx.author.bot:
        pass
    elif client.user.mentioned_in(ctx):
        if "@everyone" not in ctx.content and "@here" not in ctx.content and ctx.reference == None:
            greeting = random.choice(greetings_2)
            await ctx.channel.send(f"{ctx.author.mention} don't ping the bot da {greeting}")
        else:
            await client.process_commands(ctx)
    else:
        await client.process_commands(ctx)


@client.event
async def on_command_error(ctx, error):
    author = ctx.message.author
    if CHANNEL_BOT_LOGS is not None:
        channel = client.get_channel(CHANNEL_BOT_LOGS)
        await channel.send(
            f"{author.mention} made this error in {ctx.message.channel.mention}:\n{error}")
    content = f"Aye nakkan {author.mention}\nType `pes.help` if you do not know how to use the bot."
    await ctx.send(content)


@client.command()
async def echo(ctx, *, query=None):
    await client.wait_until_ready()
    if await checkUserIsAdminOrBotDev(ctx):
        channel = query.split()[0]
        pattern = re.compile(r"^<#\d+>")
        _, content = re.split(pattern, query)
        content = content.strip()
        channel = client.get_channel(int(channel[2:-1]))
        await channel.send(content)
    else:
        author = ctx.message.author
        greeting = random.choice(greetings_2)
        await ctx.send(f"Aye {author.mention}, you don't have permission to do that da {greeting}")


@client.command()
async def reply(ctx, *, query=None):
    await client.wait_until_ready()
    if await checkUserIsAdminOrBotDev(ctx):
        parent_message_url = query.split()[0]
        _, content = query.split(parent_message_url)
        parent_message_url_components = parent_message_url.split('/')
        server_id = int(parent_message_url_components[4])
        channel_id = int(parent_message_url_components[5])
        parent_message_id = int(parent_message_url_components[6])
        server = client.get_guild(server_id)
        channel = server.get_channel(channel_id)
        parent_message = await channel.fetch_message(parent_message_id)
        await parent_message.reply(content)
    else:
        author = ctx.message.author
        greeting = random.choice(greetings_2)
        await ctx.send(f"Aye {author.mention}, you don't have permission to do that da {greeting}")


@client.command(aliases=["vc", "pride"])
async def prideofpesu(ctx):
    greeting = random.choice(greetings_1)
    embed = discord.Embed(
        title=f"{greeting}, may the PRIDE of PESU be with you!", color=0x03f8fc)
    await ctx.send(embed=embed)
    await ctx.send("https://tenor.com/view/pes-pesuniversity-pesu-may-the-pride-of-pes-may-the-pride-of-pes-be-with-you-gif-21274060")


@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000, 2)} ms")


@client.command(aliases=["h"])
async def help(ctx):
    content = '''
1. `.hello`: Be nice to me. Say `.hello` once in a while 👋
2. `.search`: To search the Class and Section Database, use `.search [SRN | email]`
3. `.pesdb`: Search in the PESU Database using `.pesdb [search 1] & [search 2]`. String together as many filters as needed. You can also use emails and names.
4. `.news`: Fetch PESU Announcements using `.news [OPTIONAL=today] [OPTIONAL=N]`. Get today's announcements with `.news today`. Fetch all announcements using `.news`. Specify the number of news using `N`.
5. `.bitly`: Create a shortened bitly link using `.bitly [LONG URL]`
6. `.longrip`: Create a shortened long.rip link using `.longrip [URL]`
7. `.goto`: Create customized redirection links using `.goto [LONG URL] [SHORT URL]`
8. `.exec`: Use this to execute Python scripts. Attach your script within blockquotes on the next line. 
   **Example**: 
   .exec
```Python
import math
print(math.pi)```
9. `.insta`: Fetch the last Instagram post from PESU Academy
10. `.reddit`: Fetch the latest posts from r/PESU using `.reddit [NUMBER OF POSTS]`
11. `.sim`: Find similarity between uploaded files using Doc2Vec. Upload files into a channel and use `.sim [FILENAMES]`. 
12. `.eval`: Evaluate a single Python expression using `.eval [EXPRESSION]`
13. `.flames`: To calculate FLAMES scores for your ladies use `.flames [name 1] [name 2]`
14. `.spongebob` or `.sb`: Create a SpongeBob mocking meme. `.sb [top text] & [bottom-text]` or `.sb [bottom-text]`
15. `.8b`: Ask a question and receive an answer using `.8b [question]`
16. `.dict`: Search for the meaning of word using `.dict [word]`
17. `.ping`: Perform a `ping` test'''
    await ctx.send(content)


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
        author = ctx.message.author
        greeting = random.choice(greetings_2)
        await ctx.send(f"Aye {author.mention}, you don't have permission to do that da {greeting}")


@client.command(aliases=["searchsrn", "searchpes"])
async def search(ctx, query):
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    result = await searchPESUAcademy(driver, query)
    if result == None:
        author = ctx.message.author
        await ctx.send(f"Aye nakkan {author.mention}, don't make me search for imaginary people.")
    else:
        embed = discord.Embed(title=f"Search Results",
                              color=0x03f8fc)
        for prn, srn, name, semester, section, cycle, department, branch, campus in result:
            embed.add_field(name=f"**{name}**", value=f'''**PRN**: {prn}
**SRN**: {srn}
**Semester**: {semester}
**Section**: {section}
**Cycle**: {cycle}
**Department**: {department}
**Branch**: {branch}
**Campus**: {campus}''')
        await ctx.send(embed=embed)
    driver.quit()


@client.command()
async def pesdb(ctx, *, query):
    result, truncated, base_url = await getPESUDBResults(query)
    if result == None:
        author = ctx.message.author
        await ctx.send(f"Aye nakkan {author.mention}, don't make me search for imaginary people.")
    else:
        embed = discord.Embed(title=f"Search Results",
                              color=0x03f8fc)
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
**E-Mail**: {email}''')
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
    author = ctx.message.author
    flag, result = await getDictionaryMeaning(query, n)
    if flag:
        meanings, antonyms = result
        embed = discord.Embed(title=f"Search Results",
                              color=0x03f8fc)
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
            await ctx.send(f"Aye nakkan {author.mention}, your spelling is so bad that I don't even know what to suggest")
        else:
            await ctx.send(f"Word not found. Did you mean {result}?")


'''@client.command()
async def bitly(ctx, long_url):
    short_url, response = await shortenLinkBitly(long_url, BITLY_TOKEN, BITLY_GUID)
    if response.status_code == 201:
        await ctx.send(f"{long_url} is now shortened to {short_url}")
    else:
        await ctx.send("Failed to create bitly link.")'''


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


def handler(signum, frame):
    print("Code took too long - terminating script")
    raise Exception("Time limit exceeded")


signal.signal(signal.SIGALRM, handler)


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


@client.command(aliases=["exec"])
async def execute(ctx, *, code):
    code = '\n'.join(code.split('\n')[1:-1])
    check_malicious_code_flag = await checkMaliciousCode(code)
    if not check_malicious_code_flag:
        with stdoutIO() as sio:
            signal.alarm(5)
            try:
                exec(code)
                try:
                    await ctx.reply(sio.getvalue(), mention_author=False)
                except:
                    await ctx.reply("No output generated.", mention_author=False)
            except Exception as e:
                await ctx.reply(f"**{e}**: Execution halted.", mention_author=True)
            signal.alarm(0)
    else:
        greeting = random.choice(greetings_2)
        await ctx.reply(f"Aye {greeting}, what are you trying to do?\nUsage of `os` and `subprocess` is not allowed.", mention_author=True)
        if CHANNEL_BOT_LOGS is not None:
            channel = client.get_channel(CHANNEL_BOT_LOGS)
            author = ctx.message.author
            await channel.send(f"{author.mention} tried executing this bad script on {ctx.message.channel.mention}:\n```Python\n{code}```")


@client.command(aliases=["eval"])
async def evaluate(ctx, *, code):
    check_malicious_code_flag = await checkMaliciousCode(code)
    if not check_malicious_code_flag:
        signal.alarm(5)
        try:
            x = eval(code)
            await ctx.reply(x, mention_author=False)
        except Exception as e:
            await ctx.reply(f"**{e}**: Execution halted.", mention_author=True)
        signal.alarm(0)
    else:
        greeting = random.choice(greetings_2)
        await ctx.reply(f"Aye {greeting}, what are you trying to do?\nUsage of `os` and `subprocess` is not allowed.", mention_author=True)
        if CHANNEL_BOT_LOGS is not None:
            channel = client.get_channel(CHANNEL_BOT_LOGS)
            author = ctx.message.author
            await channel.send(f"{author.mention} tried executing this bad script on {ctx.message.channel.mention}:\n```Python\n{code}```")


@client.command(aliases=["sim"])
async def similarity(ctx, *, filenames):
    filenames = filenames.split()
    all_attachments = list()
    async for message in ctx.history(limit=50):
        if message.attachments:
            async for attachment in message.attachments:
                with open(attachment.filename, "wb") as f:
                    await attachment.save(f)
                all_attachments.append(attachment.filename)

    flag = True
    async for fname in filenames:
        if fname not in all_attachments:
            flag = False
            await ctx.send(f"{fname} not found. Please reupload file and try again.")
            break

    if flag:
        result = await getDocumentSimilarity(filenames)
        result = [
            f"{doc1} -- {doc2}: **{round(sim*100, 2)}%**" for doc1, doc2, sim in result]
        string = "\n\n".join(result)
        embed = discord.Embed(
            title="Document Similarity Results", color=0x03f8fc, description=string)
        await ctx.send(embed=embed)


async def getRedditEmbed(post):
    embed = discord.Embed(title="New Reddit Post",
                          url=post["url"], color=0xff5700)
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
async def reddit(ctx, n=5):
    reddit_posts = await getRedditPosts(REDDIT_PERSONAL_USE_TOKEN, REDDIT_SECRET_TOKEN, REDDIT_USER_AGENT, n)
    for p in reddit_posts:
        embed = await getRedditEmbed(p)
        await ctx.send(embed=embed)


async def getInstagramEmbed(username):
    html = getInstagramHTML(username)
    photo_time = getLastPhotoDate(html)
    post_embed = discord.Embed(
        title=f'New Instagram Post', url=getPostLink(html), color=0x8a3ab9)
    if(checkVideo(html)):
        post_embed.set_image(url=getVideoURL(html))
    else:
        post_embed.set_image(url=getLastThumbnailURL(html))

    post_embed.add_field(name="\u200b", value=getPhotoDescription(html)[
                         :1000] + "... ", inline=False)
    post_embed.set_footer(text=datetime.fromtimestamp(photo_time))
    return post_embed, photo_time


@client.command()
async def insta(ctx):
    username = 'pesuniversity'
    post_embed, _ = await getInstagramEmbed(username)
    await ctx.channel.send(embed=post_embed)


async def getAnnouncementEmbed(announcement):
    title = announcement["header"]
    if len(title) > 256:
        embed = discord.Embed(title=title[:253] + "...", description="..." +
                              title[253:], color=0x03f8fc)
    else:
        embed = discord.Embed(
            title=title, color=0x03f8fc)

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

    print(f"Announcements TODAY: {len(TODAY_ANNOUNCEMENTS_MADE)}")
    print(f"Announcements ALL: {len(ALL_ANNOUNCEMENTS_MADE)}")

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


@tasks.loop(minutes=10)
async def checkInstagramPost():
    await client.wait_until_ready()
    print("Fetching Instagram posts...")

    username = 'pesuniversity'
    channel = client.get_channel(CHANNEL_PESU_ANNOUNCEMENT)
    post_embed, photo_time = await getInstagramEmbed(username)
    curr_time = time.time()
    if (curr_time - photo_time) < 600:
        await channel.send("@everyone", embed=post_embed)

'''
@tasks.loop(minutes=10)
async def checkRedditPost():
    await client.wait_until_ready()
    print("Fetching Reddit posts...")

    reddit_posts = await getRedditPosts(REDDIT_PERSONAL_USE_TOKEN, REDDIT_SECRET_TOKEN, REDDIT_USER_AGENT)
    latest_reddit_post = reddit_posts[0]
    post_time = latest_reddit_post["create_time"]
    current_time = datetime.now()
    print("Outside Loop")
    print(f"Last Reddit post time: {post_time}\nCurrent time: {current_time}")
    if (current_time - post_time).seconds < 600:
        print("Inside loop")
        print(f"Diff = {(current_time - post_time).seconds}")
        channel = client.get_channel(CHANNEL_PESU_ANNOUNCEMENT)
        post_embed = await getRedditEmbed(latest_reddit_post)
        # await channel.send("@everyone", embed=post_embed)
        await channel.send(embed=post_embed)

        log_channel = client.get_channel(CHANNEL_BOT_LOGS)
        await log_channel.send(f"Posting Reddit announcement\ncurrent = {current_time}\npost = {post_time}\ndiff = {(current_time - post_time).seconds}")
'''

@tasks.loop(minutes=5)
async def checkPESUAnnouncement():
    global TODAY_ANNOUNCEMENTS_MADE
    global ALL_ANNOUNCEMENTS_MADE
    await client.wait_until_ready()

    print("Fetching announcements...")
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    all_announcements = await getPESUAnnouncements(driver, PESU_SRN, PESU_PWD)
    print(f"Fetched announcements: {len(all_announcements)}")

    for a in all_announcements:
        if a not in ALL_ANNOUNCEMENTS_MADE:
            ALL_ANNOUNCEMENTS_MADE.append(a)
    print(f"All announcements found: {len(ALL_ANNOUNCEMENTS_MADE)}")
    ALL_ANNOUNCEMENTS_MADE.sort(key=lambda x: x["date"], reverse=True)

    current_date = datetime.now().date()
    channel = client.get_channel(CHANNEL_PESU_ANNOUNCEMENT)
    for announcement in all_announcements:
        if announcement["date"] == current_date:
            if announcement not in TODAY_ANNOUNCEMENTS_MADE:
                embed = await getAnnouncementEmbed(announcement)
                if announcement["img"] != None:
                    img_base64 = announcement["img"].strip()[22:]
                    imgdata = base64.b64decode(img_base64)
                    filename = "announcement-img.png"
                    with open(filename, 'wb') as f:
                        f.write(imgdata)
                    with open(filename, 'rb') as f:
                        img_file = discord.File(f)
                        await channel.send(file=img_file)

                await channel.send("@everyone", embed=embed)
                if announcement["attachments"]:
                    for fname in announcement["attachments"]:
                        attachment_file = discord.File(fname)
                        await channel.send(file=attachment_file)
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


checkNewDay.start()
# checkPESUAnnouncement.start()
checkInstagramPost.start()
# checkRedditPost.start()
changeStatus.start()
client.run(BOT_TOKEN)
