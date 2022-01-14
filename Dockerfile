FROM osgeo/gdal:ubuntu-small-latest

RUN apt-get update
RUN apt-get -y install python3-pip

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY eomosaics /app/eomosaics
WORKDIR /app/

ENTRYPOINT  [ "python3", "-W", "ignore", "-m", "eomosaics" ]