#  -*- coding: utf8 -*-
import gettext
import json
import locale
import logging
import sys

import src.cogs.core as core
from src.DiscordBot import DiscordBot

__appname__ = 'Scheduling Discord Bot'
__version__ = "0.1"
__author__ = "Vincent 'Doezer' AIRIAU"


def get_prompt():
    prompt = "!"
    try:
        with open('config.json', mode='r+', encoding='utf-8') as f:
            config = json.load(f)
            try:
                prompt = config["prompt"]
            except KeyError:
                config.update({"prompt": prompt})
                f.seek(0)
                f.write(json.dumps(config))
                f.truncate()
            prompt = config["prompt"]
    except:
        logging.debug("Prompt not found. Using default '{}'.".format(prompt))

    logging.info('The prompt is {}.'.format(prompt))
    return prompt


def set_locale():
    try:
        with open('config.json', mode='r+', encoding='utf-8') as f:
            config = json.load(f)
            language = config["language"]
        locale.setlocale(locale.LC_ALL, language)
    except:
        locale.setlocale(locale.LC_ALL, '')

    loc = locale.getlocale()
    filename = "res/messages_%s.mo" % locale.getlocale()[0][0:2]

    try:
        logging.debug("Opening message file %s for locale %s", filename, loc[0])
        trans = gettext.GNUTranslations(open(filename, "rb"))
    except IOError:
        logging.debug("Locale not found. Using default messages")
        trans = gettext.NullTranslations()

    trans.install()


def main():
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s <%(lineno)d>",
    )
    prompt = get_prompt()

    set_locale()

    cmd_list = {'^{}help$'.format(prompt): core.bot_help_embed,
                '^{}(?:schedule)$'.format(prompt): core.schedule_post,
                '^{}(?:language)'.format(prompt): core.language}


    with open('config.json') as f:
        config = json.load(f)

    bot = DiscordBot(prompt)
    for action in cmd_list:
        bot.register_action(action, cmd_list[action])

    bot.run(config['token'])


if __name__ == '__main__':
    main()
