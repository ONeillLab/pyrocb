# Load Modules
ml StdEnv/2023 gcc/12.3 openmpi/4.1.5 hdf5 netcdf netcdf-fortran
echo "Modules Loaded!"

# Adapted from ./personal-ideal.sh 
cd $PCB_OUT_DIR/WRF-SFIRE

echo "[LOG] Compiling WRF-SFIRE"
mkdir -p $PCB_LOGS_DIR/compile
./compile em_real >& $PCB_LOGS_DIR/compile/compile.log
echo "[LOG] Finished Compiling WRF-SFIRE. View log in logs/compile/compile.log"