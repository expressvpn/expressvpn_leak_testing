#!/usr/bin/env bash

for var in "$@"
do
    # Don't force sudo if the user just wants help
    if [[ "$var" == "-h" || "$var" == "--help" ]]; then
        ./run_tests.py -h
        exit $?
    fi
done

RUN_TESTS="./tools/run_tests.py"

# Use the correct python version
. activate

unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
    echo "Leak tools require root permissions..."
    sudo -E $RUN_TESTS $@
elif [[ "$unamestr" == 'Darwin' ]]; then
    echo "Leak tools require root permissions..."
    sudo $RUN_TESTS $@
else
    $RUN_TESTS $@
fi
