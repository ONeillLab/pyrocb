cd $DIR
wget https://www.mpich.org/static/downloads/5.0.1/mpich-5.0.1.tar.gz
tar xzvf mpich-5.0.1.tar.gz
rm -rf ./mpich-5.0.1.tar.gz
cd mpich-5.0.1
./configure --prefix=$DIR/mpich
make -j$(nproc)
make install
cd ../
rm -rf ./mpich-5.0.1
