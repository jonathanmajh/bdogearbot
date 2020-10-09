import requests
from metaphone import doublemetaphone
import sqlite3

URL = f'https://bdocodex.com/query.php?a=items&type=version&slot=20200916&l=us'
data = requests.get(URL)
if data.status_code == 200:
    data = data.json()['aaData']
    for item in data:
        items = []
        item_id = item[0]
        item_name = item[2].split('<span></span>')[1].split('</b></a>')[0]
        lcase_name = item_name.lower().strip().replace("(", "").replace(")", "").replace("-", "").replace("'","").replace(":", "").replace("[", "").replace("]", "").replace("/", " ").replace("  ", " ")

        dmp = doublemetaphone(lcase_name)
        items.append([item_id, item_name, dmp[0], dmp[1], lcase_name])
    print("fetched")
else:
    print('url is invalid')

DB_PATH = '/home/jon/Documents/BDOGearBot/bin/bdo_items.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executemany(
    "insert into item_names(item_id, item_name, pri_phone, sec_phone, lcase_name) values (?,?,?,?,?)", items)
conn.commit()
print(cur.fetchall())
# not available on mp