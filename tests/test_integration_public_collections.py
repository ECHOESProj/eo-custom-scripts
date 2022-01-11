from eomosaics.__main__ import main
import pytest
from eomosaics.core.settings import configuration
from eomosaics.core.storage.store_objects import ReadWriteData


config_s3 = configuration()
store = ReadWriteData(config_s3, 'product_name')

@pytest.fixture
def remove_objects():
    store.remove_temp()
    yield
    store.remove_temp()  # To see the output, comment out this line and look in
                         # <bucketname>/_tests/


def process(instrument, processing_module, start, end):

    area_wkt = "POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, -6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, -6.3777351379394 52.344188690186))"
    obj_names = main(instrument, processing_module, area_wkt, start, end, testing=True)
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

def test_corine_land_cover(remove_objects):
    instrument = 'copernicus_services'
    processing_module = 'corine_land_cover'
    for year in (2000, 2006, 2012, 2018):
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


