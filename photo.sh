#!/bin/bash

read -p "Exposure time [ms]: "  msecs

EXPTIME=$(( msecs*1000 ))
IMAGE=photo
STATS_FILE=image_stats.csv
for (( ; ; ))
do
   read -p "Enter wavelength [nm], hit CTRL+C to stop: "  wavelength
   read -p "Enter current [pA], hit CTRL+C to stop: "  current
   echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain 4 --digitalgain 1 --output ${IMAGE}.jpg"
   raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain 4 --digitalgain 1 --output ${IMAGE}.jpg
   mv ${IMAGE}.jpg ${IMAGE}_${wavelength}.jpg
   echo "gonetutils -c image stats -w ${wavelength} -c ${current} -e ${EXPTIME} -i ${IMAGE}_${wavelength}.jpg -o ${STATS_FILE}"
   gonetutils -c image stats -w ${wavelength} -c ${current} -e ${EXPTIME} -i ${IMAGE}_${wavelength}.jpg -o ${STATS_FILE}
done
#nohup raspistill -n -t 0 -drc off -ss 600000 -ex off -awb off -ag 4 -dg 1 -r -s -o /home/pi/test.jpg > /dev/null 2>&1 &
