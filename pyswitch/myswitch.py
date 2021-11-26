#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# INFO: script na zobrazeni informaci ze switche a upraveni jeho configurace
# KDO: iceman
# KDY: @ 10/2021

import os, sys
import pydb as db
import argparse
import pyswitch as sw
from termcolor import colored
import ipaddress

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


# FUNCTIOS
def get_input():
    ''' Parser na vstupni parametry '''

#    if len(sys.argv) < 2:
#        exit('Chyba: Musite zadat vstupni parametry. Pro blizsi informace zadete s parametrem -h.')
    # Required positional argument
    parser = argparse.ArgumentParser(description='Popis pouziti scriptu:')
    parser.add_argument('server', help='Server hostname - [gmnXXXX]')
    parser.add_argument('--switch', nargs='?', help='Switch hostname - [AB13.TTC]')
    parser.add_argument('--port', nargs='?', type=int, help='Switch port - [45]')
    parser.add_argument('--vlan', nargs='?', type=int, help='Switch vlan - [1600]')
    parser.add_argument('--desc', nargs='?', help='Switch port description ["Server gmnXXXX"]')
    if DEBUG:
        args = parser.parse_args(['--server', 'bbbe1'])
    else:
        args = parser.parse_args()
    args.switch = str(args.switch).lower()
    if DEBUG:
        print(f'Vsechny vstupni parametry: {args}')
    return args

def get_db_info(vstup):

    server = vstup.server
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
        \nVLAN NAME:\t{vlan.name}\nVLAN NUM:\t{vlan.id_vlan}\n\
        ')

def get_sw_info(vstup, cmd):
    s = sw.Switch(vstup.switch, sw.switches[vstup.switch], vstup.port)
    s.get_info(cmd)

def set_sw_desc(vstup, cmd):
    s = sw.Switch(vstup.switch, sw.switches[vstup.switch], vstup.port)
    s.set_desc(cmd)

def printb(text):
    print(colored(text, 'blue'))

def printy(text):
    print(colored(text, 'yellow'))
    
def printg(text):
    print(colored(text, 'green'))
    
def printr(text):
    print(colored(text, 'green'))


# MAIN
def main():
    global DEBUG
    DEBUG = False
    dev = Device()
    os.system('clear')
    printg('##################\n# MYSWITCH v1.25 #\n##################')
    vstup = get_input() # vyhodnoceni vstupnich parametry
    if DEBUG:
        print(vstup.server)
    printy('# MOTHER INFO ##################################################')
    get_db_info(vstup)
    print(f'DEBUG: Vstupni parametry - {vstup}')
    #cmd = 'display current-configuration interface g1/0/' + str(vstup.port)
    if vstup.switch != None and vstup.port != None and vstup.vlan != None:
        printb('# SWITCH INFO ##################################################')
        # VYPISE PORTY gi1,2, bridge port, mac adresu na portech
        cmds_info = []
        cmd1 = 'display current-configuration interface gi1/0/' + str(vstup.port)
        cmd2 = 'display current-configuration interface gi2/0/' + str(vstup.port)
        cmd3 = 'display current-configuration interface bridge-aggregation ' + str(vstup.port)
        cmd4 = 'display mac-address interface Bridge-Aggregation ' + str(vstup.port)
        cmds_info.extend([cmd1, cmd2, cmd3, cmd4])
        for c in cmds_info:
            get_sw_info(vstup, c)
            # doresit disconnect ...
        text = printr('\nMam nyni pokracovat ve zmene konfigurace portu switche (zmenim vlanu description) ? (ano | ne): ')
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
            printb('################################################################')

if __name__ == "__main__":
    main()