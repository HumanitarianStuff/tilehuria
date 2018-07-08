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
    
        infofile.write('Number of rows in tiles table: ')
        rows = cursor.fetchall()
        infofile.write(str(len(rows)))
        infofile.write('\n')

        infofile.write('Individual tile filenames: \n')
        for row in rows:
            infofile.write(str(row[0]) + '_' + str(row[1]) + '_' + str(row[2]) \
                           + '.png')
            infofile.write('\n')
            outfilename = ('{}{}_{}_{}.png'
                       .format(outdirpath, row[0], row[1], row[2]))
            print(outfilename)
            with open(outfilename, 'wb') as outfile:
                outfile.write(row[3])
    
        cursor.close()
        connection.close()
                
if __name__ == '__main__':
    main(sys.argv[1])
