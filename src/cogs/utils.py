# -*- coding: utf8 -*-
import gettext
import logging
import re

import discord

from src.config_utils import set_config_value


def write_config(element, value):
    set_config_value(element, value)


def load_language(locale):
    filename = f"res/messages_{locale}.mo"
    try:
        with open(filename, "rb") as f:
            trans = gettext.GNUTranslations(f)
    except OSError:
        trans = gettext.NullTranslations()
    trans.install()


def get_emoji_code(bot, emoji_to_search):
    emojis = getattr(bot.client, "emojis", [])
    tmp = discord.utils.get(emojis, name=emoji_to_search)
    if not tmp:
        logging.error("Couldn't find emote %s in the bot emojis. Please add it to a server.", emoji_to_search)
        tmp = discord.utils.get(emojis, name=bot.default_emote)
        logging.debug("transformed emoji is %s", tmp)
    return tmp


def transform_emojis_in_str(bot, message_to_post):
    emoji_list = re.findall(r":(\S+):", message_to_post)
    logging.info("emoji_list is %s", emoji_list)

    for emoji in emoji_list:
        logging.info("message emoji is %s", emoji)
        trans_emoji = get_emoji_code(bot, emoji)
        if trans_emoji:
            pattern_to_repl = rf"<:{emoji}[^>]*>"
            message_to_post = re.sub(
                pattern=pattern_to_repl,
                repl=f"<:{trans_emoji.name}:{trans_emoji.id}>",
                string=message_to_post,
            )
            logging.info(message_to_post)
        else:
            logging.warning(f"No emoji found for :{emoji}:")
    return message_to_post
