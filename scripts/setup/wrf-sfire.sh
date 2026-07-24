cd $PCB_OUT_DIR
git clone https://github.com/openwfm/WRF-SFIRE.git
cd WRF-SFIRE
./configure

sed -i 's/^DM_CC[[:space:]]*=.*$/DM_CC           =       mpicc/' configure.wrf

echo "[LOG] WRF-SFire Configured"

cd $PCB_OUT_DIR
git clone https://github.com/wrf-model/WPS.git

cd $PCB_OUT_DIR/WPS
export WRF_DIR=$PCB_OUT_DIR/WRF-SFIRE
./configure
echo "[LOG] WPS Configured"
