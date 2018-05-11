# -*- coding: utf8 -*-
import asyncio
import datetime
import logging
import re

import discord

from .utils import write_config, load_language


async def language(bot, channel, author, message, server, o_message):
    """ Sets and updates current language of the bot
    """
    modrole = discord.utils.get(server.roles, name=bot.modrole_name)
    adminrole = discord.utils.get(server.roles, name=bot.adminrole_name)
    pattern = re.compile(r'^.language (en|fr)')

    if modrole in author.roles or adminrole in author.roles:
        try:
            inputlocale = pattern.findall(message.strip())[0]
            if inputlocale == "":
                inputlocale = "en"
            bot.language = inputlocale

            # Writing the updated value in config file
            write_config("language", inputlocale)
            load_language(inputlocale)

            await bot.add_reaction(o_message, '👍')
        except IndexError:
            await bot.say(channel, _('The language is not available.\nAvailable languages: fr, en'))
    else:
        await bot.say(channel, _('You need to be moderator or administrator to do this.'))


async def bot_help_embed(bot, channel, author, message, server, o_message):
    embed = discord.Embed(title=_('Scheduling bot - Help'))
    bnet_field = [_('**{prompt}schedule** ').format(prompt=bot.prompt),
                  _('Schedule a post (interactive mode).')]
    lang_field = [_('**{prompt}language <language>**').format(prompt=bot.prompt),
                  _('Set the bot language : "en" or "fr".').format(prompt=bot.prompt)]
    fields = [bnet_field, lang_field]

    embed.description = _("Find below the explanation for all commands.")
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=False)
    await bot.say(channel, embed=embed)


async def schedule_post(bot, channel, author, message, server, o_message):
    """

    :param DiscordBot.DiscordBot bot:
    :param channel:
    :param author:
    :param message:
    :param discord.Server server:
    :param o_message:
    """

    # Todo add checks for inputs
    # todo add type interval

    # ask for message
    modrole = discord.utils.get(server.roles, name=bot.modrole_name)
    adminrole = discord.utils.get(server.roles, name=bot.adminrole_name)

    message_to_post, timing, date_timing, channel_to_post = None, None, None, None
    if modrole in author.roles or adminrole in author.roles:
        try:
            await bot.say(channel, _('Please ID the channel in which you want to send your message:'))

            channel_message = await bot.client.wait_for_message(timeout=30, author=author, channel=channel)
            channel_id = re.findall('(\d+)', channel_message.content)[0]  # Retrieve the channel ID
            channel_to_post = discord.utils.get(server.channels, id=channel_id)  # Retrieve the Discord.Channel

            await bot.say(channel, _('Please post the message you want to send at a later date:'))
            message_to_post = await bot.client.wait_for_message(timeout=30, author=author, channel=channel)
            message_to_post = message_to_post.content
            # Transform the emojis so that it is displayed by the bot if it knows them
            message_to_post = transform_emojis_in_str(bot, message_to_post)

            await bot.say(channel, _('This is how your message will display (removing any everyone or here, make sure '
                                     'the bot has permissions if any has to be said)!'))
            await bot.say(channel, message_to_post.replace('@', ''))
            await bot.say(channel, _('Please confirm (Y/N) whether this is the message you want to send or not:'))
            tmp = await bot.client.wait_for_message(timeout=15, author=author, channel=channel)
            tmp = tmp.content
            if tmp.upper() == 'N':
                await bot.say(channel, _('Scheduling cancelled.'))
                return

            # ask for type
            await bot.say(channel, _('Please post the type of message you want : interval or date'))
            # record timing
            type_schedule = await bot.client.wait_for_message(timeout=30, author=author, channel=channel)
            type_schedule = type_schedule.content

            if type_schedule.upper() == 'INTERVAL':
                await bot.say(channel, _('This type is not yet available. Use only for specific announcements for now.'))
                # # ask for timing
                # await bot.say(channel, _('Please post the interval using cron format separated by / :'))
                # # record timing
                # interval = await bot.client.wait_for_message(timeout=30, author=author, channel=channel)
                # interval = interval.content
                # # Transform to datetime
                # interval = interval.split('/')
                type_schedule = 'date'

            if type_schedule.upper() == 'DATE':
                # ask for timing
                await bot.say(channel,_('Please post the date you want to send the message '
                                        'using this format : YYYY.MM.DD HH:mm'))
                # record timing
                timing = await bot.client.wait_for_message(timeout=30, author=author, channel=channel)
                timing = timing.content
                # Transform to datetime
                date_timing = datetime.datetime.strptime(timing, "%Y.%m.%d %H:%M")
            else:
                await bot.say(channel,_('I could not recognize the parameter'))
                return

        except asyncio.TimeoutError or AttributeError:
            logging.exception('Either the message or the date was not provided quickly enough.')
            await bot.say(channel, _('Timeout!'))
            return
        except ValueError:
            logging.exception('Date format is wrong. Date entered %s.', timing)
            await bot.say(channel, _('Wrong format for date!'))
            return

        # schedule job
        bot.scheduler.add_job(bot.say, trigger='date', args=(channel_to_post, message_to_post), run_date=date_timing)
        await bot.say(channel, _('Message will be posted in channel %s at date %s'), )
    else:
        await bot.say(channel, _('You need to be moderator or administrator to do this.'))


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
