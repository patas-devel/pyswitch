#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__app__ = 'MyAdmin'
__version__ = "1.5"
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

# TODO
# prepsat printx
# nahradit mother_id za machine_id
# pres connect to switch, overit ze je dostupny !

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
    mother_id = ''
    
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
    printx(f'INFO - Parsing csv file: [{csv_file}] content: {servers} servers | {params} params.\n', 'b')
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
    if DEBUG:
        print(f'DEBUG - Show data values: {DATA[6].name}')
    # GRR - NUMBER OF SERVERS TO PROCESS
    for srv in DATA[1:2]:
        prepare_data(srv)
            

def check_empty(data):
    OK = []
    for attr, value in data.__dict__.items():
        if DEBUG:
            print(f'DEBUG - check empty: {attr},{value}')
        # vyhodit radku se zacatkem na #
        if '#' in attr:
            continue
        if value == '' or value == None or value is None:
            printx(f'- Variable: {attr} has empty value:  {value}.','r') 
            OK.append(0)
    return True if 0 in OK else False
        
def encode_net(data, txt):
    if txt == 'mgmt':
        mac = (data.mgmt_mac).replace(':', '').lower()
        port = data.mgmt_port
        msg = mac + ';' + port
    elif txt == 'eth' or txt == 'e1' or txt == 'e2' or txt == 'e3':
        mac = (data.eth_mac).replace(':', '').lower()
        port = data.eth_port
        msg = mac + ';' + port
    message_bytes = msg.encode('ascii')
    msg_enc = base64.b64encode(message_bytes)
    msg_out = msg_enc.decode('ascii')
    return msg_out 

def decode_string(data, text):
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
   
   
def mother_script_query(data, mother_script):
    data.state = encode_string(data.state)
    mother_query = {
        'machine_id': sshserver + mother_script + ' ' + str(data.mother) + ' query machine ' + str(data.mother),
        'project_id': sshserver + mother_script + ' ' + str(data.mother) + ' query project ' + str(data.project),
        'type_id': sshserver + mother_script + ' ' + str(data.mother) + ' query type ' + str(data.type),
        'maintainer_id': sshserver + mother_script + ' ' + str(data.mother) + ' query maintainer ' + str(data.maintainer),
        'rack_id': sshserver + mother_script + ' ' + str(data.mother) + ' query rack ' + str(data.rack),
        'state_id': sshserver + mother_script + ' ' + str(data.mother) + ' query state ' + str(data.state),
        'server_type_id': sshserver + mother_script + ' ' + str(data.mother) + ' query server_type ' + str(data.server_type),
        'machinegroups_id': sshserver + mother_script + ' ' + str(data.mother) + ' query groups ' + encode_string(data.machinegroups)
    }
    if RUNQUERY:
        printx(f'INFO - Query to mother over script - server: {data.mother}\n','b')
    # !!! pozor kdyz neprobehne mother_query - dosadi se data.project= cely command !!!
    for k, v in mother_query.items():
        if DEBUG:
            print(f'DEBUG - k: {k:16} v: {v:50}')
        if RUNQUERY:
            mother_query[k] = runcmd(v).split(':')[1]
        else:
            pass
    #print(mother_query)
    Dict2class.mother_id = mother_query['machine_id']
    data.project = mother_query['project_id']
    data.type = mother_query['type_id']
    data.maintainer = mother_query['maintainer_id']
    data.rack = mother_query['rack_id'] 
    data.state = mother_query['state_id']
    data.server_type = mother_query['server_type_id']
    data.machinegroups = mother_query['machinegroups_id']
    return data

def mother_update(data, mother_script):
    MOTHER_CMDS = {
        # nutne prevest na ID
        'project':  sshserver + mother_script + ' ' + str(data.mother) + ' project_id ' + str(data.project),  #name
        # nutne prevest na ID
        'type':     sshserver + mother_script + ' ' + str(data.mother) + ' hw_type ' + str(data.type),  #name
        # nutne prevest na ID
        'srv_type':   sshserver + mother_script + ' ' + str(data.mother) + ' server_type ' + str(data.server_type),  #name
        'inventory':sshserver + mother_script + ' ' + str(data.mother) + ' inventory ' + str(data.inventory),  #name
        # nutne prevest na ID
        'state':    sshserver + mother_script + ' ' + str(data.mother) + ' state ' + str(data.state),  #name
        'cpu':      sshserver + mother_script + ' ' + str(data.mother) + ' cpu ' + str(data.cpu),  #name
        'ram':      sshserver + mother_script + ' ' + str(data.mother) + ' ram ' + str(data.ram),  #name
        'os':       sshserver + mother_script + ' ' + str(data.mother) + ' os ' + str(data.os),  #name
        'qr':       sshserver + mother_script + ' ' + str(data.mother) + ' qr_code ' + str(data.qr_code),  #name
        'purchase': sshserver + mother_script + ' ' + str(data.mother) + ' purchase_date ' + str(data.purchase_date),  #name
        'sn':       sshserver + mother_script + ' ' + str(data.mother) + ' serial_number ' + str(data.serial_number),  #name
        # NUTNE PREVEST na ID
        'rack':     sshserver + mother_script + ' ' + str(data.mother) + ' rack ' + str(data.rack),  #name
        'rack_pos':   sshserver + mother_script + ' ' + str(data.mother) + ' rack_position ' + str(data.rack_position),  #name
        # NUTNE prevest na ID
        'maintainer': sshserver + mother_script + ' ' + str(data.mother) + ' maintainer ' + str(data.maintainer),  #name
        'groups':  sshserver + mother_script + ' ' + str(data.mother) + ' machinegroups ' + str(data.machinegroups),
        'switch_port': sshserver + mother_script + ' ' + str(data.mother) + ' switch_port ' + str(data.switch_port),  #name
        'notes':    sshserver + mother_script + ' ' + str(data.mother) + ' notes ' + str(data.notes),  #name
        # !! POZOR VKLADA SE MACHINE_ID + specialne se encoduje
        'mgmt':     sshserver + mother_script + ' ' + str(data.mother_id) + ' mgmt ' + encode_net(data, 'mgmt'),
        #'mg_v':     sshserver + mother_script + ' ' + str(data.mother) + ' mgtm_vlan ' + str(data.mgmt_vlan),  #name
        'eth':      sshserver + mother_script + ' ' + str(data.mother_id) + ' eth ' + encode_net(data, 'eth'),
        #'e_v':      sshserver + mother_script + ' ' + str(data.mother) + ' eth_vlan ' + str(data.eth_vlan),  #name
        'e1':       sshserver + mother_script + ' ' + str(data.mother_id) + ' e1 ' + encode_net(data, 'e1'),
        'e2':       sshserver + mother_script + ' ' + str(data.mother_id) + ' e2 ' + encode_net(data, 'e2'),
        'e3':       sshserver + mother_script + ' ' + str(data.mother_id) + ' e3 ' + encode_net(data, 'e3'),
        # RESIT JAKO POSLEDNI
        'name': sshserver + mother_script + ' ' + str(data.mother) + ' name ' + str(data.name),  #name
        # TODO - nagiosgroup chybi 
    }
    return MOTHER_CMDS
    
    
def prepare_data(data):
    if DEBUG:
        print(f'DEBUG - Input data: {data}')
    # CONTROL INPUT VALUES
    if check_empty(data):
        printx('CSV PARSER: V souboru jsou promenne, ktere nemaji definovou hodnotu - UKONCUJI BEH ZPRACOVANI.','r')
        if CHECK_STOP:
            exit(0)
            
    # DEV
    if ENV == 'DEV':
        try:
            data.mother= 'gmn1003-old' # test purpose
            pom = db.session.query(db.Machine).filter(db.Machine.name == data.mother).first()
            data.server_type = pom.server_type_id
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
            srv = db.session.query(db.Machine).filter(db.Machine.name == data.mother).first()
            mg = db.session.query(db.MachineGroup).filter(db.MachineGroup.machine_id == srv.id).first()
            data.machinegroups = mg.machinegroup_id
            # NAGIOS GROUPS
            # gm-cache = 116, gm-storage = 69
            
            
        except AttributeError as err:
            print(f'ERR - Chyba cteni z DB {err}')
        else:
            printx('INFO - db query run succesully.', 'b') 
            # LOCAL VARIABLES    
            # SWITCH NAME LOW CASE
            # FIXME: kam to dat ?
            data.sw_name = data.sw_name.lower()
            sshserver = 'ssh root@10.20.100.133 '
            mother_script = sshserver + ' /root/mother/mother/machines/machines_update.py'
            CMD = mother_update(data, mother_script) 

    # PREPRO
    elif ENV == 'PREPRO':
        data.sw_name = data.sw_name.lower()
        data.notes = encode_string(data.notes)
        sshserver = 'ssh root@10.20.100.133 '
        mother_script = sshserver + ' /root/mother/mother/machines/machines_update.py'
        mother_script_query(data, mother_script) 
        CMD = mother_update(data, mother_script) 

    # PRODUCTION
    elif ENV == 'PROD':
        data.sw_name = data.sw_name.lower()
        data.notes = encode_string(data.notes)
        sshserver = 'ssh root@mother.cent ' 
        mother_script = sshserver + ' /usr/share/pyshared/mother/machines/machines_update.py'  
        # QUERY TO MOTHER SERVER
        mother_script_query(data, mother_script)
        CMD = mother_update(data, mother_script) 
    
    # PROCESSING DATA        
    if RUNPROCS:
        process_data(data, CMD)
    
    # SWITCH 
    if RUNSWITCH:
        switch_info(data)

        
def process_data(data, CMD):
    printx(f'\nINFO: MOTHER CMD - Processing Server: {data.mother}','b')
    printx('----------------------------------------------------------','b')
    for cmd in CMD.values():
        print(cmd)
        if RUNSSH:
            runcmd(cmd)



def mother_info(vstup):
    server = vstup.server
    printx(f'INFO - MOTHER DB: {MOTHER_DB}\n','b')
    try: 
        #print(server)
        srv = db.session.query(db.Machine).filter(db.Machine.name == server).first()
        int = db.session.query(db.Interface).filter(db.Interface.machine_id == srv.id).first()
        subnet = db.session.query(db.Subnet).filter(db.Subnet.id == int.subnet_id).first()
        vlan = db.session.query(db.Vlan).filter(db.Vlan.id == subnet.vlan_id).first()
        typ = db.session.query(db.Type).filter(db.Type.id == srv.type_id).first()
        ra = db.session.query(db.Rack).filter(db.Rack.id == srv.rack_id).first()
        if DEBUG:
            print(f'DEBUG - DB QUERY INFO: {server}-{srv.id}, {int.subnet_id},{subnet.vlan_id},{vlan.id},{vlan.name},{srv.rack_id}')
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
        printx(f'ERROR - Server {server} doesnt exist!','r')
        if DEBUG:
            print(f'---> Error: {err}')
    else:
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
    if 'Traceback' in out:
        printx(f'\nERR - when script running on remote host with next of the command: {cmd}\nERR - {out}', 'r')
        exit(0)
    else:
        return out


def switch_info(data):
    # nactu parametry z motheru
#    if 'mother' in vstup:
#        info = mother_info(vstup)
#    else:
#        info = vstup
    printx('# SWITCH INFO ##################################################','b')
    print(f'INFO - server_mac: {data.eth_mac}, switch: {data.sw_name}, port: {data.sw_port}, vlan: {data.sw_vlan}, desc: {data.sw_desc}\n')
    ss = sw.Switch(data.sw_name, sw.switches[data.sw_name], data.sw_port)
    sw_output = ss.get_config('check', data)
    out = sw_output
    for k, v in out.items():
        print(f'{k:10} {v}')
    if sw_check_output(sw_output):
        printx('START - RUN SWITCH UPDATE CONFIGURATION.','g')
        switch_config(data)
    else:
        printx('QUITING.....','r')

def sw_check_output(sw_out):
  #  print(data)
    ge1_loop = sw_out['GE1-CONF'][0].split(':')[1].strip()
    ge1_broad = sw_out['GE1-CONF'][1].split(':')[1].strip()
    ge1_link = sw_out['GE1-CONF'][2].split(':')[1].strip()
    ge1_vlan = sw_out['GE1-CONF'][3].split(':')[1].strip() 
    ge2_loop = sw_out['GE2-CONF'][0].split(':')[1].strip()
    ge2_broad = sw_out['GE2-CONF'][1].split(':')[1].strip()
    ge2_link = sw_out['GE2-CONF'][2].split(':')[1].strip()
    ge2_vlan = sw_out['GE2-CONF'][3].split(':')[1].strip() 
    bagg_dynamic = sw_out['BAGG-CONF'][0].split(':')[1].strip()
    bagg_vlan = sw_out['BAGG-CONF'][1].split(':')[1].strip()
    print(f'{ge1_loop}, {ge1_broad}, {ge1_link}, {ge1_vlan}')
    print(f'{ge2_loop}, {ge2_broad}, {ge2_link}, {ge2_vlan}')
    print(f'{bagg_dynamic}, {bagg_vlan}')
    print('\nINFO - VYHODNOCENI VYSTUPU ZE SWITCHe\n-------------------------------------------------\n')
    if not sw_out['GE1-UP'] and not sw_out['GE2-UP'] and not sw_out['BAGG-UP'] and not sw_out['BAGG-S']:
        printx('INFO - All ports is DOWN and BAGG not selected ports.\nWe can run update sw config.','g')
        return True
    elif not sw_out['GE1-MAC'] and not sw_out['GE2-MAC'] and not sw_out['BAGG-MAC'] and not sw_out['BAGG-S']:
        printx('INFO - NO MACs on ports and BAGG not selected ports.\n We can run update sw config.','g')
        return True
    elif not sw_out['GE1-MAC'] and not sw_out['GE2-MAC'] and sw_out['BAGG-MAC'] and not sw_out['BAGG-S'] and \
            bagg_vlan == '3':
        return True
    elif ge1_vlan == '0' or ge2_vlan == '0' or bagg_vlan == '0':
        printx('WARNING: CHECK SWITCH PORT CONFIGURATION !!!!','r')
        return False
    else:
        printx('WARNING: CHECK SWITCH PORT CONFIGURATION !!!!','r')
        return False
    
def switch_config(data):
    printx('# SWITCH UPDATE COFIGURATION ###########################################','b')
    # Varianta postupnych dotazu na konfiguraci
#    text = printx('\nContinue to update switch configuration ? (change - vlan and description) ? ( Yes | No): ','r')
#    choice = input()
    choice = 'yes'
    if choice.lower() == 'yes':
        CMDS = []
        # CHANGE VLAN + DESC
        c1 = 'interface bridge-aggregation ' + str(data.sw_port)
        c2 = 'port access vlan ' + str(data.sw_vlan)
        c3 = 'description ' + str(data.sw_desc)
        c4 = 'interface GigabitEthernet 1/0/' + str(data.sw_port)
        c5 = 'description ' + str(data.sw_desc)
        c6 = 'interface GigabitEthernet 2/0/' + str(data.sw_port)
        c7 = 'description ' + str(data.sw_desc)
        CMDS = (c1, c2, c3, c4, c5, c6, c7)
        print(f'commands: {CMDS}')
        print(f'switch info: {data.sw_name},{data.sw_vlan}, {data.sw_port}')
        s = sw.Switch(data.sw_name, sw.switches[data.sw_name], data.sw_port)
        s.set_config(CMDS)
        printx('################################################################','b')
    else:
        printx('Exiting ...', '')


def init():
    global DEBUG, ENV, MOTHER_DB, CHECK_STOP, RUNSSH, RUNSWITCH, RUNPROCS, RUNQUERY
    # PROSTREDI - PROD  | PREPRO | DEV
    ENV = 'PREPRO'
    CHECK_STOP = False
    RUNPROCS = False
    RUNQUERY = False 
    RUNSSH = False 
    RUNSWITCH = True
    MOTHER_DB = 'LOCAL DB [Updated: 09.12.2021]'
    DEBUG = False
    printx(f'# MYADMIN {__version__} #', 'g')
    printx(f'----------------\n', 'g')
    # PROD (script to DB mother prod, script to switch)
    # PREPRO (script to DB mother prepro, script to switch)
    # DEV (locale DB with data from mother prod)
    printx(f'# ENVIRONMENT:\t\t{ENV}', 'r')
    printx(f'# MOTHER DB:\t\t{MOTHER_DB}', '')
    printx(f'------------------------------------------------------','')
    printx(f'# DEBUG:\t\t{DEBUG} [Set debug mode]','y')
    printx(f'# PROCESS DATA:\t\t{RUNPROCS} [Processing data from csv file]', 'y')
    printx(f'# QUERY DATA:\t\t{RUNQUERY} [Queries to server]', 'y')
    printx(f'# STOP CHECK:\t\t{CHECK_STOP} [If find any error/mistaches then stop]', 'y')
    printx(f'# RUN SSH:\t\t{RUNSSH} [Run commands over ssh]', 'y')
    printx(f'# SWITCH:\t\t{RUNSWITCH} [Connecting to switch and get info and more]', 'y')
    printx(f'----------------------------------------------------------------------------\n','y')
    
def get_input():
    ''' Parser na vstupni parametry '''

    # Required positional argument
    parser = argparse.ArgumentParser(description='Information about utility:')
    parser.add_argument('server', nargs='?', help='Server hostname - [gmnXXXX]')

    # Optional
    parser.add_argument('-i', nargs='?', help='Information about server - [mother] or [switch]')
    parser.add_argument('-f', nargs='?', help='Import csv config file and automatic update mother parameters and switch configuration - [file_name]')
    try:
        args = parser.parse_args()
    except Error as err:
        print(f'ERR: {err}')
    else:
        pass
    if DEBUG:
        print(f'DEBUG: Inputs params: {args}\n')
    return args      

# MAIN
def main():
    # Clear
    os.system('clear')
    # Vyhodnoceni vstupnich parametry
    #vstup = get_input()
    if len(sys.argv) > 2:
        init()    
        vstup = get_input()
        if vstup.i != None:
            if vstup.i == 'mother':
                mother_info(vstup)
            elif vstup.i == 'switch':
                print('SWITCH INFO - soon')
                #switch_info(vstup)
            else:
                printx('Nezadan zdroj informaci ! Moznosti: mother, switch.','r')
        # Aktualizace parametru v motheru nebo zmena nastaveni switche (vlan, desc)
        elif vstup.f != None:
            import_auto(vstup.f)
        else:
            printx('ERROR - Unknown parameters, try it with -h!','r')
        # Informace o nastaveni switchi pro dany port
    else:
        printx('ERROR - Input parameters required, for more information: -h pro help.\n','r')

if __name__ == "__main__":
    main()