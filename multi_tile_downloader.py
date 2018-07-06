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
import time
import urllib.request

def managechunk(chunk):
    """Downloads all tiles contained in a chunk (list of tile rows)"""
    for item in chunk:
        tile_row = item[0].split(';')
        url = (tile_row[4])
        outfilename = ('local_data/tiles/from_dg/{}_{}_{}.png'
                       .format(tile_row[1], tile_row[2], tile_row[3]))
        rawdata = urllib.request.urlopen(url).read()
        print('Writing {}'.format(outfilename))
        with open(outfilename, 'wb') as outfile:
            outfile.write(rawdata)

def task(inlist, num_threads):
    header_row = inlist.pop(0)
    # Break the list into chunks of approximately equal size
    chunks = [inlist[i::num_threads] for i in range(num_threads)]

    threads = []
    for chunk in chunks:

        thread = threading.Thread(target=managechunk, args=(chunk,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def main(infile):
    """Eat CSV of tile urls, spit out folder full of tiles"""
    start = time.time()

    (infilename, extension) = os.path.splitext(infile)
    threads_to_use=50

    with open(infile) as csvfile:
        reader = csv.reader(csvfile)
        tile_rows = list(reader)
        task(tile_rows, threads_to_use)

    end = time.time() - start
    print('Finished. Downloading took {} seconds'.format(end))

if __name__ == "__main__":

    if len( sys.argv ) != 2:
        print("[ ERROR ] you must supply 1 argument: ")
        print("1) a CSV file")

        sys.exit(1)

    main(sys.argv[1])
