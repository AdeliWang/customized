#!/usr/bin/env python

import os, sys, subprocess

from lib.nm import NM_watcher, NM_manager
from lib.nm import Settings_IP4, Settings_IP6, Settings_eth

from service import UCI_base
import dbus

class hostapd:

    def config(self, ifname, ssid, passwd):
        if (ifname == None or ssid == None or passwd == None):
            return

        txt = '''
interface=%s
driver=nl80211
ssid=%s
ignore_broadcast_ssid=0
hw_mode=g
#country_code=GB
channel=6
ieee80211n=1
wme_enabled=1
ht_capab=[HT40+][SHORT-GI-40][DSSS_CCK-40]
auth_algs=1
# Enable WPA2 only (1 for WPA, 2 for WPA2, 3 for WPA + WPA2)
wpa=3
wpa_passphrase=%s
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
'''%(ifname, ssid, passwd)

        f_cnf="/etc/hostapd/hostapd.conf"
        fh = open(f_cnf, 'w')
        fh.write(txt)
        fh.stop()

    def enable(self):
        subprocess.call("service hostapd restart")

    def disable(self):
        subprocess.call("service hostapd stop")
        pass

class route:

    def enable(self):
        # Delete NAT rules
        cmd = "iptables -t nat -F"
        # Add NAT rule
        cmd = cmd + " && iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"
        # Enable ip forwoad
        cmd = cmd + " && sysctl net.ipv4.ip_forward=1"
        subprocess.call(cmd)

    def disable(self):
        # Delete NAT Setting
        cmd = "iptables -t nat -F"
        # Disable ip forward
        cmd = cmd + "; sysctl net.ipv4.ip_forward=0"
        subprocess.call(cmd)


class wifi_sta:
    def __init__(self, bus):
        self.bus = bus
        pass

    def set_parm(self, parms):
        pass

    def start(self):
        subprocess.call("rfkill unblock wifi")
        m = NM_manager(self.bus)
        m.enable_wifi(True)
        #todo ....

    def stop(self):
        pass

class wifi_off:
    def __init__(self, bus):
        self.bus = bus
        pass

    def set_parm(self, parms):
        pass

    def start(self):
        subprocess.call("rfkill block wifi")

    def stop(self):
        pass

class wifi_ap:
    def __init__(self, bus):
        self.bus = bus
        self.ifname = None
        self.ssid = None
        self.passwd = None

    def set_parm(self, parms):
        if not isinstance(parms, dict) or\
           ("ifname" not in parms) or \
           ("ssid" not in parms) or \
           ("passwd" not in parms) :
            raise Exception("parameter invalid for AP mode")

        self.ifname = parms["ifname"]
        self.ssid = parms["ssid"]
        self.passwd = parms["passwd"]

    def start(self):
        m = NM_manager(self.bus)
        m.enable_wifi(False)
        subprocess.call("rfkill unblock wifi")
        r = route()
        r.enable()
        h = hostapd()
        h.config(self.ifname, self.ssid, self.passwd)
        h.enable()

    def stop(self):
        r = route()
        r.stop()
        h = hostapd()
        h.stop()

class UCI_wireless(UCI_base):

    def __init__(self):
        super(UCI_wireless, self).__init__()
        self.bus = dbus.SystemBus()
        self.attrs={
                "mode": "ap",
                "parms": {
                    "ifname": "wlan0",
                    "ssid": "AP_LINK",
                    "passwd": "12345678"
                    }
                }

    def Set(self, attrs):
        if "mode" in attrs and "parms" in attrs:
            try:
                if attrs["mode"] == "ap":
                    obj = wifi_ap(self.bus)
                elif attrs["mode"] == "sta":
                    obj = wifi_stat(self.bus)
                else:
                    obj = wifi_off()
                obj.set_parm(attrs["parms"])
                # cur_mode.stop  ##todo
                obj.start()
            except Exception as inst:
                print inst
                return {"500": "internal exception"}
        ##TODO else
        return {"200": "OK"}

    def Get(self):
        return self.attrs

### EOF
