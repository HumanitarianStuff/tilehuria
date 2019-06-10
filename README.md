# TileHuria

*Project name: "Tile" referring to map tiles. "Huria" means "Free" or "Open" in Swahili.*

[![Build Status](https://travis-ci.com/HumanitarianStuff/tilehuria.svg?branch=master)](https://travis-ci.com/HumanitarianStuff/tilehuria)

This is a set of minimal utilities to download imagery and create MBtiles for basemaps on mobile devices or for digitization with low Internet bandwidth. Intended for use by contributors to [OpenStreetMap](https://www.openstreetmap.org/) and/or users of [OpenDataKit](http://opendatakit.org/) for humanitarian mapping.

This might not be for everyone: there are tools like [tilemill](http://tilemill-project.github.io/tilemill/) and [SAS Planet](http://www.sasgis.org/sasplaneta/) that make MBTiles, and may work better for many users. We were having trouble getting exactly what we wanted with the available tools, so we built our own. This is mostly for people like [us](https://www.hotosm.org/), who run OpenStreetMap projects like [Ramani Huria](http://ramanihuria.org/), often in Africa or other low-connectivity areas.

# Appropriate Use (Do's and Don'ts)
Users should **_always_** respect the terms of use of the imagery providers such as Bing (Microsoft) and Digital Globe, who have gone out of their way to allow contributors to OpenStreetMap to use their imagery to build [the free map of the world](https://www.openstreetmap.org).

The intended use of this toolset is to allow people in low-connectivity environments to make use of the imagery for effective mapping. It was developed in Dar es Salaam by the Humanitarian OpenStreetMap Team/Ramani Huria in order to allow Tanzanian students to work effectively in large numbers with marginal Internet connections (digitizers and field mappers are no longer stuck waiting for Internet, and can map to their full potential). 

The terms of service of both DG and Bing permit "caching for performance," in other words allowing users to retain tiles locally in order to work more efficiently. These terms do **not** permit use of offline tiles in products, for example in the background of a finished map, or redistribution of any kind.

You may legally and ethically use the tilesets generated with these tools to:
1. Digitize using [JOSM](https://josm.openstreetmap.de/), even when you have a poor Internet connection, and
2. Place a background tileset on your mobile device when mapping, even if you are out of mobile service areas. 

Please do not risk our community's access to imagery to build the open map of the world! Respect the terms and conditions of the donors of the imagery we use! Do not use these tools for uses other than contributing to OpenStreetMap!

# Setting it Up
This toolset is written in Python 3, with two dependencies: [GDAL](https://www.gdal.org/) and [pillow (the Python Imaging Library)](https://pillow.readthedocs.io/en/5.2.x/).

If you have [QGIS](https://qgis.org/en/site/) (at least version 3.0) installed on your computer, you should already have GDAL. In any case QGIS is useful to create the areas of interest you will need to use this tool, as well as to view the resulting MBTiles.

At the moment TileHuria requires using the command line; there is no Graphical User Interface (GUI) for it. We're working on a mimimal Web service for it.

#### Setting up, in this case on a fresh Ubuntu 18.04 Digital Ocean instance
```
sudo apt update
sudo apt install -y python3-gdal
sudo apt install -y python3-pip
sudo pip3 install pillow
git clone https://github.com/ivangayton/tilehuria
cd tilehuria/tilehuria/
```

#### Setting it up on Windows
1. If you have a version of Windows later than XP, download ["Windows X86-64 Executable Installer"](https://www.python.org/downloads/windows/) from the left column under "Stable Releases"
2. Run installer, **check box Add python 3.x to PATH** and click "install now"
Then in your command prompt...
```
pip install gdal
pip install pillow
git clone https://github.com/ivangayton/tilehuria
cd tilehuria/tilehuria/ (the path to the scripts folder)
```
Note: if you see the error ```error: no module named osgeo```, there is an issue with the GDAL library. Make sure that you have [MS Visual Studio](https://visualstudio.microsoft.com/downloads/) installed. Also, [this link may provide further help](https://pythongisandstuff.wordpress.com/2016/04/13/installing-gdal-ogr-for-python-on-windows/).


#### Testing it
```
python3 polygon2mbtiles.py example_files/San_Francisco_Shipyard.geojson
```

That should result in the creation of a small MBTile file in the example_files folder (along with a folder full of tile image files and a couple of ancillary files). If that happens, you've got a working setup.

# Example Use:

#### First create a polygon for your Area of Interest (AOI)

*More detailed instructions for doing this are just below in the next section!*

Use QGIS or another GIS program to create a single polygon. Use any shape you like, but only one polygon please! Make sure that polygon is in the "default" projection, which is EPSG 4326 (if you don't do anything weird, that's likely how it will be saved anyway). Save the polygon in GeoJSON format, and place it on your hard drive in a sensible location. There's a GeoJSON file in the example folder in this repo, callled San_Francisco_Shipyard.geojson, that you can use to test.

There is also a brilliant Web service at [geojson.io](geojson.io) that allows you to create a GeoJSON area of interest quickly and easily. Detailed instructions below.

#### Now launch Tilehuria:

To create an mbtile set from a GeoJSON polygon with all default settings:

```python3 polygon2mbtiles.py /path/to/myPolygon.geojson```

To create an mbtile set with minimum zoom 12 and max 20, using Bing imagery:

```python3 polygon2mbtiles.py /path/to/mypolygon.geojson -minz 12 -maxz 20 -ts bing```

Create an mbtile set with zoom and tileserver selected, verbose mode (so you'll see a lot of information flash by), clean mode (so all intermediate files are deleted), conversion from PNG format to JPEG with YCbCr colorspace and 70% quality setting, attributed to Digital Globe and versioned 1.1:

```python3 polygon2mbtiles.py /path/to/mypolygon.geojson -minz 12 -maxz 19 -ts digital_globe_premium -c -v -f JPEG -q 70 -cs YCBCR -a "Digital Globe Premium under the terms of use specified by DG for OpenStreetMap" -ver 1.1```

## Detailed Instructions to create an Area of Interest

#### Using [QGIS](https://qgis.org/en/site/)

Open [QGIS](https://www.qgis.org/en/site/). I hope you know what area you wish to map! If you don't have any kind of map already, download the [QuickMapServices](http://nextgis.com/blog/quickmapservices/) plugin for QGIS, and load up the OpenStreetMap layer or something similar to help you find the area you need).

Zoom into an area you want an MBTile for. You will need to create a single polygon. In QGIS, go to ```Layer -> Create Layer -> New Temporary Scratch Layer```. Choose ```Polygon / CurvePolygon``` as the geometry type, and give it a name like "MyArea".

Click on the Add Polygon button and trace a polygon. Make sure it has valid geometry (no lines crossing over themselves, no duplicate nodes, etc). Don't make one that's too big! Using zoom level 16-20, you'll encounter something like 1000 tiles per square kilometer. That'll translate to about 25MB of tiles in PNG format, or about 10MB in JPEG format (which is why, if you are using a tileserver that serves PNG files, it's a good idea to use the conversion and compression script here to go from PNG to JPEG before actually creating your MBTile file). We would not recommend using this for anything more than 100 square km (10 km on a side). Anything larger than that, break it up into multiple areas and create multiple MBTile files. 

Once you are happy with the polygon, save your edits, leave editing mode in QGIS, and right-click on the layer to export it.

Choose ```Export -> Save Features As``` choose GeoJSON as the file format, and EPSG 4326 as the coordinate system (it should be the default). Save it in the folder you created for your MBTiles.

Now you can use this GeoJSON file as input for the polygon2mbtiles.py program (as above in the Example Use section).

#### Using [geojson.io](geojson.io)

Go to the website, and zoom to the area you want tiles for.

Use the polygon tool (the pentagon icon) to trace your area of interest (finish it by clicking on the first point).

Click ```save -> GeoJSON``` and put it in a sensible folder with an appropriate filename.

Just as with the file generated using QGIS, you can use this GeoJSON file as input for the polygon2mbtiles.py program (as above in the Example Use section).

## Do it the Hard Way: Use the Individual Scripts
The polygon2mbtiles.py program doesn't actually do anything by itself, it calls a series of other programs:
- create_tile_list.py (creates a CSV list of tiles within the area defined by the input GeoJSON file, as well as another GeoJSON file with the perimeters of the tiles)
- download_all_tiles_in_csv.py (does pretty much exactly what the name says, dumps the tiles into a folder next to the input file)
- convert_and_compress_tiles.py (stores all of the tile image files in jpeg format to save space; important for people working in areas with poor internet)
- write_mbtiles.py (grabs all of the tiles in a given folder and saves them into a single MBTiles file.

We built the tools this way so that someone who has another workflow or toolset can use any part of the Tilehuria toolset. If you have a better way of downloading tiles, great! 

Here's how to use the individual scripts:

Starting with the AOI file you created (let's call it myArea.geojson),

#### Create a CSV file:
The first script (program) in the toolkit just creates a CSV file (spreadsheet file) containing the addresses and names of all the tiles needed for the area. It needs to be given the *argument* (data to work on) of the Area of Interest file you created (myArea.geojson).

```python3 create_tile_list.py /path/to/myArea.geojson```

This will create a file called myArea_digital_globe_standard.csv.

If you want to use another tileserver, you can do so by using the -ts  or --tilserver flag:

```python3 create_tile_list.py /path/to/myArea.geojson -ts bing;```

or

```python3 create_tile_list.py /path/to/myArea.geojson -ts digital_globe_premium;```

#### Download all of the files in the folder

The second script downloads all of the tiles! It's *argument* is the csv file created in the previous step.

```python3 download_all_tiles_in_csv.py /path/to/myArea_digital_globe_standard.csv```

You will now see a folder appear with the same name as the CSV file (minus the .csv extension). If you look inside that folder, you will see a bunch of subfolders (one for each tile zoom level), and inside those a bunch more folders (one for each tile row) and inside those a bunch of pictures (one for each tile in that row)! 

The reason for this folder structure is that it corresponds to the [Slippy Map folder and filename structure](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames), therefore can be served directly by a webserver. You can of course simply turn this folder into an MBTile set, but if you like, you can use it as the base folder for a tileserver to share with multiple people on the same Local Area Network (hint: great for mapathons with poor Internet connections). 

#### Save space (and download bandwidth if you are doing this on a server rather than a local machine)
This optional step saves all of the tile image files in a folder in JPEG format. This is three or four times smaller than the PNG format used by some tile providers.

```python3 convert_and_compress_tiles.py /path/to/myArea_digital_globe_standard``` (note that this input is a folder, not a file).

#### Turn the tiles into a single MBTile file

The final script takes the folder full of tiles as it's *argument* and places them all in a single MBTile file.

```python3 write_mbtiles.py /path/to/myArea_digital_globe_standard``` (again, not that this input is a folder, not a file)

You will now see a new file appear called myArea_digital_globe_standard.mbtiles. Don't try to use it until the program finishes! Watch the terminal, which will tell you when the program is finished.

#### Use the MBTiles to make the world a better (or at least better-mapped) place!

Drop the MBTile file into QGIS, load it onto your phone to use it with [ODK Collect](https://docs.opendatakit.org/collect-offline-maps/), or open it in JOSM, and map quickly and effeciently with fast-loading tiles!

# Advanced Information: Full Argument List

- infile: An input file as GeoJSON in EPSG 4326 Coordinate Reference System, containing exactly one polygon. This is the only required parameter; all others are optional. The input file can be typed straight into the terminal after the text running the program (see examples below).
- -minz or --minzoom": Minimum tile level desired. Integer, defaults to 16
- -maxz or --maxzoom": Maximum tile level desired. Integer, defaults to 20
- -ts or --tileserver": A tile server where the needed tiles can be downloaded. Examples: ```digital_globe_standard```, ```digital_globe_premium```, ```bing``` (later versions will allow user to configure arbitrary tile servers). Defaults to digital_globe_standard (if you don't specify a tileserver, it will use DG Standard, which is fine).
- -f or --format: Actual tiles can be changed from one file format to another, for example PNG to JPEG (useful for reducing file size). ```PNG``` or ```JPEG```. 
- -cs or --colorspace: JPEG files (but not PNG files) can be encoded either using RGB or YCbCr; the latter can be used for more aggressive compression with relatively little perceptible quality loss with most aerial imagery. ```RGB``` or ```YCBCR```.
- -q or --quality: JPEG compression quality setting, just as in any image processing software. Number from 1 to 100, defaults to 75. 
- -t or --type: some programs that display MBTiles want to know whether the data is intended as a baselayer or an overlay (to help decide what to put on top of what). ```baselayer``` or ```overlay```.
- -c or --clean: Delete intermediate files (the tools generate several files the end user does not need, as well as a folder full of tiles, which will take up as much space as the MBTile set! If you set this flag, all of those will be removed when the script is finished.
- -ver or --verbose: you will see lots of cryptic information going by as the script works. Useful if something has gone wrong and you're trying to figure out the problem.

# TODO (for developers or contributors)
- MetaTODO: put this TODO list into the Issues on Github instead of tacked onto the readme
- Create web-based workflow to spin up a cloud server that does the CSV creation, downloading, type conversion/compression, and spits out a highest-zoom-level-only MBTile set for download (should reduce the amount of bandwidth required for DG tilesets by something like 5x
- Create desktop GUI
  - Ideally as a QGIS plugin
- Create an output file with a list of files that timed out both tries; maybe make a CSV of them (maybe replace the original CSV with one containing only the timed-out MBTiles?)
- Figure out what to do about areas where there are some high-zoom tiles and not others (currently I think this may break the MBTile set if there are, for example, a few tiles at zoom 19 but other areas with only 18).
- Consider an option to save only tiles from the highest zoom level in any given spot (for people who really need to save download bandwidth and don't mind using GDAL or QGIS locally to create overviews)
- Consider an option to try to select the "best" tile from all providers for a given spot (a person could just download all tiles from all providers and switch during use, but for the low-bandwidth user it seems useful to provide a single tileset with whatever is best for each individual tile area)
  - Check all providers for the highest tile level available
  - Check all providers for the most recent tile (don't know if this is possible; I think there is some timestamp data in the metadata for each URL?)
  - Use pillow to check for cloudy areas (probably just highest overall RGB pixel value, maybe something more complicated like Hamming distance from an all-white tile, maybe even looking for sections of all white)?
 
- Create error message for fuckup with polygon in GDAL part of things
- Investigate possibilities for multi-polygons, polygons with holes in them, etc
- Finish implementing all of the flag options (verbose, clean etc)
- Investigate how to make it all work locally on Windows (PyPi should help with this, right?)
- Investigate YCbCr and JPEG setting options more thoroughly (get compression down harder)
- Write a couple of tests (start by convertng the file in the example folder and checking that this doesn't throw errors)
- Set up Continuous Integration (with TravisCI)
- Publish TileHuria to PyPi so that it can be installed via pip. 
  - This should handle the dependency installs (pillow and python-gdal), no?
- Now that it's going to be published and perhaps fairly easy to access, be more careful with the legal/licensing issues:
  - Maybe hold the commercial tileserver URLs in a local file (with .gitignore to avoid it being published)? Perhaps do what QuickMapServices does and use a "contributed pack" for testing purposes?
