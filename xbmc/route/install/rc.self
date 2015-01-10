#!/usr/bin/env bash

#power save
[ -b /dev/sdb1 ] && hdparm -Y /dev/sdb

