#     conn = create_connection(ITEM_DB_PATH)
#     if conn is not None:
#         cur = conn.cursor()
#         cur.execute('''
#         SELECT name FROM sqlite_master WHERE type='table' AND name='item_names';
#         ''')
#         row = cur.fetchall()
#         if len(row) == 0:
#             print('creating item table')
#             cur.execute('''
# CREATE TABLE IF NOT EXISTS item_names (
#     item_id int PRIMARY KEY,
#     item_name text NOT NULL,
#     pri_phone text,
#     sec_phone text,
#     lcase_name text
# );''')
#         else:
#             print('items table already exists')

# def batch_update_phone(params):
#     """[[pri_phone, sec_phone, item_id], ...]"""
#     conn = create_connection(ITEM_DB_PATH)
#     cur = conn.cursor()
#     cur.executemany("UPDATE item_names set pri_phone=?, sec_phone=? where item_id=?", params)
#     conn.commit()
#     cur.execute("drop TABLE leven_name;", )
#     cur.execute("CREATE VIRTUAL TABLE leven_name USING spellfix1;", )
#     cur.execute("INSERT INTO leven_name(rowid, word) SELECT item_id, lcase_name FROM item_names;")
#     conn.commit()

# def batch_add_mp():
#     """batch create metaphone entries"""
#     empty_mps = item_no_phone()
#     created_mps = []
#     for count, empty_mp in enumerate(empty_mps):
#         if count % 1000 == 0:
#             print(f'working on entry: {count}')
#         dmp = doublemetaphone(empty_mp[1])
#         created_mps.append([dmp[0], dmp[1] if len(
#             dmp[1]) > 0 else None, empty_mp[0]])
#     print('now sending data to db')
#     batch_update_phone(created_mps)