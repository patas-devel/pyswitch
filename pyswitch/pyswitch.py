#!/usr/bin/env python3

# INFO: script na zobrazeni informaci ze switche a upraveni jeho configurace
# KDO: iceman
# KDY: @ 10/2021

# HOWTO
# https://hub.packtpub.com/using-python-automation-to-interact-with-network-devices-tutorial/

# TODO
# - overit ze hostname sw ma ip adresu z moji tabulky !

# MODULS
from re import I
import sys, os
import subprocess
import netaddr
from netaddr import EUI
from netmiko import ConnectHandler
from colorama import Fore, Style
import pyconfig as conf


# VAR
# # aa08, ab08,ab10,ab11,ab12 nejsou
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
def commands(cmd, port):
    port = str(port)
    if cmd == 'config':
        check_sw_config = [
            'display current-configuration interface gi1/0/' + port, 
            'display current-configuration interface gi2/0/' + port,
            'display current-configuration interface bridge-aggregation ' + port,
            'display mac-address interface Bridge-Aggregation ' + port,
            'display link-aggregation verbose Bridge-Aggregation ' + port
        ]
        return check_sw_config
    elif cmd == 'port':
        check_sw_port = [
            'display interface brief | incl GE1/0/' + port,
            'display interface brief | incl GE2/0/' + port
        ]
        return check_sw_port


# Login information
setup = conf.Config('switch')
swuser = setup.get_value('user')
swpass = setup.get_value('pass') 
swtype = setup.get_value('type')


# CLASS
class Switch():
    ''' Class switch '''

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

    def get_info(self, cmd):
        #self.sw_connect()
        self.sw_out = self.device.send_command(cmd)
        print(f'{Fore.BLUE}{self.sw_out}{Style.RESET_ALL}')
#        self.sw_disconnect()

    def set_desc(self, cmd):
        self.sw_connect()
        self.sw_out = self.device.send_config_set(cmd)
        print(f'{Fore.BLUE}{self.sw_out}{Style.RESET_ALL}')
        self.sw_disconnect()
    
    def get_config(self, cmd, port):
        self.sw_connect()
        for c in commands(cmd, port):
            #print(c)   
            self.get_info(c)
        self.sw_disconnect()

    def set_config_old(self, note):
        self.sw_connect()
        self.sw_note = 'description ' + note 
        configcmds=[self.sw_port, self.sw_note]
        #configcmds=['interface g1/0/26', 'description TESTING1']
        self.sw_out = self.device.send_config_set(configcmds)
        if DEBUG:
            print(self.sw_out)
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