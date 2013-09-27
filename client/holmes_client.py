# -*- coding: utf-8 -*-
#!/usr/bin/python
"""

Module      :   holmes.py

Usage       :   Track the current running application, get the opened windows
                and save them to database.


Author      :   Abhishek Garg <abhishekgarg12@yahoo.com>

"""

__autor__ = "abhishek.garg"
__version__ = 0.1


# IMPORTS
import platform
import re
import os
import time
import json
import ast
import logging
from collections import defaultdict

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=r'error.log',
                    level=logging.DEBUG,
                    filemode="a")

WHICHOS = platform.system()

if WHICHOS == 'Windows':
    try:
        from win32gui import GetForegroundWindow, GetWindowText
        from win32process import GetWindowThreadProcessId
        from psutil import Process
    except ImportError, e:
        raw_input(e)

def tree():
    return defaultdict(tree)

TODAY = time.strftime('%d%m%Y')
USERNAME = os.environ['USERNAME']
DB = os.path.join(r'T:\VDT\TEMP\chronos', USERNAME)
SLEEP = 2

def removeNonAscii(s): return ''.join(i for i in s if ord(i)<128)

def upload_data(userdata):
    """ Upload data to the json file. """
    orig = ast.literal_eval(json.dumps(userdata))
    try:
        data = ast.literal_eval(open(DB, 'rb').read())
    except:
        data = {USERNAME:{TODAY:{}}}

    if orig.has_key(USERNAME):
        if data[USERNAME].has_key(TODAY):
            for app_name in orig[USERNAME][TODAY].keys():
                if data[USERNAME][TODAY].has_key(app_name):
                    for app_state in orig[USERNAME][TODAY][app_name].keys():
                        if data[USERNAME][TODAY][app_name].has_key(app_state):
                            old = data[USERNAME][TODAY][app_name][app_state]
                            new = orig[USERNAME][TODAY][app_name][app_state]
                            data[USERNAME][TODAY][app_name][app_state] = old+new
                        else:
                            data[USERNAME][TODAY][app_name][app_state] = orig[USERNAME][TODAY][app_name][app_state]
                else:
                    data[USERNAME][TODAY][app_name] = orig[USERNAME][TODAY][app_name]
        else:
            data[USERNAME][TODAY] = orig[USERNAME][TODAY]

    with open(DB+"_lock", 'wb') as _f:
        json.dump(data, _f)
        _f.close()

    if os.path.exists(DB):
        os.remove(DB)

    os.rename(DB+"_lock", DB)

    return True


def get_app_info(userdata):
    """ Get the tracking info. """
    for _x in xrange(5):
        app_name = ""
        app_state = ""

        # if the OS is linux then run the following code
        if WHICHOS == 'Linux':
            win_id_cmd = os.popen('xprop -root _NET_ACTIVE_WINDOW').read()
            win_id_srch = re.search(r'(_NET_ACTIVE_WINDOW[(]WINDOW[)]: window id # )([0-9a-z]*)', win_id_cmd)

            if win_id_srch:
                win_id = win_id_srch.group(2)
                app_cmd = os.popen('xprop -id %s WM_CLASS' % win_id).read()
                app_state_cmd = os.popen('xprop -id %s WM_NAME' % win_id).read()
                # Get the Application Name
                app_name = app_cmd.split()[-1].strip().replace('\"','')
                # Get the Current process of that application
                app_state = removeNonAscii(app_state_cmd.split("=")[-1].strip().translate(None, "\"*"))

        # if the OS is Windows then run the following code
        elif WHICHOS == 'Windows':
            pid = GetWindowThreadProcessId(GetForegroundWindow())
            # Get the Application Name
            app_name = os.path.splitext(Process(pid[1]).name)[0].replace('\"','')
            # Get the Current process of that application
            app_state = removeNonAscii(GetWindowText(GetForegroundWindow())).translate(None, "\"*")

        if app_name != "" and app_state != "":
            if userdata[USERNAME][TODAY][app_name][app_state]:
                val = userdata[USERNAME][TODAY][app_name][app_state]
                userdata[USERNAME][TODAY][app_name][app_state] = val + SLEEP
            else:
                userdata[USERNAME][TODAY][app_name][app_state] = SLEEP
        else:
            if userdata[USERNAME][TODAY]["window"]["idle"]:
                val = userdata[USERNAME][TODAY]["window"]["idle"]
                userdata[USERNAME][TODAY]["window"]["idle"] = val + SLEEP
            else:
                userdata[USERNAME][TODAY]["window"]["idle"] = SLEEP

        time.sleep(SLEEP)

    return userdata


def main():
    """ Get the data from json read new data and upload it back to json file """
    while True:
        userdata = get_app_info(tree())
        upload_data(userdata)


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        logging.error(e)
