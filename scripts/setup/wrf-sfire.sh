cd $PCB_OUT_DIR
git clone https://github.com/openwfm/WRF-SFIRE.git
cd WRF-SFIRE
./configure

bash $PCB_SCRIPTS_DIR/override/configure-wrf.sh
echo [LOG] Overrode configure file with fixed configure files.