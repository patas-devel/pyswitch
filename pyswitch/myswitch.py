#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__app__ = 'MyAdmin'
__version__ = "1.26"
__author__ = "Iceman"
__copyright__ = "Copyright 2021"
__license__ = "GPL"


import os
import subprocess as sub
import pydb as db
import argparse
import pyswitch as sw
from termcolor import colored
import ipaddress
import pyconfig as conf


# VARS
mother_prepro = '10.20.100.133'
mother_prod = ''

# CLASS
class Device():

    def __init__(self, server='', switch='', port='', desc=''):
        self.server = server
        self.switch = switch
        self.port = port
        self.desc = desc
        
    def __str__(self):
        print(f'{self.server}, {self.switch}, {self.port}, {self.desc}')

    def show(self):
        print(f'INPUT: {self.server}, {self.switch}, {self.port}, {self.desc}')

# FUNC
def printx(text, c):
    if c == 'b':
        colour = 'blue'
    elif c == 'y':
        colour = 'yellow'
    elif c == 'g':
        colour = 'green'
    elif c == 'r':
        colour = 'red'
    else:
        colour = 'white'
    print(colored(text, colour))

def get_input(test):
    ''' Parser na vstupni parametry '''

    # Required positional argument
    parser = argparse.ArgumentParser(description='Popis pouziti scriptu:')
    parser.add_argument('server', help='Server hostname - [gmnXXXX]')
    # Optional
    parser.add_argument('--update', nargs='?', help='Update mother parameters - ["inventory,hp134ndda"]')
    parser.add_argument('--switch', nargs='?', help='Switch hostname - [AB13.TTC]')
    parser.add_argument('--port', nargs='?', type=int, help='Switch port - [45]')
    parser.add_argument('--vlan', nargs='?', type=int, help='Switch vlan - [1600]')
    parser.add_argument('--desc', nargs='?', help='Switch port description ["Server gmnXXXX"]')
    if DEBUG:
        args = parser.parse_args(test)
        print(args)
    else:
        args = parser.parse_args()
    args.switch = str(args.switch).lower()
    if DEBUG:
        print(f'Vsechny vstupni parametry: {args}\n')
    return args

def mother_info(vstup):
    server = vstup.server
    printx('# MOTHER INFO ##################################################','y')
    try: 
        srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
        subnet = db.session.query(db.Subnet).join(db.Interface).join(db.Machine).filter(db.Machine.name == server).first()
        vlan = db.session.query(db.Vlan).filter(db.Vlan.id == subnet.vlan_id).first()
        typ = db.session.query(db.Type).filter(db.Type.id == srv.type_id).first()
        int = db.session.query(db.Interface).filter(db.Interface.machine_id == srv.id).first()
        ra = db.session.query(db.Rack).filter(db.Rack.id == srv.rack_id).first() 
        try:
            ip = round((int.ip))
        except TypeError as error:
            # pripad skynet1 ... why ?
            print(f'Error: {error}')
            ipv = '-- '
        else:
            ipv = str(ipaddress.IPv4Address(ip))
        QR = srv.qr_code
        swi = 'A' + ra.name 
        if DEBUG:
            print(f'server id = {srv.id}')
            print(f'Type: {typ.name}')
            print(f'MAC: {int.mac},IP ADDR: {ipv}')
            print(f'RACK: {ra.name}')
    except AttributeError as err:
        print(f'Server {server} pravdepodobne neexistuje!')
        print(f'---> Error: {err}')
        exit(0)
    else:
        print(f'\
        \nSERVER:\t\t{srv.name}\nMODEL:\t\t{typ.name}\nQR CODE:\t{QR}\
        \nRACK:\t\t{ra.name}\nSWITCH:\t\t{swi}\nPORT\t\t{int.port}\
        \nMAC ADDR:\t{int.mac}\nIP ADDR:\t{ipv} (primary)\
        \nVLAN NAME:\t{vlan.name}\nVLAN:\t\t{vlan.id_vlan}\n\
        ')

def mother_update(vstup):
    if DEBUG:
        print(vstup)
    print(vstup)
    printx(f'\nMother updating parameters ...\n','y')
    mother_server = '10.20.100.133'
    mother_dir = '/root/mother/mother/machines/'
    mother_script = 'mother_update.py'
    sshinfo = 'ssh root@' + mother_server + ' ' + mother_dir + mother_script 
    stype = vstup.update.split(',')[0]
    value = vstup.update.split(',')[1]
    cmd = sshinfo + ' ' + vstup.server + ' ' + stype + ' ' + value
    if DEBUG:
        print(f'SSH COMMAND: {cmd}')
    runcmd(cmd)

def get_sw_info(vstup, cmd):
    s = sw.Switch(vstup.switch, sw.switches[vstup.switch], vstup.port)
    s.get_info(cmd)

def get_sw_config(vstup):
    s = sw.Switch(vstup.switch, sw.switches[vstup.switch], vstup.port)
    s.get_config(vstup.port)
    
def set_sw_desc(vstup, cmd):
    s = sw.Switch(vstup.switch, sw.switches[vstup.switch], vstup.port)
    s.set_desc(cmd)

def runcmd(cmd):
    return sub.getoutput(cmd)

def switch_info(vstup):
    printx('# SWITCH INFO ##################################################','b')
    # dodat sw port, ktere overujeme
    get_sw_config(vstup)
    # Varianta postupnych dotazu na konfiguraci
    text = printx('\nMam nyni pokracovat ve zmene konfigurace portu switche (zmenim vlanu description) ? (ano | ne): ','r')
    choice = input(text)
    if choice.lower() == 'ne':
        #   print('Ukoncuji pripojeni.')
        exit(0) # koncim
    else:
        cmds = []
        # CHANGE VLAN + DESC
        cmd1 = 'interface bridge-aggregation ' + str(vstup.port)
        cmds.append(cmd1)
        cmd2 = 'port access vlan ' + str(vstup.vlan)
        cmds.append(cmd2)
        cmd3 = 'description ' + vstup.desc
        cmds.append(cmd3)
        set_sw_desc(vstup, cmds)
        printx('################################################################','b')
 
def init():
    global DEBUG
    DEBUG = False
    dev = Device()
    os.system('clear')
    printx('# MYADMIN v1.26 #', 'g')
    if DEBUG:
        printx('DEBUGGING: ON','r')

# MAIN
def main():
    # Zakladni nastaveni a debug on/off 
    init()
    # Vyhodnoceni vstupnich parametry
    test = ['a-server4', '--update', 'ram,16']
    #test = ['bbbe1']
    vstup = get_input(test)
    # Informace o zadanem serveru z motheru
    #mother_info(vstup)
    # Aktualizace parametru serveru v motheru
    if vstup.update != None:
        mother_update(vstup)
    # Informace o nastaveni switchi pro dany port
    #if vstup.switch != None and vstup.port != None and vstup.vlan != None:
    #    switch_info(vstup)

if __name__ == "__main__":
    main()