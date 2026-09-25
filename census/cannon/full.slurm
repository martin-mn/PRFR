#!/bin/bash
#SBATCH --job-name=PartnersRivals1.xq
#SBATCH --comment=PartnersRivals1
#SBATCH -p test
#SBATCH -N 1
#SBATCH -c 48
#SBATCH -t 01:00:00
#SBATCH --mem=8G
#SBATCH -o full_%j.out
#SBATCH -e full_%j.err
cd $SLURM_SUBMIT_DIR
bash task.sh all 512 48
