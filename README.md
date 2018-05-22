# scheduling-discord-bot
## What does it do

This is a bot for discord which enables users to schedule posts to a given date or at any interval of days.

The command *schedule* is working if you select the date type (so a specific announcement)


## Run the bot
This is a basic Python bot, no need for extra servers or anything. Simply create a config.json file following the example file
then run main.py.

To add the bot to your server, use the OAUTH URL given by discord in the dev panel of the website. 
The bot only needs to write & read, but you need to authorize external emojis if you want 
it to use emojis coming from the other servers it's connected on.

### Contributions
* If you want to contribute, please fork and submit a pull request
* If you want to translate the bot in your language, please fork and create a messages_XX file (in res dir) using poedit. Then submit a pull request and I'll add it.

### Todo
* Need to finish the interval type.
* add input checks
