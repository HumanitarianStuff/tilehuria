# Instructions for use

## Download the Tile Huria program
Go onto the Internet and go to to

https://github.com/ivangayton/tilehuria

Find the button on the right which says "Clone or download".

Easiest way is to download the zip file and extract the folder with the program. If you know how to use a terminal (in Mac or Linux), type:

```git clone https://github.com/ivangayton/tilehuria```

## Create an Area of Interest

First, create a new empty folder for your MBTiles.

Open QGIS. I hope you know what area you wish to map! If you don't have any kind of map already, download the [QuickMapServices](link) plugin for QGIS, and load up the OpenStreetMap layer or something similar to help you find the area you need).

Zoom into an area you want an MBTile for. You will need to create a single polygon. In QGIS, go to ```Layer -> Create Layer -> New Temporary Scratch Layer```. Choose ```Polygon / CurvePolygon``` as the geometry type, and give it a name like "MyAOI".

Click on the Add Polygon button ![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1") and trace a polygon. Make sure it doesn't cross over itself or otherwise be an invalid polygon!

Also, don't make one that's too big! More than 1km across and you're asking for trouble; the resulting MBTile file will be way to big and take far too long to download.

Once you are happy with the polygon, save your edits, leave editing mode in QGIS, and right-click on the layer to export it.

Choose ```Export -> Save Features As``` and choose GeoJSON as the file format. Save it in the folder you created for your MBTiles.

Minimize QGIS.

## Create a simple MBTile file with all defaults

Go to the folder where you extracted (or cloned) the Tile Huria program, and type:

```python3 polygon2mbtiles.py /path/to/myAOI.geojson```

(Hint: if you don't want to type the path to your AOI file, just drop it into the terminal after typing ```python3 polygon3mbtiles.py ```).

## The Hard Way

Starting with the AOI file you created (let's call it myArea.geojson),

#### Create a CSV file:
The first script (program) in the toolkit just creates a CSV file (spreadsheet file) containing the addresses and names of all the tiles needed for the area. It needs to be given the *argument* (data to work on) of the Area of Interest file you created (myArea.geojson).

```python3 create_tile_list.py /path/to/myArea.geojson```

This will create a file called myArea_digital_globe_standard.csv.

If you want to use another tileserver, you can do so by using the -ts  or --tilserver flag:

```python3 create_tile_list.py /path/to/myArea.geojson -ts bing;```

or

```python3 create_tile_list.py /path/to/myArea.geojson -ts google;```

#### Download all of the files in the folder

The second script downloads all of the tiles! It's *argument* is the csv file created in the previous step.

```python3 download_all_tiles_in_csv.py myArea_digital_globe_standard.csv```

You will now see a folder appear with the same name as the CSV file (minus the .csv extension). If you look inside that folder, you will see a bunch of subfolders (one for each tile zoom level), and inside those a bunch more folders (one for each tile row) and inside those a bunch of pictures (one for each tile in that row)!

#### Turn the tiles into a single MBTile file

The final script takes the folder full of tiles as it's *argument* and places them all in a single MBTile file.

```python3 write_mbtiles.py myArea_digital_globe_standard```

You will now see a new file appear called myArea_digital_globe_standard.mbtiles. Don't try to use it until the program finishes! Watch the terminal, which will tell you when the program is finished.

Drop the MBTile file into QGIS, or load it onto your phone, or open it in JOSM, to enjoy superfast imagery!