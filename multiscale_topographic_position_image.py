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
from optparse import OptionParser
import numpy as np
from osgeo import gdal, gdalconst


def multiscale(local, meso, broad, input_tif, output_tif, cutoff):
    loc = np.fromfile(local, dtype=np.float32)
    mes = np.fromfile(meso, dtype=np.float32)
    bro = np.fromfile(broad, dtype=np.float32)

    # standardise and take absolute, and scale by cutoff
    loc = (np.abs(loc - np.mean(loc)) / np.std(loc)) * 255/cutoff
    mes = (np.abs(mes - np.mean(mes)) / np.std(mes)) * 255/cutoff
    bro = (np.abs(bro - np.mean(bro)) / np.std(bro)) * 255/cutoff

    # source information
    src_ds = gdal.Open(input_tif, gdalconst.GA_ReadOnly)

    # import IPython; IPython.embed(); import sys; sys.exit()
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
    out_ds.GetRasterBand(1).WriteArray(
        bro.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
    out_ds.GetRasterBand(2).WriteArray(
        mes.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))
    out_ds.GetRasterBand(3).WriteArray(
        loc.reshape((src_ds.RasterYSize, src_ds.RasterXSize)))

    out_ds.FlushCache()


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