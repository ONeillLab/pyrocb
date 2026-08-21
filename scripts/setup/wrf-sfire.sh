# Sylvio Dos Reis, 2026
# Clones and configures the WRF-SFIRE git repository and compile script. Also clones WPS.

cd $PCB_OUT_DIR
export NETCDF=$DIR/netcdf

# Clones WRF-SFIRE from GitHub
git clone https://github.com/openwfm/WRF-SFIRE.git
cd WRF-SFIRE
./configure <<< $'34\n1' # We pass 34 for the configuration because we want to use multiple cores, and use the default 1 option 

# We override the CPP compiler in WRF to point it to our CPP as it does not properly do this automatically and may not compile otherwise.
sed -i 's/^DM_CC[[:space:]]*=.*$/DM_CC           =       mpicc/' configure.wrf
grep -n "^CPP" configure.wrf
sed -i "s|/lib/cpp|$(which cpp)|" configure.wrf

echo "[LOG] WRF-SFire Configured"

# Clones WPS
cd $PCB_OUT_DIR
git clone https://github.com/wrf-model/WPS.git
# We dont yet configure WPS because WRF needs to be compiled before we configure and compile WP, and compiling is done with the scripts/compile/nibi-real.sh script.
