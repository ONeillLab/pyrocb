# Sylvio Dos Reis, Micah Yoon, 2026
# Downloads and compiles the netcdf for c library.

cd $DIR
wget https://downloads.unidata.ucar.edu/netcdf-c/4.10.0/netcdf-c-4.10.0.tar.gz
tar xzvf netcdf-c-4.10.0.tar.gz
rm -rf ./netcdf-c-4.10.0.tar.gz
cd netcdf-c-4.10.0
CPPFLAGS="-I$DIR/hdf5/include" \
LDFLAGS="-L$DIR/hdf5/lib" \
LD_LIBRARY_PATH="$DIR/hdf5/lib:$LD_LIBRARY_PATH" \
./configure --prefix=$DIR/netcdf --disable-dap --enable-netcdf-4 --with-hdf5=$DIR/hdf5
make -j$(nproc)
make install
cd ../
rm -rf ./netcdf-c-4.10.0

