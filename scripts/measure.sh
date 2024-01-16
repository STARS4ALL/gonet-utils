#!/bin/bash

read -p "Exposure time [us], , hit CTRL+C to stop: "  usecs
read -p "Analog Gain [1..16], , hit CTRL+C to stop: " analog_gain
read -p "central width , hit CTRL+C to stop: " width
read -p "central height , hit CTRL+C to stop: " height

EXPTIME=$(( usecs*1000000 ))
IMAGE=photo.jpg
for (( ; ; ))
do
   echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${IMAGE}"
   raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${IMAGE} || exit 255
   echo "gonet-stats --console -i ${IMAGE} -wi ${width} -he ${height}"
   gonet-stats --console -i ${IMAGE} -wi ${width} -he ${height}
   sleep 2
done
#nohup raspistill -n -t 0 -drc off -ss 600000 -ex off -awb off -ag 4 -dg 1 -r -s -o /home/pi/test.jpg > /dev/null 2>&1 &
