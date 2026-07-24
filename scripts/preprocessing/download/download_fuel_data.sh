
echo [LOG] Downloading Canada Fire Behavior Prediction Fuel Types
wget "https://cwfis.cfs.nrcan.gc.ca/downloads/fuels/current/FBP_fueltypes_Canada_30m_EPSG3978_20240522.zip" -O "$PCB_DATA_DIR/FBP_fueltypes_Canada_30m_EPSG3978_20240522.zip"
mkdir "$PCB_DATA_DIR/FBP_fueltypes_Canada_30m" 
unzip -n -d "$PCB_DATA_DIR/FBP_fueltypes_Canada_30m" "$PCB_DATA_DIR/FBP_fueltypes_Canada_30m_EPSG3978_20240522.zip"
rm -rf "$PCB_DATA_DIR/FBP_fueltypes_Canada_30m_EPSG3978_20240522.zip"


echo [LOG] Downloading 13 Anderson Fire Behavior Fuel Models
wget "https://www.landfire.gov/data-downloads/CONUS_LF2024/LF2024_FBFM13_CONUS.zip" -O "$PCB_DATA_DIR/LF2024_FBFM13_CONUS.zip"
mkdir "$PCB_DATA_DIR/LF2024_FBFM13_CONUS"
unzip -n -d "$PCB_DATA_DIR/LF2024_FBFM13_CONUS" "$PCB_DATA_DIR/LF2024_FBFM13_CONUS.zip"
rm -rf "$PCB_DATA_DIR/LF2024_FBFM13_CONUS.zip"

wget "https://www.landfire.gov/data-downloads/AK_LF2024/LF2024_FBFM13_AK.zip" -O "$PCB_DATA_DIR/LF2024_FBFM13_AK.zip"
mkdir "$PCB_DATA_DIR/LF2024_FBFM13_AK"
unzip -n -d "$PCB_DATA_DIR/LF2024_FBFM13_AK" "$PCB_DATA_DIR/LF2024_FBFM13_AK.zip"
rm -rf "$PCB_DATA_DIR/LF2024_FBFM13_AK.zip"

echo [LOG] Downloading 40 Scott and Burgan Fire Behavior Fuel Models
wget "https://www.landfire.gov/data-downloads/CONUS_LF2024/LF2024_FBFM40_CONUS.zip" -O "$PCB_DATA_DIR/LF2024_FBFM40_CONUS.zip"
mkdir "$PCB_DATA_DIR/LF2024_FBFM40_CONUS"
unzip -n -d "$PCB_DATA_DIR/LF2024_FBFM40_CONUS" "$PCB_DATA_DIR/LF2024_FBFM40_CONUS.zip"
rm -rf "$PCB_DATA_DIR/LF2024_FBFM40_CONUS.zip"

wget "https://www.landfire.gov/data-downloads/AK_LF2024/LF2024_FBFM40_AK.zip" -O "$PCB_DATA_DIR/LF2024_FBFM40_AK.zip"
mkdir "$PCB_DATA_DIR/LF2024_FBFM40_AK"
unzip -n -d "$PCB_DATA_DIR/LF2024_FBFM40_AK" "$PCB_DATA_DIR/LF2024_FBFM40_AK.zip"
rm -rf "$PCB_DATA_DIR/LF2024_FBFM40_AK.zip"

