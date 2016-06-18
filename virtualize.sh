#!/bin/bash

APP_NAME=${1}
SOURCE_NAME=${2}

./mosaic.py -a virtualize -c calibration_${SOURCE_NAME}.events -i ${APP_NAME}_${SOURCE_NAME}.events > ${APP_NAME}_${SOURCE_NAME}.virtual
