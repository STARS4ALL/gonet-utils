#!/bin/bash

read -p "Exposure time [ms], , hit CTRL+C to stop: "  msecs
read -p "Analog Gain [1..16], , hit CTRL+C to stop: " analoggain
read -p "central width , hit CTRL+C to stop: " width
read -p "central height , hit CTRL+C to stop: " height

EXPTIME=$(( msecs*1000 ))
IMAGE=photo.jpg
for (( ; ; ))
do
   echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
   raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain 4 --digitalgain 1 --output ${IMAGE} || exit 255
   echo "gonet-stats -i ${IMAGE} -wi ${width} -he ${height}"
   gonet-stats -i ${IMAGE} -wi ${width} -he ${height}
   sleep 2
done
#nohup raspistill -n -t 0 -drc off -ss 600000 -ex off -awb off -ag 4 -dg 1 -r -s -o /home/pi/test.jpg > /dev/null 2>&1 &
