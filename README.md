# TileHuria

This is a set of minimal utilities to download imagery and create MBtiles for basemaps on mobile devices or for digitization with low Internet bandwidth. Intended for use by contributors to OpenStreetMap.

This might not be for everyone: there are tools like [tilemill](http://tilemill-project.github.io/tilemill/) and [SAS Planet](http://www.sasgis.org/sasplaneta/) that make MBTiles, and probably work better for most users. We were having trouble getting exactly what we wanted with those tools, so we built our own. This is mostly for people like [us](https://www.hotosm.org/), who run OpenStreetMap projects like [Ramani Huria](http://ramanihuria.org/), often in Africa or other low-connectivity areas, and are willing to take on some technical knowledge and tasks in order to get around the limitations of the environment.

# Appropriate Use (Do's and Don'ts)
Users **_should always_** respect the terms of use of the imagery providers such as Bing (Microsoft) and Digital Globe, who have gone out of their way to allow contributors to OpenStreetMap to use their imagery to build [the free map of the world](https://www.openstreetmap.org).

The intended use of this toolset is to allow people in low-connectivity environments to make use of the imagery for effective mapping. It was developed in Dar es Salaam by the Humanitarian OpenStreetMap Team/Ramani Huria in order to allow Tanzanian students to work effectively in large numbers with marginal Internet connections (digitizers and field mappers are no longer stuck waiting for Internet, and can map to their full potential). 

The terms of service of both DG and Bing permit "caching for performance," in other words allowing users to retain tiles locally in order to work more efficiently. These terms do **not** permit use of offline tiles in products, for example in the background of a finished map, or redistribution of any kind.

You may legally and ethically use the tilesets generated with these tools to:
1. Digitize using [JOSM](https://josm.openstreetmap.de/), even when you have a poor Internet connection, and
2. Place a background tileset on your mobile device when mapping, even if you are out of mobile service areas. 

Please do not risk our community's access to imagery to build the open map of the world! Respect the terms and conditions of the donors of the imagery we use! Do not use these tools for uses other than contributing to OpenStreetMap! 

# How to Use it
This toolset is written in Python 3, with one major dependency: [GDAL](https://www.gdal.org/). If you have [QGIS](https://qgis.org/en/site/) (at least version 3.0) installed on your computer, you probably have everything you need (QGIS installs both Python and GDAL, and QGIS >3.0 uses Python 3).

It requires using the command line; at this moment there is no Graphical User Interface (GUI) for it. We might get around to building this as a QGIS plugin with a nice GUI, or perhaps a web service of some kind, but we don't have much time these days... come to think of it, feel free to go ahead and do that if you have the knowledge and time!

On UNIX (MacOS or Linux), using the command line is fairly straightforward. On Windows, we can't really say (anyone willing to test it let me know; happy to get on a call with you). Basically use involves typing some commands into a terminal window.

## Automated Script
This toolkit is built of a number of small utilities, each doing a single part of the job (as per the venerable [UNIX Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy). One program creates a list of tiles from the Area of Interest, another downloads them into a set of folders, another changes the file format and compression settings, one creates a standalone MBTiles file, and a final one reads and opens an MBTile file (to check if it's working as expected and to allow various off-label uses of MBTiles from other sources). This means anyone can use any part of this toolkit for whatever they want to, and if they don't like one bit they can use something else (also, they can probably use bits of it for stuff we never thought of, which is fine as long as they don't do unethical stuff that risks our community's access to imagery for the free map of the world)! 

We've built a simple script to glue all of the pieces together, as most users will probably just want to draw an AOI and create an MBTile file. That script is called ```polygon2mbtiles.py```.

### Calling (Running) the Automated Script:
The script (program) is called from the command line using Python3, like this:

```python3 polygon2mbtiles.py```

That won't actually do anything, because the program requires *arguments* (data to work on). Most obviously, it requires an input file telling it what area to cover with the MBTile set. Other arguments include settings like min and max zoom, which tileserver to use, and so forth.

#### Arguments:

infile: An input file as GeoJSON, shp, KML, or gpkg, containing exactly one polygon. This is the only required parameter; all others are optional. The input file can be typed straight into the terminal after the text running the program (see examples below).

- -minz or --minzoom": Minimum tile level desired. Integer, defaults to 16
- -maxz or --maxzoom": Maximum tile level desired. Integer, defaults to 20
- -ts or --tileserver": A tile server where the needed tiles can be downloaded. Examples: ```digital_globe_standard```, ```digital_globe_premium```, ```bing``` (later versions will allow user to configure arbitrary tile servers). Defaults to digital_globe_standard.
- -f or --format: Actual tiles can be changed from one file format to another, for example PNG to JPEG (useful for reducing file size). ```PNG``` or ```JPEG```. 
- -cs or --colorspace: JPEG files (but not PNG files) can be encoded either using RGB or YCbCr; the latter can be used for more aggressive compression with relatively little perceptible quality loss with most aerial imagery. ```RGB``` or ```YCBCR```.
- -q or --quality: JPEG compression quality setting, just as in any image processing software. Number from 1 to 100, defaults to 75. 
- -t or --type: some programs that display MBTiles want to know whether the data is intended as a baselayer or an overlay (to help decide what to put on top of what). ```baselayer``` or ```overlay```.
- -c or --clean: Delete intermediate files (the tools generate several files the end user does not need, as well as a folder full of tiles, which will take up as much space as the MBTile set! If you set this flag, all of those will be removed when the script is finished.
- -ver or --verbose: you will see lots of cryptic information going by as the script works. Useful if something has gone wrong and you're trying to figure out the problem.

### Example Use:

#### First create a polygon for you Area of Interest (AOI)
Use QGIS or another GIS program to create a single polygon. Use any shape you like, but only one polygon please! Save it in GeoJSON format, and place it on your hard drive in a sensible location.

#### Now launch the program in one of the following ways:

Create an mbtile set from a GeoJSON polygon with all default settings:

```python3 polygon2mbtiles.py /path/to/myPolygon.geojson```

Create an mbtile set with minimum zoom 12 and max 20, using Bing imagery:

```python3 polygon2mbtiles.py mypolygon.geojson -minz 12 -maxz 20 -ts bing```

Create an mbtile set with zoom and tileserver selected, verbose mode (so you'll see a lot of information flash by), clean mode (so all intermediate files are deleted), conversion from PNG format to JPEG with YCbCr colorspace and 70% quality setting, attributed to Digital Globe and versioned 1.1:

```python3 polygon2mbtiles.py mypolygon.geojson -minz 12 -maxz 20 -ts digital_globe_premium -c -v -f JPEG -q 70 -cs YCBCR -a "Digital Globe Premium under the terms of use specified by DG for OpenStreetMap" -ver 1.1```

# More information

## Using the individual scripts

### Create a CSV file containing URLs for each of the tiles
Let's say you want to pull the tiles in an area delimited by the file myPolygon.json, and you want tile zoom level 15 to 21 (if you don't specify tile zoom levels, it will default to 16 to 20). Launch the program like so:

```
python3 create_tile_list.py /path/to/myPolygon.json -minz 15 maxz 21
```

You'll see two new files appear next to your AOI polygon: a CSV containing the tile URLs and a new GeoJSON with the tile extents.

The CSV file will have a name composed of the name of the polygon file plus the tileserver chosen. If you have follwed the example verbatim it will be called 'myPolygon_digital_globe_standard.csv'.

### Download all of the tiles
The tile downloader uses the CSV file generated in the previous step to download the tiles. That's all it needs.

```
python3 download_all_tiles_in_csv.py /path/to/myPolygon_digital_globe_standard.csv
```

A folder will appear with same name as the CSV (without the .csv extension of course). This folder will contain one sub-folder for each zoom level, and each zoom level folder will contain a numbered folder (the number actually is the x-address of the tiles within it, therefore corresponds to a particular column of tiles). Within these column folders are actual image files.

The reason for this folder structure is that it corresponds to the [Slippy Map folder and filename structure](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames), therefore can be served directly by a webserver. You can of course simply turn this folder into an MBTile set, but if you like, you can use it as the base folder for a tileserver to share with multiple people on the same Local Area Network (hint: great for mapathons with poor Internet connections). 

### Turn those tiles into an MBTile set
The actual mbtile writer doesn't know anything about what has previously transpired; it simply traverses a folder arranged in the TileCache schema and creates an MBTile set from it. 
```
python3 write_mbtiles.py /path/to/myPolygon_digital_globe_standard
```

**TODO: Add flag/option information here**

# Dev Info
## Requirements
- Python 3
- GDAL

**TODO: investigate how to make this work on Windows; probably just ensuring that we can launch using the QGIS python binaries, which already have GDAL.**

# TODO
- Complete glue script (it's a stub right now)
- Investigate YCbCr options more thoroughly (get compression down harder)
- Create GUI for the glue script
  - Ideally as a QGIS plugin
- Do something with the .timeout files
  - Try them again at the end of the download script? 
  - Create another script to try to get them later?
  - At least make a CSV of them (maybe replace the original CSV with one containing only the timed-out MBTiles?)
- Create web-based workflow to spin up a cloud server that does the CSV creation, downloading, type conversion/compression, and spits out a highest-zoom-level-only MBTile set for download (should reduce the amount of bandwidth required for DG tilesets by something like 5x
- Figure out what to do about areas where there are some high-zoom tiles and not others (currently I think this may break the MBTile set if there are, for example, a few tiles at zoom 19 but other areas with only 18).
- Create error message for fuckup with polygon in GDAL part of things
