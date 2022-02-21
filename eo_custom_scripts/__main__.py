#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

__author__ = "John Lavelle, Fergal Doyle"
__email__ = "jlavelle@compass.ie"
__version__ = "1.0"

from eo_custom_scripts.core.shub import main
import click


@click.command()
@click.argument('instrument')
@click.argument('processing_module')
@click.argument('area_wkt')
@click.argument('start')
@click.argument('end')
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
