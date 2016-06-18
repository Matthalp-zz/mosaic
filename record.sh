#!/bin/bash

APP_NAME=${1}
SOURCE_NAME=${2}

echo "Press Ctrl+C to stop recording"
./mosaic.py -a record > ${APP_NAME}_${SOURCE_NAME}.events
