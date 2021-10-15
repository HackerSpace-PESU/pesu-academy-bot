let axios = require("axios").default;
require("dotenv").config();
const clientID = process.env.clientID;
const clientSecret = process.env.clientSecret;

module.exports = {
    jdoodle:function (language, version, code, StdIn){
        try {
            const res = await axios.post('https://api.jdoodle.com/v1/execute', {
                'clientId' : clientID,
                'clientSecret': clientSecret,
                'script': code,
                'language': language,
                'versionIndex': version,
                'stdin': stdin,
                headers: {
                    Accept: 'application/json, text/plain, */*',
                    'User-Agent': 'axios/0.23.0'
                    }
                }
            );
            return res.data
        } catch (err) {
            console.error(err);
        }
    
    }
}