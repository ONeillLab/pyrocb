# Sylvio Dos Reis, Micah Yoon, 2026
# Downloads and compiles the netcdf for fortran library

cd $DIR
wget https://github.com/Unidata/netcdf-fortran/archive/refs/tags/v4.6.2.tar.gz -O netcdf-fortran-4.6.2.tar.gz
tar xzvf netcdf-fortran-4.6.2.tar.gz
rm -rf ./netcdf-fortran-4.6.2.tar.gz
cd netcdf-fortran-4.6.2
CPPFLAGS="-I$DIR/netcdf/include -I$DIR/hdf5/include" \
LDFLAGS="-L$DIR/netcdf/lib -L$DIR/hdf5/lib" \
LD_LIBRARY_PATH="$DIR/netcdf/lib:$DIR/hdf5/lib:$LD_LIBRARY_PATH" \
./configure --prefix=$DIR/netcdf
make -j$(nproc)
make install
cd ../
rm -rf ./netcdf-fortran-4.6.2