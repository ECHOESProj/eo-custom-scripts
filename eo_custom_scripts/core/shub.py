"""
Generates GeoTIFFs for the specified processing script, time intervals and ROI. It uses the Sentinel-Hub API.

The scripts are obtained from https://github.com/sentinel-hub/custom-scripts.
"""

#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

__author__ = "John Lavelle, Fergal Doyle"
__email__ = "jlavelle@compass.ie"
__version__ = "1.0"

import logging
import pathlib
from datetime import datetime, timedelta
from functools import partial
from os.path import join
from time import perf_counter

import pandas as pd
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, DataCollection, bbox_to_dimensions, SHConfig
from shapely import wkt

import eo_io


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

config_s3 = eo_io.configuration()
config_sh = SHConfig()

config_sh.instance_id = config_s3.sh_instance_id
config_sh.sh_client_id = config_s3.sh_client_id
config_sh.sh_client_secret = config_s3.sh_client_secret

script_dir = eo_io.read_yaml(join(pathlib.Path(__file__).parent, 'data_sources.yaml'))


def get_script_dir(instrument, directory):
    return join(pathlib.Path(__file__).parent.parent, 'custom_scripts', script_dir[instrument.upper()]['directory'], directory)


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
    request = SentinelHubRequest(
        evalscript=processor_script(instrument, processing_module),
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=get_data_collection(instrument, config),
                time_interval=(start, end),
                mosaicking_order=config['Output']['mosaicking_order']
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


def process(storage: object, data_source: str, processing_module: str, area_wkt: str, config: str, start: str, end: str,
            testing: bool = False) -> None:
    area = wkt.loads(area_wkt)
    bbox = BBox(bbox=area.bounds, crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox, resolution=config['Output']['resolution'])
    frequency = config['Output']['frequency']

    # interval_range was excluding the first month if it was 01-01. Minus 1 day from the start date to include first month
    start_dt = datetime.strptime(start, '%Y-%m-%d').date() - timedelta(days=1)
    intervals = pd.interval_range(start=pd.Timestamp(start_dt), end=pd.Timestamp(end), freq=interval_names[frequency])
    intervals = [(pd.to_datetime(i.left).date() + timedelta(days=1), pd.to_datetime(i.right).date())
                 for i in intervals]

    for start_i, end_i in intervals:
        # request_func has one argument: data_folder
        request_func = partial(get_request, data_source, processing_module, config, start_i, end_i, bbox, size)
        for prod_name in eo_io.store_geotiff.ToS3(storage, processing_module, frequency, request_func, testing).to_storage():
            print('s3-location: ' + ' '.join(prod_name))
            yield prod_name


def main(instrument: str, processing_module: str, area_wkt: str, start: str, end: str,
         mosaicking_order: str = None, frequency: str = None, resolution: int = None,
         testing: bool = False):
    t1_start = perf_counter()
    logging.info('Starting')

    try:
        # Where config file exists in the script directory (for the public collections)
        config_yaml = eo_io.read_yaml(join(get_script_dir(instrument, processing_module), 'config.yaml'))
    except FileNotFoundError:
        # Fallback config. Good for e.g. Sentinel-2
        config_yaml = {'Output':
                           {'mosaicking_order': 'leastCC',
                            'frequency': 'monthly',
                            'resolution': 10}}  # In metres

    config = config_yaml.copy()
    # Prioritise function kwargs first, then the config file
    for k, v in {'mosaicking_order': mosaicking_order, 'frequency': frequency, 'resolution': resolution}.items():
        config['Output'][k] = v or config_yaml['Output'][k]
    print(config)

    storage = eo_io.ReadWriteData(config_s3)
    prod_names = list(process(storage, instrument, processing_module, area_wkt, config, start, end, testing))
    t1_stop = perf_counter()
    logging.info(f'Finished, {t1_stop - t1_start}s')
    return prod_names
