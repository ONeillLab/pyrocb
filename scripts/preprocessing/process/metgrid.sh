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