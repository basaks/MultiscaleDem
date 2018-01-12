#!/usr/bin/env bash

if [ $# -ne 1 ]; then
    echo $0: usage: ./multiscale.sh flt_dem without the .flt extension
    exit 1
fi

flt=$1
echo "Constructing local, meso and broad scale MaxElevationDeviation for $1.flt"

maxeledev(){
    echo "submitting job min_scale:$2, max_scale:$3, spep: $4"
    scale=$1
    min_scale=$2
    max_scale=$3
    step=$4

    whitebox_tools -r=MaxElevationDeviation -v --dem=$PWD/${flt}.flt \
        -out_mag=$PWD/${flt}_mag${scale}.flt \
        --out_scale=$PWD/${flt}_scale${scale}.flt \
        --min_scale=${min_scale} --max_scale=${max_scale} --step=${step}

    # remove the unused _scale file
    rm $PWD/${flt}_scale${scale}.*
}

# Define the arrays
min_scales=(3 100 800)
max_scales=(99 795 1800)
steps=(1 5 10)

# do the parallel loop
for ((i=0;i<3;i++)); do
    echo "${i}, ${min_scales[$i]}, ${max_scales[$i]}, ${steps[$i]}"
    maxeledev ${i} ${min_scales[$i]} ${max_scales[$i]} ${steps[$i]} &
done

wait

echo 'Finished processing all MaxElevationDeviations'

#  MultiscaleTopographicPositionImage is not working on ubuntu
#whitebox_tools -r=MultiscaleTopographicPositionImage -v \
#    --local=$PWD/$1_mag1.flt \
#    --meso=$PWD/$1_mag2.flt \
#    --broad=$PWD/$1_mag3.flt \
#    --output=$PWD/multiscale.flt

# because MultiscaleTopographicPositionImage did not work, I copied John
# Lindsay's paper implementation in a python script:
# multiscale_topographic_position_image.py
# (http://www.sciencedirect.com/science/article/pii/S0169555X15300076)
