mkdir -p $DIR
cd $DIR

mkdir -p "$PCB_LOGS_DIR/libraries"
bash $PCB_SCRIPTS_DIR/setup/libraries/misc.sh 2>&1 | tee "$PCB_LOGS_DIR/libraries/misc.log"
bash $PCB_SCRIPTS_DIR/setup/libraries/hdf5.sh 2>&1 | tee "$PCB_LOGS_DIR/libraries/hdf5.log"
bash $PCB_SCRIPTS_DIR/setup/libraries/netcdf-c.sh 2>&1 | tee "$PCB_LOGS_DIR/libraries/netcdfc.log"
bash $PCB_SCRIPTS_DIR/setup/libraries/netcdf-fortran.sh 2>&1 | tee "$PCB_LOGS_DIR/libraries/netcdffortran.log"
bash $PCB_SCRIPTS_DIR/setup/libraries/mpich.sh 2>&1 | tee "$PCB_LOGS_DIR/libraries/mpich.log"
bash $PCB_SCRIPTS_DIR/setup/libraries/wrfxpy.sh 2>&1 | tee "$PCB_LOGS_DIR/libraries/wrfxpy.log"
bash $PCB_SCRIPTS_DIR/setup/libraries/geog.sh 2>&1 | tee "$PCB_LOGS_DIR/libraries/geog.log"