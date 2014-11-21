#!/usr/bin/env bash

conf_dnsmasq()
{
    txt="    
#domain-needed
all-servers
cache-size=5000
strict-order
interface=wlan0
bind-interfaces
listen-address=127.0.0.1,192.168.15.1
dhcp-range=192.168.15.100,192.168.15.130
dhcp-option=option:router,192.168.15.1
# Log to this syslog facility or file. (defaults to DAEMON)
log-facility=/var/log/dnsmasq.log
log-async=20
resolv-file=/etc/resolv.dnsmasq.conf
"
    f_cnf=/etc/dnsmasq.conf

    echo "$txt"  >  $f_cnf
    txt="
nameserver 101.226.4.6
nameserver 114.114.114.114
nameserver 8.8.8.8
    "
    echo "$txt" >/etc/resolv.dnsmasq.conf 
    f=/etc/default/dnsmasq
    sed -i "s|^#.*IGNORE_RESOLVCONF=yes|IGNORE_RESOLVCONF=yes|g" $f
}

conf_hostapd()
{
    txt="
# Define interface
interface=wlan0
# Select driver
driver=nl80211
# Set access point name
ssid=AP-LINK
ignore_broadcast_ssid=0
# Set access point harware mode to 802.11g
hw_mode=g
# Set WIFI channel (can be easily changed)
#country_code=GB
channel=6
ieee80211n=1
wme_enabled=1
ht_capab=[HT40+][SHORT-GI-40][DSSS_CCK-40]
auth_algs=1
# Enable WPA2 only (1 for WPA, 2 for WPA2, 3 for WPA + WPA2)
wpa=3
wpa_passphrase=03201982
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"
    f_cnf=/etc/hostapd/hostapd.conf
    echo "$txt">$f_cnf
}

###
###  --- MAIN---

echo "install config files"
conf_hostapd
conf_dnsmasq

echo "install NetworkManager hooks"
sed -i "s/^dns=/#dns=/g" /etc/NetworkManager/NetworkManager.conf
cp 99-start-wifi-route /etc/NetworkManager/dispatcher.d/

echo "install route-service"
cp route-service /etc/init.d/

echo "modify rc.local"
grep "#workround" /etc/rc.local > /dev/null 
#[ $? -ne 0 ] && sed -i "s|^exit 0|\( \[\[ \"X\$\(runmode\)\" = "Xdos" \]\] && sleep 30; service route-service restart\) \& #workround\nexit 0|g" /etc/rc.local

[ $? -ne 0 ] && sed -i "s|^exit 0|\(\[\[ \"X\$\(runmode\)\" = \"Xdos\" \]\] \&\& sleep 10 \&\& service route-service restart\) \& \#workround\
    nexit 0|g" /etc/rc.local


##EOF
