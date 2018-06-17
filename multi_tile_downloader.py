#!/bin/python
"""Downloading necessary tiles for creation of an MBTile dataset.

Arguments:
    [1] A CSV file or URL created by create_csv.py containing tile URLs
    [2] 

Usage:
    

Output:
    Pile 'o' tiles from a tileserver

Example:
    python3 multi_tile_downloader.py ARGS  
"""
import sys
import os
import threading

import csv
import urllib2
import urlparse

import math

import time

from PIL import Image
import logging

def hamming(s1, s2):
    """Calculates the Hamming distance between two strings"""
    assert len(s1) == len(s2)
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def dhash(image, size = 8):
    """Produces a 8-bit (16-character hex) perceptual hash of an image.
    Intended for use with 256x256 tiles, to check for near-duplicates.
    Expects an image as its input argument, not a file.
    """

    # Crush image down to tiny grayscale
    image = image.convert('L').resize((size+1,size),Image.ANTIALIAS,)
    pixels = list(image.getdata())

    # Compare adjacent pixels
    difference = []
    for row in xrange(size):
        for col in xrange(size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)

    # Now turn the binary array into a hex string
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0
    return ''.join(hex_string)

def calculate_image_distance(input_image_url, comparison_image):
    try:
        response = urllib2.urlopen(input_image_url)
    except Exception:
        logging.exception('Something did not work out with the URL')
        logging.exception(input_image_url)
        exit(1)
    try:
        image = Image.open(response)
    except Exception:
        logging.exception('Not able to open contents of the URL as an image')
        logging.exception('input_image_url')
        exit(1)

    infile_hash = dhash(image, 8)
    comparison_hash = dhash(comparison_image, 8)
    distance = hamming(infile_hash, comparison_hash)
    return(distance)

def get_tile_date(url):
	#request tile url
	request = urllib2.Request(url)
	#define lambda function to only request http header
	request.get_method = lambda : 'HEAD'
	#open http header
	response = urllib2.urlopen(request, timeout= 1800)
	#read http header
	header = response.info()
	#is it a tile/image ?
	if 'X-VE-TILEMETA-CaptureDatesRange' in header:
		return header['X-VE-TILEMETA-CaptureDatesRange']
	#is it no tile?
	elif 'X-VE-Tile-Info' in header:
		return header['X-VE-Tile-Info']
	#is it something else?
	else:
		return 'NULL'

def compare(chunk, comparison_image, outlist):
    """Compare a bloc of images from a CSV file to a comparison image"""
    for row in chunk:
        url = (row[1].split('$'))[4]
        wkt = (row[1].split('$'))[0]
        row.append(wkt)
        try:
            tile_info = get_tile_date(url)
            row.append(tile_info)
            #null value for skipped image comaprision distance
            row.append('Null')
            outlist.append(row)
        except Exception:
            print('Http header check failed and will be skipped. '
                  'Perhaps you are not using bing imgery?')
            distance = calculate_image_distance(url, comparison_image)
            #null value for missing tile header info
            row.append('Null')
            row.append(distance)
            outlist.append(row)

def main(infile, comparison_image, threshold):
    """Eat csv of tile urls, spit out csv flagging them as valid or not"""
    start = time.time()
    try:
        comparison_image = Image.open(comparison_image)
    except Exception:
        logging.exception('your comparison file did not open, Holmes')
        exit(1)
    with open(infile) as csvfile:
        reader = csv.reader(csvfile)
        tile_rows = list(reader) # Probably should make this a deque
        header_row = tile_rows.pop(0)

        # Prepend an ID to every row so that they can be sorted
        row_id = 0
        for tile_row in tile_rows:
            tile_row.insert(0, row_id) # Again should probably be a deque
            row_id += 1

        num_threads = 50

        # Break the list into chunks of approximately equal size
        chunks = [tile_rows[i::num_threads] for i in xrange(num_threads)]

        outlist = []
        threads = []
        for chunk in chunks:
            thread = threading.Thread(target=compare, args=(
                chunk, comparison_image, outlist))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        outlist.sort()

        # Get infile filename and extension to name outfile
	try:
	    infile_name = infile.split('.')[0]
	    infile_extension = infile.split('.')[-1]
	except Exception:
	    logging.exception("check input file")
	    sys.exit(1)
        outfile = infile_name + '_validity.csv'

        with open(outfile, 'w') as outf:
            #added wkt for visualization
            outf.write('index,wkt,tile_date,distance,validity\n')
            for item in outlist:
                validity = 0
                if(item[2] >= int(threshold)):
                    validity = 1
                outf.write(str(item[0]) + ',"' + str(item[2]
                           + '",' + str(item[3]) + ',' + str(item[4]))
                           + "," + str(validity) + '\n')
        end = time.time() - start
        print 'finished. processing tok %i seconds' % end

if __name__ == "__main__":

    if len( sys.argv ) != 4:
        print("[ ERROR ] you must supply 3 arguments: ")
        print("1) a CSV file")
        print("2) an example blank tile")
        print("3) a minimum edit distance threshold")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
