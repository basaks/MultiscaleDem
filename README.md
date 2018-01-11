### MultiscaleTopographicPositionImage of DEM

We follow the paper by J.B.Lindsay, J.M.H.Cockburn, H.A.J.Russell titled 
[`An integral image approach to performing multi-scale topographic position 
analysis`](http://www.sciencedirect.com/science/article/pii/S0169555X15300076)
to obtain a MultiElevationDeviation map of continental Australia at 90m and 
30m resolution.


### MaxElevationDeviation
We also use the [WhiteboxBoxTools](https://github.com/jblindsay/whitebox-geospatial-analysis-tools/tree/master/whitebox_tools) 
software for creating `local`, `meso`, `broad` range `MaxElevationDeviation`.


### Conversion of GeoTiffs to ArcGIS .flt and .bil formats
We have an bash script to convert commonly used `geotif` format into `
.flt` format data required by `WhiteBoxTools`. Our script uses `gdal` and 
also outputs an intermediate `.bil` binary format data, also commonly 
available via ArcGIS. 


### Steps to MultiscaleTopographicPositionImage

1. Convert `GeoTiff` into `.flt`:
    
    
    convert_tif_to_flt.sh dem dem
    
The above script read in a `GeoTiff` named `dem.tif`, and outputs a `dem.flt`
and a `dem_bil.bil` with the corresponding header files.

2. Produce `MaxElevationDevation` images from DEM

The script `multiscale.sh` produces the three `local`, `meso` and `broad` range
`MaxElevationDevation` outputs. 

2. Combine the three scales into RGB
 
The three outputs are combined in this step to produce the multibanded RGB 
image following this excerpt from the paper by Lindsay _et. al._

    python multiscale_topographic_position_image.py -l dem_mag1.flt -m dem_mag2.flt -b dem_mag3.flt -i dem.tif    

The above will output a `multiscaled_dem.tif`, which is `0-255` 8 bite 
integer for all three colours.
