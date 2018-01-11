import os
from os.path import dirname, join, abspath
import random
import string
import pytest
from subprocess import check_call
from osgeo import gdal


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

    # tif = gdal.Open(SAMPLE)
    # assert tif.RasterXSize ==
    # assert tif.RasterYSize ==
    #
    # import IPython; IPython.embed(); import sys; sys.exit()
    # pass


