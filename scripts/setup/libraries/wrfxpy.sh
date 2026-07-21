cd $DIR
git clone https://github.com/openwfm/wrfxpy
cd wrfxpy
git checkout convert_geotiff

virtualenv $DIR/py4wrf
source $DIR/py4wrf/bin/activate

pip install --no-index rasterio pyproj numpy scipy pandas h5py dill requests psutil pytz paramiko f90nml xmltodict cdsapi requests json sys
pip install "numpy<2"

echo 'export PYTHONPATH=/cvmfs/soft.computecanada.ca/easybuild/software/2023/x86-64-v4/Compiler/gcc12/gdal/3.9.1/lib/python3.11/site-packages:$PYTHONPATH' >> $DIR/py4wrf/bin/activate

sed -i 's|export PYTHONPATH=src|export PYTHONPATH=src:$PYTHONPATH|' $DIR/wrfxpy/convert_geotiff.sh
sed -i 's/import gdal, osr, pyproj, rasterio/from osgeo import gdal, osr\nimport pyproj, rasterio/' $DIR/wrfxpy/src/geo/geodriver.py

