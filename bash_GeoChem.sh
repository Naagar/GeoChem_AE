#!/bin/bash
#SBATCH -A research
#SBATCH --job-name=___
#SBATCH --qos=medium
#SBATCH -n 20
#SBATCH --gres=gpu:2
#SBATCH --output=output_files/r_VAE_GeoChem_%j.txt       # Output file.
#SBATCH --mail-type=END                # Enable email about job finish
#SBATCH --mail-user=sandeep.nagar@research.iiit.ac.in    # Where to send mail
#SBATCH --mem-per-cpu=3000
#SBATCH --time=4-00:00:00
#SBATCH --mail-type=END

module load cudnn/7-cuda-10.0

python VAE_k-Mean_GeoChem_ver_04_final.py
# eval "$(conda shell.bash hook)"
# conda activate my-rdkit-env
#
#
# echo "extracting ZINC to dataset_ZINC"
# cd ..
# cd ..
# cd scratch/
# mkdir -p dataset_ZINC
# wget --no-check-certificate http://zinc15.docking.org/substances/subsets/for-sale.mol2?count=all -O /scratch/dataset_ZINC/all.mol2
# obabel -imol2 /scratch/dataset_ZINC/all.mol2 -omol2 -/scratch/dataset_ZINC/zinc.mol2 -m
# spc share1/sandeep.nagar/dataset_ZINC/zinc.mol2 /scratch
# HYDRA_FULL_ERROR=1 python preprocess_zinc.py /scratch
# HYDRA_FULL_ERROR=1 python filter_zinc.py

# scp /scratch/zinc.mol2  ada:/share1/sandeep.nagar/
# HYDRA_FULL_ERROR=1 python train.py
