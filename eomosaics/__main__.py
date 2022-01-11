"""
Generates GeoTIFFs for the specified processing script, time intervals and ROI. It uses the Sentinel-Hub API.

The scripts are obtained from https://github.com/sentinel-hub/custom-scripts.
"""

import logging
import pathlib
from datetime import datetime, timedelta
from functools import partial
from os.path import join
from time import perf_counter

import click
import pandas as pd
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, DataCollection, bbox_to_dimensions, SHConfig
from shapely import wkt

from eomosaics.core.settings import configuration
from eomosaics.core.storage.store import ToS3
from eomosaics.core.storage.store_objects import ReadWriteData
from eomosaics.core.tools import read_yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

config_s3 = configuration()
config_sh = SHConfig()

config_sh.instance_id = config_s3.sh_instance_id
config_sh.sh_client_id = config_s3.sh_client_id
config_sh.sh_client_secret = config_s3.sh_client_secret

script_dir = read_yaml(join(pathlib.Path(__file__).parent, 'data_sources.yaml'))


def get_script_dir(instrument, directory):
    return join(pathlib.Path(__file__).parent, 'scripts', script_dir[instrument.upper()]['directory'], directory)


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
    return SentinelHubRequest(
        evalscript=processor_script(instrument, processing_module),
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=get_data_collection(instrument, config),
                time_interval=(start, end),
                mosaicking_order=config['Output']['mosaicking_order']
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF)
        ],
        data_folder=data_folder,
        bbox=bbox,
        size=size,
        config=config_sh
    )


interval_names = {'yearly': 'Y', 'monthly': 'm'}


def process(store: object, instrument: str, processing_module: str, area_wkt: str, config: str, start: str, end: str,
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
        request_func = partial(get_request, instrument, processing_module, config, start_i, end_i, bbox, size)
        for prod_name in ToS3(store, processing_module, frequency, request_func, testing).to_store():
            print('s3-location: ' + ' '.join(prod_name))
            yield prod_name


def main(instrument: str, processing_module: str, area_wkt: str, start: str, end: str, testing: bool = False):
    t1_start = perf_counter()
    logging.info('Starting')

    try:
        # Where config file exists in the script directory (for the public collections)
        config = read_yaml(join(get_script_dir(instrument, processing_module), 'config.yaml'))
    except FileNotFoundError:
        # Otherwise use the default configuration
        config = {'Output':
                      {'mosaicking_order': 'leastCC',
                       'frequency': 'monthly',
                       'resolution': 10}}  # In metres

    store = ReadWriteData(config_s3, 'product_name')
    prod_names = list(process(store, instrument, processing_module, area_wkt, config, start, end, testing))
    t1_stop = perf_counter()
    logging.info(f'Finished, {t1_stop - t1_start}s')
    return prod_names


@click.command()
@click.argument('instrument')
@click.argument('processing_module')
@click.argument('area_wkt')
@click.argument('start')
@click.argument('end')
# @click.option('--', default=None)
def cli(instrument: str, processing_module: str, area_wkt: str, start: str, end: str) -> None:
    """
    :param instrument: The name of the instrument (e.g. S1_SAR_GRD)
    :param processing_module: The processor to use.
    :param area_wkt: The WKT string, which is the polygon of the ROI
    :param start: The start date of the search in the format YYYY-MM-DD
    :param end: The stop date of the search in the format YYYY-MM-DD
    :return:
    """
    main(instrument, processing_module, area_wkt, start, end)


if __name__ == '__main__':
    cli()
