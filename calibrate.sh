#!/bin/bash

DEVICE_NAME=${1}

echo "Press Ctrl+C to stop recording"
./mosaic.py -a record > calibration_${DEVICE_NAME}.events
