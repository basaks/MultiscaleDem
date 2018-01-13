## MultiscaleTopographicPositionImage of DEM

We follow the paper by J.B.Lindsay, J.M.H.Cockburn, H.A.J.Russell titled 
[`An integral image approach to performing multi-scale topographic position 
analysis`](http://www.sciencedirect.com/science/article/pii/S0169555X15300076)
to obtain a `MultiscaleTopographicPositionImage` map of continental Australia 
at 90m and 30m resolution.


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
    
    
    ./tif_to_flt.sh foo bar
    
The above script read in a `GeoTiff` named `foo.tif`, and outputs a `bar.flt`
and a `bar_bil.bil` with the corresponding header and projection files.

This conversion has been tested using the `tests/test_bil.py` file. To 
run the tests, use `pytest tests/test_bil.py`.

2. Produce `MaxElevationDevation` images from DEM:

The script `multiscale.sh` produces the three `local`, `meso` and `broad` range
`MaxElevationDevation` outputs. Use it as the following:
    
    ./multiscale.sh dem
    
3. Combine the three scales into RGB:
 
The three outputs are combined in this step to produce the multibanded RGB 
image following this excerpt from the paper by Lindsay _et. al._

    python multiscale_topographic_position_image.py -l dem_mag1.flt \
        -m dem_mag2.flt -b dem_mag3.flt -i dem.tif -o multiscaled_dem.tif    

The above will output a `multiscaled_dem.tif`, which is a RGB banded 8 bite 
(0-255) integer for all three colours.


## All in one

The three scripts above are combined into the the `multiscale_all_in_one.sh`.
Use it with the input `dem.tif` geotif as the following (without the `.tif`).

    ./multiscale_all_in_one.sh dem
   
The final result of this will be `multiscaled_dem.tif` with projection and 
georeferencing information copied from the input dem.tif.


## Required softwares

One will need to install 
[WhiteboxBoxTools](https://github.com/jblindsay/whitebox-geospatial-analysis-tools/tree/master/whitebox_tools), 
[gdal](http://download.osgeo.org/gdal/) and need python with the following 
packages:

    ```bash
    $ pil list
    GDAL (this is the python binding for system isntalled gdal)
    numpy
    pytest (if testing)
    ```  
Also create a symlink to the `whitebox_tools` like so:

    sudo ln -s /path/to/whitebox-geospatial-analysis-tools/whitebox_tools/target/release/whitebox_tools /usr/local/bin/whitebox_tools

## ArcGIS .flt/.bil to geotif

We also provide a script for conversion of ArcGIS `.flt` or `.bil` file into 
getotif. Run this script as:
        
    $ python flt_to_tif.py -i dem_mag1.flt -o dem_mag1.tif -r dem.tif
  