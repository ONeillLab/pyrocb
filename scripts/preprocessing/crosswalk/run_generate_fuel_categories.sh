# Sylvio Dos Reis, 2026
# Runs python script for creating custom canadian fuel categories based on the fbp.json file, applying the crosswalk for the remaining parameters, and converting the geotiff, passing in the necessary out dir path

python3 "$PCB_SCRIPTS_DIR/preprocessing/crosswalk/generate_fuel_categories.py" $PCB_OUT_DIR