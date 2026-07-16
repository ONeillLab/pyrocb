cd $DIR
wget https://github.com/HDFGroup/hdf5/releases/download/hdf5_1.14.6/hdf5-1.14.6.tar.gz
tar xzvf hdf5-1.14.6.tar.gz
rm -rf ./hdf5-1.14.6.tar.gz
cd hdf5-1.14.6
./configure --prefix=$DIR/hdf5 --enable-fortran --enable-shared
make -j$(nproc)
make install
cd ../
rm -rf ./hdf5-1.14.6