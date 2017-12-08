import os
import pwd

def tools_root():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

def tools_user():
    uid = os.stat(tools_root()).st_uid
    return uid, pwd.getpwuid(uid)[0]
