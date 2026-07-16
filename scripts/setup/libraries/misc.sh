sudo apt -y update
sudo apt -y upgrade
# CMake, zlib, csh
sudo apt -y install cmake
sudo apt -y install zlib1g-dev pkg-config
sudo apt -y install csh

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
wget https://github.com/jasper-software/jasper/releases/download/version-4.2.4/jasper-4.2.4.tar.gz
tar xzvf jasper-4.2.4.tar.gz
rm -rf ./jasper-4.2.4.tar.gz
mkdir -p jasper-build
cd jasper-build
cmake -DCMAKE_INSTALL_PREFIX=$DIR/grib2 ../jasper-4.2.4
make -j$(nproc)
make install
cd ../
rm -rf ./jasper-4.2.4
