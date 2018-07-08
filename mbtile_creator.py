#!/usr/bin/python3
"""Create an MBTile file according to the spec at 
https://github.com/mapbox/mbtiles-spec/blob/master/1.3/spec.md

"""
import sys, os
import sqlite3
import argparse

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

    image_files = os.listdir(indir)

    for image_file in image_files:
        #TODO: fix this so it also works on Windows
        image_blob = open(indir + '/' + image_file, "rb").read()

        # Extract Z, X, Y from image file name; assumes tile files are named x_y_z.ext
        (image_filename, image_extension) = os.path.splitext(image_file)
        print(image_filename)
        (z, x, y) = image_filename.split('_')
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
