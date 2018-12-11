#!/usr/bin/env python

import inspect

def info(msg):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    print '[%s] %s' % (mod.__name__, msg)

def main():
    info('hello')

if __name__ == '__main__':
    main()
