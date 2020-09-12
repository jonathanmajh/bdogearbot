
import sqlite3
from sqlite3 import Error
from models import GearData

def create_connection(DB_PATH):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn

def table_check(conn):
    """
    Check if member_gear table exists and creates if necessary
    """
    if conn is not None:
        cur = conn.cursor()
        cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='member_gear';
        ''')
        row = cur.fetchall()
        if len(row) == 0:
            print('creating table')
            cur.execute('''
            CREATE TABLE member_gear (
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
                );
            ''')
        else:
            print('table already exists')
        return True

def update_gear(conn, gear_data):
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

def find_gear(conn, find):
    cur = conn.cursor()
    sql = f'SELECT * FROM member_gear WHERE user_id={find[0]}'
    if len(find) == 2:
        sql = sql + f' AND gear_type="{find[1]}"'
    print(sql)
    cur.execute(sql, )
    rows = cur.fetchall()
    return rows
    
def find_average(conn, find):
    cur = conn.cursor()
    sql = f'SELECT gs FROM member_gear WHERE server_id={find[0]}'
    if len(find) == 2:
        sql = sql + f' AND gear_type="{find[1]}"'
    print(sql)
    cur.execute(sql,)
    rows = cur.fetchall()
    return rows

def find_all(conn, find):
    cur = conn.cursor()
    sql = f'SELECT * FROM member_gear WHERE server_id={find[0]}'
    if len(find) == 2:
        sql = sql + f' AND gear_type="{find[1]}"'
    sql = sql + ' ORDER BY gs DESC'
    print(sql)
    cur.execute(sql,)
    rows = cur.fetchall()
    return rows