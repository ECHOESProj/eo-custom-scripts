"""
Generates GeoTIFFs for the specified processing script, time intervals and ROI. It uses the Sentinel-Hub API.

The scripts are obtained from https://github.com/sentinel-hub/custom-scripts.
"""

import logging
import pathlib
from datetime import datetime, timedelta
from functools import partial
from os.path import join

import pandas as pd
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, DataCollection, \
    bbox_to_dimensions, SHConfig, SentinelHubCatalog
from shapely import wkt


import eo_io

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

config_sh = SHConfig()
config_s3 = eo_io.configuration()

config_sh.instance_id = config_s3.sh_instance_id
config_sh.sh_client_id = config_s3.sh_client_id
config_sh.sh_client_secret = config_s3.sh_client_secret

script_dir = eo_io.read_yaml(join(pathlib.Path(__file__).parent, 'data_sources.yaml'))


def get_script_dir(instrument, directory):
    return join(pathlib.Path(__file__).parent.parent, 'custom_scripts', script_dir[instrument.upper()]['directory'],
                directory)


def processor_script(instrument, directory):
    instrument = instrument.upper()
    with open(join(get_script_dir(instrument, directory), 'script.js'),
              "r") as f:
        return f.read()


def get_data_collection(instrument, config):
    try:
        # Case for one of the default collections (e.g. Sentinel-2 data)
        return getattr(DataCollection, instrument.upper())
    except AttributeError:
        # Case for the public data collections. The parameters for the data collection are read from the config.yaml
        # file in the script directory. See https://collections.sentinel-hub.com/ for available data collections.
        kwargs = config['DataCollection']
        return DataCollection.define(**kwargs)


def get_request(instrument, processing_module, config, start, end, bbox, size, data_folder):
    data_collection = get_data_collection(instrument, config)

    if "SENTINEL2" in instrument.upper():
        query = {"eo:cloud_cover": {"lt": 98}}
    else:
        query = None

    catalog = SentinelHubCatalog(config=config_sh)
    search_iterator = catalog.search(
        data_collection,
        bbox=bbox,
        time=(start, end),
        query=query,
        fields={"include": ["id", "properties.datetime", "properties.eo:cloud_cover"], "exclude": []})

    if not list(search_iterator):
        return None

    mosaicking_order = config['Output']['mosaicking_order']

    request = SentinelHubRequest(
        evalscript=processor_script(instrument, processing_module),
        input_data=[
            SentinelHubRequest.input_data(
                data_collection,
                time_interval=(start, end),
                mosaicking_order=mosaicking_order,
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF),
        ],
        data_folder=data_folder,
        bbox=bbox,
        size=size,
        config=config_sh
    )
    request.get_data(save_data=True)
    return request


interval_names = {'yearly': 'Y', 'monthly': 'm', 'daily': 'd'}


class ProcessingChain:

    def __init__(self, instrument: str, processing_module: object, area_wkt: str, start: str, end: str,
                 mosaicking_order: str = None, frequency: str = None, resolution: str = None, testing: bool = False):
        """

        @param instrument:
        @param processing_module:
        @param area_wkt:
        @param start:
        @param end:
        @param mosaicking_order:
        @param frequency:
        @param resolution:
        @param testing:
        """
        self.instrument = instrument
        self.processing_module = processing_module
        self.area_wkt = area_wkt
        self.start = start
        self.end = end
        self.mosaicking_order = mosaicking_order
        self.frequency = frequency
        self.resolution = resolution
        self.testing = testing

        self.config = self.get_config(self.instrument, self.processing_module, self.mosaicking_order, self.frequency,
                                      self.resolution)

    @staticmethod
    def get_config(instrument, processing_module, mosaicking_order, frequency, resolution):
        """
        @param instrument:
        @param processing_module:
        @param mosaicking_order:
        @param frequency:
        @param resolution:
        @return:
        """
        logging.info('Starting')
        try:
            # Where config file exists in the script directory (for the public collections)
            config_yaml = eo_io.read_yaml(join(get_script_dir(instrument, processing_module), 'config.yaml'))
        except FileNotFoundError:
            if "SENTINEL1" in instrument.upper():
                config_yaml = {'Output':
                                   {'mosaicking_order':  None,
                                    'frequency': 'daily',
                                    'resolution': 20}}  # In metres
            else:
                # Fallback config. Good for e.g. Sentinel-2
                config_yaml = {'Output':
                                   {'mosaicking_order': 'leastCC',
                                    'frequency': 'monthly',
                                    'resolution': 10}}  # In metres
        config = config_yaml.copy()
        # Prioritise function kwargs first, then the config file
        for k, v in {'mosaicking_order': mosaicking_order, 'frequency': frequency, 'resolution': resolution}.items():
                config['Output'][k] = v or config_yaml['Output'][k]
        return config

    @staticmethod
    def process(data_source: str, processing_module: str, area_wkt: str, config_output: str, start: str, end: str,
                testing: bool = False) -> object:
        area = wkt.loads(area_wkt)
        bbox = BBox(bbox=area.bounds, crs=CRS.WGS84)
        size = bbox_to_dimensions(bbox, resolution=config_output['Output']['resolution'])
        frequency = config_output['Output']['frequency']

        # interval_range was excluding the first month if it was 01-01.
        # Minus 1 day from the start date to include first month
        start_dt = datetime.strptime(start, '%Y-%m-%d').date() - timedelta(days=1)
        intervals = pd.interval_range(start=pd.Timestamp(start_dt), end=pd.Timestamp(end),
                                      freq=interval_names[frequency])
        intervals = [(pd.to_datetime(i.left).date() + timedelta(days=1), pd.to_datetime(i.right).date())
                     for i in intervals]

        for start_i, end_i in intervals:
            # request_func has one argument: data_folder
            request_func = partial(get_request, data_source, processing_module, config_output, start_i, end_i, bbox,
                                   size)
            s3 = eo_io.store_geotiff.ToS3(processing_module, frequency, request_func, testing)
            object_names = s3.to_storage()
            yield object_names

    def __iter__(self):
        yield from self.process(self.instrument, self.processing_module, self.area_wkt, self.config, self.start,
                                self.end, self.testing)
