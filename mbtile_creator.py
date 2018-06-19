#!/usr/bin/python3
"""Create an MBTile file according to the spec at 
https://github.com/mapbox/mbtiles-spec/blob/master/1.3/spec.md

"""
import sys, os
import sqlite3

sqlite_file = '/home/ivan/Documents/git/tilehuria/tiles/tester.mbtiles'
db = sqlite3.connect(sqlite_file)
cursor = db.cursor()

cursor.execute('''
CREATE TABLE metadata (name TEXT, value TEXT);
''')

cursor.execute('''
CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB);
''')

cursor.execute('''
CREATE UNIQUE INDEX tile_index on tiles (zoom_level, tile_column, tile_row);
''')

tilesetname = 'My very own tileset'

tilesetmetadata = [('name',tilesetname),
                   ('type','overlay'),
                   ('description','My Tileset'),
                   ('version',2.4),
                   ('format','png'),
                   ('bounds', '-180.0,-85,180,85'),
                   ('center', '-122.1906,37.7599,11'),
                   ('minzoom', 10),
                   ('maxzoom', 21)]

cursor.executemany('''
INSERT INTO metadata (name, value) VALUES(?,?)
''',tilesetmetadata)
db.commit()


with open("/home/ivan/Documents/git/tilehuria/tiles/1_0_0.png", "rb") as input_file:
    ablob = input_file.read()
    cursor.execute('''
    INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES(?,?,?,?)
    ''',(0,1,1,sqlite3.Binary(ablob)))
    db.commit()

db.commit()
db.close()
