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
    connection = connect(infile)
    cursor = connection.cursor()
    print()

    # print list of tables
    print('Tables in database')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print()

    # print all rows in metadata table
    print('Rows in metadata table')
    cursor.execute("SELECT * FROM metadata;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print()

    # print all rows in tiles table
    print('Columns in tiles table')
    cursor.execute("SELECT * FROM tiles;")
    columns = cursor.description
    for column in columns:
        print(column[0])
    print()

    print('Number of rows in tiles table')
    rows = cursor.fetchall()
    print(len(rows))
    print()

    print('Rows in tiles table')
    for row in rows:
        print(str(row[0]) + ', ' + str(row[1]) + ', ' + str(row[2]))
        outfilename = 'tiles/output/' + str(row[0])\
                      + '_' + str(row[1]) + '_' + str(row[2]) + '.png'
        with open(outfilename, 'wb') as outfile:
            outfile.write(row[3])

    cursor.close()
    connection.close()
            
if __name__ == '__main__':
    main(sys.argv[1])
