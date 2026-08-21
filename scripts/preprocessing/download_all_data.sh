# Sylvio Dos Reis, 2026
# Prompts for profile selection of and downloads the selected profile's data

bash $PCB_SCRIPTS_DIR/preprocessing/select_profile.sh
bash $PCB_SCRIPTS_DIR/preprocessing/download/download_fuel_data.sh
bash $PCB_SCRIPTS_DIR/preprocessing/download/run_download_elevation_data.sh
bash $PCB_SCRIPTS_DIR/preprocessing/download/run_download_meterological_data.sh