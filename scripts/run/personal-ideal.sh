# Sylvio Dos Reis, 2026
# Run wrf.exe for the ideal case on your personal computer.

export PCB_PERSONAL_IDEAL_CASE="hill_simple"

cd $PCB_OUT_DIR/WRF-SFIRE/test/em_fire

ln -sf namelist.input_$PCB_PERSONAL_IDEAL_CASE namelist.input
ln -sf namelist.fire_$PCB_PERSONAL_IDEAL_CASE namelist.fire
ln -sf input_sounding_$PCB_PERSONAL_IDEAL_CASE input_sounding
echo [LOG] Linked files for $PCB_PERSONAL_IDEAL_CASE case.

./ideal.exe
echo [LOG] Initialized
tail -n 20 rsl.out.0000
read -p "Double check the initialization was completed successfully (last ten 20 lines printed above) and then hit enter to proceed"

echo "[LOG] Starting simulation at $(date +"%Y-%m-%d %H:%M:%S") (log in wrf.log)"
mpirun -np 4 --bind-to core --map-by core ./wrf.exe >& $PCB_LOGS_DIR/compile/wrf.log
echo "[LOG] Simulation complete at $(date +"%Y-%m-%d %H:%M:%S"). View log in wrf.log"
tail -n 20 rsl.out.0000

mkdir -p "${PCB_OUT_DIR}/output/wrf/data"
mkdir -p "${PCB_OUT_DIR}/output/wrf/logs"
rename 's/:/_/g' wrfout*
rsync -avh --progress "./"wrfout_d* "${PCB_OUT_DIR}/output/wrf/data"
echo [LOG] Data copied to "${PCB_OUT_DIR}/output/wrf/data".
rsync -avh --progress "./"rsl.* "${PCB_OUT_DIR}/output/wrf/logs"
echo [LOG] Logs copied to "${PCB_OUT_DIR}/output/wrf/logs".
read -p "Double check data was properly copied, and hit enter to ./clean. Otherwise, terminate the script"
./clean