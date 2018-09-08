#!/usr/bin/python3
"""Create an MBTile file according to the spec at 
https://github.com/mapbox/mbtiles-spec/blob/master/1.3/spec.md

"""
import sys, os
import sqlite3
import argparse
import math

def scandir(dir):
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(os.path.join(path, f))
    return filelist

def splitpathtozxy(path):
    splitpath = path.split('/')
    l = len(splitpath)
    (z,x,y) = (splitpath[l-3], splitpath[l-2], splitpath[l-1].split('.')[0])
    return (z,x,y)


def main(indir):
    basename = indir
    outfile = indir + '.mbtiles'
    if os.path.exists(outfile):
        os.remove(outfile)
    sqlite_file = outfile
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, 
                        tile_row INTEGER, tile_data BLOB);''')
    cursor.execute('''
    CREATE UNIQUE INDEX tile_index on tiles (zoom_level, tile_column, tile_row);''')
    
    image_files = scandir(indir)
    image_file_type = ''
    maxz = 0
    minz = 23
    for image_file in image_files:
        (image_filename, image_ext) = os.path.splitext(image_file)
        if(image_ext == '.png' or image_ext == '.jpeg' or image_ext == '.jpg'):
            image_file_type = image_ext.replace('.','')
            #TODO: check if there are multiple file types and throw an error if so
            image_blob = open(image_file, "rb").read()
            # Extract Z, X, Y from image file path
            (z, x, tiley) = splitpathtozxy(image_filename)
            maxz = z if int(z) > int(maxz) else maxz
            minz = z if int(z) < int(minz) else minz
            # MBTiles spec Y is upside down - subtract the tile y from max tile y
            y = int(math.pow(2.0, float(z)) - float(tiley) - 1.0)
            cursor.execute('''
            INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) 
                               VALUES(?,?,?,?)
            ''',(z,x,y,sqlite3.Binary(image_blob)))
            db.commit()
    
    # Extract parameters from config file
    cursor.execute('CREATE TABLE metadata (name TEXT, value TEXT);')

    #TODO: add a few more items such as Atribution and Center
    #TODO: might as well have the cursor iterate over the dict instead of this list
    tilesetmetadata = [('name', basename),
                       ('type', 'overlay'),
                       ('description', 'An MBTile set'),
                       ('version', '1.0'),
                       ('format', image_file_type),
                       ('bounds', ''),
                       ('minzoom', minz),
                       ('maxzoom', maxz)]
    
    cursor.executemany('''
    INSERT INTO metadata (name, value) VALUES(?,?)
    ''',tilesetmetadata)
    db.commit()

    db.commit()
    db.close()

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("input_dir", help = "Input directory of tile files")
    args = parser.parse_args()
    
    input_dir = args.input_dir  
    
    main(input_dir)
