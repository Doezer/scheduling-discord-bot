# -*- coding: utf8 -*-
import json
import logging
import re

import discord

logger = logging.getLogger(__name__)


def get_value_from_config(element, default_value=None, file_to_load=None):
    """Get the value from config file for specified element


    :param str element: element that will be searched for
    :param str default_value: value to put if no value is found in the json. Optional
    :param str file_to_load: path to the json file. If None, defaults to config.json.
    :return:
    """
    if not file_to_load:
        file_to_load = 'config.json'

    with open(file_to_load, mode='r+', encoding='utf-8') as f:
        config = json.load(f)
        try:
            value = config[element]
            logger.info('The value for element {} is {}.'.format(element, value))
        except KeyError:
            value = default_value
            config.update({element: value})
            f.seek(0)
            f.write(json.dumps(config))
            f.truncate()
            logger.info('The value for element {} is {}.'.format(element, value))
    return value


class DiscordBot(object):
    def __init__(self, prompt):
        super().__init__()
        self.client = discord.Client()
        self.prompt = prompt
        self.language = get_value_from_config("language", "en")
        self.modrole_name = get_value_from_config("modrole_name", 'Modération')
        self.adminrole_name = get_value_from_config("adminrole_name", 'Administration')
        self.default_emote = get_value_from_config("default_emote", 'robot')
        self.actions = {}
        self.user = None
        self.token = None
        self.scheduler = None

        @self.client.event
        async def on_ready():
            logger.info('Logged in as')
            logger.info(self.client.user.name)
            logger.info(self.client.user.id)
            logger.info('------')
            for server in self.client.servers:
                logger.info('Bot is connected to {}, server id is {}, owned by {}'.format(server.name,
                                                                                          server.id,
                                                                                          server.owner))
            logger.info('------')

            self.username = self.client.user.name
            self.user = self.client.user

        @self.client.event
        async def on_message(message):
            channel = message.channel
            author = message.author
            content = message.content
            server = message.server
            if author != self.user:
                logger.info('Message received [{0}]: {1} - "{2}"'.format(channel, author, content))
                for regex, command in self.actions.values():
                    match = re.match(regex, content)
                    if match:
                        try:
                            await command(self, channel, author, content, server, message, *match.groups())
                        except Exception as e:
                            logger.exception(e)
                            await self.say(channel, _('Something went wrong with that command.'))
                        break
                        
    def run(self, token):
        self.token = token
        self.client.run(self.token)

    def register_action(self, regex, coro):
        logger.info('Registering action {0}'.format(regex))
        if regex in self.actions:
            logger.info('Overwriting regex {0}'.format(regex))
        self.actions[regex] = (re.compile(regex, re.IGNORECASE), coro)

    async def say(self, channel, message=None, embed=None, image=None):

        # Case say(channel, embed)
        if embed:
            await self.client.send_message(channel, embed=embed)
        # Case say(channel, message, image)
        elif image and message:
            await self.client.send_file(channel, image, content=message)
        # Case say(channel, image)
        elif image and not message:
            await self.client.send_file(channel, image)
        # Case say(channel, message)
        else:
            await self.client.send_message(channel, message)
