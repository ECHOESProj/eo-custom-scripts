import pathlib
from functools import partial
from os.path import join

import click
import pandas as pd
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, DataCollection, bbox_to_dimensions, SHConfig
from settings import configuration
from shapely import wkt
from storage.store import ToS3
from storage.store_objects import ReadWriteData

config_s3 = configuration()
config_sh = SHConfig()

config_sh.instance_id = config_s3.sh_instance_id
config_sh.sh_client_id = config_s3.sh_client_id
config_sh.sh_client_secret = config_s3.sh_client_secret

script_dir = {'SENTINEL2_L1C': 'sentinel-2',
              'SENTINEL2_L2A': 'sentinel-2',
              'SENTINEL1': 'sentinel-1',
              'SENTINEL1_IW': 'sentinel-1',
              'SENTINEL1_IW_ASC': 'sentinel-1',
              'SENTINEL1_IW_DES': 'sentinel-1',
              'SENTINEL1_EW_ASC': 'sentinel-1',
              'SENTINEL1_EW_DES': 'sentinel-1',
              'SENTINEL1_EW_SH': 'sentinel-1',
              'SENTINEL1_EW_SH_ASC': 'sentinel-1',
              'SENTINEL1_EW_SH_DES': 'sentinel-1',
              'MODIS': 'modis',
              'LANDSAT45_L1': 'Landsat-57',  # Not sure about this
              'LANDSAT45_L2': 'Landsat-57',  # Not sure about this
              'LANDSAT8': 'landsat-8',
              'LANDSAT8_L1': 'landsat-8',
              'LANDSAT8_L2': 'landsat-8',
              'SENTINEL5P': 'sentinel-5p',
              'SENTINEL3_SLSTR': 'slstr'}


def processor_script(instrument, name):
    instrument = instrument.upper()
    with open(join(pathlib.Path(__file__).parent, 'scripts', script_dir[instrument], name, 'script.js'),
              "r") as f:
        return f.read()


def get_request(instrument, processing_module, start, end, bbox, size, data_folder):
    return SentinelHubRequest(
        evalscript=processor_script(instrument, processing_module),
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=getattr(DataCollection, instrument.upper()),
                time_interval=(start, end),
                mosaicking_order='leastCC'
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


def process(instrument: str, processing_module: str, area_wkt: str, start: str, end: str) -> None:
    resolution = 10  # Should be good for most Sentinel-2 processors
    area = wkt.loads(area_wkt)
    bbox = BBox(bbox=area.bounds, crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox, resolution=resolution)

    intervals = pd.interval_range(start=pd.Timestamp(start), end=pd.Timestamp(end), freq='M')
    intervals = [(pd.to_datetime(i.left + pd.DateOffset(days=1)).date(), pd.to_datetime(i.right).date())
                 for i in intervals]

    for start, end in intervals:
        # request_func has one argument: data_folder
        request_func = partial(get_request, instrument, processing_module, start, end, bbox, size)
        store = ReadWriteData(config_s3, 'product_name')
        ToS3(store, processing_module, 'monthly', request_func)
        break


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
    process(instrument, processing_module, area_wkt, start, end)


if __name__ == '__main__':
    cli()
