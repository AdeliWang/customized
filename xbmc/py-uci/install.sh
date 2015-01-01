#!/usr/bin/env bash

cp ./conf/com.livecloud.uci.service /usr/share/dbus-1/system-services/com.livecloud.uci.service
cp ./conf/com.livecloud.uci.conf    /etc/dbus-1/system.d/com.livecloud.uci.conf

rm -f /usr/local/sbin/uci-*
rm -f /usr/local/bin/uci-*

ln -s $(pwd)/bin/uci-cli.py /usr/local/bin/
ln -s $(pwd)/bin/uci-svr.py /usr/local/sbin/
