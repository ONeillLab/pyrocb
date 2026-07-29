
#ZLib
cd $DIR
wget https://www.zlib.net/fossils/zlib-1.3.1.tar.gz
tar xzvf zlib-1.3.1.tar.gz
rm -rf ./zlib-1.3.1.tar.gz
cd zlib-1.3.1
./configure --prefix=$DIR/grib2
make -j$(nproc)
make install
cd ../
rm -rf ./zlib-1.3.1

# Libpng
cd $DIR
wget https://download.sourceforge.net/libpng/libpng-1.6.43.tar.gz
tar xzvf libpng-1.6.43.tar.gz
rm -rf ./libpng-1.6.43.tar.gz
cd libpng-1.6.43
./configure --prefix=$DIR/grib2
make -j$(nproc)
make install
cd ../
rm -rf ./libpng-1.6.43

# Jasper (jasper-build directory must be outside source)
cd $DIR
wget https://www.ece.uvic.ca/~frodo/jasper/software/jasper-1.900.1.zip
unzip jasper-1.900.1.zip
rm -rf ./jasper-1.900.1.zip
mkdir -p jasper-build
cd jasper-build
../jasper-1.900.1/configure --prefix=$DIR/grib2
make -j$(nproc)
make install
cd ../
rm -rf ./jasper-1.900.1