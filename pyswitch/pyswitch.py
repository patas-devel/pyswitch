#!/usr/bin/env python3

# INFO: script na zobrazeni informaci ze switche a upraveni jeho configurace
# KDO: iceman
# KDY: @ 10/2021

# HOWTO
# https://hub.packtpub.com/using-python-automation-to-interact-with-network-devices-tutorial/

# TODO
# - overit ze hostname sw ma ip adresu z moji tabulky !

# MODULS
import re
from re import I
import sys, os
import subprocess
import netaddr
from netaddr import EUI
from netmiko import ConnectHandler
from colorama import Fore, Style
import pyconfig as conf


# VAR
# aa08, ab08,ab10,ab11,ab12 nejsou
# update: 07.12.2021
switches = { 
     'aa01.stl': '10.32.240.11',
     'aa02.stl': '10.32.240.12',
     'aa03.stl': '10.32.240.13',
     'aa04.stl': '10.32.240.14',
     'aa05.stl': '10.32.240.15',
     'ab01.stl': '10.32.240.31',
     'ab02.stl': '10.32.240.32',
     'ab03.stl': '10.32.240.33',
     'ab04.stl': '10.32.240.34',
     'ab05.stl': '10.32.240.35',
     'aa01.ttc': '10.33.240.11',
     'aa02.ttc': '10.33.240.12',
     'aa03.ttc': '10.33.240.13',
     'aa04.ttc': '10.33.240.14',
     'aa05.ttc': '10.33.240.15',
     'aa06.ttc': '10.33.240.16',
     'aa07.ttc': '10.33.240.17',
     'aa09.ttc': '10.33.240.19',
     'aa10.ttc': '10.33.240.10',
     'ab01.ttc': '10.33.240.31',
     'ab02.ttc': '10.33.240.32',
     'ab03.ttc': '10.33.240.33',
     'ab04.ttc': '10.33.240.34',
     'ab05.ttc': '10.33.240.35',
     'ab06.ttc': '10.33.240.36',
     'ab07.ttc': '10.33.240.37',
     'ab09.ttc': '10.33.240.39',
     'ab13.ttc': '10.33.240.43',
     'ab14.ttc': '10.33.240.44',
}

# without port
def commands(cmd, data):
    port = str(data.sw_port)
    if cmd == 'check':
        check_sw_config = {
            1: 'display interface brief | incl GE1/0/' + port,
            2: 'display interface brief | incl GE2/0/' + port,
            3: 'display interface brief | incl BAGG' + port,
            
            4: 'display mac-address interface GigabitEthernet1/0/' + port,
            5: 'display mac-address interface GigabitEthernet2/0/' + port,
            6: 'display mac-address interface Bridge-Aggregation ' + port,
            
            7: 'display link-aggregation verbose Bridge-Aggregation ' + port,
            
            8: 'display current-configuration interface gi1/0/' + port,
            9: 'display current-configuration interface gi2/0/' + port,
            10: 'display current-configuration interface bridge-aggregation ' + port
        }
        return check_sw_config
    elif cmd == 'config':
        make_config_sw = [
            'interface GigabitEthernet 1/0/' + port,
            'port link-aggregation group ' + port,
            'description gmnXXXX',
            'interface GigabitEthernet 2/0/' + port,
            'port link-aggregation group ' + port,
            'description gmnXXXX',
            'interface Bridge-Aggregation' + port,
            'link-aggregation mode dynamic',
            'port access vlan ' # FIXME potrebuji jeste vlanu
            'description gmnXXXX'
        ]


CHECK = {
1: 'The brief information of interface(s) under bridge mode:\nLink: ADM - administratively down; Stby - standby\nSpeed or Duplex: (a)/A - auto; H - half; F - full\nType: A - access; T - trunk; H - hybrid\nInterface            Link Speed   Duplex Type PVID Description\nGE1/0/30             DOWN auto    A      A    1601\n', 
2: 'The brief information of interface(s) under bridge mode:\nLink: ADM - administratively down; Stby - standby\nSpeed or Duplex: (a)/A - auto; H - half; F - full\nType: A - access; T - trunk; H - hybrid\nInterface            Link Speed   Duplex Type PVID Description\nGE2/0/30             DOWN auto    A      A    1601\n', 
3: 'The brief information of interface(s) under bridge mode:\nLink: ADM - administratively down; Stby - standby\nSpeed or Duplex: (a)/A - auto; H - half; F - full\nType: A - access; T - trunk; H - hybrid\nInterface            Link Speed   Duplex Type PVID Description\nBAGG30               DOWN auto    A      A    1601\n', 
4: 'MAC ADDR       VLAN ID  STATE          PORT INDEX               AGING TIME(s)\n3473-5a9f-de6c 3        Learned        Bridge-Aggregation2      AGING\n---  1 mac address(es) found  ---\n',
5: 'MAC ADDR       VLAN ID  STATE          PORT INDEX               AGING TIME(s)\n\n  ---  No mac address found  ---\n', 
6: 'MAC ADDR       VLAN ID  STATE          PORT INDEX               AGING TIME(s)\n\n  ---  No mac address found  ---\n', 
7: '\nLoadsharing Type: Shar -- Loadsharing, NonS -- Non-Loadsharing\nPort Status: S -- Selected, U -- Unselected\nFlags:  A -- LACP_Activity, B -- LACP_Timeout, C -- Aggregation,\n        D -- Synchronization, E -- Collecting, F -- Distributing,\n        G -- Defaulted, H -- Expired\n\nAggregation Interface: Bridge-Aggregation30\nAggregation Mode: Dynamic\nLoadsharing Type: Shar\nSystem ID: 0x8000, b8af-67e7-0a15\nLocal:\n  Port             Status  Priority Oper-Key  Flag\n--------------------------------------------------------------------------------\n  GE1/0/30         U       32768    29        {ACG}\n  GE2/0/30         U       32768    29        {ACG}\nRemote:\n  Actor            Partner Priority Oper-Key  SystemID               Flag\n--------------------------------------------------------------------------------\n  GE1/0/30         0       32768    0         0x8000, 0000-0000-0000 {EF}\n  GE2/0/30         0       32768    0         0x8000, 0000-0000-0000 {EF}', 
8: '#\ninterface GigabitEthernet1/0/30\n port access vlan 1601\n loopback-detection enable\n broadcast-suppression 1\n multicast-suppression 1\n unicast-suppression 1\n undo jumboframe enable\n stp edged-port enable\n undo lldp enable\n port link-aggregation group 30\n#\nreturn', 
9: '#\ninterface GigabitEthernet2/0/30\n port access vlan 1601\n loopback-detection enable\n broadcast-suppression 1\n multicast-suppression 1\n unicast-suppression 1\n undo jumboframe enable\n stp edged-port enable\n undo lldp enable\n port link-aggregation group 30\n#\nreturn', 
10: '#\ninterface Bridge-Aggregation30\n port access vlan 1601\n link-aggregation mode dynamic\n stp edged-port enable\n#\nreturn'
}

# Login information
setup = conf.Config('switch')
swuser = setup.get_value('user')
swpass = setup.get_value('pass') 
swtype = setup.get_value('type')


# CLASS
class Switch():
    ''' Class switch '''
    OUTPUT = {}
    
    def __init__(self, name='', ip='', port='', dc='', desc='', out=''):
        self.sw_name = name
        self.sw_ip = ip
        self.sw_port = port
        self.sw_dc = dc
        self.sw_desc = desc
        self.sw_out = out

    def sw_connect(self):
        print(f'Connecting to switch: {self.sw_name} [{self.sw_ip}]\n')
        self.device = ConnectHandler(device_type=swtype, ip=self.sw_ip, username=swuser, password=swpass)

    def __str__(self):
        return f'SWITCH\nDC: {self.sw_dc}\nSWITCH: {self.sw_name}\nIP: {self.sw_ip}\nPORT: {self.sw_port}\nDESC: {self.sw_desc}' 

    def __repr__(self):
        return f'DC: {self.sw_dc}, SWITCH: {self.sw_name}, IP: {self.sw_ip}, PORT: {self.sw_port}, DESC: {self.sw_desc}' 

    def parser(self, name, vstup, idata):
        lines = vstup.splitlines()
        port = name + str(idata.sw_port)
        res = ''
        for line in lines:
            if port in line:
                if 'UP' in line:
                    res = True
                else:
                    res = False
        return res

    def find_mac(self, v, idata):
        DEBUG = True
        mac_server = idata.eth_mac.replace(':','')
        if v.count('No mac address found') == 1:
            return False
        else:
            if '1 mac address(es) found' in v:
                lines = v.splitlines()
                for line in lines:
                    if 'Learned' in line:
                        mac_on_port = line.split(' ')[0].replace('-', '')
                        if DEBUG:
                            return mac_server + ' | ' + mac_on_port
                        return True if mac_server ==  mac_on_port else False
            else:
                return 'STOP - MORE MAC ADDRESS'

    def parser_bagg(self, vstup, idata):
        PORTS = []
        lines = vstup.splitlines()
        port1 = 'GE1/0/' + str(idata.sw_port)
        port2 = 'GE2/0/' + str(idata.sw_port)
        for line in lines:
            if port1 in line:
                if line.split()[1] == 'S':
                    PORTS.append(1)
            if port2 in line:
                if line.split()[1] == 'S':
                    PORTS.append(1)
        if len(PORTS) == 2:
            return True
        else:
            return False
            
    def detect_vlan(self, vstup, idata):
        a = '0000' # not defined
        lines = vstup.splitlines()
        for line in lines:
            if 'access vlan' in line:
                a = line.split()[3]
        if a == '0000':
            return '0000'
        else:    
            return a
                

    def check_config(self, data, idata):
        #print(f'{data}')
        srv_mac = (idata.eth_mac).replace(':','')
        port = idata.sw_port
        #print(srv_mac)
        # TODO
        # nutne zadat port presne jinak to vypise mnohem vice portu ge1/0/2 -> 0/21 0/22xxx
        print('SW CHECK: Starting ...........................')
        RESULT = {}
        for k, v in data.items():
            if k == 1:
                RESULT['GE1-UP'] = self.parser('GE1/0/', v, idata)
            elif k == 2:
                RESULT['GE2-UP'] = self.parser('GE2/0/', v, idata)
            elif k == 3:
                RESULT['BAGG-UP'] = self.parser('BAGG', v, idata)
            elif k == 4:
                RESULT['GE1-MAC'] = self.find_mac(v, idata) 
            elif k == 5:
                RESULT['GE2-MAC'] = self.find_mac(v, idata) 
            elif k == 6:
                RESULT['BAGG-MAC'] = self.find_mac(v, idata)
            elif k == 7:
                # SS = True >> nekonfigurovat
                RESULT['BAGG-S'] = self.parser_bagg(v, idata)
            elif k == 8:
                a = 'loopback: yes' if v.count('loopback') == 1 else 'loopback: no'
                b = 'broadcast: yes' if v.count('broadcast') == 1 else 'broadcast: no'
                c = 'link-aggregation: yes' if v.count('link-aggregation group ' + str(port)) == 1 else 'link-aggregation: no'
                #d = 'vlan 3: yes' if v.count('vlan 3') == 1 else 'vlan 3: no'
                d = 'vlan: ' + str(self.detect_vlan(v, idata))
                res = (a, b, c, d)
                RESULT['GE1-CONF'] = res
            elif k == 9:
                a = 'loopback: yes' if v.count('loopback') == 1 else 'loopback: no'
                b = 'broadcast: yes' if v.count('broadcast') == 1 else 'broadcast: no'
                c = 'link-aggregation: yes' if v.count('link-aggregation group ' + str(port)) == 1 else 'link-aggregation: no'
                #d = 'vlan 3: yes' if v.count('vlan 3') == 1 else 'vlan 3: no'
                d = 'vlan: ' + str(self.detect_vlan(v, idata))
                res = (a, b, c, d)
                RESULT['GE2-CONF'] = res 
            elif k == 10:
                a = 'bagg mode dynamic: yes' if v.count('link-aggregation mode dynamic') == 1 else 'bagg mode dynamic: no'
#                b = 'vlan 3: yes' if v.count('vlan 3') == 1 else 'vlan 3: no'
                c = 'vlan: ' + str(self.detect_vlan(v, idata))
                res = (a, c)
                RESULT['BAGG-CONF'] = res
        #print(RESULT)
        return RESULT
    
    def set_desc(self, cmd):
        self.sw_connect()
        self.sw_out = self.device.send_config_set(cmd)
        print(f'{Fore.BLUE}{self.sw_out}{Style.RESET_ALL}')
        self.sw_disconnect()
    
    def get_config(self, cmd, idata):
        self.sw_connect()
        for k, cmd in commands(cmd, idata).items():
            print(cmd)   
            data = self.device.send_command(cmd)
            Switch.OUTPUT[k] = data
            print(f'{Fore.BLUE}{data}{Style.RESET_ALL}')
        self.sw_disconnect()    
        return self.check_config(Switch.OUTPUT, idata)
        # TEST from CHECK dict
        #for k, v in CHECK.items():
        #    print(f'{k} {v}')
        #return self.check_config(CHECK, idata )

    def set_config_old(self, note):
        self.sw_connect()
        self.sw_note = 'description ' + note 
        configcmds=[self.sw_port, self.sw_note]
        #configcmds=['interface g1/0/26', 'description TESTING1']
        self.sw_out = self.device.send_config_set(configcmds)
        #print(self.sw_out)
        self.sw_disconnect()
     
    
    def runcmd(self, cmd):
        return subprocess.getoutput(cmd)

    def sw_disconnect(self):
        print(f'\nOdpojuji se od switche: {self.sw_name}')
        self.device.disconnect()


def test_smycka():
    """ testovani smycky pro pousteni prikazu na cele pole switches """
    #sw_count = len(switches_stl)
    sw_count = 1
    #print(sw_count)
    for s in range(sw_count):
        hostname = list(switches_stl[s])[0] # vybere klic z listu
        #print(hostname)
        ip = switches_stl[s][hostname]
        out = 'hostname: ' + str(hostname) + ', ip: ' + str(ip)
        print(out)
        sw = Switch('',ip,)
        cmd = 'display version'
        sw.get_info(cmd)
    print('---------------')

def mac_normalize(mac):
    # pridat check na vstupni mac adresu, jestli je to vubec macovka
    m = EUI(mac)
    m.dialect = netaddr.mac_cisco # 'xxxx.xxxx.xxxx'
    m = str(m).replace('.','-')
    return m
    

def test_mac_find(mac):
    mac = mac_normalize(mac)
    # sw ab13.ttc - hosting
    #sw = Switch('','10.33.240.43',)
    #cmd = 'display mac-address interface g2/0/43'
    #sw.get_info(cmd)
    f = open('sw.txt', 'r')
    parser = f.read()
    #print(parser)
    lines = []
    if 'found' in parser:
        with open('sw.txt') as f:
            for line in f: 
                line = line.strip() #or some other preprocessing
                lines.append(line) #storing everything in memory!
        mac_sw = lines[1].split()[0]
    else:
        print('Na portu neni mac adresa')
    if mac_sw == mac:
        out = 'mac serveru: ' + str(mac) + '\nmac na switchi: ' + str(mac_sw)
        if DEBUG:
            print(out)
        print('Mac adresy se shoduji')
    else:
        print('Mac adresy jsou ruzne !')

def mac_find(mac):
    mac = mac_normalize(mac)
    # sw ab13.ttc - hosting
    sw = Switch('AB13.TTC','10.33.240.43')
    cmd = 'display mac-address interface g2/0/43'
    sw.get_info(cmd)
    print(sw.sw_out)
    sw_out = str(sw.sw_out).split()
    if DEBUG:
        print(sw_out)
    lines = []
    if 'found' in sw_out:
        if DEBUG:
            print('found')
        mac_sw = sw_out[9]
        print(mac_sw)
    else:
        print('Na portu neni mac adresa')
    if mac_sw == mac:
        out = 'mac serveru: ' + str(mac) + '\nmac na switchi: ' + str(mac_sw)
        print(out)
        print('Mac adresy se shoduji')
    else:
        print('Mac adresy jsou ruzne, nemenim konfiguraci !!!')

def show_config():
    sw = 'AB13.TTC'
    ip = '10.33.240.43'
    port = '43'
    sw = Switch('',ip, port)
    cmd = 'display current-configuration interface g1/0/' + str(port)
    sw.get_info(cmd)
    cmd = 'display current-configuration interface g2/0/' + str(port)
    sw.get_info(cmd)
    cmd = 'display link-aggregation verbose Bridge-Aggregation' + str(port)
    sw.get_info(cmd)
    
#mac_find('0021-5ef0-adb4')
#show_config('','')
#mac_find('00215ef0adb4')

# zadani vstupu
# switch_hostname switch_port server_vlan switch_desc


# CHECK PORTLING AGREGATION
# https://blog.jonsdocs.org.uk/2020/02/28/link-aggregation-on-hp-comware/
# cmd='display link-aggregation verbose Bridge-Aggregation 125' # number se lisi, musi byt videt porty gi1/0/43 a gi2/0/43

# COMMANDS
#cmd = 'display version'
#cmd = 'display interface brief'
#cmd = 'display mac-address interface g2/0/45'
#cmd = 'display interface brief'
#cmd = 'display current-configuration interface g2/0/45'
#cmd = 'display mac-address interface g2/0/45'
# HWINFO
#cmd = 'display device manuinfo' # vyrobeno, sn, vendor
#cmd = 'display clock' # datum


#sw.set_config()
#sw.parser.get('switch', 'sw_pass')
#device = ConnectHandler(device_type='hp_comware', ip='10.33.240.43', username='admin', password='')
#output = device.send_command('display current-configuration interface GigabitEthernet 2/0/45')
#output = device.send_command('display version')
#print('menim desc u portu g1/0/9')
#configcmds=['interface g1/0/9', 'description my test']
#device.send_config_set(configcmds)
#cmd = 'display mac-address interface g2/0/45'
#output = device.send_command(cmd)
#print (output)
#device.disconnect()