#!/usr/bin/env python
from service import UCI_base

class dnsmasq:
    def __init__(self):
        pass

    def config_dhcpd(self, gw, start, end):
        txt = '''
#domain-needed
all-servers
cache-size=5000
strict-order
interface=wlan0
bind-interfaces
listen-address=127.0.0.1,%s
dhcp-range=%s,%s
dhcp-option=option:router,%s
# Log to this syslog facility or file. (defaults to DAEMON)
log-facility=/var/log/dnsmasq.log
log-async=20
resolv-file=/etc/resolv.dnsmasq.conf
'''%(gw, start, end, gw)
        f_cnf="/etc/dnsmasq.conf"
        fh = open(f_cnf, 'w')
        fh.write(txt)
        fh.close()

    def config_dns(self, dns_list)
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

    def start(self):
        subprocess.call("service dnsmasqd restart", shell=True)

    def stop(self):
        subprocess.call("service dnsmasqd stop", shell=True)


class UCI_dns(UCI_base):

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

