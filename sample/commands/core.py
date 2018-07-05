# -*- coding: utf8 -*-
import asyncio
import datetime
import logging
import re

import discord

from utils import transform_emojis_in_str, write_config, load_language


async def language(bot, channel, author, message, server, o_message):
    """

    :param DiscordBot.DiscordBot bot:
    :param discord.Channel channel:
    :param discord.Member author:
    :param discord.Message.content message:
    :param discord.Server server:
    :param discord.Message o_message:
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

            await bot.client.add_reaction(o_message, '👍')
        except IndexError:
            await bot.say(channel, _('The language is not available.\nAvailable languages: fr, en'))
    else:
        await bot.say(channel, _('You need to be moderator or administrator to do this.'))


async def bot_help_embed(bot, channel, author, message, server, o_message):
    """

    :param DiscordBot.DiscordBot bot:
    :param discord.Channel channel:
    :param discord.Member author:
    :param discord.Message.content message:
    :param discord.Server server:
    :param discord.Message o_message:
    """
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
    modrole = discord.utils.get(server.roles, name=bot.modrole_name)
    adminrole = discord.utils.get(server.roles, name=bot.adminrole_name)

    message_to_post, timing, date_timing, channel_to_post, type_schedule, output = None, None, None, None, None, None
    day, hour, minute, second = '00', '00', '00', '00'
    if modrole in author.roles or adminrole in author.roles:
        try:
            # CHANNEL ID PART
            await bot.say(channel, _('Please ID the channel in which you want to send your message:'))
            channel_message = await bot.client.wait_for_message(timeout=30, author=author, channel=channel)
            channel_id = re.findall('(\d+)', channel_message.content)[0]
            channel_to_post = discord.utils.get(server.channels, id=channel_id)

            # USER POST PART
            await bot.say(channel, _('Please post the message you want to send at a later date:'))
            message_to_post = await bot.client.wait_for_message(timeout=30, author=author, channel=channel)
            message_to_post = message_to_post.content
            message_to_post = transform_emojis_in_str(bot, message_to_post)

            # VERIFICATION PART
            await bot.say(channel, _('This is how your message will display (removing any everyone or here, '
                                     'make sure the bot has permissions if any has to be said)!'))
            await bot.say(channel, message_to_post.replace('@', 'A'))
            await bot.say(channel, _('Please confirm (Y/N) whether this is the message you want to send or not:'))
            tmp = await bot.client.wait_for_message(timeout=15, author=author, channel=channel)
            tmp = tmp.content
            if tmp.upper() == 'N':
                await bot.say(channel, _('Scheduling cancelled.'))
                return

        except asyncio.TimeoutError or AttributeError:
            logging.exception('Either the message or the channel was not provided quickly enough.')
            await bot.say(channel, _('Timeout!'))
            return

        try:

            # TYPE OF SCHEDULING
            await bot.say(channel, _('Please post the type of message you want : interval or date'))
            type_schedule = await bot.client.wait_for_message(timeout=30, author=author, channel=channel)
            type_schedule = type_schedule.content

            # IF USER WANTS TO SCHEDULE A CRON JOB
            if type_schedule.upper() == 'INTERVAL':

                # POST INTERVAL PART
                await bot.say(channel, _('Please post the interval using this format : YYYY.MM.DD HH:mm x(d/h/m/s)'))
                output = await bot.client.wait_for_message(timeout=60, author=author, channel=channel)
                interval = output.content

                # GET RELEVANT INFO
                starting_date = re.findall(r'(\d{4}.\d{2}.\d{2} \d{2}:\d{2})', interval)[0]
                interval = re.findall(r'(\d{1,2}[dhms])', interval)[0]
                interval_number = re.findall(r'(\d{1,2})[dhms]', interval)[0]
                date_timing = datetime.datetime.strptime(starting_date, "%Y.%m.%d %H:%M")
                if 'd' in interval:
                    day = interval_number
                elif 'h' in interval:
                    hour = interval_number
                elif 'm' in interval:
                    minute = interval_number
                elif 's' in interval:
                    second = interval_number

                # ADD
                message_to_post = message_to_post + '\nMessage scheduled thanks to OverTown:' \
                                                    ' <http://discord.overtown.fr/>'
                bot.scheduler.add_job(bot.say,
                                      kwargs={channel: channel_to_post, message: message_to_post},
                                      trigger='cron',
                                      day=day,
                                      hour=hour,
                                      minute=minute,
                                      second=second,
                                      run_date=date_timing)

            # IF USER WANTS TO ONE SHOT SCHEDULE
            elif type_schedule.upper() == 'DATE':
                # TIMING PART
                await bot.say(channel, _('Please post the date you want to send the message using this '
                                         'format : YYYY.MM.DD HH:mm.'))
                output = await bot.client.wait_for_message(timeout=60, author=author, channel=channel)
                timing = output.content

                # GET DATE
                date_timing = datetime.datetime.strptime(timing, "%Y.%m.%d %H:%M")

                # ADD JOB
                message_to_post = message_to_post + '\nMessage scheduled thanks to OverTown: <http://discord.overtown.fr/>'
                bot.scheduler.add_job(bot.say, trigger='date',
                                      kwargs={channel: channel_to_post, message: message_to_post},
                                      run_date=date_timing)

            else:
                await bot.say(channel, _('Unrecognized type. Use *date* or *interval*.'))
                return
        except asyncio.TimeoutError or ValueError:
            logging.exception('Either date wasn\'t entered or format is wrong. Date entered %s.', output)
            await bot.say(channel, _('Wrong format for date!'))
            return

        await bot.say(channel, _('Message will be posted in channel %s at date %s'), channel_to_post, date_timing)
    else:
        await bot.say(channel, _('You need to be moderator or administrator to do this.'))
