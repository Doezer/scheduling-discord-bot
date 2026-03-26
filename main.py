# -*- coding: utf8 -*-
import gettext
import logging
import sys

import src.cogs.core as core
from src.config_utils import load_config
from src.DiscordBot import DiscordBot

__appname__ = "Scheduling Discord Bot"
__version__ = "0.1"
__author__ = "Vincent 'Doezer' AIRIAU"


def set_locale(language: str):
    filename = f"res/messages_{language[:2]}.mo"
    try:
        logging.debug("Opening message file %s for language %s", filename, language)
        with open(filename, "rb") as f:
            trans = gettext.GNUTranslations(f)
    except OSError:
        logging.debug("Locale file not found. Using default messages.")
        trans = gettext.NullTranslations()
    trans.install()


def main():
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s <%(lineno)d>",
    )

    config = load_config()
    prompt = config.get("prompt", "!")
    language = config.get("language", "en")
    token = config.get("token")

    set_locale(language)

    cmd_list = {
        f"^{prompt}help$": core.bot_help_embed,
        f"^{prompt}(?:schedule)$": core.schedule_post,
        f"^{prompt}(?:language)": core.language,
    }

    bot = DiscordBot(prompt)
    for action, handler in cmd_list.items():
        bot.register_action(action, handler)

    bot.run(token)


if __name__ == "__main__":
    main()
