#!/usr/bin/python3
"""
Various utilities for MBTile creation, mostly math.
"""
import sys, os

from osgeo import ogr


def get_ogr_driver(extension):
    """Load a driver from GDAL for the input file. Only GeoJSON guaranteed to work."""
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
        print('Check input file format for {}'.format(infile))
        print('Only polygon GeoJSON in EPSG 4326 is guaranteed to work.')
        sys.exit()
    return driver

def get_extent(infile, extension):
    try:
        driver = get_ogr_driver(extension)
        datasource = driver.Open(infile, 0)
        layer = datasource.GetLayer()
        extent = layer.GetExtent()
        (xmin, xmax, ymin, ymax) = (extent[0], extent[1], extent[2], extent[3])
        return (xmin, xmax, ymin, ymax)
    except Exception as e:
        print('Something went wrong with the ogr driver')
        print(e)
        exit(1)
    
def get_geomcollection(infile, extension):
    try:
        driver = get_ogr_driver(extension)
        datasource = driver.Open(infile, 0)
        layer = datasource.GetLayer()
        extent = layer.GetExtent()
        (xmin, xmax, ymin, ymax) = (extent[0], extent[1], extent[2], extent[3])
        featurecount = layer.GetFeatureCount()
        geomcollection = ogr.Geometry(ogr.wkbGeometryCollection)

        # using a horrible range iterator to work around an apparent bug in OGR
        # (layer won't iterate in some versions of OGR)
        for i in range(featurecount):
            feature = layer.GetNextFeature()
            geomcollection.AddGeometry(feature.GetGeometryRef())
        return geomcollection
    except Exception as e:
        print('Something went wrong with the ogr driver')
        print(e)
        exit(1)

        
def intersect(tileX, tileY, zoom, geomcollection):
    """Checks if a given tile intersects with a polygon geometry collection"""
    (latt, lonl) = lat_long_upper_left(tileX, tileY, zoom)
    (latb, lonr) = lat_long_lower_right(tileX, tileY, zoom)
    
    # Create a polygon (square) for the tile
    ring = ogr.Geometry(ogr.wkbLinearRing)
    points = [(lonl, latt), (lonr, latt), (lonr, latb), (lonl, latb), (lonl, latt)]
    for point in points:
        ring.AddPoint(point[0], point[1])
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    # Check if the tile intersects the polygon of the Area of Interest
    intersect = geomcollection.Intersect(poly)
    return poly.ExportToWkt() if intersect else None
