# Sylvio Dos Reis, 2026
# Compiles WRF-SFIRE to be run on your personal machine

cd $PCB_OUT_DIR/WRF-SFIRE

echo "[LOG] Compiling WRF-SFIRE"
mkdir -p $PCB_LOGS_DIR/compile
./compile em_fire >& $PCB_LOGS_DIR/compile/compile.log
echo "[LOG] Finished Compiling WRF-SFIRE. View log in logs/compile/compile.log"