#!/usr/bin/env python
import os, sys
import imp, inspect

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

class UCI_svr(dbus.service.Object):
    OBJ_PATH="/com/livecloud/uci"
    IF_NAME="com.livecloud.uci"

    def __init__(self, bus, object_path=OBJ_PATH):
        dbus.service.Object.__init__(self, bus, object_path)
        path=os.path.split(os.path.realpath(__file__))[0]
        sys.path.append(path + "/..")

    @dbus.service.method(dbus_interface=IF_NAME,in_signature='sa{sv}', out_signature='a{sv}')
    def Set(self, propname, attrs):
        return self.__call("Set", propname, attrs)
        '''
        ret = {}
        module_name = "UCI_%s"%propname
        path=os.path.split(os.path.realpath(__file__))[0]
        fp = None
        try:
            fp, pathname, desc = imp.find_module(module_name, [path+"/../service"])
            module = imp.load_module(module_name, fp, pathname, desc)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and (name == module_name):
                    instance = obj()
                    ret = instance.Set(attrs)
                    break
        except Exception as inst:
            print inst
            ret = {"500": "properties item: %s is unusable"%propname}
        finally:
            if fp:
                fp.close()
        return dbus.Dictionary(ret, signature='sv')
        '''

    @dbus.service.method(dbus_interface=IF_NAME,in_signature='s', out_signature='a{sv}')
    def Get(self, propname):
        return self.__call("Get", propname)

    def __call(self, method, propname, attrs=None):
        ret = {}
        module_name = "UCI_%s"%propname
        path=os.path.split(os.path.realpath(__file__))[0]
        fp = None
        try:
            fp, pathname, desc = imp.find_module(module_name, [path+"/../service"])
            module = imp.load_module(module_name, fp, pathname, desc)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and (name == module_name):
                    instance = obj()
                    if method == "Set":
                        ret = instance.Set(attrs)
                    elif method == "Get":
                        ret = instance.Get()
                    else:
                        raise Exception("unknown method")
                    break
        except Exception as inst:
            print inst
            ret = {"500": "properties item: %s is unusable"%propname}
        finally:
            if fp:
                fp.close()
        return dbus.Dictionary(ret, signature='sv')

    @dbus.service.method(dbus_interface=IF_NAME, in_signature='', out_signature='s')
    def hello(self):
        return 'hello'

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    name = dbus.service.BusName(UCI_svr.IF_NAME, bus)
    the_object = UCI_svr(bus)
    loop = gobject.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
