FROM python:3.8

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY ./eo-mosaics /app/eo-mosaics
WORKDIR /app/

ENTRYPOINT  [ "python3", "-W", "ignore", "eo-mosaics" ]