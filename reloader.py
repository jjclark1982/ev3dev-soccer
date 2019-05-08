#!/usr/bin/env python3

from datetime import datetime, timedelta
import atexit
import importlib
import os.path
import signal
import sys

class Reloader:
    '''
    Load a named Python module, and run its `update()` function
    continuously.
    Reload the module whenever its file is modified.
    If there are functions named `start()` or `stop()`, also run
    those once each at the beginning and end of the process.

    For instructions to set up a cache between reloads, see
    https://docs.python.org/3/library/importlib.html#importlib.reload
    '''

    def __init__(self, filename):
        self.program = importlib.import_module(os.path.splitext(filename)[0])
        self.stat_time = datetime.now()
        self.old_mtime = os.path.getmtime(self.program.__file__)

    def reload_program(self):
        '''
        Reload the program if its file has been modified.
        '''
        # poll at most once per second
        if datetime.now() - self.stat_time < timedelta(0,1):
            return

        self.stat_time = datetime.now()
        new_mtime = os.path.getmtime(self.program.__file__)
        if new_mtime != self.old_mtime:
            print("Change detected. Reloading {}".format(self.program.__file__))
            self.old_mtime = new_mtime
            try:
                importlib.reload(self.program)
            except Exception as e:
                print(e)

    def stop(self, *args):
        '''
        Run the program's `stop()` function.
        This wrapper function will be called exactly once with the latest code,
        even if the program has been modified multiple times.
        '''
        if callable(getattr(self.program, 'stop', None)):
            self.program.stop()

    def handle_signal(self, signo, frame=None):
        signals = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
            if v.startswith('SIG') and not v.startswith('SIG_'))

        print("Received {}, stopping program.".format(signals[signo]))
        sys.exit(0)

    def run(self):
        '''
        Run the program's `start()` function once.
        Then continuously run the `update()` function and check for changes
        until the program exits or is interrupted.
        Then run the `stop()` function once.
        '''
        atexit.register(self.stop)
        signal.signal(signal.SIGINT,  self.handle_signal) # Handle Ctrl-C
        signal.signal(signal.SIGTERM, self.handle_signal) # Handle `kill`
        signal.signal(signal.SIGHUP,  self.handle_signal) # Handle disconnect
        if callable(getattr(self.program, 'start', None)):
            self.program.start()
        while True:
            self.reload_program()
            try:
                self.program.update()
            except Exception as e:
                print(e)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=Reloader.__doc__)
    parser.add_argument('filename', nargs='?', default='main.py',
        help='filename of the module to run (default: main.py)')
    args = parser.parse_args()

    reloader = Reloader(filename=args.filename)
    reloader.run()
