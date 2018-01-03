#!/usr/bin/env bash

UNAMESTR=`uname`
if [[ $UNAMESTR == *"CYGWIN"* ]]; then
    # Explicitly specify the interpretor on Windows else we can end up using a Windows version of
    # python (if the user has one) which will fail due to missing posix modules.
    PYTHON=/usr/bin/python3
    PIP=/usr/bin/pip3
else
    PYTHON=python3
    PIP=pip3
fi

$PYTHON -m ensurepip

$PIP install virtualenv

$PYTHON tools/setup_python.py $@
