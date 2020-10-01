# import os

# from metaphone import doublemetaphone

# with open('bdoitems.html', 'r') as reader:
#     line = reader.readline()
#     counter = 1
#     items = []
#     while line != '':
#         if counter == 1:
#             item_id = int(line[18:][:-4])
#             counter = 2
#         elif counter == 2:
#             counter = 3
#         else:
#             counter = 1
#             item_name = line.split('<span></span>')[1].split('</b></a>')[0]
#             lcase_name = item_name.lower().strip().replace("(", "").replace(")", "").replace("-", "").replace("'",
#                                                                                                               "").replace(":", "").replace("[", "").replace("]", "").replace("/", " ").replace("  ", " ")
#             dmp = doublemetaphone(lcase_name)
#             items.append([item_id, item_name, dmp[0], dmp[1], lcase_name])
#             # print([item_id, item_name, dmp[0], dmp[1], lcase_name])
#         line = reader.readline()


import sqlite3

DB_PATH = '/home/jon/Documents/BDOGearBot/bin/bdo_items.db'
conn = sqlite3.connect(DB_PATH)

conn.enable_load_extension(True)
conn.load_extension("./bin/spellfix1.so")
conn.enable_load_extension(False)
cur = conn.cursor()
cur.execute("SELECT item_id, item_name, editdist3(lcase_name, 'backstar staf') AS edit_dist FROM item_names ORDER BY edit_dist ASC", )
rows = cur.fetchall()
print(rows)

# cur.execute('''
# CREATE TABLE IF NOT EXISTS item_names (
#     item_id int NOT NULL,
#     item_name text NOT NULL,
#     pri_phone text,
#     sec_phone text,
#     lcase_name text
# );''')

# cur.executemany(
#     "insert into item_names(item_id, item_name, pri_phone, sec_phone, lcase_name) values (?,?,?,?,?)", items)
# conn.commit()
# cur.execute("CREATE VIRTUAL TABLE leven_name USING spellfix1;", ) #!!! no longer need special leven table
# cur.execute(
#     "INSERT INTO leven_name(rowid, word) SELECT item_id, lcase_name FROM item_names;")
# conn.commit()

# look for duplicate item ids before uploading
# SELECT item_id, COUNT(*) FROM item_names GROUP BY item_id HAVING COUNT(*) > 1;
