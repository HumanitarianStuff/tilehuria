#!/usr/bin/python3

import sys, os
import argparse
import math
import sqlite3
from sqlite3 import Error

from arguments import argumentlist, set_defaults

def connect(infile):
    try:
        connection = sqlite3.connect(infile)
        return connection
    except Error as e:
        print(e)
        
    return None

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(os.path.join(path, ''))

def read_mbtiles(infile, opts = {}):
    (infilename, extension) = os.path.splitext(infile)
    outdirpath = (opts['output_dir'] if opts['output_dir']
                  else '{}_mbtiles'.format(infilename))
    check_dir(outdirpath)

    infofilename = infilename + '_mbtiles_info.txt'
    with open(infofilename, 'w') as infofile:
        connection = connect(infile)
        cursor = connection.cursor()
    
        # print list of tables
        infofile.write('Tables in database:\n')
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = cursor.fetchall()
        for row in rows:
            for info in row:
                if(info != None):
                    infofile.write(info)
                    infofile.write('\n')
        infofile.write('\n')
    
        # infofile.write all rows in metadata table
        infofile.write('Columns in metadata table:\n')
        cursor.execute("SELECT * FROM metadata;")
        columns = cursor.description
        for column in columns:
            infofile.write(column[0])
            infofile.write('\n')
        infofile.write('\n')
        infofile.write('Rows in metadata table:\n')
        rows = cursor.fetchall()
        metadata_dict = dict(rows)
        for item in metadata_dict:
            infofile.write('{} {}\n'.format(item, metadata_dict[item]))
        image_format = metadata_dict['format']
        infofile.write('\n')
    
        # infofile.write all rows in tiles table
        infofile.write('Columns in tiles table:\n')
        cursor.execute("SELECT * FROM tiles;")
        columns = cursor.description
        for column in columns:
            infofile.write(column[0])
            infofile.write('\n')
        infofile.write('\n')
    
        infofile.write('Number of rows in tiles table: ')
        rows = cursor.fetchall()
        infofile.write(str(len(rows)))
        infofile.write('\n')

        infofile.write('Individual tile filenames: \n')
        for row in rows:
            (z, x, tiley) = (str(row[0]), str(row[1]), str(row[2]))
            y = int(math.pow(2.0, float(z)) - float(tiley) - 1.0)
            infofile.write('{}/{}/{}.{}\n'.format(z, x, y, image_format))
            path_to_dir = os.path.join(outdirpath, z, x)
            check_dir(path_to_dir)
            ofname = os.path.join(path_to_dir, '{}.{}'.format(y, image_format))
            oftowrite = get_unique_fn(ofname)
            with open(oftowrite, 'wb') as outfile:
                outfile.write(row[3])
    
        cursor.close()
        connection.close()

def get_unique_fn(ofname):
    while(os.path.isfile(ofname)):
        endchar = ofname[-1]
        if endchar.isdigit():
            endnum = int(endchar) + 1
            ofname = ofname[:-1] + str(endnum)
        # It was a duplicate but the first one (no number yet appended)
        else:
            ofname = ofname + '1'
    return ofname
               

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("infile", help = "An MBTile file to be read.")
    p.add_argument("-od", "--output_dir",
                   help = "The directory to store extracted tiles.")
    p.add_argument("-v", "--verbose", action = 'store_true',
                        help = "Use if you want to see a lot of "
                        "command line output flash by!")

    opts = vars(p.parse_args())
    infile = opts['infile']
    
    read_mbtiles(infile, opts)
