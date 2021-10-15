module.exports = {
    checkEchoPerms:function(userObj){
        //TODO - get userAuth independent of the server and roles
        if(userObj.id == 718845827413442692) return true;
        return false;
    },
    ping: function(message) {
        this.message = message;
        message.channel.send({
            content: `Latency is ${
                Date.now() - message.createdTimestamp
            }ms. API Latency is ${this.client.ws.ping}ms`,
        });
    },

    echo:function(message, args){

        //syntax - `+e <#channelname> whatever to be echoed
        //paste the required attachment along with that
        this.message = message;
        if (this.checkEchoPerms(message.member)) {
            if (args[0]) {
                // still too unsafe to give others perms to use the command
                let channel = message.mentions.channels;
                let channelID = channel.keys().next().value;
                if(channelID == undefined){
                    return message.reply("Mention the channel")
                } 
                let channelObj = this.client.channels.cache.get(channelID); 
                args.shift() //remove the first element i.e the channel mention
                channelObj.send(args.join(" "))
                for (let [key, value] of message.attachments) {
                    channelObj.send(value.url);
                }
                return
            }
            message.reply("what should i even echo");
        } else {
            message.reply("You dont have the perms to execute the command");
        }
    },
}