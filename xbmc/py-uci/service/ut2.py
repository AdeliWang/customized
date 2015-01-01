#!/usr/bin/env python

import os, sys

def ut():
    path=os.path.split(os.path.realpath(__file__))[0]
    sys.path.append(path + "/..")
    w = UCI_wireless()
    print w.Get()

ut()
