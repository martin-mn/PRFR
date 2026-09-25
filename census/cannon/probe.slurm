#!/bin/bash
#SBATCH --job-name=PartnersRivals1.xq
#SBATCH --comment=PartnersRivals1
#SBATCH -p test
#SBATCH -N 1
#SBATCH -c 16
#SBATCH -t 00:20:00
#SBATCH --mem=4G
#SBATCH -o probe_%j.out
#SBATCH -e probe_%j.err
cd $SLURM_SUBMIT_DIR
bash task.sh probe 512 16 0 7 100 255
