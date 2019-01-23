#!/usr/bin/python3
"""
Create a CSV document containing a list of URLs of tiles from a Tile Map Service 
(TMS or tileserver).
"""
# Ivan Buendia Gayton, Humanitarian OpenStreetMap Team/Ramani Huria 2018
import sys, os
import argparse
import csv
import math

from utils import lat_long_zoom_to_pixel_coords
from utils import pixel_coords_to_tile_address
from utils import tile_coords_to_url
from utils import tile_coords_to_quadkey
from utils import url_template_from_file

from geo_utils import intersect
from geo_utils import get_ogr_driver
from geo_utils import get_extent
from geo_utils import get_geomcollection

from arguments import argumentlist, set_defaults

def create_tile_list(infile, optsin = {}):
    """Read a polygon file and create a set of output files to create tiles"""
    #print('\nThe opts received by create_tile_list are:{}'.format(type(optsin)))
    #print('\nThe opts received by create_tile_list are:\n{}\n'.format(optsin)) 
    opts = set_defaults(optsin)
    url_template = (opts['url_template'] if opts['url_template']
                    else url_template_from_file(opts['tileserver']))
    #print(url_template)
    #print('\nThe opts returned by set_defaults are:{}'.format(type(opts)))
    #print('\nThe opts returned by set_defaults are:\n{}\n'.format(opts))
    (infilename, extension) = os.path.splitext(infile)
    minzoom = opts['minzoom']
    maxzoom = opts['maxzoom']
    tileserver = opts['tileserver'] if opts['tileserver'] else 'from_url'

    # Create the main output file which will contain the URL list
    outfile = '{}_{}.csv'.format(infilename, tileserver)
    if os.path.exists(outfile):
        os.remove(outfile)
    writer = csv.writer(open(outfile, 'w'), delimiter = ';')
    writer.writerow(['wkt','Tilex','TileY','TileZ','URL'])

    (xmin, xmax, ymin, ymax) = get_extent(infile, extension)
    geomcollection = get_geomcollection(infile, extension)
    
    for zoom in range(int(minzoom), int(maxzoom)+1):
        
        # get coordinate address of upper left left tile
        pixel = lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
        tile = pixel_coords_to_tile_address(pixel[0], pixel[1])
        tileX_left = tile[0]
        tileY_top = tile[1]
        
        # get coordinate address of lower right tile
        pixel = lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
        tile = pixel_coords_to_tile_address(pixel[0], pixel[1])    
        tileX_right = tile[0]
        tileY_bottom = tile[1]

        for tileY in range(tileY_top, tileY_bottom + 1):
            for tileX in range(tileX_left, tileX_right + 1):
                if intersect(tileX, tileY, zoom, geomcollection):
                    wkt_outline = '\"{}\"'.format(intersect)
                    URL = tile_coords_to_url(int(tileX), int(tileY),
                                             int(zoom), url_template)    
                    writer.writerow([wkt_outline,
                                     str(tileX), str(tileY), str(zoom), URL])

    print('\nInput file: ' + infile)
    print('Zoom levels: {} to {}'.format(str(minzoom), str(maxzoom)))
    print('Output files:\n{}\n'
          .format(outfile))
    print()

if __name__ == "__main__":

    arguments = argumentlist()
    p = argparse.ArgumentParser()
    
    p.add_argument('infile', help = "Input file as GeoJSON polygons")
    
    for (shortarg, longarg, actionarg, helpstring, defaultvalue) in arguments:
        p.add_argument('-{}'.format(shortarg), '--{}'.format(longarg),
                       action = actionarg,  help = helpstring)

    opts = vars(p.parse_args())
    infile = opts['infile']

    create_tile_list(infile, opts)
