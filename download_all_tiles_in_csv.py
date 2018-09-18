#!/bin/python
"""Download necessary tiles for creation of an MBTile dataset.

Arguments:
    A CSV file containing tile URLs

Usage:
    
Output:
    Pile 'o' tiles from a tileserver

Example:
    python3 download_all_tiles_in_csv.py mylist.csv  
"""
import sys
import os
import threading
import csv
import time
import urllib.request

def check_dir(path):
    """If a directory does not exist, create it. Not thread-safe!"""
    if not os.path.exists(path):
        outdir = os.makedirs(path)

def parse_url_for_imtype(url):
    imtype = 'png'
    if('.jpeg' in url or '.jpg' in url):
        imtype = 'jpeg'
    if('google' in url):  # Yes, a crude and brittle hack
        imtype = 'jpeg' 
    return imtype

def get_list_of_timeouts(dirpath):
    """Create a list of URLs of all of tiles that timed out the first time"""
    urllist = []
    for path, dirs, files in os.walk(dirpath):
        for f in files:
            (infilename, extension) = os.path.splitext(f)
            if extension == '.timeout':
                url = None
                try:
                    infile = os.path.join(path, f)
                    urlfile = open(infile)
                    url = urlfile.read()
                except:
                    print('{} did not work'.format(urlfile))
                urllist.append(url)
    return urllist

def managechunk(chunk, outdirpath):
    """Downloads all tiles contained in a chunk (sub-list of tile rows)"""

    chunkfailedlines = []
    for item in chunk:
        row = item[0].split(';')
        url = (row[4])
        (z, x, y) = (str(row[3]), str(row[1]), str(row[2]))
        
        rawdata = None
        try:
            rawdata = urllib.request.urlopen(url, timeout=10).read()
        except:
            # Download failed. Create a text file called {y}.timeout containing URL
            outfilename = ('{}/{}/{}/{}.{}'.format(outdirpath, z, x, y, 'timeout'))
            with open(outfilename, 'w') as outfile:
                outfile.write(url)
                
        if(rawdata):
            imtype = parse_url_for_imtype(url)
            outfilename = ('{}/{}/{}/{}.{}'.format(outdirpath, z, x, y, imtype))
            
            # if the file is less than 1040 bytes, there's no tile here. Save nothing.
            if(len(rawdata) > 1040):
                with open(outfilename, 'wb') as outfile:
                    outfile.write(rawdata)

def task(inlist, num_threads, outdirpath):
    header_row = inlist.pop(0)
    # Break the list into chunks of approximately equal size
    chunks = [inlist[i::num_threads] for i in range(num_threads)]

    # Create Slippy Map-type folder structure (before tasking for thread safety)
    for line in inlist:
        row = line[0].split(';')
        (z, x) = (str(row[3]), str(row[1]), )
        check_dir('{}{}/{}'.format(outdirpath, z, x))

    threads = []

    #TODO Send off an empty list to each chunk manager to get failed lines back
    for chunk in chunks:
        thread = threading.Thread(target=managechunk, args=(chunk, outdirpath))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def main(infile):
    """Eat CSV of tile urls, spit out folder full of tiles"""
    (infilename, extension) = os.path.splitext(infile)
    outdirpath = '{}/'.format(infilename)
    check_dir(outdirpath)
    threads_to_use=50
    
    start = time.time()
    with open(infile) as csvfile:
        reader = csv.reader(csvfile)
        tile_rows = list(reader)
        if(len(tile_rows)) < 100:
           threads_to_use = int(len(tile_rows)/2)
        task(tile_rows, threads_to_use, outdirpath)

    end = time.time() - start
    print('Finished. Downloading took {} seconds'.format(end))
    tile_timeouts = get_list_of_timeouts(outdirpath)
    print('{} tiles failed to download due to timeout. Trying again.'
          .format(len(tile_timeouts)))
    #TODO create list with zxy and URL, calculate threads to use, task it.

if __name__ == "__main__":

    if len( sys.argv ) != 2:
        print("[ ERROR ] you must supply 1 argument: ")
        print("1) a CSV file")

        sys.exit(1)

    main(sys.argv[1])
