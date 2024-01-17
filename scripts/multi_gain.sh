#!/bin/bash
# takes dark farmes at different gains
DEF_TAG="dark"
DEF_EXPTIME=10000

read -p "Image tag [$DEF_TAG]: " tag
read -p "Image exposure (us) [$DEF_EXPTIME]: " exptime

tag=${tag:-$DEF_TAG}
exptime=${exptime:-$DEF_EXPTIME}

echo "Taking an image with at different gains, same exp. time"

for (( analog_gain=1; analog_gain<=16; analog_gain++  ))
do
	t=${exptime}
	padded=$(printf "%06d" $t)
	image=${tag}_g${analog_gain}_${padded}_a.jpg
   	echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image}"
   	raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image} || exit 255

	image=${tag}_g${analog_gain}_${padded}_b.jpg
   	echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image}"
   	raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image} || exit 255
done
