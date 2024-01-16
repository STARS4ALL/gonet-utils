#!/bin/bash

read -p "Max Exposure time [ms], , hit CTRL+C to stop: "  tmax
read -p "Min Exposure time [ms], , hit CTRL+C to stop: "  tmin
read -p "Analog Gain [1..16], , hit CTRL+C to stop: "  analoggain

exposure_plan=$(gonet-exposure --console stops -t0 ${tmin}/1000 -t1 ${msecs}/1000 -m 4095 -ppl 5)

for label in ${exposure_plan}
do
	i=${label:0:3}
	t=${label:4:7}
	IMAGE=flat_g${analoggain}_${i}_${t}_a.jpg
	echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
	raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE} || exit 255

	IMAGE=flat_g${analoggain}_${i}_${t}_b.jpg
	echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
	raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE} || exit 255
done
