# -*- coding: utf8 -*-
import asyncio
import datetime
import gettext
import logging
import re

import discord

from .utils import transform_emojis_in_str, write_config, load_language


# S'assurer que _ est toujours défini pour la traduction
try:
    _
except NameError:
    _ = gettext.gettext

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
            matches = pattern.findall(message.strip())
            inputlocale = matches[0] if matches else "en"
            if inputlocale == "":
                inputlocale = "en"
            bot.language = inputlocale

            # Writing the updated value in config file
            write_config("language", inputlocale)
            load_language(inputlocale)

            await o_message.add_reaction('👍')
        except Exception as e:
            logging.exception(e)
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
            def check_channel(m):
                return m.author == author and m.channel == channel
            channel_message = await bot.client.wait_for('message', check=check_channel, timeout=30)
            channel_ids = re.findall(r'(\d+)', channel_message.content)
            if not channel_ids:
                await bot.say(channel, _('No channel ID found.'))
                return
            channel_id = channel_ids[0]
            channel_to_post = discord.utils.get(server.channels, id=int(channel_id))

            # USER POST PART
            await bot.say(channel, _('Please post the message you want to send at a later date:'))
            message_to_post_msg = await bot.client.wait_for('message', check=check_channel, timeout=30)
            message_to_post = message_to_post_msg.content
            message_to_post = transform_emojis_in_str(bot, message_to_post)

            # VERIFICATION PART
            await bot.say(channel, _('This is how your message will display (removing any everyone or here, make sure the bot has permissions if any has to be said)!'))
            await bot.say(channel, message_to_post.replace('@', 'A'))
            await bot.say(channel, _('Please confirm (Y/N) whether this is the message you want to send or not:'))
            confirm_msg = await bot.client.wait_for('message', check=check_channel, timeout=15)
            if confirm_msg.content.upper() == 'N':
                await bot.say(channel, _('Scheduling cancelled.'))
                return

        except (asyncio.TimeoutError, AttributeError) as e:
            logging.exception('Either the message or the channel was not provided quickly enough.')
            await bot.say(channel, _('Timeout!'))
            return

        try:
            # TYPE OF SCHEDULING
            await bot.say(channel, _('Please post the type of message you want : interval or date'))
            type_msg = await bot.client.wait_for('message', check=check_channel, timeout=30)
            type_schedule = type_msg.content

            # IF USER WANTS TO SCHEDULE A CRON JOB
            if type_schedule.upper() == 'INTERVAL':
                # POST INTERVAL PART
                await bot.say(channel, _('Please post the interval using this format : YYYY.MM.DD HH:mm x(d/h/m/s)'))
                interval_msg = await bot.client.wait_for('message', check=check_channel, timeout=60)
                interval = interval_msg.content

                # GET RELEVANT INFO
                date_match = re.findall(r'(\d{4}.\d{2}.\d{2} \d{2}:\d{2})', interval)
                interval_match = re.findall(r'(\d{1,2}[dhms])', interval)
                interval_number_match = re.findall(r'(\d{1,2})[dhms]', interval)
                if not date_match or not interval_match or not interval_number_match:
                    await bot.say(channel, _('Wrong format for interval!'))
                    return
                starting_date = date_match[0]
                interval_val = interval_match[0]
                interval_number = interval_number_match[0]
                date_timing = datetime.datetime.strptime(starting_date, "%Y.%m.%d %H:%M")
                day, hour, minute, second = '00', '00', '00', '00'
                if 'd' in interval_val:
                    day = interval_number
                elif 'h' in interval_val:
                    hour = interval_number
                elif 'm' in interval_val:
                    minute = interval_number
                elif 's' in interval_val:
                    second = interval_number

                # ADD
                message_to_post = message_to_post + '\nMessage scheduled thanks to OverTown: <http://discord.overtown.fr/>'
                bot.scheduler.add_job(bot.say,
                                      kwargs={'channel': channel_to_post, 'message': message_to_post},
                                      trigger='cron',
                                      day=day,
                                      hour=hour,
                                      minute=minute,
                                      second=second,
                                      start_date=date_timing)

            # IF USER WANTS TO ONE SHOT SCHEDULE
            elif type_schedule.upper() == 'DATE':
                # TIMING PART
                await bot.say(channel, _('Please post the date you want to send the message using this format : YYYY.MM.DD HH:mm.'))
                date_msg = await bot.client.wait_for('message', check=check_channel, timeout=60)
                timing = date_msg.content

                # GET DATE
                try:
                    date_timing = datetime.datetime.strptime(timing, "%Y.%m.%d %H:%M")
                except ValueError:
                    await bot.say(channel, _('Wrong format for date!'))
                    return

                # ADD JOB
                message_to_post = message_to_post + '\nMessage scheduled thanks to OverTown: <http://discord.overtown.fr/>'
                bot.scheduler.add_job(bot.say, trigger='date',
                                      kwargs={'channel': channel_to_post, 'message': message_to_post},
                                      run_date=date_timing)

            else:
                await bot.say(channel, _('Unrecognized type. Use *date* or *interval*.'))
                return
        except (asyncio.TimeoutError, ValueError) as e:
            logging.exception('Either date wasn\'t entered or format is wrong.')
            await bot.say(channel, _('Wrong format for date!'))
            return

        await bot.say(channel, _('Message will be posted in channel %s at date %s' % (channel_to_post, date_timing)))
    else:
        await bot.say(channel, _('You need to be moderator or administrator to do this.'))
