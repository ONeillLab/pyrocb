# Recreating the following:
# RAW_DATA="$PCB_OUT_DIR/data/raw/elevation"
# cd $RAW_DATA
# #Elevation Data
# #CHANGE THE NEXT LINES to get different tiles
# #First Tile: 83C
# wget https://ftp.maps.canada.ca/pub/nrcan_rncan/elevation/cdem_mnec/083/cdem_dem_083C_tif.zip
# unzip cdem_dem_083C_tif.zip
# #Second Tile: 83D
# wget https://ftp.maps.canada.ca/pub/nrcan_rncan/elevation/cdem_mnec/083/cdem_dem_083D_tif.zip
# unzip cdem_dem_083D_tif.zip
# gdalwarp *.tif cdem_merged.tif


# #CHANGE THE NEXT LINE to reflect the lat/lon bounds you want. Usually, I will add a 0.1 degree buffer so we don't cut data from our Lambder projection.
# gdalwarp -te -118.600 52.378 -117.435 53.191 cdem_merged.tif cdem_d03.tif #West, South, East, North
# gdalwarp -s_srs EPSG:4617 -t_srs EPSG:4326 cdem_d03.tif cdem_final.tif

import json
import sys

sys.argv[0]
bounds = ()
tiles = []
time = {}

with open('strings.json') as f:
    d = json.load(f)
    print(d)