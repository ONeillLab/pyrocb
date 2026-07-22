cd $PCB_OUT_DIR/WPS/geogrid/
ln -sf GEOGRID.TBL.FIRE GEOGRID.TBL

PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

mkdir $PCB_OUTPUT_DIR/$PROFILE/
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/input
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/geo_em
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/met_em
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/real_em
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/logs
# Directories for wrf.exe output
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/wrfout
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/history

cd $PCB_OUTPUT_DIR/$PROFILE/input
ln -sf $PCB_OUTPUT_DIR/WPS/geogrid.exe
ln -sf $PCB_OUTPUT_DIR/WPS/ungrib.exe
ln -sf $PCB_OUTPUT_DIR/WPS/metgrid.exe
ln -sf $PCB_OUTPUT_DIR/WPS/link_grib.csh
ln -sf $PCB_OUTPUT_DIR/WPS/ungrib/Variable_Tables

cd $PCB_OUTPUT_DIR/$PROFILE/output/geo_em
ln -sf $PCB_OUTPUT_DIR/$PROFILE/inputnamelist.wps
mpirun -np 1 $PCB_OUTPUT_DIR/$PROFILE/input/geogrid.exe 2>&1 | tee $PCB_OUTPUT_DIR/$PROFILE/logs/geogrid.log