#!/bin/bash


APP_NAME=${1}
SOURCE_NAME=${2}
DESTINATION_NAME=${3}

./mosaic.py -a translate -c calibration_${DESTINATION_NAME}.events -i ${APP_NAME}_${SOURCE_NAME}.virtual > ${APP_NAME}_${SOURCE_NAME}_to_${DESTINATION_NAME}.reran
