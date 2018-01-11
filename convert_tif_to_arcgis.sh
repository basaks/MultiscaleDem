#!/usr/bin/env bash

# usage: convert_tif_to_flt.sh k_15v5 k_15v5

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

echo "Converting $1 to $2"


# first convert to bil
gdal_translate -of EHdr -ot Float32 $1.tif $2_bil.bil

# mv .bil to flt, don't copy to save space, helpful for really large files
cp $2_bil.bil $2.flt

# make a copy of the projection so `gdalinfo` shows projection information
cp $2_bil.prj $2.prj


# now change header
python header.py -b $2_bil.hdr -f $2.hdr