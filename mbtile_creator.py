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


def main(infile, configfile, indir):
    (infilename, extension) = os.path.splitext(infile)
    basename = os.path.splitext(os.path.basename(infile))[0]

    # Extract parameters from config file
    config_list = open(configfile).read().splitlines()

    #TODO: Parse input folder for image file type and min/max zooms
    config_dict = {'format': 'png', 'minzoom': 16, 'maxzoom': 20}
    for pair in config_list:
        (key, value) = pair.split('=')
        config_dict[key] = value

    outfile = infilename + '.mbtiles'
    if os.path.exists(outfile):
        os.remove(outfile)
    sqlite_file = outfile
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    
    cursor.execute('CREATE TABLE metadata (name TEXT, value TEXT);')
    
    cursor.execute('''
    CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, 
                        tile_row INTEGER, tile_data BLOB);
    ''')
    
    cursor.execute('''
    CREATE UNIQUE INDEX tile_index on tiles (zoom_level, tile_column, tile_row);
    ''')

    #TODO: add a few more items such as Atribution and Center
    #TODO: might as well have the cursor iterate over the dict instead of this list
    tilesetmetadata = [('name', basename),
                       ('type', config_dict['type']),
                       ('description', config_dict['description']),
                       ('version', config_dict['version']),
                       ('format', config_dict['format']),
                       ('bounds', config_dict['bounds']),
                       ('minzoom', config_dict['minzoom']),
                       ('maxzoom', config_dict['maxzoom'])]
    
    cursor.executemany('''
    INSERT INTO metadata (name, value) VALUES(?,?)
    ''',tilesetmetadata)
    db.commit()

    # walk the folder full of tiles
    
    image_files = scandir(indir)

    for image_file in image_files:
        image_blob = open(image_file, "rb").read()

        # Extract Z, X, Y from image file path
        (image_filename, image_extension) = os.path.splitext(image_file)
        print('{}{}'.format(image_filename, image_extension))
        (z, x, tiley) = splitpathtozxy(image_filename)
        # MBTiles spec Y is upside down - subtract the tile y from max tile y
        y = int(math.pow(2.0, float(z)) - float(tiley) - 1.0)
        cursor.execute('''
        INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) 
                           VALUES(?,?,?,?)
        ''',(z,x,y,sqlite3.Binary(image_blob)))
        db.commit()
    
    db.commit()
    db.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help = "An input file as GeoJSON, shp, KML, "
                        "or gpkg, containing exactly one polygon.")
    parser.add_argument("-cf", "--config_file", help = "Configuration file")
    parser.add_argument("-d", "--input_dir", help = "Input directory of tile files")
    args = parser.parse_args()
    
    infile = args.infile
    (infilename, extension) = os.path.splitext(infile)
    conf_file = args.config_file if args.config_file else (infilename + '_config.txt')
    input_dir = args.input_dir if args.input_dir else '{}/'.format(infilename)
    
    main(infile, conf_file, input_dir)
