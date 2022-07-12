#FROM osgeo/gdal:ubuntu-small-latest
FROM ubuntu:22.04

ENV TZ=Europe/Dublin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y python3-pip python3-gdal git

# Authorize SSH Host
RUN mkdir -p /root/.ssh
COPY credentials/config /root/.ssh/
COPY credentials/*_rsa /root/.ssh/
COPY credentials/config_eo_service.yml /root/config_eo_service.yml
RUN chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts && \
    chmod 600 /root/.ssh/config && \
    chmod 600 /root/.ssh/*_rsa

RUN pip3 install git+ssh://github-eo-io/ECHOESProj/eo-io#egg=eo-io

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY eo_custom_scripts /app/eo_custom_scripts
WORKDIR /app/

ENTRYPOINT  [ "python3", "-W", "ignore", "-m", "eo_custom_scripts" ]