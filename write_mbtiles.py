#!/usr/bin/python3
"""Create a raster MBTile file from a Slippy Map-style folder 
https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames) 
in (attempted) compliance with the spec at 
https://github.com/mapbox/mbtiles-spec/blob/master/1.3/spec.md
"""
# Ivan Buendia Gayton, Humanitarian OpenStreetMap Team/Ramani Huria, 2018
import sys, os
import sqlite3
import argparse
import math

def scandir(dir):
    """Walk recursively through a directory and return a list of all files in it"""
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(os.path.join(path, f))
    return filelist

def path_to_zxy(path):
    """Return zoom, x, y coordinates from the path of a tile in a slippy map folder"""
    splitpath = path.split('/')
    l = len(splitpath)
    (z,x,y) = (splitpath[l-3], splitpath[l-2], splitpath[l-1].split('.')[0])
    return (z,x,y)

def increment_bounds(zoom, x, y, left, bottom, right, top):
    """Takes zoom, x, y of tile and previous extents, returns bounds including tile"""
    n = math.pow(2.0, float(zoom))  # Tile rows/columns in world at this zoom level
    (zoom, x, y) = (float(zoom), int(x), int(y))
    newleft = (x / n * 360) - 180  # longitude of the left edge of this tile
    newright = ((x + 1) / n * 360) - 180  # lon of right edge of this tile
    newtop = (math.atan(math.sinh(math.pi * (1 - 2 * y / n)))) * 180 / math.pi
    newbott = (math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))) * 180 / math.pi
    
    left = newleft if newleft < left else left
    bottom = newbott if newbott < bottom else bottom
    right = newright if newright > right else right
    top = newtop if newtop > top else top
    return(left, bottom, right, top)

def write_mbtiles(opts):
    """Take a folder of tiles in Slippy Map-style schema, return an MBtiles file."""
    indir = opts['tiledir']
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
    maxz = 0  # Max zoom will be incremented when we actually find tiles
    minz = 23  # As above but decrementing
    # Set initial bounds at opposite sides of their global extents
    (left, bottom, right, top) = (180.0, 85.05113, -180.0, -85.05113)
    (centerlon, centerlat) = ('','')
    for image_file in image_files:
        (image_filename, image_ext) = os.path.splitext(image_file)
        # Don't add the file to the tileset if it's not an image
        if(image_ext == '.png' or image_ext == '.jpeg' or image_ext == '.jpg'):
            # Save a string with the filetype (extension) for use in metadata table
            #TODO: check if there are multiple file types and throw an error if so
            image_file_type = image_ext.replace('.','')
            image_blob = open(image_file, "rb").read()
            (z, x, tiley) = path_to_zxy(image_filename)
            # MBTiles spec Y is upside down - subtract the tile y from max tile y
            y = int(math.pow(2.0, float(z)) - float(tiley) - 1.0)
            cursor.execute('''
            INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) 
                               VALUES(?,?,?,?)
            ''',(z,x,y,sqlite3.Binary(image_blob)))
            db.commit()

            # Update min and max zoom levels and bounds for use in metadata table
            maxz = z if int(z) > int(maxz) else maxz  # Will end at correct max zoom
            minz = z if int(z) < int(minz) else minz  # As above for min zoom
            (left, bottom, right, top) = increment_bounds(z, x, tiley,
                                                          left, bottom,
                                                          right, top)
            centerlon = float(right) - float(left)
            centerlat = float(top) - float(bottom)
    
    cursor.execute('CREATE TABLE metadata (name TEXT, value TEXT);')
    tilesetmetadata = [('name', basename),
                       ('type', 'overlay'),
                       ('description', 'An MBTile set'),
                       ('attribution', 'Somebody made it'),
                       ('version', '1.0'),
                       ('format', image_file_type),
                       ('bounds', '{},{},{},{}'.format(left, bottom, right, top)),
                       # Don't include center as it crashes the Mapbox Android driver
                       #('center', '{},{}'.format(centerlon, centerlat)), 
                       ('minzoom', minz),
                       ('maxzoom', maxz)]
    cursor.executemany(
        '''INSERT INTO metadata (name, value) VALUES(?,?)''',tilesetmetadata)
    db.commit()
    db.close()
    
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("tiledir", help = "Input directory of tile files")
    p.add_argument("-f", "--format",
                   help = "Output tile file format: png, jpg, or jpeg")
    p.add_argument("-cs", "--colorspace",
                   help = "Color space of tile format: RGB or YCBCR.")
    p.add_argument("-t", "--type", help = "Layer type: overlay or baselayer.")
    p.add_argument("-d", "--description",
                   help = "Describe it however you like!")
    p.add_argument("-a", "--attribution", help = "Should state data origin.")
    p.add_argument("-v", "--version",
                   help = "The version number of the tileset "
                   "(the actual data, not the program)")
    
    opts = vars(p.parse_args())
        
    write_mbtiles(opts)
