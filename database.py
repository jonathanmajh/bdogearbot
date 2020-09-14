import os
import sqlite3
from sqlite3 import Error
from models import GearData
from random import choice
from dotenv import load_dotenv

load_dotenv()
HOME_PATH = os.getenv('HOME_PATH')
DB_PATH = f'{HOME_PATH}gear_bot_db.db'


def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
    except Error as e:
        print(e)

    return conn


def table_check():
    """
    Check if member_gear table exists and creates if necessary
    """
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='member_gear';
        ''')
        row = cur.fetchall()
        if len(row) == 0:
            print('creating member table')
            cur.execute('''
CREATE TABLE IF NOT EXISTS member_gear (
    user_id int NOT NULL, 
    gear_type text NOT NULL,
    gear_photo text NOT NULL,
    awak_ap integer NOT NULL,
    succ_ap integer NOT NULL,
    dp integer NOT NULL,
    gs integer NOT NULL,
    family_name text NOT NULL,
    server_id int NOT NULL,
    datestamp date NOT NULL,
    PRIMARY KEY(user_id, gear_type)
);''')
        else:
            print('member table already exists')

        cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='server_info';
        ''')
        row = cur.fetchall()
        if len(row) == 0:
            print('creating server table')
            cur.execute('''
CREATE TABLE IF NOT EXISTS server_info (
    server_id int PRIMARY KEY,
    server_owner int,
    requests_made int,
    general_channel_id int,
    gear_photo_id int,
    gear_talk_id int
);''')
        else:
            print('server table already exists')

        cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='server_messages';
        ''')
        row = cur.fetchall()
        if len(row) == 0:
            print('creating message table')
            cur.execute('''
CREATE TABLE IF NOT EXISTS server_messages (
    server_id int NOT NULL,
    message text NOT NULL
);''')
        else:
            print('message table already exists')
        return True


def add_server(server_info):
    conn = create_connection()
    sql = '''insert or replace into server_info(server_id,server_owner,
             requests_made,general_channel_id,gear_photo_id,gear_talk_id)
             values(?,?,?,?,?,?)'''
    cur = conn.cursor()
    payload = (server_info.server_id, server_info.server_owner, server_info.requests_name,
               server_info.general_channel_id, server_info.gear_photo_id, server_info.gear_talk_id)
    cur.execute(sql, payload)
    conn.commit()
    return server_info


def update_server_requests(server_id):
    conn = create_connection()
    sql = f'''UPDATE server_info SET requests_made = 
    (SELECT(SELECT requests_made FROM server_info WHERE server_id = {server_id})-1)
    WHERE server_id = {server_id};'''
    cur = conn.cursor()
    cur.execute(sql, )
    conn.commit()
    return True


def update_gear(gear_data):
    conn = create_connection()
    sql = '''insert or replace into member_gear(user_id,gear_type,
             gear_photo,awak_ap,succ_ap,dp,gs,family_name,server_id,datestamp)
             values(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    payload = (gear_data.user_id, gear_data.gear_type, gear_data.scrn_path,
               gear_data.awak_ap, gear_data.succ_ap, gear_data.dp, gear_data.gs,
               gear_data.family_name, gear_data.server_id, gear_data.datestamp)
    cur.execute(sql, payload)
    conn.commit()
    return gear_data


def find_gear(find):
    conn = create_connection()
    cur = conn.cursor()
    sql = f'SELECT * FROM member_gear WHERE user_id={find[0]}'
    if len(find) == 2:
        sql = sql + f' AND gear_type="{find[1]}"'
    cur.execute(sql, )
    rows = cur.fetchall()
    return rows


def find_average(find):
    conn = create_connection()
    cur = conn.cursor()
    sql = f'SELECT gs FROM member_gear WHERE server_id={find[0]}'
    if len(find) == 2:
        sql = sql + f' AND gear_type="{find[1]}"'
    cur.execute(sql,)
    rows = cur.fetchall()
    return rows


def find_all(find):
    conn = create_connection()
    cur = conn.cursor()
    sql = f'SELECT * FROM member_gear WHERE server_id={find[0]}'
    if len(find) == 2:
        sql = sql + f' AND gear_type="{find[1]}"'
    sql = sql + ' ORDER BY gs DESC'
    cur.execute(sql,)
    rows = cur.fetchall()
    return rows


def add_server_message(server_id, message):
    conn = create_connection()
    sql = 'INSERT INTO server_messages(server_id,message) values (?,?)'
    cur = conn.cursor()
    payload = (server_id, message)
    cur.execute(sql, payload)
    conn.commit()
    return True


def get_server_message(server_id, all):
    conn = create_connection()
    cur = conn.cursor()
    sql = f'SELECT message FROM server_messages WHERE server_id={server_id};'
    cur.execute(sql,)
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    if all:
        return list(rows)
    else:
        return [choice(list(rows))]
