#!/bin/env bash

#apt-get install vnc4server
#apt-get install gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal

xstartup="
#!/bin/sh

export XKL_XMODMAP_DISABLE=1
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS

[ -x /etc/vnc/xstartup ] && exec /etc/vnc/xstartup
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
xsetroot -solid grey
vncconfig -iconic &

gnome-panel &
gnome-settings-daemon &
metacity &
nautilus &
gnome-terminal &
"

mkdir -p ~/.vnc
echo "$xstartup" > ~/.vnc/xstartup
chmod a+x ~/.vnc/xstartup
