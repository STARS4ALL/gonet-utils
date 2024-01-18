#!/bin/bash

DEF_WIDTH="1/20"
DEF_HEIGHT="1/16"
DEF_GAIN=1

read -p "Exposure time (us): "  usecs
read -p "Analog Gain (1..16) [$DEF_GAIN]: " analog_gain
read -p "central width [$DEF_WIDTH]: " width
read -p "central height [$DEF_HEIGHT]: " height

width=${width:-$DEF_WIDTH}
height=${height:-$DEF_HEIGHT}
analog_gain=${analog_gain:-$DEF_GAIN}

IMAGE=photo.jpg
for (( ; ; ))
do
   echo "raspistill --raw  --shutter ${usecs} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${IMAGE}"
   raspistill --raw  --shutter ${usecs} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${IMAGE} || exit 255
   echo "gonet-stats --console -i ${IMAGE} -wi ${width} -he ${height}"
   gonet-stats --console -i ${IMAGE} -wi ${width} -he ${height}
done
#nohup raspistill -n -t 0 -drc off -ss 600000 -ex off -awb off -ag 4 -dg 1 -r -s -o /home/pi/test.jpg > /dev/null 2>&1 &
