#!/usr/bin/env bash

dem=$1

# convert geotif into arcgis flt
# ./tif_to_flt.sh ${dem} ${dem} 1

# generate the local, meso and broad `MaxElevationDeviation`s
./multiscale_signed_max.sh ${dem}

# generate the final RGB `MultiscaleTopographicPositionImage` geotif output
python multiscale_topographic_position_image.py \
    -l ${dem}_max_mag0.flt \
    -m ${dem}_max_mag1.flt \
    -b ${dem}_max_mag2.flt \
    -i ${dem}.tif \
    -o multiscaled_max_${dem}.tif
