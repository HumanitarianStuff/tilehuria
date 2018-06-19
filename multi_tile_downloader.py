#!/bin/python
"""Downloading necessary tiles for creation of an MBTile dataset.

Arguments:
    [1] A CSV file or URL created by create_csv.py containing tile URLs

Usage:
    

Output:
    Pile 'o' tiles from a tileserver

Example:
    python3 multi_tile_downloader.py mylist.csv  
"""
import sys
import os
import threading

import csv
import urllib2
import urlparse
import math
import time
import logging

def fetch(chunk):
    print(chunk)

def download(url):
        try:
        response = urllib2.urlopen(url)
    except Exception:
        logging.exception('Something did not work out with the URL')
        logging.exception(input_image_url)
        exit(1)

def main(infile):
    """Eat csv of tile urls, spit out folder full of tiles"""
    start = time.time()

    with open(infile) as csvfile:
        reader = csv.reader(csvfile)
        tile_rows = list(reader) 
        header_row = tile_rows.pop(0)

        num_threads = 50

        # Break the list into chunks of approximately equal size
        chunks = [tile_rows[i::num_threads] for i in xrange(num_threads)]

        threads = []
        for chunk in chunks:
            thread = threading.Thread(target=compare, args=(chunk))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        end = time.time() - start
        print 'finished. processing tok %i seconds' % end

if __name__ == "__main__":

    if len( sys.argv ) != 2:
        print("[ ERROR ] you must supply 1 argument: ")
        print("1) a CSV file")

        sys.exit(1)

    main(sys.argv[1])
