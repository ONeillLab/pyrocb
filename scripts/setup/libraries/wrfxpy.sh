# Sylvio Dos Reis, 2026
# Downloads the wrfxpy github library, creates a virtual enviorment, and downloads the python packages necessary to run all scripts.

cd $DIR
wget https://github.com/openwfm/wrfxpy/archive/refs/heads/convert_geotiff.zip # Using the git clone and git checkout methods led to several crashes when trying to switch branches, so we are instead download the zip of the branch and decompressing it
unzip convert_geotiff.zip
rm -rf convert_geotiff.zip
mv $DIR/wrfxpy-convert_geotiff $DIR/wrfxpy

# Create virtual enviornment
virtualenv $DIR/py4wrf
source $DIR/py4wrf/bin/activate

# Installs all necessary python packages in the virtual enviornment. If more python packages are needed, add it to this line.
pip install rasterio pyproj numpy scipy pandas h5py dill requests psutil pytz paramiko f90nml xmltodict cdsapi requests geopandas matplotlib alpha_shapes imageio xarray wrf-python
pip install gdal
pip install "numpy<2"

# We make sure that the python path for the alliance canada computers are properly configured
echo 'export PYTHONPATH=/cvmfs/soft.computecanada.ca/easybuild/software/2023/x86-64-v4/Compiler/gcc12/gdal/3.9.1/lib/python3.11/site-packages:$PYTHONPATH' >> $DIR/py4wrf/bin/activate

# Properly set the python path for the convert_geotiff.sh script.
sed -i 's|export PYTHONPATH=src|export PYTHONPATH=src:$PYTHONPATH|' $DIR/wrfxpy/convert_geotiff.sh
sed -i 's/import gdal, osr, pyproj, rasterio/from osgeo import gdal, osr\nimport pyproj, rasterio/' $DIR/wrfxpy/src/geo/geodriver.py # GeoDriver was using an outdated osgeo import line, so we're replacing it with and import for gdal.
