# TileHuria

A tiny utility plugin to create MBtiles for basemaps on mobile devices.

### Information needed to create a complete tileset:

- Extent (a polygon, either a file or perhaps a description like a bbox)
- minzoom
- maxzoom
- Bounds (computed from the polygon or from the highest tile level, in WGS84 lat/long)
- Center (in WGS84 lat/long)
- Type (overlay or baselayer)
- Description of the whole tileset
- Version (of the tileset itself, not of the spec)
- format of tiles (png, png8, or jpeg)
- Attribution

### User provides:

Mandatory:
- A polygon (maybe multiple polygons, but for now let's say just one)

Optional:
- Desired min and max zoom. If not specified will default to 16-20.
- A tile server. If not specified will default to bing. 
- Type (either overlay or baselayer). Default is baselayer.
- Description.
- Version number for the tileset itself. If not provided will be omitted.
- Attribution (for now this is simply going to be the name of the tileserver)


