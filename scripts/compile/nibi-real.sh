# Sylvio Dos Reis, Micah Yoon, Noah Vaillant, 2026
# Compiles WRF-SFIRE, configures WPS, and compiles WPS to be run on alliance canada computers.

# Load Modules
ml StdEnv/2023 gcc/12.3 openmpi/4.1.5
module load wrf/4.7.1
echo "[LOG] Modules Loaded"

# Adapted from ./personal-ideal.sh 
cd $PCB_OUT_DIR/WRF-SFIRE
export NETCDF=$DIR/netcdf

echo "[LOG] Compiling WRF-SFIRE"
mkdir -p $PCB_LOGS_DIR/compile
./compile em_real 2>&1 | tee $PCB_LOGS_DIR/compile/compile_wrf.log

echo "[LOG] Finished Compiling WRF-SFIRE. View log in logs/compile/compile_wrf.log"

if [ -f test/em_real/real.exe ]; then
    echo "[LOG] WRF-SFIRE compiled!"
    ls -la test/em_real/*.exe
else
    echo "[ERROR] Compilation failed. check compile.log"
    tail -50 $PCB_LOGS_DIR/compile/compile_wrf.log
    exit 1
fi


cd $PCB_OUT_DIR/WPS
export WRF_DIR=$PCB_OUT_DIR/WRF-SFIRE
# We are passing 3 again to configure it for multicore running
./configure <<< "3"
CPP_PATH="$(command -v cpp)"
sed -i "s|/usr/bin/cpp|${CPP_PATH}|g" configure.wps # We override the cpp path again the point it to the right file
sed -i 's/-lnetcdff -lnetcdf/-lnetcdff -lnetcdf -lhdf5_hl -lhdf5/g' configure.wps # We pass in our netcdf, netcdff, and hdf5 libraries.

echo "[LOG] WPS Configured"

# We properly compile WPS.
./compile 2>&1 | tee $PCB_LOGS_DIR/compile/compile_wps.log
echo "[LOG] WPS Compiled"


# We check to make sure geogrid.exe, metgrid.exe, and ungrib.exe are properly located.
if [ -f geogrid.exe ] && [ -f metgrid.exe ] && [ -f ungrib.exe ]; then
    echo "[LOG] WPS compiled!"
    ls -la *.exe
else
    echo "[ERROR] Compilation failed. check compile_wps.log"
    tail -50 $PCB_LOGS_DIR/compile/compile_wps.log
    exit 1
fi
