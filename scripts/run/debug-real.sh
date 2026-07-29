PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

cd $PCB_OUTPUT_DIR/$PROFILE/real_em
rm -f wrfinput_d0* wrfbdy_d01
srun ./real.exe 2>&1 | tee $PCB_LOGS_DIR/$PROFILE/real.log
echo "[LOG] Exit code: $?"
echo "[LOG] tail of rsl.out.0000:"

tail -n 20 rsl.out.0000
