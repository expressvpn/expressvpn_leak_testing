#!/usr/bin/env python3
import codecs
import pickle
import sys

def debug_scriptlet():
    '''Set this function to return True if you need to debug any of the scriptlets. It will prevent
    output and exceptions from being encoded and also enable logging in the scriplets (if they
    implement any logging).'''
    return False

def debug_output(msg):
    if not debug_scriptlet():
        return
    print("SCRIPTLET DEBUG: {}".format(msg))

def wrap_scriptlet(func):
    if debug_scriptlet():
        print(func())
    else:
        try:
            sys.stdout.write(codecs.encode(pickle.dumps(func()), "base64").decode())
            return 0
        except BaseException as ex:
            sys.stderr.write(codecs.encode(pickle.dumps(ex), "base64").decode())
            return 1
