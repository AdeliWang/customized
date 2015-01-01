#!/usr/bin/env python

import os, sys, subprocess

from lib.nm import NM_watcher, NM_manager
from lib.nm import Settings_IP4, Settings_IP6, Settings_eth

from service import UCI_base
import dbus

class hostapd:

    def config(self, attrs):
        if ("ifname" not in attrs) or \
           ("ssid" not in attrs) or \
           ("passwd" not in attrs) :
           raise Exception("parameter error for hostapd")

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
'''%(attrs["ifname"], attrs["ssid"], attrs["passwd"])

        f_cnf="/etc/hostapd/hostapd.conf"
        fh = open(f_cnf, 'w')
        fh.write(txt)
        fh.close()

    def enable(self):
        subprocess.call("service hostapd restart", shell=True)

    def disable(self):
        subprocess.call("service hostapd stop", shell=True)
        pass

class dnsmasq:
    def __init__(self):
        pass

    def config_dhcpd(self, attrs):
        if ("ifname" not in attrs) or \
           ("gw" not in attrs) or \
           ("start" not in attrs) or \
           ("end" not in attrs) :
           raise Exception("parameter error for dhcpd")

        txt = '''
#domain-needed
all-servers
cache-size=5000
strict-order
interface=%s
bind-interfaces
listen-address=127.0.0.1,%s
dhcp-range=%s,%s
dhcp-option=option:router,%s
# Log to this syslog facility or file. (defaults to DAEMON)
log-facility=/var/log/dnsmasq.log
log-async=20
resolv-file=/etc/resolv.dnsmasq.conf
'''%(attrs["ifname"], attrs["gw"], attrs["start"], attrs["end"], attrs["gw"])

        f_cnf="/etc/dnsmasq.conf"
        fh = open(f_cnf, 'w')
        fh.write(txt)
        fh.close()
        cmd = "ifconfig %s up && ifconfig %s %s"%(attrs["ifname"], attrs["ifname"], attrs["gw"])
        subprocess.call(cmd, shell=True)

    def config_dns(self, dns_list):
        if not isinstance(dns_list, list):
            raise Exception("parameter error for setting dnsmasq's dns")
        txt=""
        for dns in dns_list:
            txt = "%snameserver %s \n"%(txt, dns)

        f_cnf="/etc/resolv.dnsmasq.conf"
        fh = open(f_cnf, 'w')
        fh.write(txt)
        fh.close()
        f="/etc/default/dnsmasq"
        subprocess.call('sed -i "s|^#.*IGNORE_RESOLVCONF=yes|IGNORE_RESOLVCONF=yes|g" %s', shell=True)
        cmd = 'sed -i "s/^dns=/#dns=/g" /etc/NetworkManager/NetworkManager.conf'
        subprocess.call(cmd, shell=True)

    def enable(self):
        subprocess.call("service dnsmasq restart", shell=True)

    def disable(self):
        subprocess.call("service dnsmasq stop", shell=True)

class route:

    def enable(self):
        # Delete NAT rules
        cmd = "iptables -t nat -F"
        # Add NAT rule
        cmd = cmd + " && iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"
        # Enable ip forwoad
        cmd = cmd + " && sysctl net.ipv4.ip_forward=1"
        subprocess.call(cmd, shell=True)

    def disable(self):
        # Delete NAT Setting
        cmd = "iptables -t nat -F"
        # Disable ip forward
        cmd = cmd + "; sysctl net.ipv4.ip_forward=0"
        subprocess.call(cmd, shell=True)


class wifi_sta:
    def __init__(self, bus):
        self.bus = bus
        pass

    def set_parm(self, parms):
        pass

    def start(self):
        subprocess.call("rfkill unblock wifi", shell=True)
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
        subprocess.call("rfkill block wifi", shell=True)

    def stop(self):
        pass

class wifi_ap:
    def __init__(self, bus):
        self.bus = bus

    def set_parm(self, parms):
        if not isinstance(parms, dict):
            raise Exception("parameter invalid for AP mode")

        dnsd = dnsmasq()
        if "dhcpd" in parms:
            dnsd.config_dhcpd(parms["dhcpd"])
        if "dns" in parms:
            dnsd.config_dns(parms["dns"])
        if "hostapd" in parms:
            hapd = hostapd()
            hapd.config(parms["hostapd"])

    def start(self):
        m = NM_manager(self.bus)
        m.enable_wifi(False)
        subprocess.call("rfkill unblock wifi", shell=True)
        d = dnsmasq()
        d.enable()
        r = route()
        r.enable()
        h = hostapd()
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
        self.attrs4ap= {
                    "hostapd": {
                       "ifname": "wlan0",
                       "ssid": "AP-LINK",
                       "passwd": "12345678"
                    },
                    "dns": [
                        "101.226.4.6",
                        "114.114.114.114",
                        "8.8.8.8"
                    ],
                    "dhcpd":{
                        "ifname": "wlan0",
                        "gw": "192.168.15.1",
                        "start": "192.168.15.100",
                        "end": "192.168.15.200"
                    }
                }
        self.attrs4sta = {}

        ##pass

    def Set(self, attrs):
        if "mode" in attrs:
            try:
                if attrs["mode"] == "ap":
                    obj = wifi_ap(self.bus)
                    if "parms" not in attrs:
                        attrs["parms"] = self.attrs4ap
                elif attrs["mode"] == "sta":
                    obj = wifi_stat(self.bus)
                    if "parms" not in attrs:
                        attrs["parms"] = self.attrs4sta
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
