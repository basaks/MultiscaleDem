"""
A quick and dirty script to add to the mask of a raster using an external mask.
Worked perfectly first time :)
"""
import numpy as np
from osgeo import gdal, gdalconst
dem = 'D90_M_NoData.tif'
mask = 'Mask90.tif'
output_tif = 'D90_M_Masked.tif'

src_ds = gdal.Open(dem, gdalconst.GA_ReadOnly)
ms = gdal.Open(mask, gdalconst.GA_ReadOnly)

print('opened rasters')

ds_data = src_ds.GetRasterBand(1).ReadAsArray()

ds_nodata = getattr(np, str(ds_data.dtype))(
    src_ds.GetRasterBand(1).GetNoDataValue()
)
ds_mask = ds_data == ds_nodata

print('got data')

ms_data = ms.GetRasterBand(1).ReadAsArray()
ms_nodata = getattr(np, str(ms_data.dtype))(
    ms.GetRasterBand(1).GetNoDataValue()
)
ms_mask = ms_data == ms_nodata
print('got mask data')

ds_mask += ms_mask
ds_data[ds_mask] = ds_nodata

driver = gdal.GetDriverByName('GTiff')
out_ds = driver.Create(output_tif,
                       xsize=src_ds.RasterXSize,
                       ysize=src_ds.RasterYSize,
                       bands=1,
                       eType=gdal.GDT_Float32
                       )
out_ds.SetGeoTransform(src_ds.GetGeoTransform())
out_ds.SetProjection(src_ds.GetProjection())

print('now writing new geotiff')

# write data in band 1
out_ds.GetRasterBand(1).WriteArray(
    ds_data.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
out_ds.GetRasterBand(1).SetNoDataValue(ds_nodata)
out_ds.FlushCache()
out_ds = None

