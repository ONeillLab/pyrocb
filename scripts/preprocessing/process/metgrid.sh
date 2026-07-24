PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

cd $PCB_OUTPUT_DIR/$PROFILE/output/met_em
ln -sf $PCB_OUTPUT_DIR/$PROFILE/input/geo_em.d01.nc .
ln -sf $PCB_OUTPUT_DIR/$PROFILE/input/geo_em.d02.nc .
ln -sf $PCB_OUTPUT_DIR/$PROFILE/input/geo_em.d03.nc .
ln -sf $PCB_OUTPUT_DIR/$PROFILE/input/namelist.wps .

cd $PCB_OUTPUT_DIR/$PROFILE/output/met_em
export FI_PROVIDER=tcp
$PCB_OUTPUT_DIR/$PROFILE/input/metgrid.exe 2>&1 $PCB_OUTPUT_DIR/$PROFILE/logs/metgrid.log
echo "Metgrid exit code: $?"