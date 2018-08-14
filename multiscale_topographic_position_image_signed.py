import os
from optparse import OptionParser
import logging
import csv
import numpy as np
from osgeo import gdal, gdalconst

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def read_flt(flt_file):
    data = np.fromfile(flt_file, dtype=np.float32)
    flt_hdr_file = os.path.splitext(flt_file)[0] + '.hdr'
    if not os.path.exists(flt_hdr_file):
        raise FileNotFoundError('{flt_file} corresponding header file was not '
                                'found'.format(flt_file=flt_file))

    def _get_no_data(hdr_file):
        with open(hdr_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=' ')
            for l in csvreader:
                k, v = l
                if k == 'NODATA_VALUE':
                    return float(v)
            raise ValueError('NODATA_VALUE was not found '
                             'in the {}'.format(flt_hdr_file))

    nodata_value = _get_no_data(flt_hdr_file)
    # import IPython; IPython.embed(); import sys; sys.exit()
    masked_data = np.ma.array(data, dtype=np.float32,
                              mask=data == nodata_value)

    return masked_data, nodata_value


def multiscale(local, meso, broad, input_tif, output_tif, cutoff,
               reversed=0):

    log.info('Reading the three scales from MadElevationDeviation .flt files')
    log.debug('Reading local .flt file')
    loc, loc_nodata = read_flt(local)
    log.debug('Reading meso .flt file')
    mes, mes_nodata = read_flt(meso)
    log.debug('Reading broad .flt file')
    bro, bro_nodata = read_flt(broad)

    # standardise and take absolute, and scale by cutoff
    log.info('Standardization and RGB conversion')

    if reversed:
        sign = -1
    else:
        sign = 1

    loc = sign*(loc - loc.mean()) / loc.std()
    mes = sign*(mes - mes.mean()) / mes.std()
    bro = sign*(bro - bro.mean()) / bro.std()

    # source information
    src_ds = gdal.Open(input_tif, gdalconst.GA_ReadOnly)

    # output ds
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_tif,
                           xsize=src_ds.RasterXSize,
                           ysize=src_ds.RasterYSize,
                           bands=3,
                           eType=gdal.GDT_Float32
                           )
    out_ds.SetGeoTransform(src_ds.GetGeoTransform())
    out_ds.SetProjection(src_ds.GetProjection())

    # write data in the three bands
    log.info('Writing RGB data into the output miltibanded RGB geotif')
    out_ds.GetRasterBand(1).WriteArray(
        bro.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
    out_ds.GetRasterBand(1).SetNoDataValue(sign*bro_nodata)
    out_ds.GetRasterBand(2).WriteArray(
        mes.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
    out_ds.GetRasterBand(2).SetNoDataValue(sign*mes_nodata)
    out_ds.GetRasterBand(3).WriteArray(
        loc.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
    out_ds.GetRasterBand(3).SetNoDataValue(sign*loc_nodata)

    out_ds.FlushCache()
    out_ds = None
    log.info('Finished!')


if __name__ == '__main__':
    parser = OptionParser(usage='%prog -l local_mag  -m meso_mag \n'
                                '-b broad_mag -i input.tif -o output.tif \n'
                                '-c cutoff')
    parser.add_option('-l', '--local', type=str, dest='local',
                      help='name of input local mag file')

    parser.add_option('-m', '--meso', type=str, dest='meso',
                      help='name of input meso mag file')

    parser.add_option('-b', '--broad', type=str, dest='broad',
                      help='name of input broad mag file')

    parser.add_option('-i', '--input_tif', type=str, dest='input_tif',
                      help='Input tif file to copy projections and '
                           'georeferencign information from')

    parser.add_option('-o', '--output_tif', type=str, dest='output_tif',
                      default='multiscaled_dem.tif',
                      help='Optional output tif filename')

    parser.add_option('-c', '--cutoff', type=float, dest='cutoff',
                      default=2.58,
                      help='Cutoff value for integer scaling. See J. Lindsay '
                           'paper for details.')

    parser.add_option('-r', '--reversed', type=int, dest='reversed',
                      default=0,
                      help='Cutoff value for integer scaling. See J. Lindsay '
                           'paper for details.')

    options, args = parser.parse_args()

    if not options.local:  # if filename is not given
        parser.error('Input local mag file must be provided.')

    if not options.meso:  # if filename is not given
        parser.error('Input meso mag file must be provided.')

    if not options.broad:  # if filename is not given
        parser.error('Input broad mag file must be provided.')

    if not options.input_tif:  # if filename is not given
        parser.error('Input geotif file must be provided.')

    multiscale(options.local, options.meso, options.broad,
               options.input_tif, options.output_tif, options.cutoff,
               options.reversed)

