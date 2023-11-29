#!/bin/bash

read -p "Exposure time [ms], , hit CTRL+C to stop:: "  msecs
read -p "Enter filter [B|O|R|C] (BG38|OG570|RG830|Clear), hit CTRL+C to stop: "  filter

EXPTIME=$(( msecs*1000 ))
IMAGE=photo
STATS_FILE=image_stats.csv
for (( ; ; ))
do
   read -p "Enter wavelength [nm], hit CTRL+C to stop: "  wavelength
  
   DATE=$(date +%Y%m%dT%H%M%S)
   echo "raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain 4 --digitalgain 1 --output ${IMAGE}.jpg"
   raspistill --raw  --shutter ${EXPTIME} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain 4 --digitalgain 1 --output ${IMAGE}.jpg || exit 255
   mv ${IMAGE}.jpg ${IMAGE}_${wavelength}_${filter}_${DATE}.jpg
   echo "gonetutils -c image stats -w ${wavelength} -c ${current} -e ${msecs} -i ${IMAGE}_${wavelength}_${filter}_${DATE}.jpg -o ${STATS_FILE}"
   gonetutils -c image stats -w ${wavelength} -f ${filter} -e ${msecs} -i ${IMAGE}_${wavelength}_${filter}_${DATE}.jpg -o ${STATS_FILE}
done
#nohup raspistill -n -t 0 -drc off -ss 600000 -ex off -awb off -ag 4 -dg 1 -r -s -o /home/pi/test.jpg > /dev/null 2>&1 &
