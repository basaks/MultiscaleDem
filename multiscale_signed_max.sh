#!/usr/bin/env bash

if [[ $# -lt 1 ]]; then
    echo $0: usage1: ./multiscale.sh flt_dem
    echo $0: usage2: ./multiscale.sh flt_dem 1
    echo $0: "2nd parameter is the parallel boolean flag, needs GNU parallel
    package. Default is 0 or sequential processing."
    echo $0: the flt_dem is the dem flt filename without the .flt extension
    exit 1
fi

WHITEBOX_TOOLS=/home/sudipta/repos/whitebox-tools/target/release/whitebox_tools

flt=$1
parallel_bool=${2-0}  # default is 0, i.e.,sequential
echo "Constructing local, meso and broad scale MaxElevationDeviation for $1
.flt in parallel"

maxeledev(){
    echo "Calculate maxeledev for flt: $5 with params min_scale:$2, max_scale:$3, step: $4"
    scale=$1
    min_scale=$2
    max_scale=$3
    step=$4
    flt=$5

    $WHITEBOX_TOOLS -r=MaxSignedElevationDeviation -v --dem=$PWD/${flt}.flt \
        -out_mag=$PWD/${flt}_max_mag${scale}.flt \
        --out_scale=$PWD/${flt}_max_scale${scale}.flt \
        --min_scale=${min_scale} --max_scale=${max_scale} --step=${step}

    # remove the unused _scale file
    rm $PWD/${flt}_max_scale${scale}.*
}

# Define the arrays
min_scales=(3 100 800)
max_scales=(99 795 1800)
steps=(1 5 10)

export -f maxeledev

if ! [[ -x "$(command -v parallel)" ]]; then
    echo "Warning: GNU parallel is not installed. Install it with 'apt install parallel' "
    echo "Info: Will process dems in sequence"
    parallel_bool=0
fi

if [[ ${parallel_bool} -eq 1 ]]; then
        echo 'Info: Parallel processin g of MaxElevationDeviation.'
        echo 'Info: Needs ~3X memory compared to sequential processing'
        parallel --jobs 3 -m maxeledev ::: \
            0 ${min_scales[0]} ${max_scales[0]} ${steps[0]} ${flt} \
            1 ${min_scales[1]} ${max_scales[1]} ${steps[1]} ${flt} \
            2 ${min_scales[2]} ${max_scales[2]} ${steps[2]} ${flt}
else
    echo 'Info: Sequential processing of MaxElevationDeviation.'
    echo 'Info: Choose this option when not enough memory is available'
    for ((i=0;i<3;i++)); do
        maxeledev ${i} ${min_scales[$i]} ${max_scales[$i]} ${steps[$i]} ${flt}
    done
fi

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
