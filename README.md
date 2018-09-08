# TileHuria

A tiny utility to create MBtiles for basemaps on mobile devices or for digitization with low Internet bandwidth.

## User provides:

Mandatory arguments:
- input file: A polygon (maybe multiple polygons, but for now let's say just one) in GeoJson format

Optional arguments:
- -minz or --minzoom, -maxz or --maxzoom: Desired min and max zoom. If not specified will default to 16-20.
- -ts or --tileserver: A tile server. If not specified will default to bing. 
- -tp or --type: Type (either overlay or baselayer). Default is baselayer.
- -d or --description: Description.
- -ver or --version: Version number for the tileset itself. If not provided will be omitted.

## Requirements
- Python 3
- GDAL

Both of these will be installed if you have installed QGIS 3.x on your computer.

**TODO: investigate how to make this work on Windows; probably just ensuring that we can launch using the QGIS python binaries, which already have GDAL.**<

## Example: create an offline MBTile set for a given AOI

### Create a polygon for you Area of Interest (AOI)
Use QGIS or another GIS program to create a single polygon. Use any shape you like, but only one polygon please! Save it in GeoJSON format, and place it on your hard drive in a sensible location.

**TODO: change this to URLs that the user can enter in JOSM-style format**

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

The reason for this folder structure is that it corresponds to the TileCache format [TODO: create a link](link.to.explanation.of.tilecache), therefore can be served directly by a webserver [TODO: link to instructions to do this](link.to.webserver.instructions).

### Turn those tiles into an MBTile set
The actual mbtile writer doesn't know anything about what has previously transpired; it simply traverses a folder arranged in the TileCache schema and creates an MBTile set from it. 
```
python3 write_mbtiles.py /path/to/myPolygon_digital_globe_standard
```

