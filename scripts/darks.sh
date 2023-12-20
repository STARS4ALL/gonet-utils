#!/bin/bash

read -p "Enter Analog Gain [1..16], , hit CTRL+C to stop:: "  analoggain

EXPTIME=1000
DATE=$(date +%Y%m%dT%H%M%S)

# take a pair of darks
FILE=dark_a_g${analoggain}.jpg
echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${FILE}"
raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${FILE} || exit 255

FILE=dark_b_g${analoggain}.jpg
echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${FILE}"
raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${FILE} || exit 255
