#!/usr/bin/python3
"""
This script automates the use of the other scripts in this repository, allowing a user to call a single script that takes an Area of Interest polygon and creates an MBTile file. 

Arguments (using bash-style flags):

infile: An input file as GeoJSON, shp, KML, or gpkg, containing exactly one polygon. This is the only required parameter; all others are optional (and must be preceded with POSIX-style flags, only the input file is written without flags). 

-minz, --minzoom": Minimum tile level desired. Integer, defaults to 16
-maxz, --maxzoom": Maximum tile level desired. Integer, defaults to 20
-ts, --tileserver": A tile server where the needed tiles can be downloaded. Examples: digital_globe_standard, digital_globe_premium, bing (later versions will allow user to configure arbitrary tile servers). Defaults to digital_globe_standard.
-f, --format: Actual tiles can be changed from one file format to another, for example PNG to JPEG (useful for reducing file size). PNG or JPEG. 
-cs, --colorspace: JPEG files (but not PNG files) can be encoded either using RGB or YCbCr; the latter can be used for more aggressive compression with relatively little perceptible quality loss with most aerial imagery. RGB or YCBCR.
-q, --quality: JPEG compression quality setting, just as in any image processing software. Number from 1 to 100, defaults to 75. 

Example use:

Create an mbtile set from a GeoJSON polygon with all default setting:
python3 make_mbtiles_from_aoi.py myPolygon.geojson

Create an mbtile set with minimum zoom 12 and max 20, using Bing imagery:
python3 make_mbtiles_from_aoi.py mypolygon.geojson -minz 12 -maxz 20 -ts bing

Create an mbtile set with zoom and tileserver selected, verbose mode (so you'll see a lot of information flash by), clean mode (so all intermediate files are deleted), conversion from PNG format to JPEG with YCbCr colorspace and 70% quality setting, attributed to Digital Globe and versioned 1.1:
python3 make_mbtiles_from_aoi.py mypolygon.geojson -minz 12 -maxz 20 -ts digital_globe_premium -c -v -f JPEG -q 70 -cs YCBCR -a "Digital Globe Premium under the terms of use specified by DG for OpenStreetMap" -v 1.1 

"""
# Ivan Buendia Gayton, Humanitarian OpenStreetMap Team/Ramani Huria, 2018
import sys, os
import argparse
import create_tile_list
import download_all_tiles_in_csv
import write_mbtiles

def main(infile, opts):
    """Take an Area of Interest (AOI) polygon, return an MBtiles file.""" 
    (basename, extension) = os.path.splitext(infile)
    csvfile = '{}_{}.csv'.format(basename, opts['tileserver'])
    foldername = '{}_{}'.format(basename, opts['tileserver'])

    create_tile_list.main(infile,
                          opts['minzoom'], opts['maxzoom'], opts['tileserver'])
    download_all_tiles_in_csv.main(csvfile)
    write_mbtiles.main(foldername)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help = "An input file as GeoJSON, shp, KML, "
                        "or gpkg, containing exactly one polygon.")
    parser.add_argument("-minz", "--minzoom", help = "Minimum tile level desired")
    parser.add_argument("-maxz", "--maxzoom", help = "Maximum tile level desired")
    parser.add_argument("-ts", "--tileserver", help = "A tile server where the"
                        "needed tiles can be downloaded: digital_globe_standard, "
                        "digital_globe_premium, bing, etc")
    parser.add_argument("-f", "--format", help = "Output tile file format: PNG, "
                        "JPEG, or JPEG")
    parser.add_argument("-cs", "--colorspace", help = "Color space of tile format: "
                        "RGB or YCBCR.")
    parser.add_argument("-t", "--type", help = "Layer type: overlay or baselayer.")
    parser.add_argument("-d", "--description", help = "Describe it however you like!")
    parser.add_argument("-a", "--attribution", help = "Should state data origin.")
    parser.add_argument("-ver", "--version", help = "The version number of the"
                        "tileset (the actual data, not the program)")
    parser.add_argument("-v", "--verbose", help = "Use if you want to see a lot of "
                        "command line output flash by!")
    parser.add_argument("-c", "--clean", help = "Delete intermediate files.")
    parser.add_argument("-q", "--quality", help = "JPEG compression quality setting.")


    defaults = {'minzoom': 16, 'maxzoom': 20, 'tileserver': 'digital_globe_standard'}
    opts = vars(parser.parse_args())

    opts['minzoom'] = 16 if opts['minzoom'] == None else opts['minzoom']
    opts['maxzoom'] = 20 if opts['maxzoom'] == None else opts['maxzoom']
    opts['tileserver'] = ('digital_globe_standard' if opts['tileserver'] == None
                          else opts['tileserver'])

    input_file = opts['infile']
    
    main(input_file, opts)
