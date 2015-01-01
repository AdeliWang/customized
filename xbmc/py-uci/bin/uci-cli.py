#!/usr/bin/env python

import os, sys
import gobject
import dbus
import json


class UCI_cli():
    OBJ_PATH = "/com/livecloud/uci"
    IF_NAME =  "com.livecloud.uci"
    def __init__(self, bus):
        self.bus=bus
        self.timeout = 30

    def set_timeout(self, timeout):
        timeout = float(timeout)
        if timeout >= 25.0 and timeout <= 180.0:
            self.timeout = float(timeout)
        else:
            self.timeout = 30

    def Set(self, propname, args):
        if (not isinstance(propname, str)) or (not isinstance(args, dict)):
            raise Exception("parameter error!")
        return self.__sync_call("Set", propname, args)

    def Get(self, propname):
        if not isinstance(propname, str):
            raise Exception("parameter error!")
        return self.__sync_call("Get", propname)

    def __sync_call(self, method, propname, args=None):
        try:
            if method == "Set":
                signature = dbus.Signature("sa{sv}")
                para=[propname, args]
            elif method == "Get":
                signature = dbus.Signature("s")
                para = [propname]
            reply = self.bus.call_blocking(UCI_cli.IF_NAME, \
                                           UCI_cli.OBJ_PATH, \
                                           UCI_cli.IF_NAME, \
                                           method, \
                                           signature, \
                                           para, \
                                           self.timeout)
        except dbus.DBusException as inst:
            raise inst
        else:
            return dict(reply)

def usage():
    txt = '''\
    $0 set propname {}
    $0 get propname
'''
    print txt

def main():
    n = len(sys.argv)
    if (n !=3) and (n != 4):
        usage()
        exit(250)

    if (n == 4) and (sys.argv[1] != "Set"):
        usage()
        exit(251)
    if (n == 3 ) and (sys.argv[1] not in ["Get"]):
        usage()
        exit(252)

    bus = dbus.SystemBus()
    cli = UCI_cli(bus)
    ret = None
    if sys.argv[1] == "Set":
        args = json.loads(sys.argv[3])
        #args = sys.argv[3]
        ret = cli.Set(sys.argv[2], args)
    elif  sys.argv[1] == "Get":
        ret = cli.Get(sys.argv[2])
    print ret
if __name__ == '__main__':
    main()

