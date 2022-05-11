# eo-custom-scripts

eo-custom-scripts generates GeoTIFFs for the specified processing module.

The code uses [Sentinel-Hub Python API](https://sentinelhub-py.readthedocs.io/en/latest/).
The [Sentinel Custom-Script repository](https://custom-scripts.sentinel-hub.com/) is a collection of scripts for
Sentinel-Hub, which have been copied to this repository. The scripts in this repository can be called from the command
line using this program. It will store the resulting GeoTIFFs, in an S3 compatible object store.

### Minio (prerequisite when running locally)

When running locally, the GeoTIFFs generated from the process will be stored in Minio. Minio is an S3 compatible object
store. If it is run on CreoDIAS, the results will be stored on its object store and Minio is not required. Therefore,
Minio should be running when running locally. See here for instruction on installing
Minio: https://docs.min.io/docs/minio-quickstart-guide.html

### Installation

Pip install the requirements from requirements.txt as follows:

    pip3 install -r /tmp/requirements.txt

This has been tested in Ubuntu 20.04.

Alternatively, run using Docker (see below).

### Credentials

The credential can be obtained from the Compass Informatics password manager, under "eo-custom-scripts configuration files".
Unzip the config files in there and put the yaml files in the home directory in a directory called eoconfig.

When Minio is started, it displays and endpoint. Copy this URL into both the endpoint_url_local and endpoint_url_ext
entries of the config (yaml) file.

### Usage

The command line arguments are as follows:

    INSTRUMENT         The instrument name 
    PROCESSING_MODULE  The processing module from the scripts
    AREA_WKT           The polygon WKT with the bounding box
    START              The start of the date interval   
    END                The end of the date interval   

The full list of instruments for the INSTRUMENT arguments is as follows:

    LANDSAT45_L1
    LANDSAT45_L2
    LANDSAT8
    LANDSAT8_L1
    LANDSAT8_L2
    MODIS
    SENTINEL1
    SENTINEL1_EW_ASC
    SENTINEL1_EW_DES
    SENTINEL1_EW_SH
    SENTINEL1_EW_SH_ASC
    SENTINEL1_EW_SH_DES
    SENTINEL1_IW
    SENTINEL1_IW_ASC
    SENTINEL1_IW_DES
    SENTINEL2_L1C
    SENTINEL2_L2A
    SENTINEL3_SLSTR
    SENTINEL5P
    COPERNICUS_SERVICES

The processing modules, for the PROCESSING_MODULE argument, are given in https://github.com/sentinel-hub/custom-scripts
and under the "scripts" directory in the repository (but without and documentation). The processing module is the name
of the directory that contains script.js. For example, under sentinel-2 there is false_color_composite, barren_soil etc,
each of which contain script.js.

The instrument will map to the corresponding directory in the scripts directory, so for example with "SENTINEL1"
instrument any of the scripts in the "sentinel-1" directory can be used.

An example usage is as follows:

    python3 -m eo-custom-scripts sentinel2_l1c ndvi_greyscale "POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, -6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, -6.3777351379394 52.344188690186))" 2019-01-01 2019-12-31

The GeoTIFFs should be in object store after this has executed. The location where the data is store is printed to the
terminal.

### Alternatively, Run Using Docker

##### Step 1: build the container:

    docker build . -t eocs --network host

##### Step 2: run the container:

Examples with docker:

    docker run --network host -it eocs sentinel2_l1c ndvi_greyscale "POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, -6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, -6.3777351379394 52.344188690186))" 2019-01-01 2019-12-31
    docker run --network host -it eocs copernicus_services global_surface_water_change "POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, -6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, -6.3777351379394 52.344188690186))" 2015-01-01 2020-12-31

In the second example, copernicus_services is the name of the data source (it is not an instrument even though it is
passed to that argument). For the Copernicus services a config.yaml file is required for them to work in the directory
of the script.

    corine_land_cover
    corine_land_cover_accounting_layer
    global_land_cover
    global_surface_water_change
    global_surface_water_extent
    global_surface_water_occurrence
    global_surface_water_recurrence
    global_surface_water_seasonality
    global_surface_water_transitions
    vpp-amplitude-ampl
    vpp-end-of-season-value-eosv
    vpp-season-maximum-value-maxv
    vpp-season-minimum-value-minv
    vpp-seasonal-productivity-sprod
    vpp-slope-of-greening-up-period-lslope
    vpp-slope-of-senescent-period-rslope
    vpp-start-of-season-value-sosv
    vpp-total-productivity-tprod
    water-bodies
    water-bodies-occurence

##### Deploy

    #local:
    git archive main --output deploy.zip 
    pscp deploy.zip eouser@eo-stack:/home/eouser/

    #remote:
    unzip deploy.zip -d eo-custom-scripts
    docker build eo-custom-scripts -t eom --network host

## TODO

* Use Pydantic (https://pydantic-docs.helpmanual.io/usage/settings/) to read config file, with the option of using
  environment variables instead those in the config file.

* Map config files from local to docker container. See https://dantehranian.wordpress.com/2015/03/25/how-should-i-get-application-configuration-into-my-docker-containers/

## Update Custom Scripts

Use rsync to update the /scripts directory with the https://github.com/sentinel-hub/custom-scripts repo.

rsync -a --include='*/' --include="*.html" --include="*.js" --include="*.json" --include="*.lnk" --include="*.md"
--include="*.txt" --include="*.yml" --include="*.idx" --exclude="*" custom-scripts/ eo-custom-scripts/eo-custom-scripts/scripts/