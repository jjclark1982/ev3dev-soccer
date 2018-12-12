#!/usr/bin/env python3

import importlib
import os
from datetime import datetime, timedelta
import atexit

import main as program

stat_time = datetime.now()
old_mtime = os.path.getmtime(program.__file__)
def reload_program():
    global stat_time, old_mtime

    if datetime.now() - stat_time < timedelta(0,1): # one second
        return

    stat_time = datetime.now()
    new_mtime = (os.path.getmtime(program.__file__))
    if new_mtime > old_mtime:
        print("Change detected. Reloading {}".format(program.__file__))
        old_mtime = new_mtime
        try:
            importlib.reload(program)
        except Exception as e:
            print(e)

def stop():
    if getattr(program, 'stop'):
        program.stop()

def run():
    if getattr(program, 'start'):
        program.start()
    while True:
        reload_program()
        try:
            program.update()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    atexit.register(stop)
    run()
