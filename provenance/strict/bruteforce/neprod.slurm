#! /bin/bash
# Strict-NE frequency over the whole strategy space -- PRODUCTION.
# 512 cells as 8 tasks of 64 contiguous rows.  Size -t from the probe's
# measured rate, not from this comment.
#SBATCH -J DiskM2IN.nescan
#SBATCH --comment=DiskM2IN
#SBATCH -p sapphire
#SBATCH -t 4:00:00
#SBATCH --nodes=1
#SBATCH -c 112
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH -o log/nes_%A_%a.txt
#SBATCH -e log/nese_%A_%a.txt

module load intel/25.2.1-fasrc01
export OMP_NUM_THREADS=112
export OMP_PROC_BIND=spread
export OMP_PLACES=cores
ulimit -s unlimited
export OMP_STACKSIZE=64M

cd $SLURM_SUBMIT_DIR
D=$SLURM_SUBMIT_DIR/ne_n100b3sun
mkdir -p $D
FIRST=$(( (SLURM_ARRAY_TASK_ID - 1) * 64 + 1 ))
LAST=$(( SLURM_ARRAY_TASK_ID * 64 ))
echo "task $SLURM_ARRAY_TASK_ID  rows $FIRST..$LAST  $(date '+%F %T')"
./nescan.x games_sun.dat $FIRST $LAST 4 run_n100b3sun $D
echo "task $SLURM_ARRAY_TASK_ID done $(date '+%F %T')"
