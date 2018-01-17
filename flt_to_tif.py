from optparse import OptionParser
import logging
from osgeo import gdal, gdalconst
from multiscale_topographic_position_image import read_flt
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def convert_flt_to_geotif(flt_file, output_tif, ref):
    """
    Assume flt_file is single banded float32.
    """

    src_ds = gdal.Open(ref, gdalconst.GA_ReadOnly)

    log.info('Reading flt data from {}'.format(flt_file))
    flt, nodata_value = read_flt(flt_file)

    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_tif,
                           xsize=src_ds.RasterXSize,
                           ysize=src_ds.RasterYSize,
                           bands=1,
                           eType=gdal.GDT_Float32
                           )
    out_ds.SetGeoTransform(src_ds.GetGeoTransform())
    out_ds.SetProjection(src_ds.GetProjection())

    # write data in band 1
    log.info('Writing flt data into the output geotif')
    out_ds.GetRasterBand(1).WriteArray(
        flt.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
    out_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
    out_ds.FlushCache()
    out_ds = None
    log.info('Finished!')


if __name__ == '__main__':
    parser = OptionParser(usage='%prog -i input_flt -o output_tif -r ref_tif')

    parser.add_option('-i', '--input_flt', type=str, dest='input_flt',
                      help='Input flt file to covert into tif')

    parser.add_option('-o', '--output_tif', type=str, dest='output_tif',
                      default='output.tif', help='Output geotif file.')

    parser.add_option('-r', '--ref_tif', type=str, dest='ref_tif',
                      help='ref_tif to copy projection and georeference from')

    options, args = parser.parse_args()

    if not options.input_flt:  # if filename is not given
        parser.error('Input flt file not provided.')

    # TODO: provide default proj and reference
    if not options.ref_tif:  # if filename is not given
        parser.error('Reference geotif file must be provided.')

    convert_flt_to_geotif(options.input_flt, options.output_tif,
                          options.ref_tif)
