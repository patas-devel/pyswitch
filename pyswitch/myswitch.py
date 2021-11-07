#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# INFO: script na zobrazeni informaci ze switche a upraveni jeho configurace
# KDO: iceman
# KDY: @ 10/2021

import os
from re import A, I
#import pynetwork as net
import pydb as db
import argparse
import configparser
import pyswitch as sw
from termcolor import colored
import pyconfig as conf

# VARS
DEBUG = False

# CLASS

class Device():

    def __init__(self, server='', switch='', port='', desc=''):
        self.server = server
        self.switch = switch
        self.port = port
        self.desc = desc
        
    def __str__(self):
        print(f'{self.server}, {self.switch}, {self.port}, {self.desc}')

    def repr(self):
        print(f'{self.server}, {self.switch}, {self.port}, {self.desc}')
    
    def show(self):
        print(f'{self.server}, {self.switch}, {self.port}, {self.desc}')


# FUNCTIOS

def get_input():
    ''' Parser na vstupni parametry '''

    parser = argparse.ArgumentParser(description='Popis pouziti programu:')
    parser.add_argument('server', help='Server hostname - [gmnXXXX]')
    parser.add_argument('switch', help='Switch hostname - [AB13.TTC]')
    # Required positional argument
    parser.add_argument('port', type=int, help='Switch port - [45]')
    # Optional argument
    parser.add_argument('--desc', nargs='?', help='Switch port description ["Server gmnXXXX"]')
    if DEBUG:
        pass
    else:
        args = parser.parse_args()  
    args.switch = str(args.switch).lower()
    if DEBUG:
        print(f'Vsechny vstupni parametry: {args}')
        print(args.server)
        print(args.switch)
        print(args.port)
        print(args.desc)
    try:
        pom_sw1 = args.switch.split('.')[1]
        pom_sw2 = args.switch.split('.')[0]
    except IndexError as error:
        print('Chybne zadany parametry pro switch !')
    else:
       return args
#        if sw_dc == 'ttc':
#            for c in range(len(sw.switches_ttc)):
#                name = list(sw.switches_ttc[c])[0]
#                if DEBUG:
#                    print(f'name = {name}, swname = {sw.sw_name}')
#                if name == sw_name:
#                    sw_ip = sw.switches_ttc[c][name]
#        sw_port = args.port
#        sw_desc = args.desc
#        print('-- Parametry nacteny')


# MAIN
def main():
    dev = Device()
    os.system('clear')
    print(colored('##################################################', 'green'))
    vstup = get_input() # vyhodnoceni vstupnich parametry
    # info z motheru o serveru
    dev.port = vstup.port
    dev.switch = vstup.switch
    dev.server = vstup.server
    dev.desc = vstup.desc
    dev.show()
    
    # info ze switches od nastaveni dle zadani
#    s = sw.Switch('AB13.TTC', '10.33.240.43', '26')
    #cmd = 'display version'
    #s.get_info(cmd)


# TODO
# 1. script
# cteni parametru z radky - nazev serveru
#  script server switch port



    # OK
    #server = 'bbbe1'
    #mix = db.session.query(db.Subnet).join(db.Interface).join(db.Machine).filter(db.Machine.name == server).first()
    #print(f'VLAN_id={mix.vlan_id}')
    #mix2 = db.session.query(db.Vlan).filter(db.Vlan.id == mix.vlan_id).first()
    #print(f'Vlan-name:\t{mix2.name}\nVlan-cislo:\t{mix2.id_vlan}')


if __name__ == "__main__":
    main()











#def main():
#    os.system('clear')


# MAIN
#if __name__ == "__main__":
#   main()