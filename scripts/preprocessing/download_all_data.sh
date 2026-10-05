# Sylvio Dos Reis, 2026
# Prompts for profile selection of and downloads the selected profile's data

python $PCB_OVERWRITE_PROFILE_VARS

bash $PCB_SCRIPTS_DIR/preprocessing/select_profile.sh
bash $PCB_SCRIPTS_DIR/preprocessing/download/download_fuel_data.sh
python $PCB_SCRIPTS_DIR/preprocessing/download/download_elevation_data.py
python $PCB_SCRIPTS_DIR/preprocessing/download/download_meterological_data.py