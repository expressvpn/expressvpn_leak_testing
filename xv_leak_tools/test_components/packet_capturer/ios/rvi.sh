#!/bin/bash
# Opens a remote virtual interface for a single iPhone

udid=$(instruments -s devices | grep -v "Simulator" | grep "iPhone" | awk -F '[][]' '{print $2}')

if [ -z $udid ]; then
    echo "No UDID found" 1>&2 
    exit 1
else
    echo "Found UDID $udid"
fi

rvi="rvi0"
if [[ $(ifconfig -l) =~ $rvi ]]; then
    echo "The $rvi interface already exists" 1>&2 
    exit 2
else
    rvictl -s $udid
    rvi_success=$?
    exit $rvi_success
fi

exit 1

