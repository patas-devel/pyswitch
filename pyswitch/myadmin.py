#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__app__ = 'MyAdmin'
__version__ = "1.41"
__author__ = "Iceman"
__copyright__ = "Copyright 2021"
__license__ = "GPL"


import csv, base64
from typing import Dict
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
DATA = []
mother_prepro = '10.20.100.133'
mother_prod = ''
sshserver = ''

# FUNC

def printx(text, c):
    if c == 'b':
        # info
        colour = 'blue'
    elif c == 'y':
        # variable show
        colour = 'yellow'
    elif c == 'g':
        # notes
        colour = 'green'
    elif c == 'r':
        # error
        colour = 'red'
    else:
        colour = 'white'
    print(colored(text, colour))


class Dict2class(object):
    
    SERVER = []
    
    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])
    
    def __repr__(self):
#        return "<dict2obj: %s="">" % self.__dict__
        attrs = str([x for x in dir(self) if "__" not in x])
        return "<dict2obj: %s="">" % attrs

def counter(csv_file):
    f = open(csv_file, 'r')
    params = len(f.readlines())
    g = open(csv_file, 'r')
    servers = len((g.readline()).split(','))
    printx(f'INFO: CSV PARSER - Input file: {servers} servers | {params} params.', 'b')
    return servers

def import_auto(csv_file):
    # AUTOCOUNT - mozne zadat rucne
    servers = counter(csv_file)
    dict = {}
    for s in range(0, servers):
        with open(csv_file) as f:
            reader = csv.reader(f)
            dict = {rows[0]:rows[s] for rows in reader}
        d = Dict2class(dict)
        DATA.append(d)
#    print(DATA[6].name)
    for srv in DATA[1:2]:
        prepare_data(srv)
            

def check_empty(data):
    OK = []
    for attr, value in data.__dict__.items():
        #print(f'{attr},{value}')
        if value == '' or value == None or value is None:
            printx(f'- Promenna {attr} ma prazdnou hodnotu {value}.','r') 
            OK.append(0)
    return True if 0 in OK else False
        

def decode_string(text):
    print(f'Encode: {text}')
    base64_message = text
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    print(f'Decode: {message}')
    
def encode_string(text):
    msg = text 
    message_bytes = msg.encode('ascii')
    msg_enc = base64.b64encode(message_bytes)
    msg_out = msg_enc.decode('ascii')
    return msg_out 
   
def prepare_data(data):
#    print(data)
#   CHECK VALUES
    # KDYZ TESTUJI CI NACITAM HODNOTU Z DB REMOTELY
    DB_OFF = True
    ok = check_empty(data)
    if ok:
        printx('CSV PARSER: V souboru jsou promenne, ktere nemaji definovou hodnotu - UKONCUJI BEH ZPRACOVANI.','r')
        exit(0)
    if ENV == 'PREPRO':
        try:
            DB_OFF = False
            if DB_OFF:
                # TODO: nova polozka - server_type ( zasae na dotaz)
                pom = db.session.query(db.ServerType).filter(db.ServerType.name == 'a2hosting').first()
                data.server_type = pom.id
                pom = db.session.query(db.Project).filter(db.Project.name == data.project).first()
                data.project = pom.id
                pom = db.session.query(db.Type).filter(db.Type.name == data.type).first()
                data.type = pom.id 
                pom = db.session.query(db.State).filter(db.State.name == data.state).first()
                data.state = pom.id
                pom = db.session.query(db.Rack).filter(db.Rack.name == data.rack).first()
                data.rack = pom.id
                usr = db.session.query(db.User).filter(db.User.username == data.maintainer).first()
                data.maintainer = usr.id
                # MACHINEGROUPS 
        #    srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
        #    mg = db.session.query(db.MachineGroup).filter(db.MachineGroup.machine_id == srv.id).first()
        #    obj = db.session.query(db.Group).filter(db.Group.id == mg.machinegroup_id).first()
            #print(obj.id)
        #    svalue = obj.id
        except AttributeError as err:
            print(f'ERR: Chyba cteni z DB {err}')
        # LOWER SWITCH NAME
        data.sw_name = data.sw_name.lower()
        sshserver = 'ssh root@10.20.100.133 '
        mother_script = '/root/mother/mother/machines/machines_update.py'

    elif ENV == 'PROD':
        sshserver = 'ssh root@mother.cent ' 
        mother_script = '/usr/share/pyshared/mother/networking/interfaces_update.py'  

    # QUERY TO MOTHER SERVER
    TEST = True
    if TEST:
        # OK
        sshserver = 'ssh root@10.20.100.133 '
        mother_script = '/root/mother/mother/machines/machines_update.py'
        data.state = encode_string(data.state)
        test = [ 
        sshserver + mother_script + ' ' + str(data.mother) + ' query project ' + str(data.project),
        sshserver + mother_script + ' ' + str(data.mother) + ' query type ' + str(data.type),
        sshserver + mother_script + ' ' + str(data.mother) + ' query maintainer ' + str(data.maintainer),
        sshserver + mother_script + ' ' + str(data.mother) + ' query rack ' + str(data.rack),
        sshserver + mother_script + ' ' + str(data.mother) + ' query state ' + str(data.state),
        sshserver + mother_script + ' ' + str(data.mother) + ' query server_type ' + str(data.server_type)
        ]
        for i in test:
            print(i)
            runcmd(i)
        #runcmd(cmd)  
    exit(0)
    # lower switch name
    data.sw_name = data.sw_name.lower()
    # ENCRYPT NOTES
    data.note = encode_string(data.notes)
    MOTHER_CMDS = {
        # nutne prevest na ID
        'project':  sshserver + mother_script + ' ' + str(data.mother) + ' project ' + str(data.project),  #name
        # nutne prevest na ID
        'type':     sshserver + mother_script + ' ' + str(data.mother) + ' type ' + str(data.type),  #name
        # nutne prevest na ID
        'srv_type':   sshserver + mother_script + ' ' + str(data.mother) + ' server_type ' + str(data.server_type),  #name
        'inventory':sshserver + mother_script + ' ' + str(data.mother) + ' inventory ' + str(data.inventory),  #name
        # nutne prevest na ID
        'state':    sshserver + mother_script + ' ' + str(data.mother) + ' state ' + str(data.state),  #name
        'cpu':      sshserver + mother_script + ' ' + str(data.mother) + ' cpu ' + str(data.cpu),  #name
        'ram':      sshserver + mother_script + ' ' + str(data.mother) + ' ram ' + str(data.ram),  #name
        'os':       sshserver + mother_script + ' ' + str(data.mother) + ' cpu ' + str(data.os),  #name
        'qr':       sshserver + mother_script + ' ' + str(data.mother) + ' qr_code ' + str(data.qr_code),  #name
        'purchase': sshserver + mother_script + ' ' + str(data.mother) + ' purchase_date ' + str(data.purchase_date),  #name
        'sn':       sshserver + mother_script + ' ' + str(data.mother) + ' serial_number ' + str(data.serial_number),  #name
        # NUTNE PREVEST na ID
        'rack':     sshserver + mother_script + ' ' + str(data.mother) + ' rack ' + str(data.rack),  #name
        'rack_pos': sshserver + mother_script + ' ' + str(data.mother) + ' rack_position ' + str(data.rack_position),  #name
        # NUTNE prevest na ID
        'maintainer': sshserver + mother_script + ' ' + str(data.mother) + ' maintainer ' + str(data.maintainer),  #name
        'switch_port': sshserver + mother_script + ' ' + str(data.mother) + ' switch_port ' + str(data.switch_port),  #name
        'notes':    sshserver + mother_script + ' ' + str(data.mother) + ' notes ' + str(data.notes),  #name
        # DB INTEFACE
        'mg_m':     sshserver + mother_script + ' ' + str(data.mother) + ' mgmt_mac ' + str(data.mgmt_mac),  #name
        'mg_p':     sshserver + mother_script + ' ' + str(data.mother) + ' mgmt_port ' + str(data.mgmt_port),  #name
        'mg_v':     sshserver + mother_script + ' ' + str(data.mother) + ' mgtm_vlan ' + str(data.mgmt_vlan),  #name
        'e_m':      sshserver + mother_script + ' ' + str(data.mother) + ' eth_mac ' + str(data.eth_mac),  #name
        'e_p':      sshserver + mother_script + ' ' + str(data.mother) + ' eth_port ' + str(data.eth_port),  #name
        'e_v':      sshserver + mother_script + ' ' + str(data.mother) + ' eth_vlan ' + str(data.eth_vlan),  #name
        'e1':       sshserver + mother_script + ' ' + str(data.mother) + ' e1_mac ' + str(data.e1_mac),  #name
        'e2':       sshserver + mother_script + ' ' + str(data.mother) + ' e2_mac ' + str(data.e2_mac),  #name
        'e3':       sshserver + mother_script + ' ' + str(data.mother) + ' e3_mac ' + str(data.e3_mac),  #name
        'sw':       sshserver + mother_script + ' ' + str(data.mother) + ' sw_name ' + str(data.sw_name),  #name
        'sw_port':  sshserver + mother_script + ' ' + str(data.mother) + ' sw_port ' + str(data.sw_port),  #name
        'sw_vlan':  sshserver + mother_script + ' ' + str(data.mother) + ' sw_vlan ' + str(data.sw_vlan),  #name
        'sw_desc':  sshserver + mother_script + ' ' + str(data.mother) + ' sw_desc ' + str(data.sw_desc),  #name
        # RESIT JAKO POSLEDNI
        'name': sshserver + mother_script + ' ' + str(data.mother) + ' name ' + str(data.name),  #name
    }

    # A. MOTHER REMOTE UPDATE     
    printx(f'INFO: MOTHER CMD - Processing Server: {data.mother}','b')
    printx('----------------------------------------------------------','b')
    for cmd in MOTHER_CMDS.values():
        print(cmd)
        if MOTHER_RUN:
            #runcmd(cmd)
            pass
    
    # B. SWITCH UPDATE
    if SWITCH_RUN:
        switch_info_auto(data)


def mother_info(vstup):
    server = vstup.server
    if vstup.i == 'mother' or vstup.ua != '':
        printx(f'# MOTHER INFO (DB: {MOTHER_DB}) #########\n','b')
    try: 
        #print(server)
        srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
        #print(srv.id)
        int = db.session.query(db.Interface).filter(db.Interface.machine_id == srv.id).first()
        #print(int.subnet_id) 
        subnet = db.session.query(db.Subnet).filter(db.Subnet.id == int.subnet_id).first()
        #print(subnet.vlan_id)
        vlan = db.session.query(db.Vlan).filter(db.Vlan.id == subnet.vlan_id).first()
        #print(vlan.name)
        typ = db.session.query(db.Type).filter(db.Type.id == srv.type_id).first()
        #print(srv.rack_id)
        ra = db.session.query(db.Rack).filter(db.Rack.id == srv.rack_id).first() 
        try:
            ip = round((int.ip))
        except TypeError as error:
            # pripad skynet1 ... why ?
            print(f'ERR: {error}')
            ipv = '-- '
        else:
            ipv = str(ipaddress.IPv4Address(ip))
        srv.qr_code = srv.qr_code
        switch = 'A' + ra.name.split(' ')[0]  
        if DEBUG:
            print(f'server id = {srv.id}')
            print(f'Type: {typ.name}')
            print(f'MAC: {int.mac},IP ADDR: {ipv}')
            print(f'RACK: {ra.name}')
    except AttributeError as err:
        printx(f'ERR: Server {server} doesnt exist!','r')
        if DEBUG:
            print(f'---> Error: {err}')
        exit(0)
    else:
        if vstup.i == 'mother':
            OUTPUT = {
                'SERVER:': srv.name,
                'MODEL:': typ.name,
                'QR CODE:': srv.qr_code,
                'RACK': ra.name,
                'SW_NAME:': switch,
                'SW_PORT:': int.port,
                'MAC_ADDR:': int.mac,
                'IP_ADDR': ipv,
                'VLAN_NAME': vlan.name,
                'VLAN:': vlan.id_vlan
            }
            for k, v in OUTPUT.items():
                print('{0:10}\t{1}'.format(k, v))


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
        if MOTHER:
            print('WRITE: ON')
            #runcmd(cmd)
        else:
            print('WRITE: OFF')
        

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
    out = output
    out = output.decode('utf-8').split('.')[0] # item from list
    out = out.strip()
    err = stderr
    # status - 0 ok, 1 fail
    print(f'{out}')
    #print(f'{err}') # err nic nevypisuje
    return out


def switch_info(data):
    # nactu parametry z motheru
#    if 'mother' in vstup:
#        info = mother_info(vstup)
#    else:
#        info = vstup
    printx('# SWITCH INFO ##################################################','b')
    print(f'ZADANO - switch: {data.sw_name}, port: {data.sw_port}, vlan: {data.sw_vlan}, desc: {data.sw_desc}\n')
    ss = sw.Switch(data.sw_name, sw.switches[data.sw_name], data.sw_port)
    sw_output = ss.get_config('check', data.sw_port)
    #print(sw_output)
    if sw_check_config_state(sw_output):
        print('START: Spoustim configuraci sw - sw_config.')
    else:
        printx('STOP: Nebudu spoustet sw configuraci.')


def switch_info_auto(data):
    # nactu parametry z motheru
#    if 'mother' in vstup:
#        info = mother_info(vstup)
#    else:
#        info = vstup
    printx('# SWITCH INFO ##################################################','b')
    print(f'ZADANO - switch: {data.sw_name}, port: {data.sw_port}, vlan: {data.sw_vlan}, desc: {data.sw_desc}\n')
    ss = sw.Switch(data.sw_name, sw.switches[data.sw_name], data.sw_port)
    sw_output = ss.get_config('check', data.sw_port)
    #print(sw_output)
    if sw_check_config_state(sw_output):
        print('START - sw_config()')
    else:
        print('STOP - je nutne zkontrolovat nastaveni na SW')

def sw_check_config_state(data):
  #  print(data)
    print('HERE')
    if not data['GE1-UP'] and not data['GE2-UP'] and not data['BAGG-UP']:
        print('ALL PORTS is DOWN.')
        print('RUN SW CONFIG')
        return True
    elif data['GE1-MAC'] and data['GE2-MAC'] and data['BAGG-MAC']:
        print('NO MAC ADDRESSES')
        print('RUN SW CONFIG')
        return True
    else:
        return False
    
    
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

    
def init():
    global DEBUG, ENV, MOTHER_RUN, SWITCH_RUN, MOTHER_DB
    # PROSTREDI - PROD / PREPRO
    DEBUG = False
    ENV = 'PREPRO'
    MOTHER_RUN = False
    SWITCH_RUN = False
    MOTHER_DB = 'LOCAL'
    os.system('clear')
    printx(f'# MYADMIN {__version__} #', 'g')
    printx(f'----------------\n', 'g')
    printx(f'# ENVIRONMENT:\t\t{ENV}', 'y')
    printx(f'# MOTHER DB:\t\t{MOTHER_DB}', 'y')
    printx(f'# MOTHER RUN UPDATE:\t{MOTHER_RUN}', 'y')
    printx(f'# SWITCH RUN UPDATE:\t{SWITCH_RUN}', 'y')
    printx(f'# DEBUG:\t\t{DEBUG}\n','y')
    #printx(f'-----------------------------\n','y')

# MAIN
def main():
    # Zakladni nastaveni a debug on/off 
    init()
    # Vyhodnoceni vstupnich parametry
    test = ['a-server4'] # DEBUG
    vstup = get_input(test)
    # Informace o zadanem serveru z mother
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
            #new_way(vstup.f)
            import_auto(vstup.f)
            
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