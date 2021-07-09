# eo-mosaics

eo-mosaics generates GeoTIFFs for the specified processing module. 

The code uses [Sentinel-Hub Python API](https://sentinelhub-py.readthedocs.io/en/latest/).
The [Sentinel Custom-Script repository](https://custom-scripts.sentinel-hub.com/) is a collection of scripts for Sentinel-Hub,
which have been copied to this repository.
The scripts in this repository can be called from the command line using this program. It will store the resulting GeoTIFFs,
in an S3 compatible object store.


### Minio (prerequisite when running locally)

When running locally, the GeoTIFFs generated from the process will be stored in Minio. Minio is an S3 compatible object store.
If it is run on CreoDIAS, the results will be stored on its object store and Minio is not required. Therefore, Minio should be
running when running locally. See here for instruction on installing Minio: https://docs.min.io/docs/minio-quickstart-guide.html


### Install

Pip install the requirements from requirements.txt.

### Credentials

The credential can be obtained from the Compass Informatics password manager, under "eo-mosaics configuration files". Unzip the
config files in there and put the yaml files in the config directory in this repository. 


### Usage 

An example usage is as follows:

    python eo-mosaics sentinel2_l1c ndvi_greyscale "POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, -6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, -6.3777351379394 52.344188690186))" 2019-01-01 2019-12-31

The GeoTIFFs should be in Minio after this has executed.

The command line arguments are as follows: 

    INSTRUMENT         The instrument name 
    PROCESSING_MODULE  The processing module from the scripts
    AREA_WKT           The polygon WKT with the bounding box
    START              The start of the date interval   
    END                The end of the date interval   


The full list of instruments for the INSTRUMENT arguments is as follows:

    SENTINEL2_L1C
    SENTINEL2_L2A
    SENTINEL1
    SENTINEL1_IW
    SENTINEL1_IW_ASC
    SENTINEL1_IW_DES
    SENTINEL1_EW_ASC
    SENTINEL1_EW_DES
    SENTINEL1_EW_SH
    SENTINEL1_EW_SH_ASC
    SENTINEL1_EW_SH_DES
    MODIS
    LANDSAT45_L1
    LANDSAT45_L2
    LANDSAT8
    LANDSAT8_L1
    LANDSAT8_L2
    SENTINEL5P
    SENTINEL3_SLSTR

The processing modules, for the PROCESSING_MODULE argument, are given in https://github.com/sentinel-hub/custom-scripts 
and under the "scripts" directory in the repository (but without and documentation). 
The processing module is the name of the directory that contains script.js. For example, under sentinel-2 
there is false_color_composite, barren_soil etc, each of which contain script.js. 

The instrument will modify the path to the scripts directory, so for example with "SENTINEL1" instrument any of the
scripts in the "sentinel-1" directory can be used.   


### Alternatively, Run Using Docker


##### Step 1: build the container:

    docker build . -t eom --network host

##### Step 2: run the container:


Example:

    docker run --network host -it eom sentinel2_l1c ndvi_greyscale "POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, -6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, -6.3777351379394 52.344188690186))" 2019-01-01 2019-12-31


##### Deploy

    #local:
    git archive main --output deploy.zip 
    pscp deploy.zip eouser@eo-stack:/home/eouser/

    #remote:
    unzip deploy.zip -d eo-mosaics
    docker build eo-mosaics -t eom --network host


## TODO

* Modify the endpoint for running on CreoDIAS. See following from Sentinel-Hub support:

    to use Sentinel Hub on CreoDIAS platform at this stage it is easier to use your paid account (jlavelle@compass.ie) and simply use CreoDIAS end-point:
    https://docs.sentinel-hub.com/api/latest/data/#creodias-sentinel-hub-deployment
    You essentially just need to change the service.sentinel-hub,com to creodias.sentinel-hub.com


* Use Pydantic (https://pydantic-docs.helpmanual.io/usage/settings/) to read config file, with the option of using environment
variables instead those in the config file.
