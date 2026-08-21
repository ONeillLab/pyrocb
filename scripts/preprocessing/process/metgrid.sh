# Sylvio Dos Reis, Micah Yoon, Noah Vaillant, 2026
# Links all necessary files to the right location and runs metgrid. 
# Common errors includes not having an empty line at the end of your namelist.wps file, which will lead to metgrid not finding the end of the file, and not having run the download_meteoreological_data or ungrib script.
# Best approach to solving these errors is restarting the process from the "Download all data" step, and making sure to use process_all_data.sh to run this script.

PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

cd $PCB_OUTPUT_DIR/$PROFILE/met_em
ln -sf $PCB_INPUT_DIR/$PROFILE/geo_em.d01.nc .
ln -sf $PCB_INPUT_DIR/$PROFILE/geo_em.d02.nc .
ln -sf $PCB_INPUT_DIR/$PROFILE/geo_em.d03.nc .
ln -sf $PCB_INPUT_DIR/$PROFILE/namelist.wps .

cd $PCB_OUTPUT_DIR/$PROFILE/met_em
export FI_PROVIDER=tcp
$PCB_INPUT_DIR/$PROFILE/metgrid.exe 2>&1 $PCB_LOGS_DIR/$PROFILE/metgrid.log
echo "Metgrid exit code: $?"