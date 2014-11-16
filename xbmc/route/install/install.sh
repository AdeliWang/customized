#! /usr/bin/env bash

sudo sed -i "s/^dns=/#dns=/g" /etc/NetworkManager/NetworkManager.conf
sudo cp route-service /etc/init.d/
sudo cp 99-start-wifi-route /etc/NetworkManager/dispatcher.d/
sudo cp dnsmasq.conf /etc/
sudo cp hostapd.conf /etc/hostapd/


f_resolv="/etc/resolv.conf"
[ -f $f_resolv ] && mv $f_resolv  $f_resolv.bak
echo "127.0.0.1" >  $f_resolv 

# Custom configurations can be created for dnsmasq by creating 
# configuration files in /etc/NetworkManager/dnsmasq.d/. 
# For example, to change the size of the DNS cache (which is stored in RAM)
# /etc/NetworkManager/dnsmasq.d/cache
#
# refer to: https://wiki.archlinux.org/index.php/Dnsmasq
# echo "cache-size=1000" >/etc/NetworkManager/dnsmasq.d/cache

# To see if dnsmasq started properly, check the system's journal:
# $ journalctl -u dnsmasq

#refer dnsmasq:  https://help.ubuntu.com/community/Dnsmasq

