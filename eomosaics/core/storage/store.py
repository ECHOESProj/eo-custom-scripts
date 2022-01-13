import os
import tempfile
from datetime import datetime
from glob import glob
from os.path import join, basename

from osgeo import gdal


class ToS3:

    def __init__(self, store, processing_module, frequency, request_func, testing=False):
        self.store = store
        self.processing_module = processing_module
        self.frequency = frequency
        self.request_func = request_func
        self.info = None
        self.testing = testing

    @staticmethod
    def _product_path(product_identifier, extension):
        product_path = '/'.join(product_identifier.split('/')[2:])
        return os.path.splitext(product_path)[0] + extension

    def request(self, tempdir):
        return self.request_func(tempdir)

    def get_data(self, request):
        request.get_data(save_data=True)

    def object_name(self, request, local_fname):
        input = request.payload['input']['data'][0]
        instrument = input['type']
        timerange = input['dataFilter']['timeRange']
        bbox = '_'.join(str(i) for i in request.payload['input']['bounds']['bbox'])
        start = datetime.strptime(timerange['from'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y%m%d')
        end = datetime.strptime(timerange['to'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y%m%d')
        fname = join(basename(local_fname))
        try:
            mosaicking = input['dataFilter']['mosaickingOrder']
        except KeyError:
            mosaicking = 'nomosaicking'
        fname = fname.replace('response', mosaicking)
        fname = fname.replace('request', mosaicking)
        name_parts = [f'BBOX({bbox})', self.processing_module, instrument, self.frequency, f'{start}-{end}', fname]
        if self.testing:
            name_parts = ['_test'] + name_parts
        return join(*name_parts)

    @staticmethod
    def compress_geotiff(dataset, local_fname):
        creationOptions = ['COMPRESS=JPEG']
        if dataset.RasterCount >= 3:
            bandList = [1, 2, 3]
            creationOptions.append('PHOTOMETRIC=YCBCR')
            # when YCBCR is enabled, filesize will be much smaller, bump up the quality
            jpeg_quality_option = 'JPEG_QUALITY=95'
        else:
            bandList = None
            jpeg_quality_option = 'JPEG_QUALITY=85'

        creationOptions.append(jpeg_quality_option)
        gdal.Translate(f'{local_fname}.gdal', local_fname, format='GTiff', creationOptions=creationOptions,
                       bandList=bandList)

    @staticmethod
    def validate_geotiff(dataset):
        r, g, b, *_ = dataset.ReadAsArray()
        try:
            # Check that all the values are not the same
            assert not all([(r[0] == r).all(), (g[0] == g).all(), (b[0] == b).all()])
        except:
            raise AssertionError("All the bands have the same values")

    def to_store(self):
        with tempfile.TemporaryDirectory() as tempdir:
            request = self.request(tempdir)
            self.get_data(request)
            object_names = []
            for local_fname in glob(join(tempdir, '*', '*.*')):
                if local_fname.endswith('.tiff'):
                    dataset = gdal.Open(local_fname)
                    if self.testing:
                        self.validate_geotiff(dataset)
                    self.compress_geotiff(dataset, local_fname)
                    os.remove(local_fname)
                    os.rename(f'{local_fname}.gdal', local_fname)
                object_names.append(self.store.upload_file(local_fname, self.object_name(request, local_fname)))
            return object_names
