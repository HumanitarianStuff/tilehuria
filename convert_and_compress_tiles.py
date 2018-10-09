#!/usr/bin/python3
"""Batch convert and compress image tiles for the efficient creation of MBTiles
"""
import sys, os
import argparse
from PIL import Image

def scandir(dir):
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(os.path.join(path, f))
    return filelist

def main(indir):
    image_files = scandir(indir)
    numfiles = len(image_files)
    print('Launching compression of {} image files'.format(numfiles))
    print('We would love to tell you how long this will take, but we cannot')
    for image_file in image_files:
        (image_filename, image_ext) = os.path.splitext(image_file)
        if(image_ext != '.notile' and image_ext != '.timeout'):
            try:
                im = Image.open(image_file)
                im.convert('YCbCr').save(image_filename + '.jpeg', 'JPEG', quality=70)
                os.remove(image_file)
            except:
                print('{} is not a valid image file.'.format(image_file))
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("input_dir", help = "Input directory of tile files")
    args = parser.parse_args()
    
    input_dir = args.input_dir  
    
    main(input_dir)
