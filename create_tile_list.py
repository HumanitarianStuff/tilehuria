#!/bin/python3
"""Create a CSV document containing a list of URLs of tiles from a Tile Map Service (TMS or tileserver).

Arguments (using bash-style flags):

infile: An input file as GeoJSON, shp, KML, or gpkg, containing exactly one polygon.

-minz, --minzoom",Minimum tile level desired
-maxz, --maxzoom",Maximum tile level desired
-ts, --tileserver",A tile server where the needed tiles can be downloaded: digital_globe_standard digital_globe_premium, bing, etc

examples:

python3 create_tile_list.py /path/to/myPolygon.geojson

or, if the default zoom levels are not what you want:

python3 create_tile_list.py /path/to/myPolygon.geojson -minz 15 -maxz 21

"""
# Ivan Buendia Gayton, Humanitarian OpenStreetMap Team/Ramani Huria 2018

import os
import sys
import argparse
from math import ceil
import math
from osgeo import ogr, osr
import csv
import re
import random

def get_ogr_driver(extension):
    driver = None
    if extension == '.shp':
        driver = ogr.GetDriverByName('ESRI Shapefile')
    elif extension == '.geojson':
        driver = ogr.GetDriverByName('GeoJSON')
    elif extension == '.kml':
        driver = ogr.GetDriverByName('KML')
    elif extension == '.gpkg':
        driver = ogr.GetDriverByName('GPKG')
    else:
        print('Check input file format for '+infile)
        print('Supported formats shp, geojson, kml, gpkg (GeoPackage)')
        sys.exit()
    return driver

def lat_long_zoom_to_pixel_coords(lat, lon, zoom):
    """Create pixel coordinates from lat-long point at a given zoom level"""
    sinLat = math.sin(lat * math.pi/180.0)
    x = int(math.floor(((lon + 180) / 360) * 256 * math.pow(2, zoom)))
    y = int(math.floor((0.5 - math.log((1 + sinLat) / (1 - sinLat))
        / (4 * math.pi)) * 256 * math.pow(2,zoom)))
    return(x, y)

def pixel_coords_to_tile_address(x,y):
    """Create a tile address from pixel coordinates of point within tile."""
    x = int(math.floor(x / 256))
    y = int(math.floor(y / 256))
    return (x, y)

def fill_placeholders_in_url(url):
    """Randomized replacement from a switch statement in curly braces within a URL"""
    regex = r"\{(.*?)\}"
    matches = re.finditer(regex, urlf, re.MULTILINE | re.DOTALL)
    for matchNum, match in enumerate(matches):
        for groupNum in range(0, len(match.groups())):
            print(match.group(1))

def tile_coords_zoom_and_tileserver_to_URL(TileX, TileY, zoom, tileserver):
    """Create a URL for a tile based on tile coordinates and zoom"""
    URL = ''
    if tileserver=='bing':
        quadKey = tile_coords_and_zoom_to_quadKey(
            int(TileX),int(TileY),int(zoom))
        switchserver = random.choice([0,1,2,3])
        URL = ("http://t{}.tiles.virtualearth.net/tiles/a{}.jpeg?"
                "g=854&mkt=en-US&token="
               "AopsdXjtTu-IwNoCTiZBtgRJ1g7yPkzAi65nXplc-eLJwZHYlAIf2yuSY_Kjg3Wn"
               .format(switchserver, quadKey))
    elif tileserver=='digital_globe_standard':
        switchserver = random.choice(['a', 'b', 'c', 'd'])
        URL = ("https://{}.tiles.mapbox.com/v4/digitalglobe.0a8e44ba"
               "/{}/{}/{}.png?access_token="
               "pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZGFrZ3pjczNpaH"
               "YycXFyMGo0djY3N2IifQ.90uebT4-ow1uqZKTUrf6RQ"
               .format(switchserver, zoom, TileX, TileY))
    elif tileserver=='digital_globe_premium':
        switchserver = random.choice(['a', 'b', 'c', 'd'])
        URL = ("https://{}.tiles.mapbox.com/v4/digitalglobe.316c9a2e"
               "/{}/{}/{}.png?access_token="
               "pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZGFrZ2c2dzFlMW"
               "gyd2x0ZHdmMDB6NzYifQ.9Pl3XOO82ArX94fHV289Pg"
               .format(switchserver, zoom, TileX, TileY))
    elif tileserver=='google':
        switchserver = random.choice([0,1,2,3]) 
        URL = ("https://mt{}.google.com/vt/lyrs=s&hl=en&x={}&y={}&z={}"
               .format(switchserver, TileX, TileY, zoom))
    elif tileserver=='osm':
        pass
    elif tileserver=='custom':
        pass
    else:
        print('\nWhatever tileserver you think you are using is not working out')
    return URL

def tile_coords_and_zoom_to_quadKey(x, y, zoom):
    """Create a quadkey from xyzoom coordinates for Bing-style tileservers."""
    quadKey = ''
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if(x & mask) != 0:
            digit += 1
        if(y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey

def main(infile, minzoom, maxzoom, tileserver):
    """Read a polygon file and create a set of output files to create tiles"""
    (infilename, extension) = os.path.splitext(infile)
    driver = get_ogr_driver(extension)
    datasource = driver.Open(infile, 0)
    layer = datasource.GetLayer()
    layer_defn = layer.GetLayerDefn()
    extent = layer.GetExtent()
    (xmin, xmax, ymin, ymax) = (extent[0], extent[1], extent[2], extent[3])
    geomcollection = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in layer:
        geomcollection.AddGeometry(feature.GetGeometryRef())

    # Create the main output file which will contain the URL list
    #TODO use the CSV library for this instead of just writing strings
    outfile = infilename + '_' + tileserver + '.csv'
    if os.path.exists(outfile):
        os.remove(outfile)
    output_csv = open(outfile, 'w')
    writer = csv.writer(output_csv, delimiter = ';')
    writer.writerow(['wkt','Tilex','TileY','TileZ','URL'])
#    output_csv.write('wkt;TileX;TileY;TileZ;URL\n')

    # Create a new geographical file of the same type as the input file
    # which will contain polygon outlines of all tiles
    outputGridfile = infilename + '_tile_perimeters' + extension    
    if os.path.exists(outputGridfile):
        os.remove(outputGridfile)
    outDataSource = driver.CreateDataSource(outputGridfile)
    outLayer = outDataSource.CreateLayer(outputGridfile,geom_type=ogr.wkbPolygon)
    featureDefn = outLayer.GetLayerDefn()

    for zoom in range(int(minzoom), int(maxzoom)+1):
        TileX_field = ogr.FieldDefn('TileX',ogr.OFTInteger)
        outLayer.CreateField(TileX_field)
        TileY_field = ogr.FieldDefn('TileY',ogr.OFTInteger)
        outLayer.CreateField(TileY_field)
        TileZ_field = ogr.FieldDefn('TileZ',ogr.OFTInteger)
        outLayer.CreateField(TileZ_field)
        URL_field = ogr.FieldDefn('URL' , ogr.OFTString)
        outLayer.CreateField(URL_field)
    
        # get coordinate address of upper left left tile
        pixel = lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
        tile = pixel_coords_to_tile_address(pixel[0], pixel[1])
        TileX_left = tile[0]
        TileY_top = tile[1]
        
        # get coordinate address of lower right tile
        pixel = lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
        tile = pixel_coords_to_tile_address(pixel[0], pixel[1])    
        TileX_right = tile[0]
        TileY_bottom = tile[1]

        for TileY in range(TileY_top,TileY_bottom+1):
            for TileX in range(TileX_left,TileX_right+1):
                # Calculate lat, lon of upper left corner of tile
                PixelX = TileX * 256
                PixelY = TileY * 256
                MapSize = 256*math.pow(2,zoom)
                x = (PixelX / MapSize) - 0.5
                y = 0.5 - (PixelY / MapSize)
                lonleft = 360 * x
                lattop = (90-360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi)
    
                # Calculate lat, lon of lower right corner of tile
                PixelX = (TileX+1) * 256
                PixelY = (TileY+1) * 256
                MapSize = 256*math.pow(2,zoom)
                x = (PixelX / MapSize) - 0.5
                y = 0.5 - (PixelY / MapSize)
                lonright = 360 * x
                latbottom = (90 - 360 * math.atan(math.exp(-y * 2 * math.pi))/math.pi)
    
                # Create a polygon to check if it is in the AOI and, if so, to write
                ring = ogr.Geometry(ogr.wkbLinearRing)
                ring.AddPoint(lonleft, lattop)
                ring.AddPoint(lonright, lattop)
                ring.AddPoint(lonright, latbottom)
                ring.AddPoint(lonleft, latbottom)
                ring.AddPoint(lonleft, lattop)
                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)
    
                # Check if tile is within the polygon of the Area of Interest.
                intersect = geomcollection.Intersect(poly)
                if intersect == True:
                    # Tile is in the AOI. Add a row to the CSV for this tile.
                    wkt_outline = '\"{}\"'.format(poly.ExportToWkt())
                    URL = tile_coords_zoom_and_tileserver_to_URL(
                        int(TileX), int(TileY), int(zoom), tileserver)    
                    writer.writerow([wkt_outline,
                                     str(TileX), str(TileY), str(zoom), URL])
                    outFeature = ogr.Feature(featureDefn)
                    outFeature.SetGeometry(poly)
                    if extension == 'kml':
                        col_row_zoom = (str(TileX)+'_'+str(TileY)+'_'
                                        +str(int(zoom)))
                        outFeature.SetField('name', col_row_zoom)
                        desc = (str(TileX) + "_" + str(TileY) + "_"
                                + str(int(zoom)) + "\nTile URL: " + URL)
                        outFeature.SetField('description', desc)
                    else:
                        outFeature.SetField('TileX', TileX)
                        outFeature.SetField('TileY', TileY)
                        outFeature.SetField('TileZ', zoom)
                        outFeature.SetField('URL', URL)

                    outLayer.CreateFeature(outFeature)
                    outFeature.Destroy

    # Close DataSources - without this you'll get a segfault from OGR.
    outDataSource.Destroy()

    # Inform the user of completion and summarize created assets to stdout
    print('\nInput file: '+infile)
    print('Zoom levels: {} to {}'.format(str(minzoom), str(maxzoom)))
    print('Output files:\n{}\n{}\n'
          .format(outfile, outputGridfile))
    print()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help = "An input file as GeoJSON, shp, KML, "
                        "or gpkg, containing exactly one polygon.")
    parser.add_argument("-minz", "--minzoom", help = "Minimum tile level desired")
    parser.add_argument("-maxz", "--maxzoom", help = "Maximum tile level desired")
    parser.add_argument("-ts", "--tileserver", help = "A tile server where the"
                        "needed tiles can be downloaded: digital_globe_standard, "
                        "digital_globe_premium, bing, etc")
    
    args = parser.parse_args()
    
    infile = args.infile
    minz = args.minzoom if args.minzoom else 16
    maxz = args.maxzoom if args.maxzoom else 20
    tileserver = args.tileserver if args.tileserver else 'digital_globe_standard'

    print('tileserver is {}'.format(tileserver))

    main(infile, minz, maxz, tileserver)
