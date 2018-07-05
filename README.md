# Scheduling-discord-bot
## What does it do

This is a bot for discord written using discordpy, which allows users to schedule posts to a given date or at any 
interval of days/hours/minutes/seconds.

## Run the bot
This is a basic Python bot, no need for extra servers or anything. 
Simply create a config.json file following the example filethen run main.py. 
I guess you can also run it on Heroku or something.

To add the bot to your server, use the OAUTH URL given by discord in the dev panel of the website. 
The bot only needs to write & read, but you need to authorize external emojis if you want 
it to use emojis coming from the other servers it's connected on.

Then :
- Copy config.json.example to config.json and edit it to fit your case
- run python3.6 main.py

### Contributions
* If you want to contribute, please fork and submit a pull request
* If you want to translate the bot in your language, please fork and create a messages_XX file (in res dir) using 
poedit. Then submit a pull request and I'll add it.

### Todo
* Need to finish the interval type.
* add input checks
