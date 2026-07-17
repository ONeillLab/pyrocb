# Load Modules
ml StdEnv/2023 gcc/12.3 openmpi/4.1.5
module load wrf/4.7.1
echo "Modules Loaded!"

# Adapted from ./personal-ideal.sh 
cd $PCB_OUT_DIR/WRF-SFIRE

echo "[LOG] Compiling WRF-SFIRE"
mkdir -p $PCB_LOGS_DIR/compile
./compile em_real >& $PCB_LOGS_DIR/compile/compile_wrf.log
echo "[LOG] Finished Compiling WRF-SFIRE. View log in logs/compile/compile_wrf.log"

if [ -f test/em_fire/ideal.exe ]; then
    echo "SUCCESS: WRF-SFIRE compiled!"
    ls -la test/em_fire/*.exe
else
    echo "FAILED: check compile.log"
    tail -50 compile.log
    exit 1
fi


cd $PCB_OUT_DIR
git clone https://github.com/wrf-model/WPS.git

cd $PCB_OUT_DIR/WPS
export WRF_DIR=$PCB_OUT_DIR/WRF-SFIRE    # <-- points at WRF-SFIRE, not WRF-Fire
./configure
echo "WPS Configured!"

./compile 2>&1 | tee compile_wps.log
echo "WPS Compiled!"

# ====== CHECK WPS ======
if [ -f geogrid.exe ] && [ -f metgrid.exe ] && [ -f ungrib.exe ]; then
    echo "SUCCESS: WPS compiled!"
    ls -la *.exe
else
    echo "FAILED: check compile_wps.log"
    tail -50 compile_wps.log
    exit 1
fi
