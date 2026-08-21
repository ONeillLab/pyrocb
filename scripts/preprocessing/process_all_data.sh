# Sylvio Dos Reis, Micah Yoon, Noah Vaillant, 2026
# Processes the profiles selected data *after* having applied the crosswalk.
# Common errors includes not having an empty line at the end of your namelist.wps file, which will lead to metgrid, geogrid, and ungrib not finding the end of the file, and not having run the download_all_data or apply_crosswalk script.
# Best approach to solving these errors is restarting the process from the "Download all data" step, making sure the apply_crosswalk script has been run, and making sure to use process_all_data.sh to run this script.

bash $PCB_SCRIPTS_DIR/preprocessing/process/geogrid.sh
bash $PCB_SCRIPTS_DIR/preprocessing/process/ungrib.sh
bash $PCB_SCRIPTS_DIR/preprocessing/process/metgrid.sh
bash $PCB_SCRIPTS_DIR/preprocessing/process/prereal.sh