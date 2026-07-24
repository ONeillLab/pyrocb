cd $PCB_OUT_DIR/WPS/geogrid/
ln -sf $PCB_OVERRIDE_DIR/WPS/geogrid/GEOGRID.TBL.FIRE GEOGRID.TBL

PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

mkdir -p $PCB_OUTPUT_DIR/$PROFILE/
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/input
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/geo_em
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/met_em
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/real_em
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/logs
# Directories for wrf.exe output
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/wrfout
mkdir -p $PCB_OUTPUT_DIR/$PROFILE/output/history

cd $PCB_OUTPUT_DIR/$PROFILE/input
ln -sf $PCB_OUT_DIR/WPS/geogrid/geogrid.exe
ln -sf $PCB_OUT_DIR/WPS/ungrib/ungrib.exe
ln -sf $PCB_OUT_DIR/WPS/metgrid/metgrid.exe
ln -sf $PCB_OUT_DIR/WPS/link_grib.csh
ln -sf $PCB_OUT_DIR/WPS/ungrib/Variable_Tables

cd $PCB_OUTPUT_DIR/$PROFILE/output/geo_em
ln -sf $PCB_OUT_DIR/profile/namelist.wps $PCB_OUTPUT_DIR/$PROFILE/input/namelist.wps
ln -sf $PCB_OUT_DIR/profile/namelist.input $PCB_OUTPUT_DIR/$PROFILE/input/namelist.input

GEOG="$PCB_OUT_DIR/data/geog"

cp -rs $DIR/geog/ $PCB_OUT_DIR/data/

GEOGRID_TBL="$PCB_OUT_DIR/WPS/geogrid/"
METEM="$PCB_OUTPUT_DIR/$PROFILE/output/met_em/FILE"
METGRID_TBL="$PCB_OUT_DIR/WPS/metgrid/"
HISTORY_PATH="$PCB_OUTPUT_DIR/$PROFILE/output/history/wrfout_d<domain>_<date>"

sed -i \
  -e "s|^[[:space:]]*geog_data_path[[:space:]]*=.*| geog_data_path       = '$GEOG'|" \
  -e "s|^[[:space:]]*opt_geogrid_tbl_path[[:space:]]*=.*| opt_geogrid_tbl_path = '$GEOGRID_TBL'|" \
  -e "s|^[[:space:]]*prefix[[:space:]]*=.*| prefix               = '$METEM'|" \
  -e "s|^[[:space:]]*fg_name[[:space:]]*=.*| fg_name              = '$METEM'|" \
  -e "s|^[[:space:]]*opt_metgrid_tbl_path[[:space:]]*=.*| opt_metgrid_tbl_path = '$METGRID_TBL'|" \
  "$PCB_OUT_DIR/profile/namelist.wps"


PROFILE=$(cat "$PCB_OUT_DIR/profile/profile")

sed -i \
  -e "s|^[[:space:]]*history_outname[[:space:]]*=.*| history_outname = '$HISTORY_PATH'|" \
  "$PCB_OUT_DIR/profile/namelist.input"

cd $PCB_OUTPUT_DIR/$PROFILE/input
export FI_PROVIDER=tcp
mpirun -np 1 $PCB_OUTPUT_DIR/$PROFILE/input/geogrid.exe 2>&1 | tee $PCB_OUTPUT_DIR/$PROFILE/logs/geogrid.log