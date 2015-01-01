#!/usr/bin/env python

import os, sys, subprocess

class hostapd:

    def config(self, ifce, ssid, passwd):
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
'''%(ifce, ssid, passwd)
        print txt
        #fp = open()


    def enable(self):
        pass

    def disable(self):
        pass




def ut():
    h = hostapd()
    h.config("wlan0","AP_LINK", "12345678")

ut()
