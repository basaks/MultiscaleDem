"""
from: http://www.sciencedirect.com/science/article/pii/S0169555X15300076

The MTPCC image was created by combining the DEV max rasters of
the local-, meso-, and broad-scale ranges into the respective blue,
green, and red channels of a 24-bit color image. The three DEV max rasters
were first processed to linearly rescale their absolute grid cell values
within the range 0–2.58 to the output 8-bit range of 0–255. Grid cells
occupying an average landscape position within a particular range
were therefore assigned the lowest values after rescaling. Highly deviat-
ed locations (i.e. exceptionally elevated or depressed sites) with input
pixel values greater than the 2.58 cutoff value were assigned an output
value of 255. The cutoff value of 2.58 was selected because the ±2.58
standard deviation from the mean of a Gaussian distribution includes
nearly 99% of the samples.
"""
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
    masked_data = np.ma.array(data, dtype=np.float32,
                              mask=data == nodata_value)

    return masked_data


def multiscale(local, meso, broad, input_tif, output_tif, cutoff):

    log.info('Reading the three scales from MadElevationDeviation .flt files')
    log.debug('Reading local .flt file')
    loc = read_flt(local)
    log.debug('Reading meso .flt file')
    mes = read_flt(meso)
    log.debug('Reading broad .flt file')
    bro = read_flt(broad)

    # standardise and take absolute, and scale by cutoff
    log.info('Standardization and RGB converseion')
    loc = (np.ma.abs(loc - np.ma.mean(loc)) / np.ma.std(loc)) * 255/cutoff
    mes = (np.ma.abs(mes - np.ma.mean(mes)) / np.ma.std(mes)) * 255/cutoff
    bro = (np.ma.abs(bro - np.ma.mean(bro)) / np.ma.std(bro)) * 255/cutoff

    # source information
    src_ds = gdal.Open(input_tif, gdalconst.GA_ReadOnly)

    # output ds
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_tif,
                           xsize=src_ds.RasterXSize,
                           ysize=src_ds.RasterYSize,
                           bands=3,
                           eType=gdal.GDT_Byte
                           )
    out_ds.SetGeoTransform(src_ds.GetGeoTransform())
    out_ds.SetProjection(src_ds.GetProjection())

    # write data in the three bands
    log.info('Whiteing RGB data into the output miltibanded RGB geotif')
    out_ds.GetRasterBand(1).WriteArray(
        bro.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
    out_ds.GetRasterBand(2).WriteArray(
        mes.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
    out_ds.GetRasterBand(3).WriteArray(
        loc.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))

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
               options.input_tif, options.output_tif, options.cutoff)
