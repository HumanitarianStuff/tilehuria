#!/usr/bin/python3
"""
Create a set of MBTiles from a Slippy Map tileserver.
"""
# Ivan Buendia Gayton, Humanitarian OpenStreetMap Team/Ramani Huria, 2018
import sys, os
import argparse

from create_tile_list import create_tile_list
from download_all_tiles_in_csv import download_all_tiles_in_csv
from convert_and_compress_tiles import convert_and_compress_tiles
from write_mbtiles import write_mbtiles
from arguments import argumentlist, set_defaults

def polygon2mbtiles(*args, **kwargs):
    """Take an Area of Interest (AOI) polygon, return an MBtiles file."""
    if not infile:
        print('Please provide an input file')
        exit(1)
    opts = set_defaults(kwargs)    
    (basename, extension) = os.path.splitext(infile)
    csvfile = '{}_{}.csv'.format(basename, opts['tileserver'])
    foldername = '{}_{}'.format(basename, opts['tileserver'])

    print('\nCreating the CSV list of tiles in {}\n'.format(csvfile))
    create_tile_list(infile, **opts)
    
    print('Downloading the tiles into {}\n'.format(foldername))
    opts['csvinfile'] = csvfile
    download_all_tiles_in_csv(opts)
    
    print('Converting all tiles to JPEG format to save space.')
    convert_and_compress_tiles(foldername)
    
    print('Writing the actual MBTiles file {}{}'.format(foldername, '.mbtiles'))
    opts['tiledir'] = foldername
    write_mbtiles(opts)
    
if __name__ == "__main__":

    arguments = argumentlist()
    p = argparse.ArgumentParser()
    
    p.add_argument('infile', help = "Input file as GeoJSON polygons")
    
    for (shortarg, longarg, actionarg, helpstring, defaultvalue) in arguments:
        p.add_argument('-{}'.format(shortarg), '--{}'.format(longarg),
                       action = actionarg,  help = helpstring)

    opts = vars(p.parse_args())
    infile = opts['infile']
    polygon2mbtiles(infile, **opts)
