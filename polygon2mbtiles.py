#!/usr/bin/python3
"""
This script automates the use of the other scripts in this repository, allowing a user to call a single script that takes an Area of Interest polygon and creates an MBTile file. 

Arguments (using bash-style flags):

infile: An input file as GeoJSON, shp, KML, or gpkg, containing exactly one polygon. This is the only required parameter; all others are optional (and must be preceded with POSIX-style flags, only the input file is written without flags). 

-minz, --minzoom": Minimum tile level desired. Integer, defaults to 16
-maxz, --maxzoom": Maximum tile level desired. Integer, defaults to 20
-ts, --tileserver": A tile server where the needed tiles can be downloaded. Examples: digital_globe_standard, digital_globe_premium, bing (later versions will allow user to configure arbitrary tile servers). Defaults to digital_globe_standard.
-f, --format: Actual tiles can be changed from one file format to another, for example PNG to JPEG (useful for reducing file size). PNG or JPEG. 
-cs, --colorspace: JPEG files (but not PNG files) can be encoded either using RGB or YCbCr; the latter can be used for more aggressive compression with relatively little perceptible quality loss with most aerial imagery. RGB or YCBCR.
-q, --quality: JPEG compression quality setting, just as in any image processing software. Number from 1 to 100, defaults to 75. 

Example use:

Create an mbtile set from a GeoJSON polygon with all default setting:
python3 make_mbtiles_from_aoi.py myPolygon.geojson

Create an mbtile set with minimum zoom 12 and max 20, using Bing imagery:
python3 make_mbtiles_from_aoi.py mypolygon.geojson -minz 12 -maxz 20 -ts bing

Create an mbtile set with zoom and tileserver selected, verbose mode (so you'll see a lot of information flash by), clean mode (so all intermediate files are deleted), conversion from PNG format to JPEG with YCbCr colorspace and 70% quality setting, attributed to Digital Globe and versioned 1.1:
python3 make_mbtiles_from_aoi.py mypolygon.geojson -minz 12 -maxz 20 -ts digital_globe_premium -c -v -f JPEG -q 70 -cs YCBCR -a "Digital Globe Premium under the terms of use specified by DG for OpenStreetMap" -v 1.1 

"""
# Ivan Buendia Gayton, Humanitarian OpenStreetMap Team/Ramani Huria, 2018
import sys, os
import argparse

from create_tile_list import create_tile_list
from download_all_tiles_in_csv import download_all_tiles_in_csv
from convert_and_compress_tiles import convert_and_compress_tiles
from write_mbtiles import write_mbtiles

def set_defaults(opts):
    """Set sensible default options for MBTile creation. Does not overwrite 
       any values passed in, only uses defaults if values are None or absent.
    """
    defaults = [
        ('minzoom', 16),
        ('maxzoom', 20),
        ('tileserver', 'digital_globe_standard'),
        ('format', 'JPEG'),
        ('colorspace', 'RGB'),
        ('type', 'baselayer'),
        ('description', 'A tileset'),
        ('attribution', 'Copyright of the tile provider'),
        ('version', 1.0)
    ]
    for field, value in defaults:
        opts[field] = value if not opts.get(field) else opts[field]
    return opts

def polygon2mbtiles(opts):
    """Take an Area of Interest (AOI) polygon, return an MBtiles file."""
    infile = opts['infile']
    opts = set_defaults(opts)
    
    (basename, extension) = os.path.splitext(infile)
    csvfile = '{}_{}.csv'.format(basename, opts['tileserver'])
    foldername = '{}_{}'.format(basename, opts['tileserver'])

    print('\nCreating the CSV list of tiles to {}\n'.format(csvfile))
    create_tile_list(opts)
    print('Downloading the tiles into {}\n'.format(foldername))
    download_all_tiles_in_csv(csvfile)
    print('Converting all tiles to JPEG format to save space.')
    convert_and_compress_tiles(foldername)
    print('Writing the actual MBTiles file {}{}'.format(foldername, '.mbtiles'))

    opts['tiledir'] = foldername
    write_mbtiles(opts)
    
if __name__ == "__main__":

    arguments = [ # shortargument, longargument, helpargument
        ('-minz', '--minzoom', 'Minimum tile level desired.'),
        ('-maxz', '--maxzoom', 'Maximum tile level desired.'),
        ('-ts', '--tileserver', 'A server where the tiles can be downloaded:'
         ' digital_globe_standard, digital_globe_premium, bing, etc.'),
        ('-f', '--format', 'Output tile format: PNG, JPEG, or JPG'),
        ('-cs', '--colorspace', 'Color space of tile format: RGB or YCBCR.'),
        ('-q', '--quality', 'JPEG compression quality setting.'),
        ('-t', '--type', 'Layer type: overlay or baselayer.'),
        ('-d', '--description', 'Describe it however you like!'),
        ('-a', '--attribution', 'Should state data origin.'),
        ('-ver', '--version', 'The version number of the tileset (the actual data,'
         ' not the program)'),
    ]
    
    flags = [ # shortflag, longflag, action, help
        ('-v', '--verbose', 'store_true', 'Use if you want to see a lot of'
         ' command line output flash by!'),
        ('-c', '--clean', 'store_true', 'Delete intermediate files.')
    ]
    
    p = argparse.ArgumentParser()
    
    p.add_argument("infile", help = "An input file as GeoJSON, shp, KML, "
                        "or gpkg, containing exactly one polygon.")

    for shortarg, longarg, helparg in arguments:
        p.add_argument(shortarg, longarg, help = helparg)

    for shortarg, longarg, actionarg, helparg in flags:
        p.add_argument(shortarg, longarg, action = actionarg, help = helparg)

    opts = vars(p.parse_args())

    polygon2mbtiles(opts)
