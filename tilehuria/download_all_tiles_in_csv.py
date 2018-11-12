#!/usr/bin/python3
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

from . arguments import argumentlist, set_defaults

def check_dir(path):
    """If a directory does not exist, create it. Not thread-safe!"""
    if not os.path.exists(path):
        outdir = os.makedirs(path)

def parse_url_for_imtype(url):
    imtype = 'png'
    if('.jpeg' in url or '.jpg' in url):
        imtype = 'jpg'
    if('google' in url):  # Yes, a crude and brittle hack
        imtype = 'jpg' 
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

def managechunk(chunk, outdirpath, timeout):
    """Downloads all tiles contained in a chunk (sub-list of tile rows)"""

    chunkfailedlines = []
    for item in chunk:
        row = item[0].split(';')
        url = (row[4])
        (z, x, y) = (str(row[3]), str(row[1]), str(row[2]))

        timeoutfile = os.path.join(outdirpath, z, x, '{}.timeout'.format(y))
        notilefile = os.path.join(outdirpath, z, x, '{}.notile'.format(y))
        rawdata = None
        try:
            rawdata = urllib.request.urlopen(url, timeout=int(timeout)).read()
        except:
            # Download failed. Create a timeout file as a placeholder
            with open(timeoutfile, 'w') as outfile:
                writer = csv.writer(outfile, delimiter = ';')
                writer.writerow([row[0], x, y, z, url])
                
        if(rawdata):
            imtype = parse_url_for_imtype(url)
            if os.path.exists(timeoutfile):
                os.remove(timeoutfile)
            outfilename = os.path.join(outdirpath, z, x, '{}.{}'.format(y,imtype))
            
            # if the file is less than 1040 bytes, there's no tile here.
            if(len(rawdata) > 1040):
                with open(outfilename, 'wb') as outfile:
                    outfile.write(rawdata)
            else:
                with open(notilefile, 'w') as outfile:
                    writer = csv.writer(outfile, delimiter = ';')
                    writer.writerow([row[0], x, y, z, url])            

def task(inlist, num_threads, outdirpath, timeout):
    header_row = inlist.pop(0)
    # Break the list into chunks of approximately equal size
    chunks = [inlist[i::num_threads] for i in range(num_threads)]

    # Create Slippy Map-type folder structure (before tasking for thread safety)
    for line in inlist:
        row = line[0].split(';')
        (z, x) = (str(row[3]), str(row[1]), )
        check_dir('{}{}/{}'.format(outdirpath, z, x))

    threads = []

    for chunk in chunks:
        thread = threading.Thread(target=managechunk,
                                  args=(chunk, outdirpath, timeout))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def download_all_tiles_in_csv(opts):
    """Eat CSV of tile urls, spit out folder full of tiles"""
    infile = opts['csvinfile']
    (infilename, extension) = os.path.splitext(infile)
    outdirpath = os.path.join(infilename, '')
    check_dir(outdirpath)
    threads_to_use=50
    
    start = time.time()
    with open(infile) as csvfile:
        reader = csv.reader(csvfile)
        tile_rows = list(reader)
        if(len(tile_rows)) < 100:
           threads_to_use = int(len(tile_rows)/2)
        print('Starting download of {} tiles'.format(len(tile_rows)))
        task(tile_rows, threads_to_use, outdirpath, 10)

    end = time.time() - start
    print('Finished. Downloading took {} seconds'.format(end))

    # Check number of timeouts
    tile_timeouts = get_list_of_timeouts(outdirpath)
    if len(tile_timeouts):
        print('{} tiles failed to download due to timeout'
              .format(len(tile_timeouts)))
        
        print('Trying timed-out tiles again, with half the number of threads '
              'and a 100-second timeout')
        threads_to_use = 25
        if(len(tile_rows)) < 100:
            threads_to_use = int(len(tile_rows)/4)
        task(tile_rows, threads_to_use, outdirpath, 100)
    
        tile_timeouts = get_list_of_timeouts(outdirpath)
        if len(tile_timeouts):
            print('{} tiles failed to download a second time due to timeout'
                  .format(len(tile_timeouts)))
            timeoutcsv = '{}_timeouts.csv'.format(infilename)
            with open(timeoutcsv, 'w') as to:
               to.write('wkt;Tilex;TileY;TileZ;URL\n')
               for line in tile_timeouts:
                   to.write(line)
            print('See:\n{} \nfor list of failed/missing tiles'.format(timeoutcsv))
        else:
            print('Looks like all tiles were downloaded on the second and last try!')
    else:
        print('Looks like all tiles were downloaded on the first try!')

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    
    p.add_argument('csvinfile', help = "Input file as CSV of tiles with URLs")
    
    for (shortarg, longarg, actionarg, helpstring, defaultvalue) in arguments:
        p.add_argument('-{}'.format(shortarg), '--{}'.format(longarg),
                       action = actionarg,  help = helpstring)

    opts = vars(p.parse_args())

    download_all_tiles_in_csv(opts)
