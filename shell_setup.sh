export PCB_REPO_DIR="$(pwd)"
export PCB_SCRIPTS_DIR="$PCB_REPO_DIR/scripts"
export PCB_OVERRIDE_DIR="$PCB_REPO_DIR/override"
export PCB_PROFILES_DIR="$PCB_REPO_DIR/profiles"
echo ""
export PCB_OUT_DIR="$PCB_REPO_DIR/out"
export PCB_LOGS_DIR="$PCB_OUT_DIR/logs"
export PCB_PRE_DIR="$PCB_OUT_DIR/preprocessing"
export PCB_DATA_DIR="$PCB_OUT_DIR/data"
echo ""
mkdir -p $PCB_OUT_DIR
mkdir -p $PCB_LOGS_DIR
mkdir -p $PCB_PRE_DIR
mkdir -p $PCB_DATA_DIR
echo "" 
export DIR="$PCB_OUT_DIR/.libraries"
export CC=gcc
export CXX=g++
export FC=gfortran
export FCFLAGS=-m64
export F77=gfortran
export FFLAGS=-m64
export JASPERLIB=$DIR/grib2/lib
export JASPERINC=$DIR/grib2/include
export PATH="$DIR/mpich/bin:$DIR/netcdf/bin:$DIR/hdf5/bin:$PATH"
export NETCDF=$DIR/netcdf
export HDF5=$DIR/hdf5/lib
export LDFLAGS="-L$DIR/grib2/lib -L${DIR}/hdf5/lib -L${DIR}/netcdf/lib"
export CPPFLAGS="-I$DIR/grib2/include -I${DIR}/hdf5/include -I${DIR}/netcdf/include"
export LD_LIBRARY_PATH=${DIR}/netcdf/lib:$DIR/hdf5/lib:$LD_LIBRARY_PATH
source $DIR/py4wrf/bin/activate
