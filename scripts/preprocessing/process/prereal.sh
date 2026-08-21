# Sylvio Dos Reis, Micah Yoon, Noah Vaillant, 2026
# Its time to prereal
# Links all necessary files to the right location in preperation for running real.exe. 
# Common errors includes not having an empty line at the end of your namelist.wps file, and not having run metgrid, geogrid, and ungrib.

PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

cd $PCB_OUTPUT_DIR/$PROFILE/real_em
ln -sf $PCB_OUT_DIR/WRF-SFIRE/run/* .
rm -f ideal.exe tc.exe ndown.exe
ln -sf $PCB_OUT_DIR/WRF-SFIRE/main/real.exe .
ln -sf $PCB_OUT_DIR/WRF-SFIRE/main/wrf.exe .
ln -sf $PCB_OUTPUT_DIR/$PROFILE/met_em/met_em.d0*.nc .
ln -sf $PCB_INPUT_DIR/$PROFILE/namelist.input .
ln -sf $PCB_OUT_DIR/profile/namelist.fire .
ln -sf $PCB_OUT_DIR/profile/namelist.fire $PCB_OUTPUT_DIR/$PROFILE/wrfout/
ln -sf $PCB_OUT_DIR/profile/namelist.fire $PCB_OUTPUT_DIR/$PROFILE/real_em/
ln -sf $PCB_OUTPUT_DIR/$PROFILE/geo_em/geo_em.d01.nc .
ln -sf $PCB_OUTPUT_DIR/$PROFILE/geo_em/geo_em.d02.nc .
ln -sf $PCB_OUTPUT_DIR/$PROFILE/geo_em/geo_em.d03.nc .

ln /scratch/su386/pyrocb/out/WRF-SFIRE/test/em_fire/hill/namelist.fire_emissions.tracers $PCB_OUTPUT_DIR/$PROFILE/real_em/namelist.fire_emissions