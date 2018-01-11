#!/usr/bin/env bash

# usage: tif_to_flt.sh k_15v5 k_15v5

# Will produce the following files:
# k_15v5_bil.bil
# k_15v5_bil.bil.aux.xml
# k_15v5_bil.hdr
# k_15v5_bil.prj
# k_15v5.flt
# k_15v5.hdr
# k_15v5.tif is the input geotif file

# k_15v5.flt is the .flt file with the k_15v5.hdr being the corresponding header file
# k_15v5_bil.bil is the .bil file with the k_15v5_bil.hdr being the corresponding header file



if [ $# -ne 2 ]; then
    echo $0: usage: convert_tif_to_flt_bil.sh input_geotif_file_w_o_ext output_flt_file_w_o_ext
    exit 1
fi

geotif=$1
flt=$2

echo "Converting ${geotif}.tif to ${flt}.flt"


# first convert to bil
gdal_translate -of EHdr -ot Float32 ${geotif}.tif ${flt}_bil.bil

# mv .bil to flt, don't copy to save space, helpful for really large files
mv $2_bil.bil ${flt}.flt

# make a copy of the projection so `gdalinfo` shows projection information
cp ${flt}_bil.prj ${flt}.prj


# now change header
python header.py -b ${flt}_bil.hdr -f ${flt}.hdr
