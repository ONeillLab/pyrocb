#!/bin/bash
#SBATCH --account=def-oneill
#SBATCH --job-name=wrf_selkirk_wrf_t1
#SBATCH --time=24:00:00
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=192
#SBATCH --mem=0
#SBATCH --output=/scratch/su386/pyrocb/out/logs/selkirk-alt-fgi-2024/%x_%j.out
#SBATCH --error=/scratch/su386/pyrocb/out/logs/selkirk-alt-fgi-2024/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=s.dosreis@mail.utoronto.ca

source $SCRATCH/pyrocb/alliance_can_shell_setup.sh 
module load StdEnv/2023 gcc/12 openmpi/4.1.5
echo $PCB_OUT_DIR

PROFILE=`cat $PCB_OUT_DIR/profile/profile`
echo $PROFILE

# Remove old history files. Make sure you saved files before!
cd $PCB_OUTPUT_DIR/$PROFILE/history
rm -rf wrfout_d0*

cd $PCB_OUTPUT_DIR/$PROFILE/wrfout
rm -f rsl.error.* rsl.out.*

cd $PCB_OUTPUT_DIR/$PROFILE/real_em
rm -f rsl.error.* rsl.out.*
ulimit -s unlimited
echo "Starting wrf.exe at $(date)"
srun bash -c "ulimit -s unlimited && ./wrf.exe" 2>&1 | tee $PCB_LOGS_DIR/$PROFILE/wrf.log
echo "wrf.exe exit code: $?"
echo "Job finished at $(date)"

tail -n 50 rsl.out.0000