#!/bin/bash

APP_NAME=${1}
SOURCE_NAME=${2}
DESTINATION_NAME=${3}

RERAN_TRACE=${APP_NAME}_${SOURCE_NAME}_to_${DESTINATION_NAME}.reran

adb shell su -c mount -r -w -o remount /system
adb push ${RERAN_TRACE} /sdcard/
adb shell su -c cp /sdcard/${RERAN_TRACE} /system/mosaic/
adb shell su -c /system/mosaic/reran /system/mosaic/${RERAN_TRACE}
