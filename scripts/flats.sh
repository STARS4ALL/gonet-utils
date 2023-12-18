#!/bin/bash

read -p "Max Exposure time [ms], , hit CTRL+C to stop:: "  msecs
read -p "Analog Gain [1..16], , hit CTRL+C to stop:: "  analoggain

N=36
MAX=$(( msecs*1000 ))
MIN=1000
STEP=$(( ($MAX-$MIN)/$N ))

EXPTIME=$MIN
for (( i=0; i<=$N; i++ ))
do
   IMAGE=flat_${i}_a_${EXPTIME}_g${analoggain}.jpg
   echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
   #raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE} || exit 255

   IMAGE=flat_${i}_b_${EXPTIME}_g${analoggain}.jpg
   echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
   #raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE} || exit 255
   EXPTIME=$(( $EXPTIME + $STEP ))
  
done
