# -*- coding: utf8 -*-
import gettext
import json
import logging
import re

import discord


def write_config(element, value, file='config.json'):
    with open(file, mode='r+', encoding='utf-8') as f:
        file = json.load(f)
        file[element] = value
        f.seek(0)
        f.write(json.dumps(file))
        f.truncate()


def load_language(locale):
    filename = "res/messages_%s.mo" % locale
    try:
        trans = gettext.GNUTranslations(open(filename, "rb"))
    except IOError:
        trans = gettext.NullTranslations()
    finally:
        trans.install()


def get_emoji_code(bot, emoji_to_search):
    """

    :param DiscordBot.DiscordBot bot:
    :param str emoji_to_search:
    :return:
    """
    emoji_generator = bot.client.get_all_emojis()
    tmp = discord.utils.get(emoji_generator, name=emoji_to_search)
    if not tmp:
        logging.error('Couldn\'t find emote %s in the bot emojis. Please add it to a server.', emoji_to_search)
        emojis = bot.client.get_all_emojis()
        tmp = discord.utils.get(emojis, name=bot.default_emote)
        logging.debug("transformed emoji is %s", tmp)
    return tmp


def transform_emojis_in_str(bot, message_to_post):
    """

    :param DiscordBot.DiscordBot bot:
    :param str message_to_post:
    """
    emoji_list = re.findall(r':(\S+):', message_to_post)
    logging.info("emoji_list is %s", emoji_list)

    for emoji in emoji_list:
        logging.info("message emoji is %s", emoji)
        trans_emoji = get_emoji_code(bot, emoji)
        logging.info("transformed emoji is %s", trans_emoji)
        pattern_to_repl = fr'(<:{emoji}\S+>)'
        message_to_post = re.sub(pattern=pattern_to_repl,
                                 repl=f'<:{trans_emoji.name}:{trans_emoji.id}>',
                                 string=message_to_post)
        logging.info(message_to_post)
    return message_to_post