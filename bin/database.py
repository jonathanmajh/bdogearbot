import os
import sqlite3
from random import choice
from sqlite3 import Error
from dotenv import load_dotenv

from bin.models import GearData

load_dotenv()
HOME_PATH = os.getenv('HOME_PATH')
DB_PATH = f'{HOME_PATH}bin/gear_bot_db.db'
ITEM_DB_PATH = f'{HOME_PATH}bin/bdo_items.db'


def create_connection(DB_PATH):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
    except Error as e:
        print(e)

    return conn


def get_item_by_id(args):
    conn = create_connection(ITEM_DB_PATH)
    cur = conn.cursor()
    sql = f' ?'
    sql = "SELECT item_id, item_name FROM item_names WHERE item_id IN ({seq})".format(
        seq=','.join(['?']*len(args)))
    cur.execute(sql, args)
    rows = cur.fetchall()
    return rows


def item_exact_search(query: str):
    conn = create_connection(ITEM_DB_PATH)
    cur = conn.cursor()
    sql = 'SELECT item_id, item_name FROM item_names WHERE item_name=? ORDER BY length(item_name) ASC;'
    cur.execute(sql, (query, ))
    rows = cur.fetchall()
    return rows


def item_like_search(query: str):
    conn = create_connection(ITEM_DB_PATH)
    cur = conn.cursor()
    sql = f'SELECT item_id, item_name FROM item_names WHERE lcase_name LIKE ? ORDER BY length(item_name) ASC;'
    cur.execute(sql, (f'%{query}%', ))
    rows = cur.fetchall()
    return rows


def item_phone_search(query):
    conn = create_connection(ITEM_DB_PATH)
    cur = conn.cursor()
    sql = f'SELECT item_id, item_name FROM item_names WHERE pri_phone LIKE ? OR sec_phone LIKE ?'
    queries = (f'%{query[0]}%', f'%{query[0]}%')
    if query[1] != '':
        sql = f'{sql} OR pri_phone LIKE ? OR sec_phone LIKE ?'
        queries = (f'%{query[0]}%', f'%{query[0]}%', f'%{query[1]}%', f'%{query[1]}%', )
    cur.execute(sql, queries)
    rows = cur.fetchall()
    return rows


def item_leven_search(query: str):
    conn = create_connection(ITEM_DB_PATH)
    conn.enable_load_extension(True)
    conn.load_extension("./bin/spellfix1.so")
    conn.enable_load_extension(False)
    cur = conn.cursor()
    cur.execute("SELECT item_id, item_name, editdist3(lcase_name, ?) AS edit_dist FROM item_names ORDER BY edit_dist ASC", (query,))
    # cur.execute("SELECT rowid, word FROM leven_name WHERE word MATCH ?", (query,))
    rows = cur.fetchall()
    return rows


def item_no_phone():
    """gets all entries with no primary metaphone"""
    conn = create_connection(ITEM_DB_PATH)
    cur = conn.cursor()
    sql = f'SELECT item_id, lcase_name FROM item_names;'
    cur.execute(sql, )
    rows = cur.fetchall()
    return rows


def table_check():
    """
    Check if member_gear table exists and creates if necessary
    """

    conn = create_connection(DB_PATH)
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
    server_admin_role_id int,
    requests_made int,
    general_channel_id int,
    gear_channel_id int,
    boss_timer_channel_id int
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
    message text NOT NULL,
    user_id int NOT NULL
);''')
        else:
            print('message table already exists')

        cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='enhancement';
        ''')
        row = cur.fetchall()
        if len(row) == 0:
            print('creating message table')
            cur.execute('''
CREATE TABLE IF NOT EXISTS enhancement (
    item_id int PRIMARY KEY,
    base int NOT NULL,
    pri int NOT NULL,
    duo int NOT NULL,
    tri int NOT NULL,
    tet int NOT NULL,
    pen int NOT NULL,
    last_update timestamp NOT NULL
);''')
        else:
            print('enhancement table already exists')
        return True


def add_server(server_info):
    conn = create_connection(DB_PATH)
    sql = '''insert or replace into server_info(server_id,server_admin_role_id,
             requests_made,general_channel_id,gear_channel_id,boss_timer_channel_id)
             values(?,?,?,?,?,?)'''
    cur = conn.cursor()
    payload = (server_info.server_id, server_info.server_admin_role_id, server_info.requests_made,
               server_info.general_channel_id, server_info.gear_channel_id, server_info.boss_timer_channel_id)
    cur.execute(sql, payload)
    conn.commit()
    return server_info


def update_server_requests(server_id):
    conn = create_connection(DB_PATH)
    sql = f'''UPDATE server_info SET requests_made = 
    (SELECT(SELECT requests_made FROM server_info WHERE server_id = {server_id})-1)
    WHERE server_id = {server_id};'''
    cur = conn.cursor()
    cur.execute(sql, )
    conn.commit()
    sql = f'SELECT requests_made FROM server_info WHERE server_id={server_id};'
    cur.execute(sql, )
    rows = cur.fetchall()
    return rows


def reset_server_requests(new_limit):
    conn = create_connection(DB_PATH)
    sql = f'UPDATE server_info SET requests_made = ?'
    cur = conn.cursor()
    cur.execute(sql, (new_limit, ))
    conn.commit()
    return True


def update_gear(gear_data):
    conn = create_connection(DB_PATH)
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
    conn = create_connection(DB_PATH)
    cur = conn.cursor()
    sql = f'SELECT * FROM member_gear WHERE user_id=?'
    queries = (find[0],)
    if len(find) == 2:
        sql = sql + f' AND gear_type=?'
        queries = (find[0], find[1])
    cur.execute(sql, queries)
    rows = cur.fetchall()
    return rows


def del_gear(find):
    # TODO only remove gear associated with the server
    conn = create_connection(DB_PATH)
    cur = conn.cursor()
    sql_del = f'DELETE FROM member_gear WHERE user_id=?'
    sql_find = f'SELECT gear_photo FROM member_gear WHERE user_id=?'
    queries = (find[0],)
    if len(find) == 2:
        sql_del = sql_del + f' AND gear_type=?'
        sql_find = sql_find + f' AND gear_type=?'
        queries = (find[0], find[1])
    cur.execute(sql_find, queries)
    rows = cur.fetchall()
    cur.execute(sql_del, queries)
    conn.commit()
    return rows

def find_average(find):
    conn = create_connection(DB_PATH)
    cur = conn.cursor()
    sql = f'SELECT gs FROM member_gear WHERE server_id={find[0]}'
    if len(find) == 2:
        sql = sql + f' AND gear_type="{find[1]}"'
    cur.execute(sql,)
    rows = cur.fetchall()
    return rows

def find_all(find, page):
    conn = create_connection(DB_PATH)
    cur = conn.cursor()
    sql = f'FROM member_gear WHERE server_id={find[0]}'
    if len(find) == 2:
        sql = sql + f' AND gear_type="{find[1]}"'
    cur.execute(f'SELECT COUNT (*) {sql}')
    pages = cur.fetchone()[0]
    sql = f'{sql} ORDER BY gs DESC LIMIT {page*10}, 10'
    cur.execute(f'SELECT * {sql}',)
    rows = cur.fetchall()
    return [rows, pages]

def find_id(guild_id, page):
    conn = create_connection(DB_PATH)
    cur = conn.cursor()
    sql = f'FROM member_gear WHERE server_id={guild_id}'
    cur.execute(f'SELECT COUNT (*) {sql}')
    pages = cur.fetchone()[0]
    sql = f'{sql} ORDER BY gs DESC LIMIT {page*20}, 20'
    cur.execute(f'SELECT user_id, family_name {sql}',)
    rows = cur.fetchall()
    return [rows, pages]

def add_server_message(server_id, message, user_id):
    conn = create_connection(DB_PATH)
    sql = 'INSERT INTO server_messages(server_id,message,user_id) values (?,?,?)'
    cur = conn.cursor()
    payload = (server_id, message, user_id)
    cur.execute(sql, payload)
    conn.commit()
    return True

def get_server_message(server_id, all):
    conn = create_connection(DB_PATH)
    cur = conn.cursor()
    sql = f'SELECT message, user_id FROM server_messages WHERE server_id={server_id};'
    cur.execute(sql,)
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    if all:
        return list(rows)
    else:
        return [choice(list(rows))]

def get_item_price(item):
    conn = create_connection(DB_PATH)
    cur = conn.cursor()
    sql = 'SELECT * FROM enhancement WHERE item_id=?;'
    cur.execute(sql, (item,))
    rows = cur.fetchone()
    if not rows:
        return [False]
    return list(rows)

def save_item_price(item):
    conn = create_connection(DB_PATH)
    cur = conn.cursor()
    sql = 'INSERT OR REPLACE INTO enhancement (item_id, base, pri, duo, tri, tet, pen, last_update) values (?,?,?,?,?,?,?,?)'
    print(item)
    payload = (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
    cur.execute(sql, payload)
    conn.commit()
    return True