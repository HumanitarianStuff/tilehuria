#!/usr/bin/python3
"""Batch resize images for web display"""

import sys, os
import argparse
from PIL import Image

def scandir(dir):
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(os.path.join(path, f))
    return filelist

def main(indir, maxheight):
    image_files = scandir(indir)
    for image_file in image_files:
        (image_filename, image_ext) = os.path.splitext(image_file)
        try:
            im = Image.open(image_file)
            if im.height > maxheight:
                ratio = maxheight / im.height
                w = int(im.width * ratio)
                h = int(im.height * ratio)
                im.resize((w,h), Image.ANTIALIAS).save(image_filename +
                                                       '.jpeg', 'JPEG',
                                                       quality=65)
                os.remove(image_file)
        except:
            print('{} is not a valid image file.'.format(image_file))
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("input_dir", help = "Input directory of tile files")
    parser.add_argument("-mh", "--maxheight",
                        help = "New maximum height of image")
    args = parser.parse_args()
    
    input_dir = args.input_dir
    maxheight = args.maxheight if args.maxheight else 1080
    
    main(input_dir, maxheight)
