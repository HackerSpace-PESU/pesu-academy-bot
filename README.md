# PESU Academy Bot

<p align="center">
    <a href="https://github.com/HackerSpace-PESU/pesu-academy-bot" alt="Build status">
    <img src="https://github.com/HackerSpace-PESU/pesu-academy-bot/actions/workflows/node.js.yml/badge.svg"/></a>
    <a href="https://github.com/HackerSpace-PESU/pesu-academy-bot" alt="Stars">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/HackerSpace-PESU/pesu-academy-bot"></a>
</p>


## How to run PESU Academy Bot?

1. Clone the repository
```bash
git clone git@github.com:HackerSpace-PESU/pesu-academy-bot.git
```

2. Create a separate virtual environment and install the dependencies. You can use virtualenv -- simple to setup and use.
```bash
cd pesu-academy-bot
npm ci
```

3. Setup the following environment variables in a `.env`

```bash
BOT_TOKEN=
BOT_INVITE="https://discord.com/api/oauth2/authorize?client_id=847138055978614845&permissions=2148006976&scope=bot%20applications.commands"
BOT_GITHUB="https://github.com/HackerSpace-PESU/pesu-academy-bot"

clientID = "" client id and secret from the jdoodle api
clientSecret = ""
```

4. Run the bot using the following command
```bash
node index.js
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

Contact any of us for any support:

[Arvind Krishna](https://github.com/ArvindAroo)<br>
[Aditeya Baral](https://github.com/aditeyabaral)<br>
[Aronya Baksy](https://github.com/abaksy)

