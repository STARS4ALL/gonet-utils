#!/bin/bash

read -p "Max Exposure time [ms], , hit CTRL+C to stop:: "  msecs
read -p "Analog Gain [1..16], , hit CTRL+C to stop:: "  analoggain

exposure_list=$(gonet-exposure -t0 1/1000 -tf ${msecs}/1000 -n 4095 --time)

for t in ${exposure_list}
do
   IMAGE=flat_a_${t}_g${analoggain}.jpg
   echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
   raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE} || exit 255

   IMAGE=flat_b_${t}_g${analoggain}.jpg
   echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
   raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE} || exit 255
done
