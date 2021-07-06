# eo-mosaics

Create mosaics

Build:

    docker build . -t eom --network host


Example:

    docker run --network host -it eom sentinel2_l1c ndvi_greyscale "POLYGON((-6.3777351379394 52.344188690186, -6.3780784606933 52.357234954835, -6.3552474975585 52.357749938966, -6.3561058044433 52.345218658448, -6.3777351379394 52.344188690186))" 2019-01-01 2019-12-31


Deploy:

    #local:
    git archive main --output deploy.zip 
    pscp deploy.zip eouser@eo-stack:/home/eouser/

    #remote:
    unzip deploy.zip -d eo-mosaics
    docker build eo-mosaics -t eom --network host