#!/bin/bash

# Clear results folder
#rm -f results/*

# Run baseline switchpoint estimation
#declare -a array=("AN" "AR" "Belgium" "CL" "CM" "CT" "Czechia" "EX" "France" "GA" "Germany" "IB" "Italy" "MC" "MD" "PV" "Spain" "VC")

#for region in "${array[@]}"
#do
#    echo "Running 2 switchpoint estimation for $region"
#    python3 main.py -r $region -ns 2
#done

# Run death estimation
declare -a array_deaths=("AN" "AR" "CL" "CM" "CT" "EX" "GA" "IB" "MC" "MD" "PV" "Spain" "VC")

for region in "${array_deaths[@]}"
do
    echo "Running 2 switchpoint death estimation for $region...\n\n"
    python3 main.py -r $region -ns 3 -sw
done
