import csv
from optparse import OptionParser

constants = {
    'NODATA': 'NODATA_VALUE',
    'NCOLS': 'NCOLS',
    'NROWS': 'NROWS',
    'XDIM': 'CELLSIZE',
    'ULXMAP': 'XLLCORNER',
    'ULYMAP': 'YLLCORNER'
    }

conversion_map = {
    'NODATA': float,
    'NCOLS': int,
    'NROWS': int,
    'XDIM': float,
    'ULXMAP': float,
    'ULYMAP': float
    }


def main(bil_hdr_file, flt_hdr_file):
    bil_hdr = {}

    with open(bil_hdr_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for l in csvreader:
            k, v = l[0].split()
            if k in constants:
                bil_hdr[k] = conversion_map[k](v)

    with open(flt_hdr_file, 'w') as csvfile2:
        csvwriter = csv.writer(csvfile2, delimiter=' ')
        csvwriter.writerow(['BYTEORDER', 'LSBFIRST'])
        for k, v in bil_hdr.items():
            if k == 'ULYMAP':
                # TODO: can improve `yllcorner` by using gdal corner coords
                v = str(float(v) - bil_hdr['NROWS'] * bil_hdr['XDIM'])
            csvwriter.writerow([constants[k], v])


if __name__ == '__main__':
    parser = OptionParser(usage='%prog -b bil_hdr_file  -f flt_hdr_file \n'
                          'times of india')
    parser.add_option('-b', '--bil_hdr_file', type=str, dest='bil_hdr_file',
                      help='name of input .bil header file')

    parser.add_option('-f', '--flt_hdr_file', type=str, dest='flt_hdr_file',
                      help='name of output .flt header file')

    options, args = parser.parse_args()

    if not options.bil_hdr_file:  # if filename is not given
        parser.error('Input .bil header filename not given.')

    if not options.flt_hdr_file:  # if filename is not given
        parser.error('Output .flt filename not given.')

    main(options.bil_hdr_file, options.flt_hdr_file)
