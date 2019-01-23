#!/usr/bin/python3
"""
Various utilities for MBTile creation, math and string manipulation related to tiles.
"""
import sys, os
import argparse

import math
import re
import random

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

def lat_long_upper_left(tileX, tileY, zoom):
    """Provides a lat-long coordinate point for the upper left corner of a tile"""
    pixelX = tileX * 256
    pixelY = tileY * 256
    mapSize = 256*math.pow(2,zoom)
    x = (pixelX / mapSize) - 0.5
    y = 0.5 - (pixelY / mapSize)
    lonleft = 360 * x
    lattop = (90-360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi)
    return (lattop, lonleft)
    
def lat_long_lower_right(tileX, tileY, zoom):
    """Provides a lat-long coordinate point for the lower right corner of a tile"""
    pixelX = (tileX+1) * 256
    pixelY = (tileY+1) * 256
    MapSize = 256*math.pow(2,zoom)
    x = (pixelX / MapSize) - 0.5
    y = 0.5 - (pixelY / MapSize)
    lonright = 360 * x
    latbottom = (90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi)
    return (latbottom, lonright)

def tile_coords_to_url(tileX, tileY, zoom, url_template):
    """Create a URL for a tile based on XYZ coordinates and a template URL"""
    url = ''
    # Random server switching based on choices embedded in the template URL
    switchre = r"\{switch:(.*?)\}"
    matches = re.finditer(switchre, url_template, re.MULTILINE | re.DOTALL)
    switchedchoice = ''
    for match in matches:
        contents = match.group(1)
        switchedchoice = random.choice(contents.split(',')).strip()
    url = re.sub(switchre, switchedchoice, url_template)        

    # Replace {x}, {y}, and {z} placeholders with the correct values
    url = re.sub(r"\{x\}", str(tileX), url)
    url = re.sub(r"\{y\}", str(tileY), url)
    url = re.sub(r"\{z\}|\{zoom\}", str(zoom), url)

    # replace {quadkey} with the actual item
    url = re.sub(r"\{quadkey\}", tile_coords_to_quadkey(tileX, tileY, zoom), url)
                 
    # Strip prefixes from urls (JOSM-style urls contain tms information in prefix)
    url = re.sub(r".*https\:\/\/", 'https://', url)
    url = re.sub(r".*http\:\/\/", 'http://', url)
    
    return url

def tile_coords_to_quadkey(x, y, zoom):
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

def url_template_from_file(tsname, urlfile = 'URL_formats.txt'):
    """Provide a url template from a specified file or default to URL_formats.txt"""
    d = {}
    try:
        with open(urlfile) as urlfile:
            d = {k: v for line in urlfile for (k, v)
                 in (line.strip().split(None, 1),)}
    except Exception as e:
        print('Did not manage to find or open {}'.format(urlfile))
        print(e)

    if tsname in d:
        return d[tsname]
    else:
        print('No URL template for {} found in {}'.format(tsname, urlfile))
        return None
