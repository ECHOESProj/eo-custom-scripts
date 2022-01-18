"""
Integration tests which check that products are generated and put in the object store.

An error is raised if the values in is of the RGB bands of the generated GeoTIFFs are all 0 or 255.
"""

#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

import pytest
import pandas as pd

from eomosaics.__main__ import main
from eomosaics.core.settings import configuration
from eomosaics.core.storage.store_objects import ReadWriteData

config_s3 = configuration()
store = ReadWriteData(config_s3, 'product_name')


@pytest.fixture
def remove_objects():
    # pass
    store.remove_temp()
    yield
    store.remove_temp()  # To see the output, comment out this line and look in  <bucket-name>/_tests/


def process(instrument, processing_module, start, end, mosaicking_order=None, frequency=None, resolution=None,
            area_wkt="POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, "
                     "-6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, "
                     "-6.3777351379394 52.344188690186))"):
    obj_names = main(instrument, processing_module, area_wkt, start, end, mosaicking_order, frequency, resolution,
                     testing=True)
    for f in obj_names:
        obj_name = f[1].split(': ')[-1]
        assert store.check_exists(obj_name)


def test_corine_land_cover(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'corine_land_cover'
    for year in (1990, 2000, 2006, 2012, 2018):
        start = f'{year}-01-01'
        end = f'{year}-12-31'
        process(instrument, processing_module, start, end)


def test_global_land_cover(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'global_land_cover'
    start = '2015-01-01'
    end = '2019-12-31'
    process(instrument, processing_module, start, end)


def test_vpp_amplitude_ampl(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vpp-amplitude-ampl'
    start = '2017-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_vpp_end_of_season_value_eosv(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vpp-end-of-season-value-eosv'
    start = '2017-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_vpp_season_minimum_value_minv(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vpp-season-minimum-value-minv'
    start = '2017-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_vpp_season_maximum_value_maxv(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vpp-season-maximum-value-maxv'
    start = '2017-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_vpp_slope_of_greening_up_period_lslope(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vpp-slope-of-greening-up-period-lslope'
    start = '2017-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_vpp_slope_of_senescent_period_rslope(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vpp-slope-of-senescent-period-rslope'
    start = '2017-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_vpp_start_of_season_value_sosv(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vpp-start-of-season-value-sosv'
    start = '2017-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_vpp_total_productivity_tprod(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vpp-total-productivity-tprod'
    start = '2017-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_global_surface_water_change(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'global_surface_water_change'
    start = '2019-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_global_surface_water_extent(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'global_surface_water_extent'
    start = '2019-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_global_surface_water_occurrence(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'global_surface_water_occurrence'
    start = '2019-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_global_surface_water_recurrence(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'global_surface_water_recurrence'
    start = '2019-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_global_surface_water_seasonality(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'global_surface_water_seasonality'
    start = '2019-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_global_surface_water_transitions(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'global_surface_water_transitions'
    start = '2019-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end)


def test_dem_color(remove_objects):
    instrument = 'dem'
    processing_module = 'dem-color'
    start = '2020-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end, frequency='yearly')


def test_contour_lines(remove_objects):
    instrument = 'dem'
    processing_module = 'contour-lines'
    start = '2020-01-01'
    end = '2020-12-31'
    process(instrument, processing_module, start, end, frequency='yearly')


def test_water_bodies(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'water-bodies'
    area_wkt = "POLYGON ((-6.28143310546875 53.0981471886932,-6.25362396240234 53.0981471886932," \
               "-6.25362396240234 53.1146357722166,-6.28143310546875 53.1146357722166," \
               "-6.28143310546875 53.0981471886932))"
    start = '2020-11-01'
    end = '2020-02-01'
    process(instrument, processing_module, start, end, area_wkt=area_wkt)


def test_st_ppi(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'st-ppi'
    start = '2017-01-01'
    end = '2017-01-30'
    # Product is every 10 days starting 2017-01-01
    for d in pd.date_range(start=pd.Timestamp(start), end=pd.Timestamp(end), freq='10D'):
        d_str = d.date().strftime('%Y-%m-%d')
        process(instrument, processing_module, d_str, d_str)


def test_vi_fapar(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vi-fapar'
    start = '2017-03-01'
    end = '2017-04-30'
    process(instrument, processing_module, start, end)


def test_vi_lai(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vi-lai'
    start = '2017-03-01'
    end = '2017-04-30'
    process(instrument, processing_module, start, end)


def test_vi_ndvi(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vi-ndvi'
    start = '2017-03-01'
    end = '2017-04-30'
    process(instrument, processing_module, start, end)


def test_vi_ppi(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'vi-ppi'
    start = '2017-03-01'
    end = '2017-04-30'
    process(instrument, processing_module, start, end)


def test_ndvi_greyscale(remove_objects):
    instrument = 'sentinel2_l1c'
    processing_module = 'ndvi_greyscale'
    start = '2017-03-01'
    end = '2017-03-30'
    process(instrument, processing_module, start, end, frequency='monthly')
