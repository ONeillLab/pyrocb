PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

cd $PCB_OUTPUT_DIR/$PROFILE/input
./link_grib.csh $PCB_OUT_DIR/data/grib/era5_single_levels.grib $PCB_OUT_DIR/data/grib/era5_pressure_levels.grib
ln -sf Variable_Tables/Vtable.ERA-interim.pl Vtable
cd $PCB_OUTPUT_DIR/$PROFILE/input
./ungrib.exe >& $PCB_OUTPUT_DIR/$PROFILE/logs/ungrib.log
tail -100 $PCB_OUTPUT_DIR/$PROFILE/logs/ungrib.log