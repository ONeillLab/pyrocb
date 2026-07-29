cd $PCB_OUT_DIR
export NETCDF=$DIR/netcdf
git clone https://github.com/openwfm/WRF-SFIRE.git
cd WRF-SFIRE
./configure <<< $'34\n1'

sed -i 's/^DM_CC[[:space:]]*=.*$/DM_CC           =       mpicc/' configure.wrf
grep -n "^CPP" configure.wrf
sed -i "s|/lib/cpp|$(which cpp)|" configure.wrf

echo "[LOG] WRF-SFire Configured"

cd $PCB_OUT_DIR
git clone https://github.com/wrf-model/WPS.git

