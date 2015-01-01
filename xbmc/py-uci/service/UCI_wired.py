#!/usr/bin/env python
from lib.nm import NM_watcher, Wired
from lib.nm import Settings_IP4, Settings_IP6, Settings_eth

from service import UCI_base
import dbus


class UCI_wired(UCI_base):

    def __init__(self):
        super(UCI_wired, self).__init__()
        self.bus = dbus.SystemBus()
        self.ifname = "eth0"
        self.attrs={
                    "method":"dhcp"
                }

    def Set(self, attrs):
        if "method" in attrs and attrs["method"] == "dhcp":
            try:
                self.auto_mode()
            except Exception as inst:
                print inst
                return {"500": "internal exception"}
        ##TODO else
        return {"200": "OK"}

    def Get(self):
        return self.attrs



    def auto_mode(self):
        w = Wired(self.bus, self.ifname)
        s_ip4 = Settings_IP4("auto")
        s_ip6 = Settings_IP6("auto")
        s_eth = Settings_eth()
        c_id = "Wired connection 1"
        if None == w.get_conn_by_id(c_id):
            w.add_conn(c_id, s_eth, s_ip4, s_ip6)
        else:
            w.update_conn(c_id, s_eth, s_ip4, s_ip6)
        w.active_conn(c_id, self.ifname)

