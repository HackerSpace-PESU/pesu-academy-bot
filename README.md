# PESU Academy Bot

<p align="center">
    <a href="https://github.com/HackerSpace-PESU/pesu-academy-bot/issues" alt="issues">
    <img alt="GitHub forks" src="https://img.shields.io/github/issues/HackerSpace-PESU/pesu-academy-bot"></a>
    <a href="https://github.com/HackerSpace-PESU/pesu-academy-bot/stargazers" alt="Stars">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/HackerSpace-PESU/pesu-academy-bot"></a>
    <a href="https://github.com/HackerSpace-PESU/pesu-academy-bot/contributors" alt="Contributors">
    <img src="https://img.shields.io/github/contributors/HackerSpace-PESU/pesu-academy-bot"/></a>
</p>

PESU Academy Discord Bot built for PESsants and PESts of PES University

You can add the bot to your Discord Server using [this link](http://bit.ly/pesu-academy-bot). Once the bot has joined your server, please carry out the setup instructions posted by the bot.

## What can PESU Academy Bot do?

1. It periodically fetches PESU announcements and notifies you immediately (thus eliminating any reason to open PESU Academy)
2. It is connected to a student database, and allows you to perform a query based lookup to search
3. It updates you about Instagram posts made by clubs
4. It also follows PES social media handles - Instagram and Reddit
4. It contains two URL shortners - [long.rip](http://www.long.rip/) by [Adarsh Shetty](https://github.com/ObliviousParadigm) and [redirector](https://github.com/HackerSpace-PESU/redirector) by [Aditeya Baral](https://github.com/aditeyabaral)
5. You can also execute Python code!
6. It features a meme-generator - [SaaS](https://github.com/aditeyabaral/spongebob-as-a-service) and an [English Dictionary](https://github.com/aditeyabaral/pydictionary)

...and more.

Execute `pes.help` after adding the bot to your server to check out all the features.
## How to run PESU Academy Bot?

### Docker

PESU Academy Bot's environment has now been containerized to make running the bot easy. To run the bot now, all you need is the `.env` file. There are two ways to go about this:

1. Build the Docker image from scratch and run it (easy)

    - Set your environment variables in the `.env` file
    - Set your git username and email address in the `.env` file
    - Build and deploy:
    ```bash
    docker build -t pesu-academy-bot -f docker/Dockerfile .
    docker run -d pesu-academy-bot
    ```

2. Pulling a pre-built Docker image (difficult)

    - Pull the latest Docker image from DockerHub and access the filesystem
    ```bash
    docker pull aditeyabaral/pesu-academy-bot-env
    docker run -it aditeyabaral/pesu-academy-bot-env bash
    vi .env
    ```
    - This will open a Vim editor. Now, paste the contents of the `.env` file and close it. Type `exit` to quit the image. 
    - Type `docker ps -a` to see the container. Copy the container ID, and then run `docker commit CONTAINER_ID aditeyabaral/pesu-academy-bot-env` to commit the container
    - Run the container with the following commands (can also be done using Docker Desktop's CLI):
    ```bash
    docker run -it aditeyabaral/pesu-academy-bot-env bash
    python3 src/bot.py
    ```

### Python Environment

1. Clone the repository
```bash
git clone git@github.com:aditeyabaral/pesu-academy-bot.git
```

2. Create a separate virtual environment and install the dependencies. You can use virtualenv -- simple to setup and use.
```bash
cd pesu-academy-bot
virtualenv bot
source bot/bin/activate
pip3 install -r requirements.txt
```

3. Setup the `.env_template` file and rename it to `.env`

```bash
ARONYA_ID=
BARAL_ID=
CHANNEL_BOT_LOGS=
BOT_ID=
BOT_TOKEN=
BOT_INVITE="https://discord.com/api/oauth2/authorize?client_id=847138055978614845&permissions=2148006976&scope=bot%20applications.commands"
BOT_GITHUB="https://github.com/HackerSpace-PESU/pesu-academy-bot"
CHROMEDRIVER_PATH=
GOOGLE_CHROME_BIN=
PESU_DATABASE_URL=
SERVER_CHANNEL_DATABASE_URL=
PESU_SRN=
PESU_PWD=
REDDIT_SECRET_TOKEN=
REDDIT_PERSONAL_USE_TOKEN=
REDDIT_USER_AGENT=
```

4. Run the bot using the following command
```bash
python3 src/bot.py
```

## How to contribute to PESU Academy Bot?

1. Fork this repository
​
2. Create a new branch called `username-beta`
​
3. Make your changes and create a pull request with the following information in the request message: 
    - The functionality you wish to change/add | What did you change/add
    - Screenshots of the feature working at your end
​
4. Send a review request to `aditeyabaral` or `abaksy`
​
5. Wait for approval for reviewers. Your PR may be directly accepted or requested for further changes

**Important**: Under no circumstances is anyone allowed to merge to the main branch.

## Maintainers

Contact any of us for any support.

[Aditeya Baral](https://github.com/aditeyabaral)<br>
[Aronya Baksy](https://github.com/abaksy)

