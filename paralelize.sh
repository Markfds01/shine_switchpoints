declare -a array_deaths=("AN" "AR" "CL" "CM" "CT" "EX" "GA" "IB" "MC" "MD" "PV" "Spain" "VC")

# Use parallel to run the jobs concurrently
parallel -j 15 python3 main.py -r {} -ns 2 -sw -ag ::: "${array_deaths[@]}"