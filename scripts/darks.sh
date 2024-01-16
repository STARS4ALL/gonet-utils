#!/bin/bash

read -p "Enter Analog Gain [1..16], , hit CTRL+C to stop: "  analoggain

EXPTIME=100 # microseconds
DATE=$(date +%Y%m%dT%H%M%S)

# take a pair of darks
FILE=dark_g${analoggain}_a.jpg
echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${FILE}"
raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${FILE} || exit 255

FILE=dark_g${analoggain}_b.jpg
echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${FILE}"
raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${FILE} || exit 255
