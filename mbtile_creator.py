#!/usr/bin/python3
import sys, os
import sqlite3

sqlite_file = '/home/ivan/Documents/git/tilehuria/mbtiles_01.sqlite'
db = sqlite3.connect(sqlite_file)
cursor = db.cursor()

cursor.execute('''
CREATE TABLE metadata (name text, value text);
''')

cursor.execute('''
CREATE TABLE tiles (zoom_level integer, tile_column integer, tile_row integer, tile_data blob);
''')

cursor.execute('''
CREATE UNIQUE INDEX tile_index on tiles (zoom_level, tile_column, tile_row)
''')

db.commit()
db.close()
