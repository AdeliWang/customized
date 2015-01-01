
'''
@file name:   py-nm.py
@function:    wrap networkmanager interface to python class
'''


import os, sys, subprocess
import time
import socket, struct, dbus, uuid


class Util:
    @staticmethod
    def run_cmd(cmd):
        p = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            raise Exception("Failed to run %s"%cmd)
        else:
            return out.strip(" \n")

    @staticmethod
    def ssid_to_python(ssid):
        return ''.join([str(x) for x in ssid])

    @staticmethod
    def abyte_to_python(val):
        return ''.join([str(x) for x in val])

    @staticmethod
    def ssid_to_dbus(ssid):
        if isinstance(ssid, unicode):
            ssid = ssid.encode('utf-8')
        return [dbus.Byte(x) for x in ssid]

    @staticmethod
    def mac_to_python(mac):
        return "%02X:%02X:%02X:%02X:%02X:%02X" % tuple([int(x) for x in mac])

    @staticmethod
    def mac_to_dbus(mac):
        return [dbus.Byte(int(x, 16)) for x in mac.split(':')]

    @staticmethod
    def addrconf_to_python(addrconf):
        addr, netmask, gateway = addrconf
        return [
            Util.addr_to_python(addr),
            netmask,
            Util.addr_to_python(gateway)
        ]

    @staticmethod
    def addrconf_to_dbus(addrconf):
        addr, netmask, gateway = addrconf
        return [
            Util.addr_to_dbus(addr),
            Util.mask_to_dbus(netmask),
            Util.addr_to_dbus(gateway)
        ]

    @staticmethod
    def addr_to_python(addr):
        return socket.inet_ntoa(struct.pack('I', addr))

    @staticmethod
    def addr_to_dbus(addr):
        return dbus.UInt32(struct.unpack('I', socket.inet_aton(addr))[0])

    @staticmethod
    def addr6_to_python(addr):
        return socket.inet_ntop(AF_INET6, struct.pack('I', addr))

    @staticmethod
    def addr6_to_dbus(addr):
        return dbus.UInt32(struct.unpack('I', socket.inet_pton(AF_INET6, addr))[0])

    @staticmethod
    def mask_to_dbus(mask):
        return dbus.UInt32(mask)

    @staticmethod
    def route_to_python(route):
        addr, netmask, gateway, metric = route
        return [
            Util.addr_to_python(addr),
            netmask,
            Util.addr_to_python(gateway),
            socket.ntohl(metric)
        ]

    @staticmethod
    def route_to_dbus(route):
        addr, netmask, gateway, metric = route
        return [
            Util.addr_to_dbus(addr),
            Util.mask_to_dbus(netmask),
            Util.addr_to_dbus(gateway),
            socket.htonl(metric)
        ]

    @staticmethod
    def path_to_dbus(path):
        return dbus.ByteArray("file://" + path + "\0")

    @staticmethod
    def dbus_to_py(val, k=None):
        if isinstance(val, dbus.String):
            return str(val)
        #if isinstance(val, dbus.ByteArray): #seem to be useless
        #    return "".join([str(x) for x in val])
        if isinstance(val, (dbus.Array, list, tuple)):
            if not len(val):
                return []
            elif isinstance(val[0], dbus.Byte):
                if k == "mac-address":
                    return Util.mac_to_python(val)
                else:
                    return Util.abyte_to_python(val)
            else:
                return [Util.dbus_to_py(x) for x in val]
        if isinstance(val, (dbus.Dictionary, dict)):
            return dict([(Util.dbus_to_py(x), Util.dbus_to_py(y)) for x,y in val.items()])
        #if isinstance(val, (dbus.Signature, dbus.String)):
        #    return unicode(val)
        if isinstance(val, dbus.Boolean):
            return bool(val)
        if isinstance(val, (dbus.Int16, dbus.UInt16, dbus.Int32, dbus.UInt32, dbus.Int64, dbus.UInt64)):
            return int(val)
        if isinstance(val, dbus.Byte):
            return bytes([int(val)])
        return val

    @staticmethod
    def py_to_dbus(val):
        #print type(val)
        if val == None:
            return val
        else:
            dbus_simple_type = list([   dbus.Int16, dbus.UInt16, \
                                        dbus.Int32, dbus.UInt32, \
                                        dbus.Int64, dbus.UInt64, \
                                        dbus.Boolean, dbus.Double, dbus.Byte])
            if type(val) in [str, unicode, dbus.String]:
                return dbus.String(val)
            elif type(val) in [list, set, tuple, dbus.Array]:
                val = list(val)
                for i in range(len(val)):
                    val[i] = Util.py_to_dbus(val[i])
                return dbus.Array(val, signature = 'v')
            elif type(val) in [dict, dbus.Dictionary]:
                for sub_key, sub_val in val.iteritems():
                    val[sub_key] = Util.py_to_dbus(sub_val)
                return dbus.Dictionary(val, signature = 'sv')
            elif isinstance(val, int):
                return dbus.Int32(val)
            elif isinstance(val, bool):
                return dbus.Boolean(val)
            elif isinstance(val, float):
                return dbus.Double(val)
            elif type(val) in dbus_simple_type:
                return val
            else:
                raise Exception("ERROR: Unsupported native type for convert to dbus one")

#####################################################################
##
## settings class
##
class Settings(object):
    def __init__(self):
        self.settings = {}

    def update_settings(self, settings):
        self.settings.update(settings)

    def to_dbus(self):
        #return Util.py_to_dbus(self.settings)
        return dbus.Dictionary(self.settings)

    @staticmethod
    def dbus_to_py(dbus_set):
        ret = {}
        for k in dbus_set:
            k_str = str(k)
            ret[k_str] = Util.dbus_to_py(dbus_set[k_str], k_str)
        return ret

class Settings_conn(Settings):
    def __init__(self, c_id, ifname, t, ac=True):
        if t not in ["eth", "wifi"]:
            raise Exception("not support")

        types = {"eth": "802-3-ethernet", "wifi": "802-11-wireless"}
        self.settings = {
            "name": c_id,
            "id": c_id,
            "uuid": str(uuid.uuid4()),
            "type": types[t],
            "interface-name": ifname,
            "autoconnect": ac
        }

class Settings_eth(Settings):
    def __init__(self, duplex = "full",speed = 0, mtu = 0):
        self.settings = {
            "duplex": duplex,
            "speed" : speed,
            "mtu"   : mtu
        }

class Settings_wireless(Settings):
    def __init__(self, ssid = "", mode = None, security = None):
        self.settings = {
            "ssid": dbus.ByteArray(ssid),
            "mode": mode
        }
        if security:
            self.settings["security"] = security

class Settings_wireless_security(Settings):
    def __init__(self, key_mgmt, auth_alg=None, proto=None, pairwise=None):
        self.settings = {
            "key-mgmt": key_mgmt
        }
        if auth_alg:
            self.settings["auth-alg"] = auth_alg
        if proto:
            self.settings["proto"] = proto
        if pairwise:
            self.settings["pairwise"] = pairwise

class Settings_8021x(Settings):
    def __init__(self, eap):
        self.settings = {
            "eap": eap
        }

#
# CLASS IP4
class IP4Addr():
    def __init__(self, ip_str = None, mask = None, gw = None):
        if ip_str and mask and gw:
            self.ip_info = [[ip_str, mask, gw]]
        elif (not ip_str) and (not mask) and (not gw):
            self.ip_info = []
        else:
            raise Exception("parameter error")

    def add_ele(self, ip_str, mask, gw):
        self.ip_info.append([ip_str, mask, gw])

    def replace(self, ip_str, mask, gw):
        self.ip_info = [[ip_str, mask, gw]]

    def clean(self):
        self.ip_info = []

    @staticmethod
    def verify(address):
        try:
            addr= socket.inet_pton(socket.AF_INET, address)
        except AttributeError:
            try:
                addr= socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error: # not a valid address
            return False
        return True


    @staticmethod
    def ip_to_int(ip_str):
        if IP4Addr.verify(ip_str) == False:
            raise Exception("invalid ipv4 address: %s"%ip_str)
        return struct.unpack("=I", socket.inet_aton(ip_str))[0]

    @staticmethod
    def int_to_ip(ip_int):
        return socket.inet_ntoa(struct.pack("=I", ip_int))

    @staticmethod
    def ele_to_dbus(ip_str, mask, gw):
        return  dbus.Array([IP4Addr.ip_to_int(ip_str),
                            dbus.UInt32(mask),
                            IP4Addr.ip_to_int(gw)],
                           signature=dbus.Signature('u'))

    def to_dbus(self):
        dbus_ip = dbus.Array([], signature=dbus.Signature('au'))
        for i in self.ip_info:
            dbus_ip.append(IP4Addr.ele_to_dbus(i[0], i[1], i[2]))
        return dbus_ip

    @staticmethod
    def dbus_to_py(dbus_ip):
        ret = []
        for i in dbus_ip:
            ip = IP4Addr.int_to_ip(i[0])
            mask = int(i[1])
            gw = IP4Addr.int_to_ip(i[2])
            ret.append([ip, mask, gw])
        return ret

class IP4Dns():
    def __init__(self, str_ip=None):
        if str_ip:
            self.dns_info = [str_ip]
        else:
            self.dns_info = []

    def add_ele(self, str_ip):
        self.dns_info.append(str_ip)

    def clean(self):
        self.dns_info = []

    def to_dbus(self):
        dbus_dns = dbus.Array([], signature=dbus.Signature('u'))
        for i in self.dns_info:
            dbus_dns.append(IP4Addr.ip_to_int(i))
        return dbus_dns

    @staticmethod
    def dbus_to_py(dbus_dns):
        ret = []
        for i in dbus_dns:
            ret.append(IP4Addr.int_to_ip(i))
        return ret


class IP4Route():
    def __init__(self, ip_str = None, mask = None, gw = None, metric = None):
        if ip_str and mask and gw and metric:
            self.route_info = [[ip_str, mask, gw, metric]]
        elif (not ip_str) and (not mask) and (not gw) and (not metric):
            self.route_info = []
        else:
            raise Exception("parameter error")


    def add_ele(self, ip_str, mask, gw, metric):
        self.route_info.append([ip_str, mask, gw, metric])


    def clean(self):
        self.route_info = []

    @staticmethod
    def ele_to_dbus(ip_str, mask, gw, metric):
        return dbus.Array([
            IP4Addr.ip_to_int(ip_str),
            dbus.UInt32(mask),
            IP4Addr.ip_to_int(gw),
            dbus.UInt32(metric)],
            signature=dbus.Signature('u'))


    def to_dbus(self):
        dbus_r = dbus.Array([], signature=dbus.Signature('au'))
        for i in self.route_info:
            dbus_r.append(IP4Route.ele_to_dbus(i[0], i[1], i[2], i[3]))
        return dbus_r

    @staticmethod
    def dbus_to_py(dbus_r):
        ret = []
        for i in dbus_r:
            ip = IP4Addr.int_to_ip(i[0])
            mask = int(i[1])
            gw = IP4Addr.int_to_ip(i[2])
            metric = int(i[3])
            ret.append([ip, mask, gw, metric])
        return ret


#
# CLASS IP6
class IP6Addr():
    def __init__(self, ip_str = None, prefix = None, gw = None):
        if ip_str and prefix and gw:
            self.ip_info = [[ip_str, prefix, gw]]
        elif (not ip_str) and (not prefix) and (not gw):
            self.ip_info = []
        else:
            raise Exception("parameter error")

    def add_ele(self, ip_str, prefix, gw):
        self.ip_info.append([ip_str, prefix, gw])

    def replace(self, ip_str, prefix, gw):
        self.ip_info = [[ip_str, prefix, gw]]

    def clean(self):
        self.ip_info = []


    @staticmethod
    def verify(address):
        try:
            addr= socket.inet_pton(socket.AF_INET6, address)
        except socket.error: # not a valid address
            return False
        return True

    @staticmethod
    def ip_to_py(addr):
        if len(addr) != 16:
            raise Exception("invalid v6 addr")
        return socket.inet_ntop(socket.AF_INET6,
                struct.pack('!16B',
                    addr[0], addr[1], addr[2], addr[3],
                    addr[4], addr[5], addr[6], addr[7],
                    addr[8], addr[9], addr[10], addr[11],
                    addr[12], addr[13], addr[14], addr[15]
                ))

    @staticmethod
    def ip_to_dbus(addr):
        if IP6Addr.verify(addr) == False:
            raise Exception("invalid ipv6 address: %s"%addr)
        ret = dbus.Array([], signature=dbus.Signature('y'))
        res = struct.unpack('!16B', socket.inet_pton(socket.AF_INET6, addr))
        for x in res:
            ret.append(dbus.Byte(int(x)))
        return ret
    '''
    @staticmethod
    def ip_to_dbus(addr):
        return dbus.ByteArray(addr)
    '''

    @staticmethod
    def ele_to_dbus(ip_str, prefix, gw):
        dip = IP6Addr.ip_to_dbus(ip_str)
        dgw = IP6Addr.ip_to_dbus(gw)
        return dbus.Struct((dip, int(prefix), dgw))

    def to_dbus(self):
        dbus_ip = dbus.Array([], signature=dbus.Signature('(ayuay)'))
        for i in self.ip_info:
            dbus_ip.append(IP6Addr.ele_to_dbus(i[0], i[1], i[2]))
        return dbus_ip

    @staticmethod
    def dbus_to_py(dbus_ip):
        ret = []
        for i in dbus_ip:
            ip = IP6Addr.ip_to_py(i[0])
            prefix = int(i[1])
            gw = IP6Addr.ip_to_py(i[2])
            ret.append([ip, prefix, gw])
        return ret


class IP6Dns():
    def __init__(self, str_ip=None):
        if str_ip:
            self.dns_info = [str_ip]
        else:
            self.dns_info = []

    def add_ele(self, str_ip):
        self.dns_info.append(str_ip)

    def clean(self):
        self.dns_info = []

    def to_dbus(self):
        dbus_dns = dbus.Array([], signature=dbus.Signature('u'))
        for i in self.dns_info:
            dbus_dns.append(IP6Addr.ip_to_dbus(i))
        return dbus_dns

    @staticmethod
    def dbus_to_py(dbus_dns):
        ret = []
        for i in dbus_dns:
            ret.append(IP6Addr.ip_to_py(i))
        return ret


class IP6Route():
    def __init__(self, ip_str = None, prefix = None, gw = None, metric = None):
        if ip_str and prefix and gw and metric:
            self.route_info = [[ip_str, prefix, gw, metric]]
        elif (not ip_str) and (not prefix) and (not gw) and (not metric):
            self.route_info = []
        else:
            raise Exception("parameter error")


    def add_ele(self, ip_str, prefix, gw, metric):
        self.route_info.append([ip_str, prefix, gw, metric])


    def clean(self):
        self.route_info = []

    @staticmethod
    def ele_to_dbus(ip_str, prefix, gw, metric):
        return (IP6Addr.ip_to_dbus(ip_str),
                dbus.UInt32(prefix),
                IP6Addr.ip_to_dbus(gw),
                dbus.UInt32(metric))


    def to_dbus(self):
        dbus_r = dbus.Array([], signature=dbus.Signature('au'))
        for i in self.route_info:
            dbus_r.append(IP6Route.ele_to_dbus(i[0], i[1], i[2], i[3]))
        return dbus_r

    @staticmethod
    def dbus_to_py(dbus_r):
        ret = []
        for i in dbus_r:
            ip = IP6Addr.ip_to_py(i[0])
            prefix = int(i[1])
            gw = IP6Addr.ip_to_py(i[2])
            metric = int(i[3])
            ret.append([ip, prefix, gw, metric])
        return ret


class Settings_IP(object):
    def __init__(self, m, ipxaddr=None, ipxdns=None, ipxroute=None):
        self.method = m  #str
        self.ip = ipxaddr  #obj
        self.dns = ipxdns  #obj
        self.routes = ipxroute #obj

    def get_method(self):
        return self.method

    def get_ip(self):
        return self.ip

    def get_dns(self):
        return self.dns

    def to_dbus(self):
        return self.settings

    def set_method(self, method):
        self.method = method
        if method in ["auto","link-local", "manual", "shared", "disabled", "ignore"]:
            self.settings = dbus.Dictionary({'method': method})


class Settings_IP4(Settings_IP):
    def __init__(self, m, ip4addr=None, ip4dns=None, ip4route=None):
        if  m not in ["auto","link-local", "manual", "shared", "disabled"]:
            raise Exception("unknown method")

        self.method = m  #str
        self.ip4 = ip4addr  #obj
        self.dns = ip4dns  #obj
        self.routes = ip4route #obj

    def add_ip(self, ip_str, mask, gw):
        if self.ip4:
            self.ip4.add_ele(ip_str, mask, gw)
        else:
            self.ip4 = IP4Addr(ip_str, mask, gw)

    def clean_ip(self):
        self.ip4.clean()

    def replace_ip(self, ip_str, mask, gw):
        if self.ip4:
            self.ip4.replace(ip_str, mask, gw)
        else:
            self.ip4 = IP4Addr(ip_str, mask, gw)


    def add_dns(self, ip_str):
        if self.dns:
            self.dns.add_ele(ip_str)
        else:
            self.dns = IP4Dns(ip_str)

    def clean_dns(self):
        self.dns.clean()

    def add_route(self, ip_str, mask, gw, metric):
        if self.routes:
            self.routes.add_ele(ip_str, mask, gw, metric)
        else:
            self.routes = IP4Route(ip_str, mask, gw, metric)

    def clean_route(self):
            self.routes.clean()

    def to_dbus(self):
        settings = {}
        if self.method in ["auto", "disable"]:
            settings['method'] =  self.method
        elif self.method in ["link-local", "manual", "shared"]:
            if not isinstance(self.ip4, IP4Addr):
                raise Exception("ip4 addr not set")

            settings["method"] = self.method
            if  self.ip4 :
                settings["addresses"] = self.ip4.to_dbus()
        else:
            raise Exception("unknown method")


        if self.method in ["manual", "auto"]:
            if self.dns :
                settings["dns"] = self.dns.to_dbus()

            if self.routes :
                settings["routes"] = self.routes.to_dbus()

        return dbus.Dictionary(settings)

    @staticmethod
    def dbus_to_py(dbus_s_ip4):
        ret = {}
        #keys = ["method", "addresses", "dns", "routes"]
        if "method" in dbus_s_ip4:
            ret["method"] = str(dbus_s_ip4["method"])
        if "addresses" in dbus_s_ip4:
            ret["addresses"] = IP4Addr.dbus_to_py(dbus_s_ip4["addresses"])
        if "dns" in dbus_s_ip4:
            ret["dns"] = IP4Dns.dbus_to_py(dbus_s_ip4["dns"])
        if "routes" in dbus_s_ip4:
            ret["routes"] = IP4Route.dbus_to_py(dbus_s_ip4["routes"])
        return ret

class Settings_IP6(Settings_IP):
    def __init__(self, m, addr=None, dns=None, routes=None):
        if  m not in ["auto", "dhcp", "link-local", "manual", "ignore"]:
            raise Exception("unknown method")

        self.method = m  #str
        self.addr = addr  #obj
        self.dns = dns  #obj
        self.routes = routes #obj

    def add_ip(self, ip_str, prefix, gw):
        if self.addr:
            self.addr.add_ele(ip_str, prefix, gw)
        else:
            self.addr = IP6Addr(ip_str, prefix, gw)

    def clean_ip(self):
        self.addr.clean()

    def replace_ip(self, ip_str, prefix, gw):
        if self.addr:
            self.addr.replace(ip_str, prefix, gw)
        else:
            self.addr = IP6Addr(ip_str, prefix, gw)


    def add_dns(self, ip_str):
        if self.dns:
            self.dns.add_ele(ip_str)
        else:
            self.dns = IP6Dns(ip_str)

    def clean_dns(self):
        self.dns.clean()

    def add_route(self, ip_str, prefix, gw, metric):
        if self.routes:
            self.routes.add_ele(ip_str, prefix, gw, metric)
        else:
            self.routes = IP6Route(ip_str, prefix, gw, metric)

    def clean_route(self):
            self.routes.clean()

    def to_dbus(self):
        settings = {}
        if self.method in ["auto", "dhcp", "ignore"]:
            settings['method'] =  self.method
        elif self.method in ["link-local", "manual", "shared"]:
            if not isinstance(self.addr, IP6Addr):
                raise Exception("ip6 addr not set")

            settings["method"] = self.method
            if  self.addr :
                settings[dbus.String("addresses")] = self.addr.to_dbus()
        else:
            raise Exception("unknown method")


        if self.method in ["manual", "auto", "dhcp"]:
            if self.dns :
                settings["dns"] = self.dns.to_dbus()

            if self.routes :
                settings["routes"] = self.routes.to_dbus()

        return dbus.Dictionary(settings)

    @staticmethod
    def dbus_to_py(dbus_s_ip6):
        ret = {}
        #keys = ["method", "addresses", "dns", "routes"]
        if "method" in dbus_s_ip6:
            ret["method"] = str(dbus_s_ip6["method"])
        if "addresses" in dbus_s_ip6:
            ret["addresses"] = IP6Addr.dbus_to_py(dbus_s_ip6["addresses"])
        if "dns" in dbus_s_ip6:
            ret["dns"] = IP6Dns.dbus_to_py(dbus_s_ip6["dns"])
        if "routes" in dbus_s_ip6:
            ret["routes"] = IP6Route.dbus_to_py(dbus_s_ip6["routes"])
        return ret


#####################################################################
##
## Dbus Interface class
##
class NM_base(object):
    #bus = dbus.SystemBus()
    service = 'org.freedesktop.NetworkManager'
    prop = "org.freedesktop.DBus.Properties"
    #obj_path = None

    def __init__(self, bus):
        self.bus = bus

    def get_prop(self, path, name):
        pxy = self.bus.get_object(self.service, path)
        iface = dbus.Interface(pxy, self.prop)
        return iface.GetAll(name)

class NM_manager(NM_base):
    def __init__(self, bus):
        super(NM_manager, self).__init__(bus)
        self.name = 'org.freedesktop.NetworkManager'
        self.path = '/org/freedesktop/NetworkManager'
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    '''
    NM_STATE_UNKNOWN = 0
    Networking state is unknown.
    NM_STATE_ASLEEP = 10
    Networking is inactive and all devices are disabled.
    NM_STATE_DISCONNECTED = 20
    There is no active network connection.
    NM_STATE_DISCONNECTING = 30
    Network connections are being cleaned up.
    NM_STATE_CONNECTING = 40
    A network device is connecting to a network and there is no other available network connection.
    NM_STATE_CONNECTED_LOCAL = 50
    A network device is connected, but there is only link-local connectivity.
    NM_STATE_CONNECTED_SITE = 60
    A network device is connected, but there is only site-local connectivity.
    NM_STATE_CONNECTED_GLOBAL = 70
    A network device is connected, with global network connectivity.
    '''

    def get_status(self):
        #self.iface.Get(self.name, "State")
        ret={}
        cmd = "pgrep NetworkManager |wc -l"
        res = int(Util.run_cmd(cmd))
        ret["running"] = (False if res == 0 else True)

        p = self.get_prop(self.path, self.name)
        #keys = ["NetworkingEnabled", "WirelessEnabled",
        #        "State", "WirelessHardwareEnabled", "ActiveConnections"]
        keys = ["NetworkingEnabled", "WirelessEnabled", "WirelessHardwareEnabled"]
        for k in keys:
            if k in p:
                ret[k] = (True if p[k] else False)

        if "State" in p:
            ret["State"] = int(p["State"])
        return ret

    def get_all_active_conn_path(self):
        p_iface = dbus.Interface(self.proxy, "org.freedesktop.DBus.Properties")
        paths = p_iface.Get(self.name, "ActiveConnections")
        ret = []
        for p in paths:
            ret.append(str(p))
        return ret

    def get_all_active_conn_info(self):
        paths = self.get_all_active_conn_path()
        ret = []
        for p in paths:
            ac = NM_active_conn(self.bus, p)
            info = {}
            info["settings"] = ac.get_conn_info()
            info["devs"] = ac.get_all_dev_info()
            ret.append(info)
        return ret


    def get_active_conn_by_id(self, c_id):
        paths = self.get_all_active_conn_path()
        ret = {}
        for p in paths:
            ac = NM_active_conn(self.bus, p)
            settings = ac.get_conn_info()
            if settings["connection"]["id"] != c_id:
                continue

            info = {}
            info["settings"] = settings
            info["devs"] = ac.get_all_dev_info()
            ret["path"] = p
            ret["info"] = info
        return (ret if ret else None)

    def get_active_conn_by_ifname(self, ifname):
        paths = self.get_all_active_conn_path()
        ret = {}
        for p in paths:
            ac = NM_active_conn(self.bus, p)
            devs = ac.get_all_dev_info()
            found = False
            for d in devs:
                if ("ifname" in d) and (d["ifname"] == ifname):
                    found = True
                    break
            if not found:
                continue

            info = {}
            info["settings"] = ac.get_conn_info()
            info["devs"] = devs
            ret["path"] = p
            ret["info"] = info
        return (ret if ret else None)


    def get_all_dev_path(self):
        paths = self.iface.GetDevices()
        ret = []
        for p in paths:
            ret.append(str(p))
        return ret

    def get_all_dev_info(self):
        paths = self.get_all_dev_path()
        ret = []
        for p in paths:
            dev = NM_dev(self.bus, p)
            ret.append(dev.get_info())
        return ret

    def get_dev_by_ifname(self, ifname):
        paths = self.get_all_dev_path()
        ret = {}
        for p in paths:
            dev = NM_dev(self.bus, p)
            info = dev.get_info()
            if info['ifname'] == ifname:
                ret["path"] = p
                ret["info"] = info
                break
        return (ret if ret else None)


    def enable_network(self, v):
        if v not in [True, False]:
            raise Exception("parameter error")

        p_iface = dbus.Interface(self.proxy, "org.freedesktop.DBus.Properties")
        res = (True if p_iface.Get(self.name, "NetworkingEnabled") else False)
        #res = self.get_status()["NetworkingEnabled"]
        if res != v:
            self.iface.Enable(v)

    def enable_wifi(self, v):
        if v not in [True, False]:
            raise Exception("parameter error")
        p_iface = dbus.Interface(self.proxy, "org.freedesktop.DBus.Properties")
        res =(True if p_iface.Get(self.name, "WirelessEnabled") else False)
        if res != v:
            p_iface.Set(self.name, "WirelessEnabled", v)
            #print "Set done"


class NM_ap(NM_base):
    def __init__(self, bus, path):
        super(NM_ap, self).__init__(bus)
        self.name = 'org.freedesktop.NetworkManager.AccessPoint'
        self.path = path
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    def get_info(self):
        ret = {}
        props = self.get_prop(self.path, self.name)
        if "Flags" in props:
            ret["Flags"]  = int(props["Flags"])
        if "WpaFlags" in props :
            ret["WpaFlags"] = int(props["WpaFlags"])
        if "RsnFlags" in props:
            ret["RsnFlags"]  = int(props["RsnFlags"])
        if "Ssid" in props :
            ret["Ssid"] = Util.ssid_to_python(props["Ssid"])
        if "Frequency" in props:
            ret["Frequency"]  = int(props["Frequency"])
        if "HwAddress" in props :
            ret["HwAddress"] = str(props["HwAddress"])
        if "Mode" in props:
            ret["Mode"]  = str(props["Mode"])
        if "MaxBitrate" in props :
            ret["MaxBitrate"] = int(props["MaxBitrate"])
        if "Strength" in props:
            ret["Strength"]  = int(props["Strength"])
        return ret

class NM_dev(NM_base):
    STATE = {
        0 : "DEVICE_STATE_UNKNOWN",
        10 : "DEVICE_STATE_UNMANAGED",
        20 : "DEVICE_STATE_UNAVAILABLE",
        30 : "DEVICE_STATE_DISCONNECTED",
        40 : "DEVICE_STATE_PREPARE",
        50 : "DEVICE_STATE_CONFIG",
        60 : "DEVICE_STATE_NEED_AUTH",
        70 : "DEVICE_STATE_IP_CONFIG",
        80 : "DEVICE_STATE_IP_CHECK",
        90 : "DEVICE_STATE_SECONDARIES",
        100 : "DEVICE_STATE_ACTIVATED",
        110 : "DEVICE_STATE_DEACTIVATING",
        120 : "DEVICE_STATE_FAILED",
    }
    def __init__(self, bus, path):
        super(NM_dev, self).__init__(bus)
        self.name = "org.freedesktop.NetworkManager.Device"
        self.path = path
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)
        self.devtypes = {
            1: "Ethernet",
            2: "WiFi",
            5: "Bluetooth",
            6: "OLPC",
            7: "WiMAX",
            8: "Modem",
            9: "InfiniBand",
            10: "Bond",
            11: "VLAN",
            12: "ADSL",
            13: "Bridge",
            14: "Generic",
            15: "Team"
        }


        self.states = {
            0: "Unknown",
            10: "Unmanaged",
            20: "Unavailable",
            30: "Disconnected",
            40: "Prepare",
            50: "Config",
            60: "Need Auth",
            70: "IP Config",
            80: "IP Check",
            90: "Secondaries",
            100: "Activated",
            110: "Deactivating",
            120: "Failed"
        }

    def disconnect(self):
        try:
            self.iface.Disconnect()
        except Exception as inst:
            raise inst

    def set_autoconnect(self, auto):
        p_iface = dbus.Interface(self.proxy, "org.freedesktop.DBus.Properties")
        old = bool(p_iface.Get(self.name, "Autoconnect"))
        if old != auto:
            p_iface.Set(self.name, "Autoconnect", dbus.Boolean(auto))

    def get_info(self):
        dev = {}
        props = self.get_prop(self.path, self.name)
        dev['ifname'] = str(props['Interface'])
        dev['type'] =  self.devtypes[props['DeviceType']]
        dev['state'] = self.states[props['State']]
        if "Autoconnect" in props:
            dev["autoconnect"] = bool(props["Autoconnect"])
        hw = self.__get_hw_info(int(props['DeviceType']))
        dev["hw"] = hw
        if props['State'] == 100:
            if props['Ip4Config'].startswith("/org/freedesktop/NetworkManager/IP4Config/"):
                ip4 = NM_IP4Config(self.bus, props['Ip4Config'])
                dev["IP4"] = ip4.get_info()
            if props['Ip6Config'].startswith("/org/freedesktop/NetworkManager/IP6Config/"):
                ip6 = NM_IP6Config(self.bus, props['Ip6Config'])
                dev["IP6"] = ip6.get_info()
        else:
            dev["IP4"] = {}
            dev["IP6"] = {}
        return dev

    def __get_hw_info(self, t):
        if t == 1:
            w = NM_wired(self.bus, self.path)
        elif t == 2:
            w = NM_wireless(self.bus, self.path)
        else:
            raise Exception("parameter error")

        return w.get_info()

class NM_wired(NM_base):
    def __init__(self, bus, path):
        super(NM_wired, self).__init__(bus)
        self.path = path
        self.name = "org.freedesktop.NetworkManager.Device.Wired"
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    def get_info(self):
        ret = {}
        props = self.get_prop(self.path, self.name)
        if "HwAddress" in props:
            ret["HwAddress"]  = str(props["HwAddress"])
        if "Speed" in props :
            ret["Speed"] = int(props["Speed"])
        if "Carrier" in props :
            ret["plugin"] = (True if props["Carrier"] else False)
        return ret

class NM_wireless(NM_base):
    def __init__(self, bus, path):
        super(NM_wireless, self).__init__(bus)
        self.path = path
        self.name = "org.freedesktop.NetworkManager.Device.Wireless"
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    def get_info(self):
        ret = {}
        props = self.get_prop(self.path, self.name)
        if "HwAddress" in props:
            ret["HwAddress"]  = str(props["HwAddress"])
        if "PermHwAddress" in props:
            ret["PermHwAddress"]  = str(props["PermHwAddress"])
        if "Mode" in props :
            ret["Mode"] = int(props["Mode"])
        if "Bitrate" in props :
            ret["Bitrate"] = int(props["Bitrate"])
        if "ActiveAccessPoint" in props :
            ret["ActiveAccessPoint"] = str(props["ActiveAccessPoint"])
        if "WirelessCapabilities" in props :
            ret["WirelessCapabilities"] = int(props["WirelessCapabilities"])
        return ret

    def get_all_ap_path(self):
        aps = self.iface.GetAccessPoints()
        ret = []
        for i in aps:
            ret.append(str(i))
        return ret

    def get_all_ap_info(self):
        paths = self.get_all_ap_path()
        ret = []
        for p in paths:
            ap = NM_ap(self.bus, p)
            ret.append(ap.get_info())
        return ret

    def get_ap_by_id(self, _id):
        paths = self.get_all_ap_path()
        for p in paths:
            ap = NM_ap(self.bus, p)
            ap_info = ap.get_info()
            if ap_info['Ssid'] == _id:
                return ap_info
        return None

    def request_scan(self, opt):
        self.iface.RequestScan(opt)

class NM_IP4Config(NM_base):
    def __init__(self, bus, path):
        super(NM_IP4Config, self).__init__(bus)
        self.path = path
        self.name = "org.freedesktop.NetworkManager.IP4Config"
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    def get_info(self):
        props = self.get_prop(self.path, self.name)
        cb = {
                "Addresses", IP4Addr,
                "Nameservers", IP4Dns,
                "Routes", IP4Route
             }
        ret = {}
        for key in props.keys():
            k = str(key)
            if k == "Addresses":
                ret[k] = IP4Addr.dbus_to_py(props[k])
            elif k == "Nameservers":
                ret[k] = IP4Dns.dbus_to_py(props[k])
            elif k ==  "Routes":
                ret[k] = IP4Route.dbus_to_py(props[k])
        return ret

class NM_IP6Config(NM_base):
    def __init__(self, bus, path):
        super(NM_IP6Config, self).__init__(bus)
        self.path = path
        self.name = "org.freedesktop.NetworkManager.IP6Config"
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    def get_info(self):
        props = self.get_prop(self.path, self.name)
        cb = {
                "Addresses", IP6Addr,
                "Nameservers", IP6Dns,
                "Routes", IP6Route
             }
        ret = {}
        for key in props.keys():
            k = str(key)
            if k == "Addresses":
                ret[k] = IP6Addr.dbus_to_py(props[k])
            elif k == "Nameservers":
                ret[k] = IP6Dns.dbus_to_py(props[k])
            elif k ==  "Routes":
                ret[k] = IP6Route.dbus_to_py(props[k])
        return ret


class NM_settings(NM_base):
    def __init__(self, bus):
        super(NM_settings, self).__init__(bus)
        self.path = "/org/freedesktop/NetworkManager/Settings"
        self.name = "org.freedesktop.NetworkManager.Settings"
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    def get_all_conn_path(self):
        conns = self.iface.ListConnections()
        ret = []
        for i in conns:
            ret.append(str(i))

        return ret

    def get_all_conn_info(self):
        paths = self.get_all_conn_path()
        ret = []
        for p in paths:
            c = NM_connection(self.bus, p)
            set = c.get_settings()
            if set:
                ret.append(set)
        return ret

    def get_conn_by_id(self, _id):
        o_name = "org.freedesktop.NetworkManager.Settings.Connection"
        cs = self.get_all_conn_path()
        c_target = {}
        for c in cs:
            con_proxy = self.bus.get_object(self.service, c)
            con_if = dbus.Interface(con_proxy, o_name)
            config = con_if.GetSettings()['connection']
            if str(config['id']) == _id :
                c_target["path"] = c
                keys = ["name", "id", "uuid", "interface-name", "type"]
                for k in keys:
                    if k in config:
                        c_target[k] = str(config[k])
                break
        return (c_target if c_target else None)


    def add_conn(self, conf):
        if not isinstance(conf, dbus.Dictionary):
            raise Exception("parameter error")

        try:
            return self.iface.AddConnection(conf)
        except Exception as inst:
            raise inst

    def update_conn(self, _id, conf):
        res = self.get_conn_by_id(_id)
        if res == None:
            raise Exception("the connection [id:%s] NOT exist"%_id)
        path = res["path"]
        c = NM_connection(self.bus, path)
        c.update_conn(conf)

    def del_conn(self, _id):
        res = self.get_conn_by_id(_id)
        if res == None:
            raise Exception("the connection [id:%s] NOT exist"%_id)
        path = res["path"]
        c = NM_connection(self.bus, path)
        c.del_conn()

class NM_connection(NM_base):
    def __init__(self, bus, o_path):
        super(NM_connection, self).__init__(bus)
        self.name = "org.freedesktop.NetworkManager.Settings.Connection"
        self.path = o_path
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    def get_nm_settings(self):
        config = self.iface.GetSettings()
        try:
            secrets = self.iface.GetSecrets("802-1x")
            for setting in secrets:
                for key in secrets[setting]:
                    config["802-1x"][key] = secrets[setting][key]
        except Exception:
            pass

        return config

    def get_settings(self):
        config = self.get_nm_settings()

        con_info = {}
        if "802-3-ethernet" in config:
            con_info["802-3-ethernet"] = Settings_eth.dbus_to_py(config["802-3-ethernet"])
        if "802-11-wireless" in config:
            con_info["802-11-wireless"] = Settings_wireless.dbus_to_py(config["802-11-wireless"])
        if "802-11-wireless-security" in config:
            con_info["802-11-wireless-security"] = Settings_wireless_security.dbus_to_py(config["802-11-wireless-security"])
        if "802-1x" in config:
            con_info["802-1x"] = Settings_8021x.dbus_to_py(config["802-1x"])
        ## TODO
        if "connection" in config:
            con_info["connection"] = Settings_conn.dbus_to_py(config["connection"])
        if "ipv4" in config:
            con_info["ipv4"] = Settings_IP4.dbus_to_py(config["ipv4"])
        if "ipv6" in config:
            con_info["ipv6"] = Settings_IP6.dbus_to_py(config["ipv6"])

        return (con_info if con_info else None)

    def update_conn(self, conf):
        if not isinstance(conf, dbus.Dictionary):
            raise Exception("parameter error")

        try:
            self.iface.Update(conf)
        except Exception as inst:
            raise inst

    def del_conn(self):
        try:
            self.iface.Delete()
        except Exception as inst:
            raise inst

class NM_active_conn(NM_base):
    def __init__(self, bus, path):
        super(NM_active_conn, self).__init__(bus)
        self.path = path
        self.name = "org.freedesktop.NetworkManager.Connection.Active"
        self.proxy = self.bus.get_object(self.service, self.path)
        self.iface = dbus.Interface(self.proxy, self.name)

    def get_conn_info(self):
        p_iface = dbus.Interface(self.proxy, "org.freedesktop.DBus.Properties")
        path = p_iface.Get(self.name, "Connection")
        c = NM_connection(self.bus, path)
        return c.get_settings()

    def get_all_dev_path(self):
        p_iface = dbus.Interface(self.proxy, "org.freedesktop.DBus.Properties")
        paths = p_iface.Get(self.name, "Devices")
        ret = []
        for p in paths:
            ret.append(str(p))
        return ret

    def get_all_dev_info(self):
        ret = []
        paths = self.get_all_dev_path()
        for p in paths:
            d = NM_dev(self.bus, p)
            info = d.get_info()
            ret.append(info)
        return ret


####################################################################
##
##  user interface
##
class Wired():
    def __init__(self, bus, ifname):
        self.ifname = ifname
        self.bus = bus

    def add_conn(self, c_id, s_eth, s_ip4=None, s_ip6=None):
        s_conn = Settings_conn(c_id, self.ifname, "eth")

        tabs = {
            "802-3-ethernet": s_eth,
            "connection": s_conn,
            "ipv4": s_ip4,
            "ipv6": s_ip6
        }

        conf = {}
        for k in tabs:
            if tabs[k] != None:
                conf[k] = tabs[k].to_dbus()

        #print conf
        setting = NM_settings(self.bus)
        setting.iface.AddConnection(dbus.Dictionary(conf))

    def update_conn(self, c_id, s_eth=None, s_ip4=None, s_ip6=None):
        if (not s_eth) and (not s_ip4) and (not s_ip6):
            raise Exception("parermeter error")

        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        s_conn = Settings_conn(c_id, self.ifname, "eth")

        tabs = {
            "802-3-ethernet": s_eth,
            "connection": s_conn,
            "ipv4": s_ip4,
            "ipv6": s_ip6
        }

        conf = {}
        for k in tabs:
            if tabs[k] != None:
                conf[k] = tabs[k].to_dbus()

        conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))

    def update_autoconnect(self, c_id, autoconnect):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "connection" not in conf:
            s_conn = Settings_conn(c_id, self.ifname, "eth", autoconnect)
            conf["connection"] = s_conn.to_dbus()
        else:
            conf["connection"]["autoconnect"] = autoconnect

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))

    def update_ip4(self, c_id, s_ip4):
        if not isinstance(s_ip4, Settings_IP4):
            raise Exception("parameter error")

        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "ipv4" not in conf:
            conf["ipv4"] = {}

        conf["ipv4"] = s_ip4.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))

    def update_ip4addr(self, c_id, ip, mask, gw):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        ip4addr = IP4Addr(ip, mask, gw)
        s_ip4 = Settings_IP4("manual", ip4addr)
        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "ipv4" not in conf:
            conf["ipv4"] = {}
        else:
            old = Settings_IP4.dbus_to_py(conf["ipv4"])
            if "dns" in old:
                for i in old["dns"]:
                    s_ip4.add_dns(i)

            if "routes" in old:
                for i in old["routes"]:
                    s_ip4.add_route(i[0], i[1], i[2], i[3])

        conf["ipv4"] = s_ip4.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))

    def update_ip4dns(self, c_id, list_dns):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "ipv4" not in conf:
            #conf["ipv4"] = {}
            #s_ip4 = Settings_IP4("auto")
            raise Exception("Failed to get old IP4 config")
        else:
            old = Settings_IP4.dbus_to_py(conf["ipv4"])
            s_ip4 = Settings_IP4(old["method"])
            if "addresses" in old:
                for i in old["addresses"]:
                    s_ip4.add_ip(i[0], i[1], i[2])

            if "routes" in old:
                for i in old["routes"]:
                    s_ip4.add_route(i[0], i[1], i[2], i[3])

        if len(list_dns) == 0:
            s_ip4.clean_dns()
        else:
            for i in list_dns:
                s_ip4.add_dns(i)

        conf["ipv4"] = s_ip4.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))


    def update_ip4routes(self, c_id, list_routes):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "ipv4" not in conf:
            #conf["ipv4"] = {}
            #s_ip4 = Settings_IP4("auto")
            raise Exception("Failed to get old IP4 config")
        else:
            old = Settings_IP4.dbus_to_py(conf["ipv4"])
            s_ip4 = Settings_IP4(old["method"])
            if "addresses" in old:
                for i in old["addresses"]:
                    s_ip4.add_ip(i[0], i[1], i[2])

            if "dns" in old:
                for i in old["dns"]:
                    s_ip4.add_dns(i)

        if len(list_routes) == 0:
            s_ip4.clean_route()
        else:
            for i in list_routes:
                s_ip4.add_route(i[0], i[1], i[2], i[3])

        conf["ipv4"] = s_ip4.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))



    def update_ip6(self, c_id, s_ip6):
        if not isinstance(s_ip6, Settings_IP6):
            raise Exception("parameter error")

        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "ipv6" not in conf:
            conf["ipv6"] = {}

        conf["ipv6"] = s_ip6.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))

    def update_ip6addr(self, c_id, ip, prefix, gw):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        ip6addr = IP6Addr(ip, prefix, gw)
        s_ip6 = Settings_IP6("manual", ip6addr)
        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "ipv4" in conf:
            del conf["ipv4"]
        if "ipv6" not in conf:
            conf["ipv6"] = {}
        else:
            old = Settings_IP6.dbus_to_py(conf["ipv6"])
            if "dns" in old:
                for i in old["dns"]:
                    s_ip6.add_dns(i)

            if "routes" in old:
                for i in old["routes"]:
                    s_ip6.add_route(i[0], i[1], i[2], i[3])

        conf["ipv6"] = s_ip6.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))

    def update_ip6dns(self, c_id, list_dns):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "ipv6" not in conf:
            raise Exception("Failed to get old IP6 config")
        else:
            old = Settings_IP6.dbus_to_py(conf["ipv6"])
            s_ip6 = Settings_IP6(old["method"])
            if "addresses" in old:
                for i in old["addresses"]:
                    s_ip6.add_ip(i[0], i[1], i[2])

            if "routes" in old:
                for i in old["routes"]:
                    s_ip6.add_route(i[0], i[1], i[2], i[3])

        if len(list_dns) == 0:
            s_ip6.clean_dns()
        else:
            for i in list_dns:
                s_ip6.add_dns(i)

        conf["ipv6"] = s_ip6.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))


    def update_ip6routes(self, c_id, list_routes):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "ipv6" not in conf:
            #conf["ipv6"] = {}
            #s_ip6 = Settings_IP6("auto")
            raise Exception("Failed to get old IP6 config")
        else:
            old = Settings_IP6.dbus_to_py(conf["ipv6"])
            s_ip6 = Settings_IP6(old["method"])
            if "addresses" in old:
                for i in old["addresses"]:
                    s_ip6.add_ip(i[0], i[1], i[2])

            if "dns" in old:
                for i in old["dns"]:
                    s_ip6.add_dns(i)

        if len(list_routes) == 0:
            s_ip6.clean_route()
        else:
            for i in list_routes:
                s_ip6.add_route(i[0], i[1], i[2], i[3])

        conf["ipv6"] = s_ip6.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))


    def update_eth(self, c_id, s_eth):
        if not isinstance(s_eth, Settings_eth):
            raise Exception("parameter error")

        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conf = conn.get_nm_settings()
        if "802-3-ethernet" not in conf:
            conf["802-3-ethernet"] = {}

        conf["802-3-ethernet"] = s_eth.to_dbus()

        #conn = NM_connection(self.bus, c["path"])
        conn.iface.Update(dbus.Dictionary(conf))


    def del_conn(self, c_id):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        conn = NM_connection(self.bus, c["path"])
        conn.iface.Delete()


    def active_conn(self, c_id, ifname):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        m = NM_manager(self.bus)
        d = m.get_dev_by_ifname(ifname)
        #if (not d) \
        #   or (d["info"]["type"] != "Ethernet") \
        #    or (d["info"]['state'] != "Disconnected"):
        #    raise Exception("can not find the usable wired dev [ifname:%s]"%ifname)

        if (not d) \
            or (d["info"]["type"] != "Ethernet"):
            raise Exception("can not find the usable wired dev [ifname:%s]"%ifname)

        m.iface.ActivateConnection(c["path"], d["path"], "/")

    def deactive_conn(self, c_id):
        m = NM_manager(self.bus)
        res = m.get_active_conn_by_id(c_id)
        if not res:
            raise Exception("can not find the usable connection [id:%s]"%c_id)
        d = res["info"]["devs"]
        if (not d) or (not d[0]):
            raise Exception("can not find the usable connection [id:%s]"%c_id)

        m.iface.DeactivateConnection(res["path"])


    def get_connections(self):
        s = NM_settings(self.bus)
        conns = s.get_all_conn_info()
        ret = []
        for i in conns:
            if "802-3-ethernet" in i :
                ret.append(i)
        return ret if len(ret) > 0 else None

    def get_conn_by_id(self, _id):
        s = NM_settings(self.bus)
        conns = s.get_all_conn_info()
        for i in conns:
            if ("802-3-ethernet" in i) \
              and ("connection" in i)  \
              and ("id" in i["connection"]) \
              and (i["connection"]["id"] == _id):
                return i
        return None



    '''
    return:
      example:
       {'duplex': 'full',
        'autoconnect': False,
        'hw': {'HwAddress': 'D0:67:E5:10:6E:EC', 'Speed': 1000, 'plugin': True},
        'IP4': {
                'Nameservers': ['64.104.123.245', '171.70.168.183', '64.104.123.228'],
                'Routes': [],
                'Addresses': [['64.104.169.94', 24, '64.104.169.1']]
                }
        }
    '''
    def get_act_settings(self):
        m = NM_manager(self.bus)
        res = m.get_active_conn_by_ifname(self.ifname)
        ret = {}
        found = False
        if res and ("info" in res) and ("devs" in res["info"]):
            devs = res["info"]["devs"]
            for d in devs:
                if ("ifname" in d) and (d["ifname"] == self.ifname):
                    if "IP4" in d:
                        ret["IP4"] = d["IP4"]

                    if "hw" in d:
                        ret["hw"] = d["hw"]

                    found = True
                    break

        if not found:
            return ret

        if res and ("info" in res) and ("settings" in res["info"]):
            conf = res["info"]["settings"]
            if ("802-3-ethernet" in conf) and ("duplex" in conf["802-3-ethernet"]):
                ret["duplex"] = conf["802-3-ethernet"]["duplex"]
            if ("connection" in conf) and ("autoconnect" in conf["connection"]):
                ret["autoconnect"] = conf["connection"]["autoconnect"]
            if ("connection" in conf) and ("id" in conf["connection"]):
                ret["c_id"] = conf["connection"]["id"]
            if ("ipv4" in conf) and ("method" in conf["ipv4"]):
                ret["method"] = conf["ipv4"]["method"]

        return ret


    def get_act_info(self):
        m = NM_manager(self.bus)
        res = m.get_active_conn_by_ifname(self.ifname)
        ret = {}
        if (not res) or ("info" not in res):
            return ret
        info = res["info"]
        found = False

        devs = ([] if ("devs" not in info) else info["devs"])
        for d in devs:
            if ("ifname" in d) and (d["ifname"] == self.ifname):
                ret["dev"] = d
                found = True
                break

        if not found:
            return ret

        ret["settings"] = ( {} if ("settings" not in info) else info["settings"])
        return ret



class Wireless():
    def __init__(self, bus, ifname):
        self.ifname = ifname
        self.bus = bus

    def add_conn(self, c_id, s_wifi, s_wsec=None, s_8021x=None, s_ip4=None, s_ip6=None):
        s_conn = Settings_conn(c_id, self.ifname, "wifi")
        tabs = dbus.Dictionary({
            'connection': s_conn,
            '802-11-wireless': s_wifi,
            '802-11-wireless-security': s_wsec,
            '802-1x': s_8021x,
            'ipv4': s_ip4,
            'ipv6': s_ip6
        })
        conf = {}
        for k in tabs:
            if tabs[k] != None:
                conf[k] = tabs[k].to_dbus()
        setting = NM_settings(self.bus)
        setting.iface.AddConnection(dbus.Dictionary(conf))

    def active_conn(self, c_id, ifname):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)
        m = NM_manager(self.bus)
        d = m.get_dev_by_ifname(ifname)
        if (not d) \
            or (d["info"]["type"] != "WiFi"):
            raise Exception("can not find the usable wireless dev [ifname:%s]"%ifname)
        m.iface.ActivateConnection(c["path"], d["path"], "/")

    def deactive_conn(self, c_id):
        m = NM_manager(self.bus)
        res = m.get_active_conn_by_id(c_id)
        if not res:
            raise Exception("can not find the usable connection [id:%s]"%c_id)
        d = res["info"]["devs"]
        if (not d) or (not d[0]):
            raise Exception("can not find the usable connection [id:%s]"%c_id)
        m.iface.DeactivateConnection(res["path"])

    def del_conn(self, c_id):
        settings = NM_settings(self.bus)
        c = settings.get_conn_by_id(c_id)
        if not c:
            raise Exception("can not find the usable connection [id:%s]"%c_id)
        conn = NM_connection(self.bus, c["path"])
        conn.iface.Delete()

class NM_watcher(NM_base):
    def __init__(self, bus, ifname):
        super(NM_watcher, self).__init__(bus)
        m = NM_manager(bus)
        res = m.get_dev_by_ifname(ifname)
        if not res:
            raise Exception("%s NOT exist"%ifname)

        self.d_type = ""
        if ("info" in res) and ("type" in res["info"]):
            self.d_type = res["info"]["type"]
        if  self.d_type not in ["Ethernet", "WiFi"]:
            raise Exception("unsupported dev")
        self.d_path = res["path"]
        self.ifname = ifname
        self.bus = bus
        self.specific = {}
        self.signals = {
                "org.freedesktop.NetworkManager": {
                        "CheckPermissions": 0,
                        "StateChanged": 0,
                        "PropertiesChanged": 0,
                        "DeviceAdded": 0,
                        "DeviceRemoved": 0
                        },
                "org.freedesktop.NetworkManager.Device":{
                        "StateChanged": 0
                        },
                "org.freedesktop.NetworkManager.Device.Wired":{
                        "PropertiesChanged": (1 if self.d_type == "Ethernet" else 0)
                        },
                "org.freedesktop.NetworkManager.DHCP4Config":{
                        "PropertiesChanged": 0
                        },
                "org.freedesktop.NetworkManager.DHCP6Config":{
                        "PropertiesChanged": 0
                        },
                "org.freedesktop.NetworkManager.Settings":{
                        "PropertiesChanged": 0,
                        "NewConnection": 0
                        },
                "org.freedesktop.NetworkManager.Settings.Connection":{
                        "Updated": 0,
                        "Removed": 0
                        },
                "org.freedesktop.NetworkManager.Connection.Active":{
                        "PropertiesChanged": 0
                        },
                "org.freedesktop.NetworkManager.Device.Wireless": {
                        "PropertiesChanged": (1 if self.d_type == "WiFi" else 0),
                        "AccessPointAdded": 0,
                        "AccessPointRemoved": 0
                },
                "org.freedesktop.NetworkManager.AccessPoint": {
                        "PropertiesChanged": 0
                }
            }

        self.ev = {
                "cable": [],
                "dhcp4": [],
                "dhcp6": [],
                "connectivity": []
            }

    def watch(self, ev, cb):
        if ev not in self.ev:
            raise Exception("unknown event")

        self.ev[ev].append(cb)

    def _triger(self, ev, ifname, *args, **kwargs):
        if ev not in self.ev:
            raise Exception("unknown event")
        for cb in self.ev[ev]:
            cb(event= ev, iface=ifname, *args, **kwargs)

    def _register(self, handler, iface, signal):
        if (iface not in self.signals) \
            or (signal not in self.signals[iface]):
            raise Exception("disallowable signal")

        k = iface +"."+ signal
        if (k in self.specific) and self.specific[k]:
            return

        obj = self.bus.add_signal_receiver(handler,
                                dbus_interface=iface,
                                signal_name=signal,
                                sender_keyword="sender",
                                path_keyword="path",
                                interface_keyword="interface",
                                member_keyword="member")

        self.specific[k] = obj

    def _deregister(self, iface, signal):
        if (iface not in self.signals) \
            or (signal not in self.signals[iface]):
            raise Exception("disallowable signal")

        k = iface +"."+ signal
        if (k in self.specific) and self.specific[k]:
            self.specific[k].remove()

    def start(self):
        for s in self.signals:
            iface = s
            for m in self.signals[s]:
                if self.signals[s][m] == 1:
                    self._register(self._dispather, iface, m)

    def reg_nm_signal(self, handler, signal):
        iface = "org.freedesktop.NetworkManager"
        self._register(handler, iface, signal)

    def dereg_nm_signal(self, signal):
        iface = "org.freedesktop.NetworkManager"
        self._deregister(iface, signal)

    def reg_dev_signal(self, handler, signal):
        iface = "org.freedesktop.NetworkManager.Device"
        self._register(handler, iface, signal)

    def _dispather(self, *args, **kwargs):
        if kwargs["path"] == self.d_path \
            and (kwargs["interface"] in ["org.freedesktop.NetworkManager.Device.Wired",     \
                                         "org.freedesktop.NetworkManager.Device.Wireless"]) \
            and kwargs["member"] == "PropertiesChanged" :
            if "Carrier" in args[0]:
                self._triger("cable", self.ifname, plugin = bool(args[0]["Carrier"]))

            if "State" in args[0]:
                st = int(args[0]["State"])
                if st in NM_dev.STATE:
                    self._triger("connectivity", self.ifname, state = NM_dev.STATE[st])
            try:
                if "Dhcp4Config" in args[0]:
                    p = str(args[0]["Dhcp4Config"])
                    if p.startswith("/org/freedesktop/NetworkManager/DHCP4Config/"):
                        #m = NM_base(self.bus)
                        res = self.get_prop(p, "org.freedesktop.NetworkManager.DHCP4Config")
                        res = Util.dbus_to_py(res)
                        self._triger("dhcp4", self.ifname, opt = res)

                if "Dhcp6Config" in args[0]:
                    p = str(args[0]["Dhcp6Config"])
                    if p.startswith("/org/freedesktop/NetworkManager/DHCP6Config/"):
                        #m = NM_base()
                        res = self.get_prop(p, "org.freedesktop.NetworkManager.DHCP6Config")
                        res = Util.dbus_to_py(res)
                        self._triger("dhcp6",  self.ifname, opt = res)
            except:
                pass


class WiredSingle(Wired):

    def __init__(self, ifname, c_id = None, bus = None):
        self.ifname = ifname
        if bus is None:
            bus = dbus.SystemBus()
        self.bus = bus
        #super(WiredSingle, self).__init__(bus, ifname)
        if c_id is None:
            c_id = ifname
        self.c_id = c_id
        conn = self.get_conn_by_id(c_id)
        if conn is None:
            self.add_conn(c_id)
        ''' why duplicated conn could be added?
        elif conn.get('interface-name') != ifname:
            self.del_conn(c_id)
            self.add_conn(c_id)
        '''

    def add_conn(self, c_id, ac = False):
        conn = Settings_conn(c_id, self.ifname, "eth", ac)
        tabs = {
            "802-3-ethernet": dbus.Dictionary({}),
            "connection": conn.to_dbus()
        }
        setting = NM_settings(self.bus)
        setting.iface.AddConnection(dbus.Dictionary(tabs))

    def set_autoconnect(self, auto):
        self.update_autoconnect(self.c_id, auto)

    def set_ip4_auto(self):
        self.update_ip4(self.c_id, Settings_IP4('auto'))

    def set_ip6_auto(self):
        self.update_ip6(self.c_id, Settings_IP6('auto'))

    def set_ip4_manual(self, ip, prefix, gw, dns = None):
        self.update_ip4addr(self.c_id, ip, prefix, gw)
        if dns is not None:
            self.update_ip4dns(self.c_id, dns)

    def set_ip6_manual(self, ip, prefix, gw, dns = None):
        self.update_ip6addr(self.c_id, ip, prefix, gw)
        if dns is not None:
            self.update_ip6dns(self.c_id, dns)

    def activate(self):
        self.active_conn(self.c_id, self.ifname)

    def remove(self):
        self.del_conn(self.c_id)

    def get_all_info(self):
        ret = {}
        m = NM_manager(self.bus)
        ret["dev"] = m.get_dev_by_ifname(self.ifname)
        ret["settings"] = self.get_conn_by_id(self.c_id)
        return ret

##### end of file
############################
