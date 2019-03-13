#!/usr/bin/python3
"""
Create a geojson file containing a tile grid matching a slippy map tile zoom level. Takes a geojson polygon or multipolygon as input.
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

from geo_utils import create_poly_if_intersect
from geo_utils import get_ogr_driver
from geo_utils import get_extent
from geo_utils import get_geomcollection

from osgeo import ogr, osr    # Temporary until get this into geo_utils

from arguments import argumentlist, set_defaults

def create_tile_list(infile, optsin = {}):
    """Read a polygon file and create a set of output files to create tiles""" 
    opts = set_defaults(optsin)
    (infilename, extension) = os.path.splitext(infile)
    zoom = float(opts['zoom'])

    # Create a new geographical file of the same type as the input file
    # which will contain polygon outlines of all tiles
    outputGridfile = infilename + '_tile_perimeters' + extension    
    if os.path.exists(outputGridfile):
        os.remove(outputGridfile)
    try:
        driver = get_ogr_driver(extension)
        outDataSource = driver.CreateDataSource(outputGridfile)
        outLayer = outDataSource.CreateLayer(outputGridfile,
                                             geom_type=ogr.wkbPolygon)
        featureDefn = outLayer.GetLayerDefn()
    except Exception as e:
        print('Did not manage to create {}'.format(outputGridfile))
        print(e)

    TileX_field = ogr.FieldDefn('TileX',ogr.OFTInteger)
    outLayer.CreateField(TileX_field)
    TileY_field = ogr.FieldDefn('TileY',ogr.OFTInteger)
    outLayer.CreateField(TileY_field)
    TileZ_field = ogr.FieldDefn('TileZ',ogr.OFTInteger)
    outLayer.CreateField(TileZ_field)
    
    (xmin, xmax, ymin, ymax) = get_extent(infile, extension)
    geomcollection = get_geomcollection(infile, extension)    
        
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
            poly = create_poly_if_intersect(tileX, tileY, zoom, geomcollection)
            if poly:
                # Add the tile outline to the perimeters file
                outFeature = ogr.Feature(featureDefn)
                outFeature.SetGeometry(poly)
                #print('setting tile x')
                outFeature.SetField('tileX', tileX)
                #print('setting tile y')
                outFeature.SetField('tileY', tileY)
                #print('setting tile zoom')
                outFeature.SetField('tileZ', zoom)
                outLayer.CreateFeature(outFeature)
                outFeature.Destroy
                
    outDataSource.Destroy()

    print('\nInput file: ' + infile)
    print('Output files:\n{}\n'.format(outputGridfile))
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
