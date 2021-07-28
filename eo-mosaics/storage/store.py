import json
import os
import tempfile
from os import makedirs, remove
from os.path import dirname, join, basename
from datetime import datetime
from glob import glob
from osgeo import gdal

class ToS3:

    def __init__(self, store, processing_module, frequency, request_func):
        self.store = store
        self.processing_module = processing_module
        self.frequency = frequency
        self.request_func = request_func
        self.info = None
        self.to_store()

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
        mosaicking = input['dataFilter']['mosaickingOrder']
        fname = fname.replace('response', mosaicking)
        fname = fname.replace('request', mosaicking)
        return join(f'BBOX({bbox})', self.processing_module, instrument, self.frequency, f'{start}-{end}', fname)

    def to_store(self):
        with tempfile.TemporaryDirectory() as tempdir:
            request = self.request(tempdir)
            self.get_data(request)
            for local_fname in glob(join(tempdir, '*', '*')):
                # run the geotiff through gdal translate before upload
                _, file_extension = os.path.splitext(local_fname)
                if file_extension.lower() == '.tiff':
                    gdal.Translate(f'{local_fname}.gdal', local_fname, format='GTiff', creationOptions=['COMPRESS=JPEG', 'TILED=YES', 'PHOTOMETRIC=YCBCR'])
                    os.remove(local_fname)
                    os.rename(f'{local_fname}.gdal', local_fname)

                self.store.upload_file(local_fname, self.object_name(request, local_fname))
