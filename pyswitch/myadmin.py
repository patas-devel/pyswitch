#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__app__ = 'MyAdmin'
__version__ = "1.30"
__author__ = "Iceman"
__copyright__ = "Copyright 2021"
__license__ = "GPL"


import csv, base64
import pandas as pd
from configparser import Error
import os, time, sys
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

class Server():
    
    SERVERS = [] 
    Servers = {}
    scount = 0
    
    def __init__(self, mother, name, project_id, type, inventory, state, cpu, ram, os, qr_code, purchase_date,
                 serial_number, rack, rack_position, maintainer, switch_port, notes, 
                 mgmt, mgmt_port, mgmt_vlan, eth, eth_port, eth_vlan, eth_e1, eth_e2, eth_e3, sw_name, sw_port, 
                 sw_vlan, sw_desc):
        self.mother = mother
        self.name = name
        self.project_id = project_id
        self.type = type
        self.inventory = inventory
        self.state = state
        self.cpu = cpu
        self.ram = ram
        self.os = os
        self.qr_code = qr_code
        self.purchase_date = purchase_date
        self.serial_number = serial_number
        self.rack = rack
        self.rack_position = rack_position
        self.maintainer = maintainer
        self.switch_port = switch_port
        self.notes = notes
        self.mgmt = mgmt
        self.mgmt_port = mgmt_port
        self.mgmt_vlan = mgmt_vlan
        self.eth = eth
        self.eth_port = eth_port
        self.eth_vlan = eth_vlan
        self.eth_e1 = eth_e1
        self.eth_e2 = eth_e2
        self.eth_e3 = eth_e3
        self.sw_name = sw_name
        self.sw_port = sw_port
        self.sw_vlan = sw_vlan
        self.sw_desc = sw_desc
        Server.scount += 1
    
    def __str__(self):
        return f'Mother: {self.mother}, name: {self.name}, project_id: {self.project_id}, type: {self.type},\n \
                inventory: {self.inventory}, state: {self.state}, cpu: {self.cpu}, ram: {self.ram}, os: {self.os}\n\
                qr_code: {self.qr_code}, purchase_date: {self.purchase_date}, serial_number: {self.serial_number}\n\
                rack: {self.rack}, rack_position: {self.rack_position}, maintainer: {self.maintainer}, switch_port: {self.switch_port}\n\
                notes: {self.notes}'

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

    
def import_csv(csv_file):
    #srv = Server()
    data = pd.read_csv(csv_file)
    #print(data)
#    df = pd.DataFrame(data, columns=['mother','Cold-dell740-35']) 
    df = pd.DataFrame(data)
    #print (df)
    #header = df.set_index['name-mother']
    first_col = df.columns[0]
    # vyber serveru pro zpracovani 1.server = 1:2, 2.server = 2:3, atd.
    for col in df.columns[2:3]:
        print(f'Zpracovavam server: <{col}> | prostredi: {ENV}')
        for i in df.index:
            server = col
            stype = df.loc[i, first_col]
            svalue = df.loc[i, col]
            #print(type(svalue))
            # kontrola na prazdne hodnoty u stringu != nan ...
            if svalue == None or svalue != svalue or '#' in stype:
                #print('PASS - not value!')
                continue
            else:
                data = server + ',' + str(stype) + ',' + str(svalue)
                #print(f'Zpracovavam: {data} ---------')
            prepare_data(data)

            
def new_way(csv_file):
    data = pd.read_csv(csv_file)
    #print(data)
    #df = pd.DataFrame(data, columns=['mother','Cold-dell740-35']) 
    df = pd.DataFrame(data)
    first_col = df.columns[0]
    # vyber serveru pro zpracovani 1.server = 1:2, 2.server = 2:3, atd.
    for col in df.columns[1:3]:
        s = Server(col)
        print(f'Zpracovavam server: <{col}> | prostredi: {ENV}')
        for i in df.index:
            prvni = col
            #druhy = col + 1
            stype = df.loc[i, first_col]
            svalue = df.loc[i, col]
            if stype == 'name':
                s.name = svalue
            elif stype == 'project_id':
                s.project_id = svalue
            elif stype == 'type':
                s.type = svalue
            elif stype == 'inventory':
                s.inventory = svalue
            elif stype == 'state':
                s.state = svalue
            elif stype == 'cpu':
                s.cpu = svalue
            elif stype == 'ram':
                s.ram == svalue
            elif  stype == 'os':
                s.os = svalue
            elif stype == 'qr_code':
                s.qr_code = svalue
            elif stype == 'purchase_data':
                s.purchase_date = svalue
            elif stype == 'serial_number':
                s.serial_number = svalue
            elif stype == 'rack':
                s.rack = svalue
            elif stype == 'rack_position':
                s.rack_position = svalue
            elif stype == 'maintainer':
                s.maintainer = svalue
            elif stype == 'switch_port':
                s.switch_port = svalue
            elif stype == 'notes':
                s.notes = svalue
            #print(f'prvni: {prvni}, stype: {stype}, svalue: {svalue}')
        s.SERVERS.append(s)
    for i in s.SERVERS:
        print(i)

def prepare_data(data):
    if DEBUG:
        print(data)
    #print(data)
    NET = False
    server = data.split(',')[0]
    stype = data.split(',')[1]
    svalue = data.split(',')[2]
    #print(f'Zpracovavam: {server},{stype},{svalue}')
    mother_prepro_script = '/root/mother/mother/machines/machines_update.py'
    # rucne doplnene
    net_list = ['mgmt', 'eth', 'e1', 'e2', 'e3']
    switch_list = ['switch_data', 'switch', 'port', 'vlan', 'desc']
    if '#' in data:
        pass
    # switch update
    elif stype in switch_list:
#        print(data)
        print('Switch configuration ...')
        print(f'Nacteno z csv: {server},{stype},{svalue}')
        #mother_update_auto(data)
        #switch_info(svalue)
    else:
        # mother update
        if stype == 'name':
            print(svalue)
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
            # test
            #svalue = 55
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
        #elif stype == 'machinegroups':
        #    srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
        #    mg = db.session.query(db.MachineGroup).filter(db.MachineGroup.machine_id == srv.id).first()
        #    obj = db.session.query(db.Group).filter(db.Group.id == mg.machinegroup_id).first()
            #print(obj.id)
        #    svalue = obj.id
        elif stype == 'switch_port':
            print(stype)
        elif stype in net_list:
            NET = True
            svalue = svalue.lower().replace(':','')
            if ENV == 'PREPRO':
                #srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
                #server = srv.id
                server = 2275 # a-server5
            # PROD
            elif ENV == 'PROD':
                srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
                server = srv.id
        else:
            pass
        # PROD / PREPRO
        if ENV == 'PREPRO':
            if NET: 
                mother_script = '/root/mother/mother/networking/interfaces_update.py'
            else:
                mother_script = '/root/mother/mother/machines/machines_update.py'
        elif ENV == 'PROD':
            if NET:
                mother_script = '/usr/share/pyshared/mother/networking/interfaces_update.py' 
            else:
                mother_script = '/usr/share/pyshared/mother/machines/machines_update.py' 

        # RESULT AND DO
        if ENV == 'PREPRO':
            cmd = 'ssh root@10.20.100.133 ' + mother_script + ' ' + str(server) + ' ' + str(stype) + ' ' + str(svalue)
        elif ENV == 'PROD':            
            cmd = 'ssh root@mother.cent ' + mother_script + ' ' + str(server) + ' ' + str(stype) + ' ' + str(svalue)
        print(cmd)
        #runcmd(cmd)


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
    parser.add_argument('-f', nargs='?', help='Import csv config file and automatic update mother parameters and switch configuration - [file_name]')
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
    server = vstup.ua
    if vstup.i == 'mother' or vstup.ua != '':
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
            print(f'ERR: {error}')
            ipv = '-- '
        else:
            ipv = str(ipaddress.IPv4Address(ip))
        QR = srv.qr_code
        switch = 'A' + ra.name.split(' ')[0]  
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
            \nRACK:\t\t{ra.name}\nSWITCH:\t\t{switch}\nPORT\t\t{int.port}\
            \nMAC ADDR:\t{int.mac}\nIP ADDR:\t{ipv} (primary)\
            \nVLAN NAME:\t{vlan.name}\nVLAN:\t\t{vlan.id_vlan}\n\
            ')
        if vstup.ua != '':
            #if 'gmn' in server:
            #    vlan = swi.split('.')[1].lower()
            info = switch + ',' + str(int.port) + ',' + str(vlan.id_vlan)
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
    #return sub.getoutput(cmd)
    ssh_cmd = cmd
    process = sub.Popen(ssh_cmd, shell=True,
            stdout=sub.PIPE, stderr=sub.STDOUT)
    output,stderr = process.communicate()
    status = process.poll()
    out = output.decode('utf-8').split('.')[0] # item from list
    err = stderr
    print(f'{status}, {out}')
    #print(f'{err}') # err nic nevypisuje


def switch_info(vstup):
    # nactu parametry z motheru
    if 'mother' in vstup:
        info = mother_info(vstup)
    else:
        info = vstup
    printx('# SWITCH INFO ##################################################','b')
    try:
        name = info.split(';')[0].lower()
        port = info.split(';')[1]
        vlan = info.split(';')[2]
        #print(f'{name},{port},{vlan}')
    except Error as err:
        print(f'Error: {err}')
    else:
        print(f'ZADANO - switch: {name}, port: {port}\n')
        ss = sw.Switch(name, sw.switches[name], port)
        sw_output = ss.get_config('check', port)
        #print(sw_output)
        if sw_check_config_state(sw_output):
            print('START - sw_config()')
        else:
            print('STOP - je nutne zkontrolovat nastaveni na SW')

def sw_check_config_state(data):
    print('HERE')
#    if data['GE1-UP'] is not data['GE2-UP'] is not data['BAGG-UP']:
#        print('ALL PORTS is DOWN.')
#        print('RUN SW CONFIG')
#        return True
#    elif data['GE1-MAC'] and data['GE2-MAC'] and data['BAGG-MAC']:
#        print('NO MAC ADDRESSES')
#        print('RUN SW CONFIG')
#        return True
#    else:
#        return False
    
    
    
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
    data = mother_info(vstup)
    try:
        switch = data.split(',')[0]
        port = data.split(',')[1]
        vlan = data.split(',')[2]
    except Error as err:
        printx('ERR: Nejsou vsechny parametry pro zmenu configurace switche.', 'r')
    else:
        print(f'{switch}, {port}, {vlan}')
    #printx('# SWITCH SHOW CONFIG ##################################################','b')
    # vstupni informace jsou z motheru - ale u novych nebude vlan, tzn. ze bude to brat z excelu nebo ?
    #get_sw_config(data)
    # Varianta postupnych dotazu na konfiguraci
    exit(0)
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
    global DEBUG, ENV
    DEBUG = False
    # PROSTREDI - PROD / PREPRO
    ENV = 'PREPRO'
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
            #import_csv(vstup.f)
            new_way(vstup.f)
        else:
            printx('Chybne zadano, pravdepodobne jste nezadal vsechny pozadovane parametry!','r')
        # Informace o nastaveni switchi pro dany port
    else:
        printx('Nutne zadat vsechny parametry nebo pouzijte paremeter: -h pro help.','r')

if __name__ == "__main__":
    main()
    
# TODO
# switch    - kontrola nastaveni portu, bridge agre a mac pred zmenou nastaveni
#           - pri zpracovani zmen nasledne vypsat zmenu ?
# mysql - propojeni do mother db remotely ...