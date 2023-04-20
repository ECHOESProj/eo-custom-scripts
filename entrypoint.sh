#!/bin/sh
# Used in Docker file for ENTRYPOINT

echo "$@"
#envsubst < /root/config_eo_service.yml | tee /root/config_eo_service.yml # this causes config_eo_service.yaml to be blank sometimes, see https://stackoverflow.com/q/60546292
FILE=/root/config_eo_service.yml
tmp=$(mktemp)
envsubst < "$FILE" > "$tmp" &&  mv "$tmp" "$FILE"
python3 -W ignore -m eo_custom_scripts "$@"
