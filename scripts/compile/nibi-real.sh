# Load Modules
ml StdEnv/2023 gcc/12.3 openmpi/4.1.5
module load netcdf-fortran-mpi/4.6.1
module load wrf/4.7.1
echo "[LOG] Modules Loaded"

# Adapted from ./personal-ideal.sh 
cd $PCB_OUT_DIR/WRF-SFIRE

# after ./configure (or on the existing configure.wrf if you're not reconfiguring)
sed -i 's/^DM_CC[[:space:]]*=.*$/DM_CC           =       mpicc/' configure.wrf

echo "[LOG] Compiling WRF-SFIRE"
mkdir -p $PCB_LOGS_DIR/compile
./compile em_real >& $PCB_LOGS_DIR/compile/compile_wrf.log

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

./compile 2>&1 | tee $PCB_LOGS_DIR/compile/compile_wps.log
echo "[LOG] WPS Compiled"


# ====== CHECK WPS ======
if [ -f geogrid.exe ] && [ -f metgrid.exe ] && [ -f ungrib.exe ]; then
    echo "[LOG] WPS compiled!"
    ls -la *.exe
else
    echo "[ERROR] Compilation failed. check compile_wps.log"
    tail -50 $PCB_LOGS_DIR/compile/compile_wps.log
    exit 1
fi
