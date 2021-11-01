#!/usr/bin/env python3

# INFO: script na zobrazeni informaci ze switche a upraveni jeho configurace
# KDO: iceman
# KDY: @ 10/2021

# HOWTO
# https://hub.packtpub.com/using-python-automation-to-interact-with-network-devices-tutorial/

# TODO
# - overit ze hostname sw ma ip adresu z moji tabulky !

# MODULS
import sys, os
import subprocess
from netmiko import ConnectHandler
import argparse
import configparser
import netaddr
from netaddr import EUI

# VARS
switches_stl = [
    { 'aa01': '10.32.240.11' },
    { 'aa02': '10.32.240.12' },
    { 'aa03': '10.32.240.13' },
    { 'aa04': '10.32.240.14' },
    { 'aa05': '10.32.240.15' },
    { 'ab01': '10.32.240.31' },
    { 'ab02': '10.32.240.32' },
    { 'ab03': '10.32.240.33' },
    { 'ab04': '10.32.240.34' },
    { 'ab05': '10.32.240.35' },
]


# aa08, ab08,ab10,ab11,ab12 nejsou
switches_ttc = [
    { 'aa01': '10.33.240.11' },
    { 'aa02': '10.33.240.12' },
    { 'aa03': '10.33.240.13' },
    { 'aa04': '10.33.240.14' },
    { 'aa05': '10.33.240.15' },
    { 'aa06': '10.33.240.16' },
    { 'aa07': '10.33.240.17' },

    { 'aa09': '10.33.240.19' },
    { 'aa10': '10.33.240.10' },
    
    { 'ab01': '10.33.240.31' },
    { 'ab02': '10.33.240.32' },
    { 'ab03': '10.33.240.33' },
    { 'ab04': '10.33.240.34' },
    { 'ab05': '10.33.240.35' },
    { 'ab06': '10.33.240.36' },
    { 'ab07': '10.33.240.37' },
    
    { 'ab09': '10.33.240.39' },
    { 'ab13': '10.33.240.43' },
    { 'ab14': '10.33.240.44' },
]


# CLASS
class Device():
    pass

class Server():
    ''' Class Server '''

    def __init__(self, srv_name='', srv_ip='', srv_mac='', srv_vendor='', srv_model=''):
        self.srv_name = srv_name
        self.srv_ip = srv_ip
        self.srv_mac = srv_mac
        self.srv_vendor = srv_vendor
        self.srv_model = srv_model

    def __str__(self):
        return self.sw_name


class Switch():
    ''' Class switch '''


    def __init__(self, sw_dc='', sw_name='', sw_ip='', sw_port='', sw_desc='', sw_out=''):
        self.sw_dc = sw_dc
        self.sw_name = sw_name
        self.sw_ip = sw_ip
        self.sw_port = sw_port
        self.sw_desc = sw_desc
        self.out = sw_out
        self.ini_file = 'switch.ini' # config file

    # https://wiki.python.org/moin/ConfigParserExamples
    def config_init(self):
        self.settings = configparser.ConfigParser()
        self.settings._interpolation = configparser.ExtendedInterpolation()
        self.settings.read(self.ini_file)

    def sw_connect(self):
        self.config_init()
        print(f'Connecting to switch: {self.sw_name} [{self.sw_ip}]\n')
        self.device = ConnectHandler(device_type=self.settings.get('switch', 'type'), ip=self.sw_ip, username=self.settings.get('switch', 'user'), password=self.settings.get('switch', 'pass'))

    def __str__(self):
        return f'SWITCH\nDC: {self.sw_dc}\nSWITCH: {self.sw_name}\nIP: {self.sw_ip}\nPORT: {self.sw_port}\nDESC: {self.sw_desc}' 

    def __repr__(self):
        return f'DC: {self.sw_dc}, SWITCH: {self.sw_name}, IP: {self.sw_ip}, PORT: {self.sw_port}, DESC: {self.sw_desc}' 

    def get_info(self, cmd):
        self.sw_out = self.device.send_command(cmd)
        if DEBUG:
            print(f'Vypis: {self.sw_out}\n')

    def get_config(self):
        self.sw_connect()
        cmd = 'display current-configuration interface g1/0/' + str(self.sw_port)
        self.get_info(cmd)
        cmd = 'display current-configuration interface g2/0/' + str(self.sw_port)
        self.get_info(cmd)
        cmd = 'display link-aggregation verbose Bridge-Aggregation' + str(self.sw_port)
        self.get_info(cmd)
        self.sw_disconnect()

    def set_config(self, note):
        self.sw_connect()
        self.sw_note = 'description ' + note 
        configcmds=[self.sw_port, self.sw_note]
        #configcmds=['interface g1/0/9', 'description TESTING1']
        self.sw_out = self.device.send_config_set(configcmds)
        if DEBUG:
            print(self.sw_out)
        self.sw_disconnect()
     
    
    def runcmd(self, cmd):
        return subprocess.getoutput(cmd)

    def sw_disconnect(self):
        print(f'\nOdpojuji se od switche: {self.sw_name}')
        self.device.disconnect()



def get_input():
    ''' Parser na vstupni parametry '''
    # check input args
    parser = argparse.ArgumentParser(description='Popis pouziti programu:')
    # Required positional argument
    parser.add_argument('switch', help='Switch hostname [AB13.TTC]')
    # Required positional argument
    parser.add_argument('port', type=int, help='Switch port [45]')
    # Optional argument
    parser.add_argument('--desc', nargs='?', help='Switch port description')
    args = parser.parse_args()  
    args.switch = str(args.switch).lower()
    if DEBUG:
        print(args)
        print(args.switch)
        print(args.port)
        print(args.desc)
    try:
        sw.sw_dc = args.switch.split('.')[1]
        sw.sw_name = args.switch.split('.')[0]
    except IndexError as error:
        print('Chybne zadany parametry sw !')
    else:
        if sw.sw_dc == 'ttc':
            for c in range(len(switches_ttc)):
                name = list(switches_ttc[c])[0]
                if DEBUG:
                    #print(f'name = {name}, swname = {sw.sw_name}')
                    pass
                if name == sw.sw_name:
                    sw.sw_ip = switches_ttc[c][name]
        sw.sw_port = args.port
        sw.sw_desc = args.desc
        print('-- Parametry nacteny')

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
    sw = Switch('',sw, ip, port)
    cmd = 'display current-configuration interface g1/0/' + str(port)
    sw.get_info(cmd)
    cmd = 'display current-configuration interface g2/0/' + str(port)
    sw.get_info(cmd)
    cmd = 'display link-aggregation verbose Bridge-Aggregation' + str(port)
    sw.get_info(cmd)
    

# MAIN
DEBUG = True
os.system('clear')
sr = Server()
sw = Switch('','AB13.TTC', '10.33.240.43', '26')
#sw.get_info('display interface brief')
#sw.get_config()
#sw.get_config()
#show_config()
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