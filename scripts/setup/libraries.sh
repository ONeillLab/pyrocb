mkdir -p $DIR
cd $DIR

bash $PCB_SCRIPTS_DIR/setup/libraries/misc.sh
bash $PCB_SCRIPTS_DIR/setup/libraries/hdf5.sh
bash $PCB_SCRIPTS_DIR/setup/libraries/netcdf-c.sh
bash $PCB_SCRIPTS_DIR/setup/libraries/netcdf-fortran.sh
bash $PCB_SCRIPTS_DIR/setup/libraries/mpich.sh