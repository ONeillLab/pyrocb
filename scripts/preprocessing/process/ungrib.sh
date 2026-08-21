# Sylvio Dos Reis, Micah Yoon, Noah Vaillant, 2026
# Links all necessary files to the right location and runs Geogrid. 
# Common errors includes not having run the download_meteoreological_data script.
# Best approach to solving these errors is restarting the process from the "Download all data" step, and making sure to use process_all_data.sh to run this script.

PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

cd $PCB_INPUT_DIR/$PROFILE
./link_grib.csh $PCB_OUT_DIR/data/grib/era5_single_levels.grib $PCB_OUT_DIR/data/grib/era5_pressure_levels.grib
ln -sf Variable_Tables/Vtable.ERA-interim.pl Vtable
cd $PCB_INPUT_DIR/$PROFILE
./ungrib.exe >& $PCB_LOGS_DIR/$PROFILE/ungrib.log
tail -100 $PCB_LOGS_DIR/$PROFILE/ungrib.log