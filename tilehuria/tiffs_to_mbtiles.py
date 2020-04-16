#!/usr/bin/python3
"""Use GDAL to convert a directory full of GeoTIFF files to MBTiles.

Arguments:
    A directory containing GeoTiff raster files

Usage:
    
Output:
    Lots of MBtiles files (one per GeoTiff)

Example:
    python3 tiffs_to_mbtiles.py /path/to/input/directory  
"""
import sys
import os
import threading
import argparse
import multiprocessing

from arguments import argumentlist, set_defaults

from osgeo import gdal

def scandir(dir):
    """Walk recursively through a directory and return a list of all files in it"""
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(os.path.join(path, f))
    return filelist

def translate(infiles):
    for infile in infiles:
        

def task(inlist, num_threads, outdirpath):
    """ """
    chunks = [inlist[i::num_threads] for i in range(num_threads)]

    threads = []

    for chunk in chunks:
        thread = threading.Thread(target=translate, args=(chunk, outdirpath))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def tiffs_to_mbtiles(indir, optsin = {}):
    """Eat folder of geotiff rasters, spit out folder full of MBTiles"""
    threads_to_use=multiprocessing.cpu_count()
        task(images, threads_to_use, outdirpath)

if __name__ == "__main__":

    arguments = argumentlist()
    p = argparse.ArgumentParser()
    
    p.add_argument('indir', help = "Input directory")
    
    for (shortarg, longarg, actionarg, helpstring, defaultvalue) in arguments:
        p.add_argument('-{}'.format(shortarg), '--{}'.format(longarg),
                       action = actionarg,  help = helpstring)

    opts = vars(p.parse_args())
    indir = opts['indir']

    tiffs_to_mbtiles(indir, opts)
