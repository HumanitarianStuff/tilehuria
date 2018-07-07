#!/usr/bin/python3
"""Create an MBTile file according to the spec at 
https://github.com/mapbox/mbtiles-spec/blob/master/1.3/spec.md

"""
import sys, os
import sqlite3
import argparse

def main(infile, tstype, desc, vers, fmt, bnds, cntr, minz, maxz):
    infilename, extension = os.path.splitext(infile)
    sqlite_file = 'local_data/tiles/' + infilename + '.mbtiles'
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    
    cursor.execute('''
    CREATE TABLE metadata (name TEXT, value TEXT);
    ''')
    
    cursor.execute('''
    CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, 
                        tile_row INTEGER, tile_data BLOB);
    ''')
    
    cursor.execute('''
    CREATE UNIQUE INDEX tile_index on tiles (zoom_level, tile_column, tile_row);
    ''')

    tilesetmetadata = [('name',infilename),
                       ('type', tstype),
                       ('description', desc),
                       ('version', vers),
                       ('format', fmt),
                       ('bounds', bnds),
                       ('center', cntr),
                       ('minzoom', minz),
                       ('maxzoom', maxz)]
    
    cursor.executemany('''
    INSERT INTO metadata (name, value) VALUES(?,?)
    ''',tilesetmetadata)
    db.commit()
    
    
    with open(infile, "rb") as input_file:
        ablob = input_file.read()
        cursor.execute('''
        INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) 
                           VALUES(?,?,?,?)
        ''',(0,1,1,sqlite3.Binary(ablob)))
        db.commit()
    
    db.commit()
    db.close()
    
if __name__ == "__main__":

    # Default arguments to be overwritten by user-supplied arguments
    minz = 16
    maxz = 20
    type = overlay
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help = "An input file")
    parser.add_argument("-mz", "--minzoom", help = "Minimum tile level desired")
    
    args = parser.parse_args()
    infile = args.infile


    #main(infile, tstype, desc, vers, fmt, bnds, cntr, minz, maxz)
    print(infile, tstype, desc, vers, fmt, bnds, cntr, minz, maxz)
