cd $PCB_OUT_DIR
git clone https://github.com/openwfm/WRF-SFIRE.git
cd WRF-SFIRE
./configure

cd $PCB_OUT_DIR
git clone https://github.com/wrf-model/WPS.git

cd $PCB_OUT_DIR/WPS
export WRF_DIR=$PCB_OUT_DIR/WRF-SFIRE    # <-- points at WRF-SFIRE, not WRF-Fire
./configure
echo "WPS Configured!"
