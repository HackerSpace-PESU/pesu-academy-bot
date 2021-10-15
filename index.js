
const Discord = require("discord.js");
const fs = require("fs");
require("dotenv").config();
const BOT_TOKEN = process.env.TOKEN;

const client = new Discord.Client({ intents: [Discord.Intents.FLAGS.GUILDS, Discord.Intents.FLAGS.GUILD_MESSAGES, Discord.Intents.FLAGS.GUILD_PRESENCES] });
client.commands = new Discord.Collection();
const command_files = fs.readdirSync("./commands").filter(file => file.endsWith(".js"));
const prefix = "pes";
const availableCommands = ['ping', 'exec', 'pride', 'echo'];

const commandFunctions = require("./commands/commands.js");


// for (const file of command_files) {
// 	const command = require(`./commands/${file}`);
// 	client.commands.set(command.data.name, command);
//     console.log("Loading", file)
// }

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
client.on("messageCreate", (message) => {
	if (!message.content.startsWith(prefix) || message.author.bot) return;
    
	  
	if(message.mentions.members.first() && message.mentions.members.first().user.id == client.user.id){
		//ie the bot is mentioned or replied to
		message.reply("Don't be a PESt by pinging the bot. Type `pes.help` to access commands.")
	}

	if(message.content.toLowerCase().includes("pride")){
		message.reply("Invoking the PRIDE of PESU!");
		message.channel.send("https://media.discordapp.net/attachments/742995787700502565/834782280236662827/Sequence_01_1.gif");
	}
	const args = message.content.slice(prefix.length).trim().split(/ +/);
    const command = args.shift().toLowerCase();
	// console.log(command)
	if (availableCommands.includes(command)) {
        if (command === "ping") {
            commandFunctions.ping(message);
		}
		if (command === "echo") {
            commandFunctions.echo(message, args);
		}
	}
});
process.on("uncaughtException", function(err) {
    console.log("Caught exception: " + err);
});


client.login(BOT_TOKEN);
