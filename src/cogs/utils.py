
# -*- coding: utf8 -*-
import gettext
import json
import logging
import re
import discord

# S'assurer que _ est toujours défini pour la traduction
try:
    _
except NameError:
    _ = gettext.gettext


def write_config(element, value, file='config.json'):
    with open(file, mode='r+', encoding='utf-8') as f:
        config = json.load(f)
        config[element] = value
        f.seek(0)
        f.write(json.dumps(config, ensure_ascii=False, indent=2))
        f.truncate()


def load_language(locale):
    filename = f"res/messages_{locale}.mo"
    try:
        with open(filename, "rb") as f:
            trans = gettext.GNUTranslations(f)
    except IOError:
        trans = gettext.NullTranslations()
    trans.install()


def get_emoji_code(bot, emoji_to_search):
    """

    :param DiscordBot.DiscordBot bot:
    :param str emoji_to_search:
    :return:
    """
    # Pour discord.py v2+, get_all_emojis() devient emojis (attribut)
    emojis = getattr(bot.client, 'emojis', [])
    tmp = discord.utils.get(emojis, name=emoji_to_search)
    if not tmp:
        logging.error('Couldn\'t find emote %s in the bot emojis. Please add it to a server.', emoji_to_search)
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
        if trans_emoji:
            pattern_to_repl = fr'<:{emoji}[^>]*>'
            message_to_post = re.sub(pattern=pattern_to_repl,
                                     repl=f'<:{trans_emoji.name}:{trans_emoji.id}>',
                                     string=message_to_post)
            logging.info(message_to_post)
        else:
            logging.warning(f"No emoji found for :{emoji}:")
    return message_to_post