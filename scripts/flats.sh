#!/bin/bash

read -p "Max Exposure time [us], , hit CTRL+C to stop: "  tmax
read -p "Min Exposure time [us], , hit CTRL+C to stop: "  tmin
read -p "Analog Gain [1..16], , hit CTRL+C to stop: "  analog_gain

# No console log as we need to capture stdout
exposure_plan=$(gonet-exposure --log-file exposure_plan.log stops -t0 ${tmin}/1000000 -t1 ${tmax}/1000000 -m 4095 -ppl 5)

for label in ${exposure_plan}
do
	i=${label:0:3}
	t=${label:4:7}
	IMAGE=flat_g${analog_gain}_${i}_${t}_a.jpg
	echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
	raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${IMAGE} || exit 255

	IMAGE=flat_g${analog_gain}_${i}_${t}_b.jpg
	echo "raspistill --raw  --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analoggain} --digitalgain 1 --output ${IMAGE}"
	raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${IMAGE} || exit 255
done
