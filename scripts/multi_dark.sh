#!/bin/bash
# takes dark farmes at different gains
DEF_TAG="dark"
DEF_EXPTIME=10000

read -p "Dark tag [$DEF_TAG]: " tag
read -p "Dark exposure (us) [$DEF_EXPTIME]: " exptime

tag=${tag:-$DEF_TAG}
exptime=${exptime:-$DEF_EXPTIME}

echo "Taking dark frames at different gains"

for (( analog_gain=1; analog_gain<=16; analog_gain++  ))
do
	t=${exptime}
	image=${tag}_g${analog_gain}_${t}_a.jpg
   	echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image}"
   	raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image} || exit 255

	image=${tag}_g${analog_gain}_${t}_b.jpg
   	echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image}"
   	raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image} || exit 255
done
