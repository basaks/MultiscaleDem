"""
A quick and dirty script to add to the mask of a raster using an external mask.
Worked perfectly first time :)
"""
import numpy as np
from osgeo import gdal, gdalconst
dem = 'multibanded_raster.tif'
mask = 'mask.tif'
output_tif = 'multibanded_masked_raster.tif'

ms = gdal.Open(mask, gdalconst.GA_ReadOnly)
ms_data = ms.GetRasterBand(1).ReadAsArray()
ms_nodata = getattr(np, str(ms_data.dtype))(
    ms.GetRasterBand(1).GetNoDataValue()
)
ms_mask = ms_data == ms_nodata
print('got mask data')

src_ds = gdal.Open(dem, gdalconst.GA_ReadOnly)
print('opened rasters')

ds_data = src_ds.ReadAsArray()
print(ds_data.shape)

# number of bands in the multibanded input raster
nbands = src_ds.RasterCount

driver = gdal.GetDriverByName('GTiff')

out_ds = driver.Create(output_tif,
                       xsize=src_ds.RasterXSize,
                       ysize=src_ds.RasterYSize,
                       bands=nbands,
                       eType=gdal.GDT_Int16  # change dtype manually
                       )
out_ds.SetGeoTransform(src_ds.GetGeoTransform())
out_ds.SetProjection(src_ds.GetProjection())


for n in range(nbands):
    print('processing band {}'.format(n+1))
    band_data = src_ds.GetRasterBand(n+1).ReadAsArray()
    print('Read data from band {}'.format(n+1))

    ds_nodata = getattr(np, str(band_data.dtype))(
        src_ds.GetRasterBand(n+1).GetNoDataValue()
        )
    print('Found nodata value of {} and type {}'.format(ds_nodata,
                                                       str(band_data.dtype)))
    ds_mask = band_data == ds_nodata

    ds_mask += ms_mask
    band_data[ds_mask] = ds_nodata

    print('now writing new masked band in geotiff for band {}'.format(n+1))
    # write data in band n
    out_ds.GetRasterBand(n+1).WriteArray(
        band_data.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))

    # might have to change dtype manually
    out_ds.GetRasterBand(n+1).SetNoDataValue(int(ds_nodata))
    out_ds.FlushCache()

out_ds = None
