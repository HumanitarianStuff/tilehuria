#!/usr/bin/python3
"""Create an MBTile file according to the spec at 
https://github.com/mapbox/mbtiles-spec/blob/master/1.3/spec.md

"""
import sys, os
import sqlite3
import argparse

def main(infile, minz, maxz, laytype, desc, version, tile_format, tileserver):
    try:
        (infilename, extension) = os.path.splitext(infile)
    except:
        print('Check input file')
        sys.exit()

    # Call the tile list creator to make a CSV. Get the bounds, center, tileserver 



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

    tilesetmetadata = [('name', infilename),
                       ('type', laytype),
                       ('description', desc),
                       ('version', version),
                       ('format', tile_format),
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
    
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help = "An input file as GeoJSON, shp, KML, "
                        "or gpkg, containing exactly one polygon.")
    parser.add_argument("-minz", "--minzoom", help = "Minimum tile level desired")
    parser.add_argument("-maxz", "--maxzoom", help = "Maximum tile level desired")
    parser.add_argument("-d", "--description", help = "Description of the tileset")
    parser.add_argument("-tp", "--type", help = "Tileset type: overlay or baselayer")
    parser.add_argument("-ver", "--version", help = "Version of the tileset")
    parser.add_argument("-f", "--format", help = "Format of the tile images"
                        ", png, png8, or jpeg")
    parser.add_argument("-ts", "--tileserver", help = "A tile server where the"
                        "needed tiles can be downloaded: digital_globe_standard, "
                        "digital_globe_premium, bing, etc")
    
    args = parser.parse_args()
    
    infile = args.infile
    minz = args.minzoom if args.minzoom else 16
    maxz = args.maxzoom if args.maxzoom else 20
    laytype = args.type if args.type else 'baselayer'
    version = args.version if args.version else '1.0'
    tile_format = args.format if args.format else 'png'
    desc = args.description if args.description else 'A set of MBTiles'
    tileserver = args.tileserver if args.tileserver else 'digital_globe_standard'

    main(infile, minz, maxz, laytype, desc, version, tile_format, tileserver)
