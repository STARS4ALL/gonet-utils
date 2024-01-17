#!/bin/bash

# -------------------------------------------------------------
# Capture a sequence of image pairs with varying exposure times
# -------------------------------------------------------------

DEF_TAG="flat"
DEF_GAIN=1
DEF_EXPOSURE_PLAN="stops"
DEF_MAX_DN=4095 # For the "stops" exposure plan
DEF_POINTS_PER_LEVEL=5 # For the "stops" exposure plan
DEF_NPOINTS=50 # For the "linear" exposure plan
DEF_LOG_FILE="exposure_plan.log"

read -p "Max Exposure time in us: " tmax
read -p "Min Exposure time in us: " tmin
read -p "Analog Gain (1..16) [$DEF_GAIN]: " analog_gain
read -p "Sequence tag [$DEF_TAG]: " tag

tag=${tag:-$DEF_TAG}
analog_gain=${analog_gain:-$DEF_GAIN}
exposure_plan=${1:-$DEF_EXPOSURE_PLAN}
max_dn=${2:-$DEF_MAX_DN}
npoints=${2:-$DEF_NPOINTS}
ppl=${3:-$DEF_POINTS_PER_LEVEL}

if [[ "$exposure_plan" = "linear" ]]
then
  	echo "gonet-exposure --log-file ${DEF_LOG_FILE} linear -t0 ${tmin}/1000000 -t1 ${tmax}/1000000 -n ${npoints})"
  	exposure_times=$(gonet-exposure --log-file ${DEF_LOG_FILE} linear -t0 ${tmin}/1000000 -t1 ${tmax}/1000000 -n ${npoints})
else
	echo "gonet-exposure --log-file ${DEF_LOG_FILE} stops -t0 ${tmin}/1000000 -t1 ${tmax}/1000000 -m ${max_dn} -ppl ${ppl})"
  	exposure_times=$(gonet-exposure --log-file ${DEF_LOG_FILE} stops -t0 ${tmin}/1000000 -t1 ${tmax}/1000000 -m ${max_dn} -ppl ${ppl})
fi

for i_t in ${exposure_times}
do
	i=${i_t:0:3}
	t=${i_t:4:7}
	image=${tag}_g${analog_gain}_${i}_${t}_a.jpg
	echo "raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image}"
	raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image} || exit 255

	image=${tag}_g${analog_gain}_${i}_${t}_b.jpg
	echo "raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image}"
	raspistill --raw --shutter ${t} --timeout 100 -drc off --nopreview -ex off -awb off --analoggain ${analog_gain} --digitalgain 1 --output ${image} || exit 255
done  
