const Discord = require("discord.js");
const fs = require("fs");
require("dotenv").config();
const BOT_TOKEN = process.env.TOKEN;

const client = new Discord.Client({ intents: [Discord.Intents.FLAGS.GUILDS, Discord.Intents.FLAGS.GUILD_MESSAGES, Discord.Intents.FLAGS.GUILD_PRESENCES] });
client.commands = new Discord.Collection();
const command_files = fs.readdirSync("./commands").filter(file => file.endsWith(".js"));

for (const file of command_files) {
	const command = require(`./commands/${file}`);
	client.commands.set(command.data.name, command);
    console.log("Loading", file)
}

client.once('ready', () => {
	console.log("Bot is alive");
});

client.on('interactionCreate', async interaction => {
	if (!interaction.isCommand()) return;

	const command = client.commands.get(interaction.commandName);

	if (!command) return;

	try {
		await command.execute(interaction);
	} catch (error) {
		console.error(error);
		return interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
	}
});

process.on("uncaughtException", function(err) {
    console.log("Caught exception: " + err);
});


client.login(BOT_TOKEN);