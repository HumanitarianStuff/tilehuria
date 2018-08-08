#!/usr/bin/python3

import sys, os
import sqlite3
from sqlite3 import Error

def connect(infile):
    try:
        connection = sqlite3.connect(infile)
        return connection
    except Error as e:
        print(e)
        
    return None

def check_dir(path):
    if not os.path.exists(path):
        outdir = os.makedirs(path)

def main(infile):
    (infilename, extension) = os.path.splitext(infile)

    outdirpath = '{}_mbtiles/'.format(infilename)
    if not os.path.exists(outdirpath):
        outdir = os.makedirs(outdirpath)
    
    infofilename = infile + '_info.txt'
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
        for row in rows:
            for info in row:
                if(info != None):
                    infofile.write(info)
                    infofile.write(' ')
            infofile.write('\n')
        infofile.write('\n')
    
        # infofile.write all rows in tiles table
        infofile.write('Columns in tiles table:\n')
        cursor.execute("SELECT * FROM tiles;")
        columns = cursor.description
        for column in columns:
            infofile.write(column[0])
            infofile.write('\n')
        infofile.write('\n')

        #TODO Read tile format from metadata table instead of hardcoding
        tformat = 'jpeg'
    
        infofile.write('Number of rows in tiles table: ')
        rows = cursor.fetchall()
        infofile.write(str(len(rows)))
        infofile.write('\n')

        infofile.write('Individual tile filenames: \n')
        for row in rows:
            (z, x, y) = (str(row[0]), str(row[1]), str(row[2]))
            infofile.write('{}/{}/{}/{}\n'.format(z,x,y,tformat))
            check_dir('{}{}/{}'.format(outdirpath, z, x))
            outfilename = ('{}{}/{}/{}.{}'.format(outdirpath, z, x, y, tformat))
            print(outfilename)
            with open(outfilename, 'wb') as outfile:
                outfile.write(row[3])
    
        cursor.close()
        connection.close()
                
if __name__ == '__main__':
    main(sys.argv[1])
