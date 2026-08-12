PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo "$PCB_OUTPUT_DIR"
echo "$PROFILE"



read -p "Enter a name to save run \"$PROFILE\" as complete: " name

read -p "Are you sure you would like to save the project to \"$PCB_OUTPUT_DIR/complete/$name\"? (y/n) " choice
case "$choice" in 
  y|Y ) echo "Saving to \"$PCB_OUTPUT_DIR/complete/$name\"";;
  n|N ) echo "Cancelling" && exit 1 || return 1;;
  * ) echo "invalid" && exit 1 || return 1;;
esac


echo "Saving history to \"$PCB_OUTPUT_DIR/complete/$name\""
mkdir -p "$PCB_OUTPUT_DIR/complete/$name"
cp -an "$PCB_OUTPUT_DIR/$PROFILE/history/." "$PCB_OUTPUT_DIR/complete/$name"
echo "Saving profile to \"$PCB_OUTPUT_DIR/complete/$name/profile\""
mkdir "$PCB_OUTPUT_DIR/complete/$name/profile"
cp -an "$PCB_OUT_DIR/profile/." "$PCB_OUTPUT_DIR/complete/$name/profile"
echo "Saving rsl.out to \"$PCB_OUTPUT_DIR/complete/$name/rsl_out\""
mkdir -p "$PCB_OUTPUT_DIR/complete/$name/rsl_out"
cp -an "$PCB_OUTPUT_DIR/$PROFILE/real_em"/rsl.out* "$PCB_OUTPUT_DIR/complete/$name/rsl_out"
echo "Saving rsl.error to \"$PCB_OUTPUT_DIR/complete/$name/rsl_error\""
mkdir "$PCB_OUTPUT_DIR/complete/$name/rsl_error"
cp -an "$PCB_OUTPUT_DIR/$PROFILE/real_em"/rsl.error* "$PCB_OUTPUT_DIR/complete/$name/rsl_error"