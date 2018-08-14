#!/usr/bin/env bash

dem=$1

# convert geotif into arcgis flt
# ./tif_to_flt.sh ${dem} ${dem} 1

# generate the local, meso and broad `MaxElevationDeviation`s
./multiscale_signed_min.sh ${dem}

# generate the final RGB `MultiscaleTopographicPositionImage` geotif output
python multiscale_topographic_position_image_signed.py \
    -l ${dem}_min_mag0.flt \
    -m ${dem}_min_mag1.flt \
    -b ${dem}_min_mag2.flt \
    -i ${dem}.tif \
    -r 1 \
    -o multiscaled_min_${dem}.tif

