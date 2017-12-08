#!/usr/bin/env bash

unamestr=`uname`
if [[ $unamestr == *"CYGWIN"* ]]; then
    # Explicitly specify the interpretor on Windows else we can end up using a Windows version of
    # python (if the user has one) which will fail due to missing posix modules.
    /usr/bin/python3 tools/setup_python.py $@
else
    python3 tools/setup_python.py $@
fi
