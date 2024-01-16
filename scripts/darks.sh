#!/bin/bash

read -p "Enter Analog Gain [1..16], , hit CTRL+C to stop: "  analog_gain

EXPTIME=100 # microseconds
DATE=$(date +%Y%m%dT%H%M%S)

# take a pair of darks
FILE=dark_g${analog_gain}_a.jpg
echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${FILE}"
raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${FILE} || exit 255

FILE=dark_g${analog_gain}_b.jpg
echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${FILE}"
raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${FILE} || exit 255
