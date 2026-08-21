# Sylvio Dos Reis 2026
# Cleans all files to reset to the "download all data" stage of the wrf run

read -p "Are you sure you would like to clean the project directory? Make sure you have saved your files first. (y/n) " choice
case "$choice" in 
  y|Y ) echo "Cleaning and resetting project directory";;
  n|N ) echo "Cancelling" && exit 1 || return 1;;
  * ) echo "invalid" && exit 1 || return 1;;
esac

cd $PCB_OUTPUT_DIR
for item in *; do
    case "$item" in
        crosswalk|crosstab|complete);;
        *)
            echo "Deleting $item"
            rm -rf -- "$item";;
    esac
done

echo "Deleting $PCB_DATA_DIR/geog"
rm -rf "$PCB_DATA_DIR/geog"
echo "Resetting profile"
rm -rf "$PCB_OUT_DIR/profile"
echo "Soft reset workspace"
echo "To launch a new instance, select a profile, download all data, process all data, and run wrf"