#!/usr/bin/python3
"""
Create a raster MBTile file from a Slippy Map-style folder 

https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames) 
in (attempted) compliance with the spec at 
https://github.com/mapbox/mbtiles-spec/blob/master/1.3/spec.md
"""
# Ivan Buendia Gayton, Humanitarian OpenStreetMap Team/Ramani Huria, 2018
import sys, os
import argparse
from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(__file__))
#from arguments import argumentlist, set_defaults

def scandir(dir):
    """Walk recursively through a directory and return a list of all files"""
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(os.path.join(path, f))
    return filelist

def composite_tiles(tiledir):
    filelist = scandir(tiledir)
    duplicates = group_duplicates(filelist)
    for bunch in duplicates:
        pics = []
        for item in bunch:
            pics.append(Image.open(item))
        basepic_file_name = os.path.splitext(bunch[0])[0] + '.jpg'
        mergedpic = merge_images(pics)
        # move all pics to safe refuge?
        print('Saving {}'.format(basepic_file_name))
        mergedpic.save(basepic_file_name, "JPEG")  
    
def group_duplicates(filelist):
    """Returns list of lists composed of filepaths differing by last char"""
    mydict = {}
    for filename in filelist:
        basepath = os.path.splitext(filename)[0]
        if basepath in mydict:
            mydict[basepath].append(filename)
        else:
            mydict[basepath] = [filename]
    grouped_files = mydict.values()
    filtered_groups = [x for x in grouped_files if len(x) > 1]
    return filtered_groups

def merge_images(pics):
    picbase = pics.pop(0)
    for pic in pics:
        picbase = ImageChops.add(picbase, pic)
    return picbase
    

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('tiledir', help = "Input directory of tile files")
    opts = vars(p.parse_args())
    tiledir = opts['tiledir']
    composite_tiles(tiledir)
