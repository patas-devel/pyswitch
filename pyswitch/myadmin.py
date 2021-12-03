#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__app__ = 'MyAdmin'
__version__ = "1.29"
__author__ = "Iceman"
__copyright__ = "Copyright 2021"
__license__ = "GPL"


import csv, base64
import pandas as pd
from configparser import Error
import os, time, sys
import subprocess as sub

from pandas._libs.missing import NA
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

#def importer_test(csv_file):
#    # prevedeni csv file do dictionary
#    dict = {}
#    with open(csv_file) as f:
#        reader = csv.reader(f)
#        dict = {rows[0]:rows[1] for rows in reader}
#    d = Dict2class(dict)
#    #d.State = 'prod'
#    # loop na objects in dict
#    for attr, value in d.__dict__.items():
#        #print(f'{attr},{value}')
#        data = d.name + ',' + attr + ',' + value
#        if '#' in data:
#            pass
#        else:
#            mother_update_auto(data)
#        #if attr == 'os':
#        #    data = attr + ',' + value
    
def importer(csv_file):
    data = pd.read_csv(csv_file)
    #print(data)
#    df = pd.DataFrame(data, columns=['mother','Cold-dell740-35']) 
    df = pd.DataFrame(data)
    #print (df)
    #header = df.set_index['name-mother']
    first_col = df.columns[0]
    # vyber serveru pro zpracovani 1.server = 1:2, 2.server = 2:3, atd.
    for sl in df.columns[1:2]:
#        print(f'server: {sl}')
        for i in df.index:
            server = sl
            stype = df.loc[i, first_col]
            svalue = df.loc[i, sl]
            #print(type(svalue))
            # kontrola na prazdne hodnoty u stringu != nan ...
            if svalue == None or svalue != svalue or '#' in stype:
                #print('PASS - not value!')
                continue
            else:
                data = server + ',' + str(stype) + ',' + str(svalue)
                #print(data)
            mother_update_auto(data)
    

#class Dict2class(object):
#    """
#    Turns a dictionary into a class
#    """
#    def __init__(self, dictionary):
#        """Constructor"""
#        for key in dictionary:
#            setattr(self, key, dictionary[key])
#    
#    def __repr__(self):
##        return "<dict2obj: %s="">" % self.__dict__
#        attrs = str([x for x in dir(self) if "__" not in x])
#        return "<dict2obj: %s="">" % attrs


def get_input(test):
    ''' Parser na vstupni parametry '''

    # Required positional argument
    parser = argparse.ArgumentParser(description='Popis pouziti utility:')
    parser.add_argument('server', nargs='?', help='Server hostname - [gmnXXXX]')
    # Optional
    parser.add_argument('-i', nargs='?', help='Information about server - [mother or switch]')
    parser.add_argument('-um', nargs='?', help='Update mother parameters - [cpu / ram / os / inventory / helios / qr / age / sn / port], usage: [cpu,8].')
    parser.add_argument('-us', nargs='?', help='Update switch configuration\n[AB13.TTC,45,1600,"Server gmnXXXX"]')
    parser.add_argument('-ua', nargs='?', help='Automatic update switch configuration\n[gmnXXXX"]')
    parser.add_argument('-f', nargs='?', help='Import csv file with information about new server - [file_name]')
    if DEBUG:
        args = parser.parse_args(test)
        print(args)
    else:
        args = parser.parse_args()
    if args.us != None:
        args.us = str(args.us).lower()
    if DEBUG:
        print(f'Vsechny vstupni parametry: {args}\n')
    return args

def mother_info(vstup):
    server = vstup.server
    if vstup.i == 'mother':
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
        swi = 'A' + ra.name.split(' ')[0]  
        if DEBUG:
            print(f'server id = {srv.id}')
            print(f'Type: {typ.name}')
            print(f'MAC: {int.mac},IP ADDR: {ipv}')
            print(f'RACK: {ra.name}')
    except AttributeError as err:
        printx(f'Server {server} pravdepodobne neexistuje!','r')
        if DEBUG:
            print(f'---> Error: {err}')
        exit(0)
    else:
        if vstup.i == 'mother':
            print(f'\
            \nSERVER:\t\t{srv.name}\nMODEL:\t\t{typ.name}\nQR CODE:\t{QR}\
            \nRACK:\t\t{ra.name}\nSWITCH:\t\t{swi}\nPORT\t\t{int.port}\
            \nMAC ADDR:\t{int.mac}\nIP ADDR:\t{ipv} (primary)\
            \nVLAN NAME:\t{vlan.name}\nVLAN:\t\t{vlan.id_vlan}\n\
            ')
        info = swi + ',' + str(int.port)
        return info

def mother_update_manual(vstup):
    if DEBUG:
        print(vstup)
    print(vstup)
    mother_server = 'ssh root@10.20.100.133'
    mother_dir = '/root/mother/mother/machines/'
    mother_script = 'machine_update.py'
    ssh = mother_server + ' ' + mother_dir + mother_script 
    try:
        stype = vstup.um.split(',')[0]
        value = vstup.um.split(',')[1]
    except IndexError as err:
        if DEBUG:
            printx(f'Error: {err}','r')
        printx(f'Mother update: Spatne zadane parametry.','r')
        exit(0)
    else:
        cmd = ssh + ' ' + vstup.server + ' ' + stype + ' ' + value
        #print(cmd)
        if DEBUG:
            print(f'SSH COMMAND: {cmd}')
        printx(f'\nMother updating parameters ...\n','y')
        #runcmd(cmd)
        
def mother_update_auto(data):
    if DEBUG:
        print(data)
    #print(data)
    server = data.split(',')[0]
    stype = data.split(',')[1]
    svalue = data.split(',')[2]
    #print(f'{server},{stype},{svalue}')
    mother_script = '/root/mother/mother/machines/machine_update.py'
    net_list = ['mgmt', 'eth', 'e1', 'e2', 'e3']
    if stype == 'name' or '#' in data:
        pass
    else:
        if stype == 'name':
        #print(data)
            svalue = data.split(',')[2]
        elif stype == 'project_id':
            srv = db.session.query(db.Project).filter(db.Project.name == svalue).first()
            #print(f'project_id: {srv.id}')
            svalue = srv.id
        elif stype == 'type':
            srv = db.session.query(db.Type).filter(db.Type.name == svalue).first()
            #print(f'server-type: {srv.id}')
            svalue = srv.id
        elif stype == 'state':
            srv = db.session.query(db.State).filter(db.State.name == svalue).first()
            #print(f'state_id: {srv.id}')
            svalue = srv.id
        elif stype == 'rack':
            srv = db.session.query(db.Rack).filter(db.Rack.name == svalue).first()
            #print(f'rack_id: {srv.id}')
            svalue = srv.id
        elif stype == 'maintainer':
            obj = db.session.query(db.User).filter(db.User.username == svalue).first()
            #print(f'user_id: {obj.id}')
            svalue = obj.id
        elif stype =='notes':
            msg = svalue
            message_bytes = msg.encode('ascii')
            msg_enc = base64.b64encode(message_bytes)
            msg_out = msg_enc.decode('ascii')
            svalue = msg_out
            #print(f'Encode: {svalue}')
            #base64_message = svalue
            #base64_bytes = base64_message.encode('ascii')
            #message_bytes = base64.b64decode(base64_bytes)
            #message = message_bytes.decode('ascii')
            #print(f'Decode: {message}')
        elif stype == 'machinegroups':
            srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
            mg = db.session.query(db.MachineGroup).filter(db.MachineGroup.machine_id == srv.id).first()
            obj = db.session.query(db.Group).filter(db.Group.id == mg.machinegroup_id).first()
            #print(obj.id)
            svalue = obj.id
        elif stype in net_list:
            srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
            #server = srv.id # a-server5
            server = 2275
            svalue = svalue.lower().replace(':','')
            mother_script = '/root/mother/mother/networking/interfaces_update.py'
        else:
            pass
        mother_prepro_ssh = 'ssh root@10.20.100.133 ' + mother_script
        cmd = mother_prepro_ssh + ' ' + str(server) + ' ' + str(stype) + ' ' + str(svalue)
        print(cmd)
        #runcmd(cmd)


def get_sw_info(vstup, cmd):
    s = sw.Switch(vstup.switch, sw.switches[vstup.switch], vstup.port)
    s.get_info(cmd)

def get_sw_config(vstup):
    try:
        name = vstup.switch.split(',')[0]
        port = vstup.switch.split(',')[1]
        vlan = vstup.switch.split(',')[2]
        desc = vstup.switch.split(',')[3]
    except Error as err:
        print(f'{err}')
    else: 
        print(f'Zadano: {name}, {port}, {vlan}, {desc}')
        s = sw.Switch(name, sw.switches[name], port)
        s.get_config('config', port)
    
def set_sw_desc(vstup, cmd):
    s = sw.Switch(vstup.switch, sw.switches[vstup.switch], vstup.port)
    s.set_desc(cmd)

def runcmd(cmd):
    return sub.getoutput(cmd)


def switch_info(vstup):
    # nactu parametry z motheru
    info = mother_info(vstup)
    printx('# SWITCH INFO ##################################################','b')
    try:
        name = str(info.split(',')[0]).lower()
        port = info.split(',')[1]
    except Error as err:
        print(f'Error: {err}')
    else:
        print(f'ZADANO - switch: {name}, port: {port}\n')
        ss = sw.Switch(name, sw.switches[name], port)
        ss.get_config('config', port)
    
def switch_update_manual(vstup):
    printx('# SWITCH UPDATE ##################################################','b')
    # dodat sw port, ktere overujeme
    get_sw_info(vstup)
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


def switch_update_auto(vstup):
    data = mother_info()
    switch = data.split(',')[0]
    port = data.split(',')[1]
    print(f'{switch}, {port}')
    exit(0)
    printx('# SWITCH UPDATE ##################################################','b')
    # dodat sw port, ktere overujeme
    get_sw_info(vstup)
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
#    dev = Device()
    os.system('clear')
    printx(f'# MYADMIN {__version__} #', 'g')
    if DEBUG:
        printx('DEBUGGING: ON','r')

# MAIN
def main():
    # Zakladni nastaveni a debug on/off 
    init()
    # Vyhodnoceni vstupnich parametry
    test = ['a-server4']
    vstup = get_input(test)
    # Informace o zadanem serveru z motheru
    #print(len(sys.argv))
    if len(sys.argv) > 2:
        if vstup.i != None:
            if vstup.i == 'mother':
                mother_info(vstup)
            elif vstup.i =='switch':
                switch_info(vstup)
            else:
                printx('Nezadan zdroj informaci ! Moznosti: mother, switch.','r')
        # Aktualizace parametru v motheru nebo zmena nastaveni switche (vlan, desc)
        elif vstup.um != None:
            mother_update_manual(vstup)
        elif vstup.us != None:
    #        switch_update_manual(vstup)
            pass
        elif vstup.ua != None:
            switch_update_auto(vstup)
        elif vstup.f != None:
            importer(vstup.f)
        else:
            printx('Chybne zadano, pravdepodobne jste nezadal vsechny pozadovane parametry!','r')
        # Informace o nastaveni switchi pro dany port
    else:
        printx('Nutne zadat vsechny parametry nebo pouzijte paremeter: -h pro help.','r')

if __name__ == "__main__":
    main()
    
# TODO
# jinak resit debug mode - ne ten test parametr
# import csv pro update mother - dalsi polozku ?