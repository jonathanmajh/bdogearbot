import os
from datetime import date

import requests
from dotenv import load_dotenv

from bin.cloud_vision import detect_text
from bin.database import (create_connection, del_gear, find_all, find_average,
                          find_gear, update_gear, update_server_requests)
from bin.models import GearData, Result, SimpleGearData

from cogs.error_handler import CommandErrorHandler

load_dotenv()
HOME_PATH = os.getenv('HOME_PATH')
DB_PATH = f'{HOME_PATH}gear_bot_db.db'


def add_gear(gear_type, ctx):
    if len(ctx.message.attachments) == 1:
        gear_data = GearData(user_id=ctx.author.id, gear_type=gear_type, scrn_path=ctx.message.attachments[0].url,
                             family_name=ctx.author.display_name, server_id=ctx.guild.id,
                             datestamp=date.today())
        limit = update_server_requests(ctx.guild.id)
        if limit[0][0] < 0:
            return Result(False, 'This guild has reached the maximum of gear update requests for this month')
        elif limit[0][0] < 20:
            message = f'Note: This guild has {limit[0][0]} gear update requests remaining'
        else:
            message = None
        # save photo
        try:
            url = gear_data.scrn_path
            r = requests.get(url, allow_redirects=True)
            filename, file_ext = os.path.splitext(
                ctx.message.attachments[0].filename)
            photo_path = f'{HOME_PATH}screenshots/{ctx.author.id}_{gear_type}{file_ext}'
            gear_data.obj = r.content
            gear_data.scrn_path = photo_path
        except Exception as error:
            CommandErrorHandler().send_pm(error=error)
            return Result(False, f'Error getting photo from discord servers')

        gear_data = detect_text(gear_data)
        if gear_data.status:
            open(photo_path, 'wb').write(r.content)
            gear_data = gear_data.gear_data
            gear_data = update_gear(gear_data)
            return Result(True, message=message, gear_data=gear_data)
        else:
            return gear_data  # with message

    else:
        return Result(False, 'Either no photos were attached or more than one were attached!')


def get_gear(user_id, gear_type=None):
    if gear_type == None:
        find = [user_id]
    else:
        find = [user_id, gear_type.lower()]

    results = find_gear(find)

    if len(results) == 0:
        return Result(False, 'That user has no gear')
    else:
        photos = []
        msg = ""
        for result in results:
            msg = msg + \
                f'{result[7]} {result[1]}: {result[4]}/{result[3]}/{result[5]}: GS: {result[6]}. Updated: {result[9]}\n'
            photos.append(result[2])
        return Result(True, msg, photos=photos)


def remove_gear(user_id, gear_type):
    if gear_type == 'all':
        find = [user_id]
    else:
        find = [user_id, gear_type.lower()]

    result = del_gear(find)
    if len(result) == 0:
        return Result(True, 'There was no gear associated with your user to remove')
    print(str(result))
    return Result(True, f'Deleted {len(result)} gear entries')


def get_average(guild_id, gear_type):
    if gear_type == None:
        find = [guild_id]
    else:
        find = [guild_id, gear_type.lower()]

    results = find_average(find)

    if len(results) == 0:
        return Result(False, 'This Guild has no gear')
    else:
        gs_sum = 0
        for result in results:
            gs_sum = gs_sum + int(result[0])
        return Result(True, gs_sum/len(results))


def get_all(guild_id, gear_type):
    if gear_type == None:
        find = [guild_id]
    else:
        find = [guild_id, gear_type.lower()]

    results = find_all(find)

    if len(results) == 0:
        return Result(False, 'This Guild has no gear')
    else:
        gear = []
        for result in results:
            gear.append(SimpleGearData(result[1], result[7], result[9],
                                       result[3], result[4], result[5],
                                       result[6]))
        return Result(True, 'done', obj=gear)
