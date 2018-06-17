#!/bin/python3
Ivan Buendia Gayton 2016
"""Create a CSV document containing a list of tile URLs for classification.

Arguments:
    [1] A single-ring polygon, either a local file (shp, KML, GeoJSON) or URL
    [2] A zoom level for the desired output (search tileserver zoom to learn)
    [3] A tileserver name (bing, digital_globe, or google)

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
import urlparse
import urllib

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
        TileX, TileY, zoomlevel, tileserver, api_key):
    """Create a URL for a tile based on tile coordinates and zoom"""
    URL = ''
    if tileserver=='bing':
        quadKey = tile_coords_and_zoom_to_quadKey(
            int(TileX),int(TileY),int(zoomlevel))
        URL = quadKey_to_Bing_URL(quadKey, api_key)
    elif tileserver=='digital_globe':
        URL = ("https://api.mapbox.com/v4/digitalglobe.nal0g75k/"
               "{}/{}/{}.png?access_token={}"
               .format(zoomlevel, TileX, TileY, api_key))
    elif tileserver=='google':
        URL = ("https://mt0.google.com/vt/lyrs=s&hl=en&x={}&y={}&z={}\n"
               .format(TileX, TileY, zoomlevel))
    elif tileserver=='osm':
        pass
    elif tileserver=='custom':
        pass

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
    #print "\nThe tile URL is: {}".format(tile_url)
    return tile_url


def main(infile, zoomlevel, tileserver):
    try:
        from osgeo import ogr, osr
        #print "Import of ogr and osr from osgeo worked.  Hurray!\n"
    except:
        print '############ ERROR ######################################'
        print '## Import of ogr from osgeo failed\n\n'
        print '#########################################################'
        sys.exit()

    # check if the input is a URL, if so, download it

    parts = urlparse.urlsplit(infile)
    if parts.scheme:
        #print('infile is a URL')
        if not os.path.exists('tmp/'):
            os.makedirs('tmp')
        temp_infile = (os.getcwd()) + '/tmp/infile.kml'
        print(temp_infile)
        urllib.urlretrieve(infile, temp_infile)
        print(temp_infile)
        infile = temp_infile

    else:
        #print "Infile is not a URL"
        pass

    try:
        infile_name = infile.split('.')[0]
        infile_extension = infile.split('.')[-1]
    except:
        print "check input file"
        sys.exit()

    # Get API key from local text file
    try:
        if tileserver == 'bing':
            f = open('api_key.txt')
            api_key = f.read()
        elif tileserver == 'digital_globe':
            f = open('digital_globe_api_key.txt')
            api_key = f.read()
        elif tileserver == 'google':
            f = open('google_api_key.txt')
            api_key = f.read()
        elif tileserver == 'osm':
            pass
    except:
        print ("Something is wrong with your API key."
               "Do you even have an API key?")

    # Get the driver --> supported formats: Shapefiles, GeoJSON, kml
    if infile_extension == 'shp':
        driver = ogr.GetDriverByName('ESRI Shapefile')
    elif infile_extension == 'geojson':
        driver = ogr.GetDriverByName('GeoJSON')
    elif infile_extension == 'kml':
        driver = ogr.GetDriverByName('KML')
    else:
        print 'Check input file format for '+infile
        print 'Supported formats .shp .geojson .kml'
        sys.exit()

    # open the data source
    datasource = driver.Open(infile, 0)
    try:
        # Get the data layer
        layer = datasource.GetLayer()
    except:
        print 'Error, please check input file!'
        print '## '+infile
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

    # get Zoomlevel
    zoom = float(zoomlevel)

    # create output file
    outputGridfn = infile_name + '_tiles.' + infile_extension

    outfile = infile_name + '_' + tileserver + '_tiles.csv'
    l = 0
    if os.path.exists(outfile):
        os.remove(outfile)
    fileobj_output = file(outfile,'w')
    fileobj_output.write('wkt$TileX$TileY$TileZ$URL\n')

    outDriver = driver
    if os.path.exists(outputGridfn):
        os.remove(outputGridfn)
    outDataSource = outDriver.CreateDataSource(outputGridfn)
    outLayer = outDataSource.CreateLayer(outputGridfn,geom_type=ogr.wkbPolygon)
    featureDefn = outLayer.GetLayerDefn()

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

    # Iterate through all tiles in the AOI and create a CSV row for each
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
                o_line = poly.ExportToWkt()
                URL = tile_coords_zoom_and_tileserver_to_URL(
                    int(TileX), int(TileY), int(zoomlevel),
                    tileserver, api_key)
                fileobj_output.write('\"'+o_line+'\"$'+str(TileX)+'$'
                                     +str(TileY)+'$'+str(zoomlevel)+'$'+ URL)

                outFeature = ogr.Feature(featureDefn)
                outFeature.SetGeometry(poly)
                if infile_extension == 'kml':
                    col_row_zoom = str(TileX)+'_'+str(TileY)+'_'+str(int(zoom))
                    outFeature.SetField('name', col_row_zoom)
                    desc = (str(TileX) + "_" + str(TileY) + "_"
                            + str(int(zoom)) + "\nTile URL: " + URL)
                    outFeature.SetField('description', desc)
                else:
                    # Tile is in bounding box but not in AOI. Throw it out.
                    outFeature.SetField('TileX', TileX)
                    outFeature.SetField('TileY', TileY)
                    outFeature.SetField('TileZ', zoom)
                    outFeature.SetField('URL', URL)
                outLayer.CreateFeature(outFeature)
                outFeature.Destroy


    # Close DataSources - without this you'll get a segfault from OGR.
    outDataSource.Destroy()

    print '############ END ######################################'
    print '##'
    print '## input file: '+infile
    print '##'
    print '## zoomlevel: '+str(zoomlevel)
    print '##'
    print '## output files:'
    print '#######################################################'


if __name__ == "__main__":

    if 3 >= len( sys.argv ) >= 4:
        print("[ ERROR ] you must supply at least 2 arguments: "
              "(input-shapefile-name.kml or URL pointing to a KML, SHP, "
              "or GeoJSON polygon) (zoomlevel) (tileserver [optional])")
        sys.exit( 1 )

    # Set tileserver to Bing if not specified in 3rd argument
    if len( sys.argv ) == 3:
        tileserver='bing'
        print('Using Bing as default since you did not specify a tileserver')
    else:
        tileserver=sys.argv[3]

    main(sys.argv[1], sys.argv[2], tileserver)
