# -*- coding: utf8 -*-
import gettext
import logging
import os
import re
from zoneinfo import ZoneInfo

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config_utils import get_config_value

logger = logging.getLogger(__name__)


class DiscordBot:
    def __init__(self, prompt):
        super().__init__()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        self.client = discord.Client(intents=intents)
        self.prompt = prompt
        self.language = get_config_value("language", "en")
        self.modrole_name = get_config_value("modrole_name", "Modération")
        self.adminrole_name = get_config_value("adminrole_name", "Administration")
        self.default_emote = get_config_value("default_emote", "robot")
        self.actions = {}
        self.user = None
        self.token = None
        self.username = None
        self.scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Paris"))

        self._set_locale(self.language)

        @self.client.event
        async def on_ready():
            logger.info("Logged in as")
            if self.client.user:
                logger.info(self.client.user.name)
                logger.info(self.client.user.id)
                self.username = self.client.user.name
                self.user = self.client.user
            else:
                logger.warning("self.client.user is None at on_ready")
            logger.info("------")
            for guild in self.client.guilds:
                logger.info(f"Bot is connected to {guild.name}, server id is {guild.id}, owned by {guild.owner}")
            logger.info("------")

            if not self.scheduler.running:
                self.scheduler.start()
                # Use this place to manually schedule any job you'd like:
                # self.scheduler.add_job(print,
                #                         trigger='cron',
                #                         args=['Hello world!'],
                #                         day='*',
                #                         hour='14',
                #                         minute='23')

        @self.client.event
        async def on_message(message):
            channel = message.channel
            author = message.author
            content = message.content
            guild = message.guild
            if author != self.user:
                logger.info(f'Message received [{channel}]: {author} - "{content}"')
                for regex, command in self.actions.values():
                    match = regex.match(content)
                    if match:
                        try:
                            await command(self, channel, author, content, guild, message, *match.groups())
                        except Exception as e:
                            logger.exception(e)
                            await self.say(channel, self._("Something went wrong with that command."))
                        break

    def _set_locale(self, locale):
        try:
            filename = os.path.join("res", f"messages_{locale}.mo")
            trans = gettext.GNUTranslations(open(filename, "rb"))
        except OSError:
            logging.warning("Locale file not found for '%s', falling back to default.", locale)
            trans = gettext.NullTranslations()
        trans.install()
        self._ = trans.gettext

    def run(self, token=None):
        self.token = token or os.environ.get("DISCORD_TOKEN")
        if not self.token:
            raise RuntimeError("No Discord token provided. Set DISCORD_TOKEN or add 'token' to config.json.")
        self.client.run(self.token)

    def register_action(self, regex, coro):
        logger.info(f"Registering action {regex}")
        compiled = re.compile(regex, re.IGNORECASE)
        if regex in self.actions:
            logger.info(f"Overwriting regex {regex}")
        self.actions[regex] = (compiled, coro)

    async def say(self, channel, message=None, embed=None, image=None):
        if embed:
            await channel.send(embed=embed)
        elif image and message:
            await channel.send(content=message, file=discord.File(image))
        elif image and not message:
            await channel.send(file=discord.File(image))
        else:
            await channel.send(message)
