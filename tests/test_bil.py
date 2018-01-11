import os
from os.path import dirname, join, abspath
import random
import string
import pytest
from pytest import approx
from subprocess import check_call
from osgeo import gdal
import numpy as np
from header import main, constants

TESTS = dirname(abspath(__file__))
SAMPLE = join(TESTS, 'LATITUDE_GRID1')
TIF2ARC = join(dirname(TESTS), 'convert_tif_to_arcgis.sh')


@pytest.fixture
def random_filename(tmpdir_factory):
    def make_random_filename(ext=''):
        dir = str(tmpdir_factory.mktemp('tif2arc').realpath())
        fname = ''.join(random.choice(string.ascii_lowercase)
                        for _ in range(10))
        return join(dir, fname + ext)
    return make_random_filename


def test_bil_header(random_filename):
    flt = random_filename()
    check_call([TIF2ARC, SAMPLE, flt])

    assert os.path.exists(flt + '.flt')
    assert os.path.exists(flt + '.hdr')
    assert os.path.exists(flt + '.prj')

    assert os.path.exists(flt + '_bil.bil')
    assert os.path.exists(flt + '_bil.hdr')
    assert os.path.exists(flt + '_bil.prj')

    flt_data = np.fromfile(flt + '.flt', dtype=np.float32)
    bil_data = np.fromfile(flt + '_bil.bil', dtype=np.float32)

    np.testing.assert_array_equal(flt_data, bil_data)

    tif = gdal.Open(SAMPLE + '.tif')
    assert tif.RasterXSize * tif.RasterYSize == flt_data.size

    bil_hdr, flt_hdr = main(flt + '_bil.hdr', flt + '.hdr')
    yllcorner = constants.pop('ULYMAP')

    for c in constants:
        assert bil_hdr[c] == flt_hdr[constants[c]]

    # assert llcorner was derived properly
    assert bil_hdr['ULYMAP'] - bil_hdr['NROWS']*bil_hdr['XDIM'] == approx(
        flt_hdr[yllcorner])

    assert tif.RasterYSize == bil_hdr['NROWS'] == flt_hdr['NROWS']
    assert tif.RasterXSize == bil_hdr['NCOLS'] == flt_hdr['NCOLS']
