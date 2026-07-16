#!/bin/bash

set -e

mkdir -p "$PCB_OUT_DIR/data"
mkdir -p "$PCB_OUT_DIR/data/geog"
mkdir -p "$PCB_OUT_DIR/data/grib"
mkdir -p "$PCB_OUT_DIR/data/raw"
RAW_DATA="$PCB_OUT_DIR/data/raw/elevation"
GEOG_DATA="$PCB_OUT_DIR/data/geog/elevation"
WRXPY="$PCB_OUT_DIR/wrfxpy"

# Added new elevationd directory for cleaner paths

# ====== LOAD MODULES ======
module load StdEnv/2023 gcc/12.3
module load gdal/3.9.1
module load python/3.11
echo "Modules Loaded!"

echo "Environment loaded!"




cd $SCRATCH/wrfxpy
./convert_geotiff.sh $RAW_DATA/cdem_final.tif $GEOG_DATA ZSF

echo "ALL DONE!"
