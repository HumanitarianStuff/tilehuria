#!/bin/python3
# Ivan Buendia Gayton, Ramani Huria 2018
"""Create a CSV document containing a list of tile URLs for classification.

Arguments:
    [1] A single-ring polygon, either a local file (shp, KML, GeoJSON) or URL
    [2] A zoom level for the desired output (search tileserver zoom to learn)
    [3] A tileserver name (bing, digital_globe_standard, or google)

example run:
    $ python create_tile_list.py polygon.shp 18
        - without third argument, default tileserver is Bing

    $ python create_tile_list.py polygon.shp 18 digital_globe
        - Uses Digital Globe tileserver (requires an API key)
"""

import os
import sys
from math import ceil
import math
#import urlparse
#import urllib

class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Tile:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

def lat_long_zoom_to_pixel_coords(lat, lon, zoom):
    """Create pixel coordinates from lat-long point at a given zoom level"""
    p = Point()
    sinLat = math.sin(lat * math.pi/180.0)
    x = ((lon + 180) / 360) * 256 * math.pow(2,zoom)
    y = (0.5 - math.log((1 + sinLat) / (1 - sinLat))
        / (4 * math.pi)) * 256 * math.pow(2,zoom)
    p.x = int(math.floor(x))
    p.y = int(math.floor(y))
    return p

def pixel_coords_to_tile_address(x,y):
    """Create a tile address from pixel coordinates of point within tile."""
    t = Tile()
    t.x = int(math.floor(x / 256))
    t.y = int(math.floor(y / 256))
    return t

def tile_coords_zoom_and_tileserver_to_URL(
        TileX, TileY, zoom, tileserver, api_key):
    """Create a URL for a tile based on tile coordinates and zoom"""
    URL = ''
    if tileserver=='bing':
        quadKey = tile_coords_and_zoom_to_quadKey(
            int(TileX),int(TileY),int(zoom))
        URL = quadKey_to_Bing_URL(quadKey, api_key)
    elif tileserver=='digital_globe_standard':
        switchserver='a' # TODO: make this alternate between a-d
        URL = ("{}.tiles.mapbox.com/v4/digitalglobe.0a8e44ba"
               "/{}/{}/{}.png?access_token={}"
               .format(switchserver, zoom, TileX, TileY, api_key))
    elif tileserver=='google':
        URL = ("https://mt0.google.com/vt/lyrs=s&hl=en&x={}&y={}&z={}\n"
               .format(TileX, TileY, zoom))
    elif tileserver=='osm':
        pass
    elif tileserver=='custom':
        pass
    else:
        print('\nWhatever tileserver you think you are using is not happening')

    return URL

def tile_coords_and_zoom_to_quadKey(x, y, zoom):
    """Create a quadkey for use with certain tileservers that use them."""
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

def quadKey_to_Bing_URL(quadKey, api_key):
    """Create a URL linking to a Bing tile server"""
    tile_url = ("http://t0.tiles.virtualearth.net/tiles/a{}.jpeg?"
                "g=854&mkt=en-US&token={}".format(quadKey, api_key))
    #print("\nThe tile URL is: {}".format(tile_url))
    return tile_url


def main(infile, minzoom, maxzoom, tileserver):
    try:
        from osgeo import ogr, osr
        #print("Import of ogr and osr from osgeo worked.  Hurray!\n")
    except:
        print('############ ERROR ######################################')
        print('## Import of ogr from osgeo failed\n\n')
        print('#########################################################')
        sys.exit()

    try:
        infile_name = infile.split('.')[0]
        infile_extension = infile.split('.')[-1]
    except:
        print("check input file")
        sys.exit()

    # Get API key from local text file
    try:
        if tileserver == 'bing':
            f = open('bing_api_key.txt')
            api_key = f.read()
        elif tileserver == 'digital_globe_standard':
            f = open('api_keys/dg_standard_api_key.txt')
            api_key = f.read()
        elif tileserver == 'google':
            f = open('google_api_key.txt')
            api_key = f.read()
        elif tileserver == 'osm':
            pass
    except:
        print("Something is wrong with your API key."
               "Do you even have an API key?")

    # Get the driver (shapefile, geopackage, GeoJSON, or KML)
    if infile_extension == 'shp':
        driver = ogr.GetDriverByName('ESRI Shapefile')
    elif infile_extension == 'geojson':
        driver = ogr.GetDriverByName('GeoJSON')
    elif infile_extension == 'kml':
        driver = ogr.GetDriverByName('KML')
    elif infile_extension == gpkg:
        driver = ogr.GetDriverByName('GPKG')
    else:
        print('Check input file format for '+infile)
        print('Supported formats .shp .geojson .kml')
        sys.exit()

    # open the data source
    datasource = driver.Open(infile, 0)
    try:
        # Get the data layer
        layer = datasource.GetLayer()
    except:
        print('Error, please check input file!')
        print('## '+infile)
        sys.exit()

    # Get layer definition
    layer_defn = layer.GetLayerDefn()

    # Get layer extent
    extent = layer.GetExtent()
    xmin = extent[0]
    xmax = extent[1]
    ymin = extent[2]
    ymax = extent[3]

    # get feature geometry of all features of the input file
    geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in layer:
        geomcol.AddGeometry(feature.GetGeometryRef())

    # create output file
    outputGridfn = infile_name + '_tiles.' + infile_extension

    outfile = infile_name + '_' + tileserver + '_tiles.csv'
    l = 0
    if os.path.exists(outfile):
        os.remove(outfile)
    fileobj_output = open(outfile,'w')
    fileobj_output.write('wkt$TileX$TileY$TileZ$URL\n')

    outDriver = driver
    if os.path.exists(outputGridfn):
        os.remove(outputGridfn)
    outDataSource = outDriver.CreateDataSource(outputGridfn)
    outLayer = outDataSource.CreateLayer(outputGridfn,geom_type=ogr.wkbPolygon)
    featureDefn = outLayer.GetLayerDefn()

    # Iterate through all zoom levels requested
    for zoom in range(int(minzoom),int(maxzoom)+1):
        # create fields for TileX, TileY, TileZ
        TileX_field = ogr.FieldDefn('TileX',ogr.OFTInteger)
        outLayer.CreateField(TileX_field)
        TileY_field = ogr.FieldDefn('TileY',ogr.OFTInteger)
        outLayer.CreateField(TileY_field)
        TileZ_field = ogr.FieldDefn('TileZ',ogr.OFTInteger)
        outLayer.CreateField(TileZ_field)
        URL_field = ogr.FieldDefn('URL' , ogr.OFTString)
        outLayer.CreateField(URL_field)
    
        # get upper left left tile coordinates
        pixel = lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
        tile = pixel_coords_to_tile_address(pixel.x, pixel.y)
        TileX_left = tile.x
        TileY_top = tile.y
        
        # get lower right tile coordinates
        pixel = lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
        tile = pixel_coords_to_tile_address(pixel.x, pixel.y)    
        TileX_right = tile.x
        TileY_bottom = tile.y

        # Iterate through all tiles in the AOI at the current zoom level
        # and create a CSV row for each
        for TileY in range(TileY_top,TileY_bottom+1):
            for TileX in range(TileX_left,TileX_right+1):
                # Calculate lat, lon of upper left corner of tile
                PixelX = TileX * 256
                PixelY = TileY * 256
                MapSize = 256*math.pow(2,zoom)
                x = (PixelX / MapSize) - 0.5
                y = 0.5 - (PixelY / MapSize)
                lon_left = 360 * x
                lat_top = (90 - 360 * math.atan(math.exp(-y * 2 * math.pi))
                           / math.pi)
    
                # Calculate lat, lon of lower right corner of tile
                PixelX = (TileX+1) * 256
                PixelY = (TileY+1) * 256
                MapSize = 256*math.pow(2,zoom)
                x = (PixelX / MapSize) - 0.5
                y = 0.5 - (PixelY / MapSize)
                lon_right = 360 * x
                lat_bottom = (90 - 360 * math.atan(math.exp(-y * 2 * math.pi))
                              / math.pi)
    
                # Create Geometry
                ring = ogr.Geometry(ogr.wkbLinearRing)
                ring.AddPoint(lon_left, lat_top)
                ring.AddPoint(lon_right, lat_top)
                ring.AddPoint(lon_right, lat_bottom)
                ring.AddPoint(lon_left, lat_bottom)
                ring.AddPoint(lon_left, lat_top)
                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)
    
                # Check if tile is within the polygon of the Area of Interest.
                intersect = geomcol.Intersect(poly)
                if intersect == True:
                    # Tile is in the AOI. Add a row to the CSV for this tile.
                    l = l+1
                    outline = poly.ExportToWkt()
                    #print('The outline is {}'.format(outline))
                    URL = tile_coords_zoom_and_tileserver_to_URL(
                        int(TileX), int(TileY), int(zoom),
                        tileserver, api_key)
                    fileobj_output.write('\"'+outline+'\"$'+str(TileX)+'$'
                                         +str(TileY)+'$'+str(zoom)+'$'
                                         + URL)
    
                    outFeature = ogr.Feature(featureDefn)
                    outFeature.SetGeometry(poly)
                    if infile_extension == 'kml':
                        col_row_zoom = (str(TileX)+'_'+str(TileY)+'_'
                                        +str(int(zoom)))
                        outFeature.SetField('name', col_row_zoom)
                        desc = (str(TileX) + "_" + str(TileY) + "_"
                                + str(int(zoom)) + "\nTile URL: " + URL)
                        outFeature.SetField('description', desc)
                    else:
                        # Tile is in bounding box but not in AOI. Throw it out.
                        # TODO: Why is this here? Why not just pass?
                        outFeature.SetField('TileX', TileX)
                        outFeature.SetField('TileY', TileY)
                        outFeature.SetField('TileZ', zoom)
                        outFeature.SetField('URL', URL)
                    outLayer.CreateFeature(outFeature)
                    outFeature.Destroy

    # Close DataSources - without this you'll get a segfault from OGR.
    outDataSource.Destroy()

    print('Input file: '+infile)
    print('Zoom levels: '+str(minzoom) + ' to ' + str(maxzoom))
    print('Output files:')
    print()

if __name__ == "__main__":

    print()
    print('Tile server: ' + sys.argv[4])

    if 4 >= len( sys.argv ) >= 5:
        print("[ ERROR ] you must supply at least 3 arguments: "
              "(A file containing a KML, SHP, or GeoJSON polygon) "
              "(minzoom) (maxzoom) (tileserver [optional])")
        sys.exit( 1 )

    # Set tileserver to Digital Globe if not specified in 3rd argument
    if len( sys.argv ) == 3:
        tileserver='digital_globe_standard'
        print('Using Digital Globe Standard as you did not specify tileserver')
    else:
        tileserver=sys.argv[4]

    main(sys.argv[1], sys.argv[2], sys.argv[3], tileserver)
