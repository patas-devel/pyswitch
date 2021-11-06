#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# HELP
# https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#common-filter-operators
# https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#building-a-relationship

import os, sys
from typing import NewType
from sqlalchemy import Date, Column, ForeignKey, Integer, String, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.sqltypes import DECIMAL, VARCHAR


Base = declarative_base()
# DB
mysql_pass_local = 'jsem.SQL1'
mysql_pass_prod = 'f72d647a45bded34f637008b4fa10109345bfcff5d3c7b5973a2260f5815f76e'

class Machines(Base):
    __tablename__ = 'machines_machine'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    server_type_id = Column(Integer)
    cpu = Column(Integer)
    ram = Column(Integer)
    os = Column(String(4))
    age = Column(Integer)
    inventory = Column(String(32), nullable=False)
    HeliosID = Column(String(10))
    purchase_date = Column(Date)
    type_id = Column(Integer)
    serial_number = Column(String(128))
    rack_id = Column(Integer)
    rack_position = Column(Integer)
    maintainer_id = Column(Integer)
    notes = Column(String(128))
    snmp_community = Column(String(32))
    nagios_system_id = Column(Integer)
    spc = Column(String(32))
    switch_port = Column(String(32))
    state_id = Column(Integer)
    site_id = Column(Integer)

class Domain(Base):
    __tablename__ = 'domains'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255))
    type = Column(VARCHAR(6))
    notified_serial = Column(Integer)
    master = Column(VARCHAR(128))
    last_check = Column(Integer)
    account = Column(VARCHAR(40))

class Rack(Base):
    __tablename__ = 'machines_rack'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    spc_sockets = Column(Integer)
    network_ports = Column(Integer)
    management_ports = Column(Integer)
    filled_positions = Column(Integer)
    location_id = Column(Integer)
    migration = Column(Integer)

class Network(Base):
    __tablename__ = 'networking_interface'
    id = Column(Integer, primary_key=True)
    ip = Column(DECIMAL(39,0))
    subnet_id = Column(Integer)
    machine_id = Column(Integer)
    type = Column(VARCHAR(32))
    mac = Column(VARCHAR(17)) 
    is_primary = Column(Integer)
    dhcp_options = Column(VARCHAR(256))
    port = Column(Integer)

class Subnet(Base):
    __tablename__ = 'networking_subnet'
    id = Column(Integer, primary_key=True)
    ip = Column(DECIMAL(39,0))
    vlan_id = Column(Integer)
    prefix = Column(Integer)
    default_gw_mac = Column(VARCHAR(17))
    dhcp_templat = Column(text)
    notes = Column(text) 
    # Text(4294000000) as longtext
    domain_id = column(Integer)
    rev_domain_id = Column(Integer)

class Vlan(Base):
    __tablename__ = 'networking_vlan'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(128))
    vlan_id = column(Integer)
    notes = Column(text)


# INIT CONNECTION ans SESSIONS
# DB LOCAL
conn_str = 'mysql://root:' + mysql_pass_local + '@127.0.0.1/mother'

# DB PROD
#conn_str = 'mysql://root:' + mysql_pass_prod + '@127.0.0.1:3306/mother'
#conn_str = 'mysql://root:' + mysql_pass_local + '@127.0.0.1:3306/mother'

engine = create_engine(conn_str, echo=False)
conn = engine.connect()
DBSession = sessionmaker(bind=engine)
session = DBSession()


# MAIN SQL COMMANDS
#session.query(Machines).all()
# vypise 
#ma = session.query(Machines).first()
#print('Server name: ' + str(ma.name))

# SELECT : vypise vse dle filtru
def get_servers(query):
    servers = []
    for name in session.query(Machines.name).filter(Machines.site_id == query).filter(Machines.type_id != 130).filter(Machines.server_type_id != 146).order_by(Machines.name):
        servers.append(name[0])
    #print(servers)
    return servers

def get_choice(query):
    servers = []
    for name in session.query(Machines.name).order_by(Machines.name):
        servers.append(name[0])
    #print(servers)
    return servers

def set_server_param(server_name, server_type, server_value):
    server = session.query(Machines).filter(Machines.name == server_name).filter(Machines.site_id == 1).first()
    if server_type == 'os':
         server.os = server_value
    elif server_type == 'ram':
         server.ram = server_value
    elif server_type == 'cpu':
        server.cpu == server_value
    else:
        print('chybne zadany typ!')
    session.commit()  

def get_server_age(server_name):
    #print(server_name)
    server = session.query(Machines).filter(Machines.name == server_name).filter(Machines.site_id == 1).first()
    server_age_purchase = str(server.purchase_date)
    if '-' in server_age_purchase:
        today = date.today()
        age = datetime.strptime(server_age_purchase, '%Y-%m-%d')
        #print(age)
        #print(today)
        server_age  = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
        #print(server_age)
        return server_age
    else:
        return 0

# GET
def get_server_rack(server_name):
    server = session.query(Machines).filter(Machines.name == server_name and Machines.site_id == 1).first()
#    print(server.rack_id)
    rack = session.query(Rack).filter(Rack.id == server.rack_id).first()
#    print(rack)
    return rack.name

def get_server_id(server_name):
    server = session.query(Machines).filter(Machines.name == server_name and Machines.site_id == 1).first()
#    print(server.id)
    return server.id

# GET
def get_switch_port(server_id, etype):
    if etype == 'eth':
        port = session.query(Network).filter(Network.machine_id == server_id and Network.type == etype and Network.is_primary == 1).first()
    elif etype == 'mgmt':
        port = session.query(Network).filter(Network.machine_id == server_id and Network.type == etype).first()
    else:
        print('nebyl zadan typ adapteru!')
    return port.port  

def get_mgmt_switch_port(server):
    rack = session.query(Rack).filter(Rack.name == server_rack).first()
    return rack.management_ports

##################################################
# SET
def set_server_age(server_name, server_age):
    server = session.query(Machines).filter(Machines.name == server_name and Machines.site_id == 1).first()
    server.age = server_age
    session.commit()


# MAIN
os.system('clear')
server = 'gmn1005'
try:
    server_rack = get_server_rack(server)
    server_id = get_server_id(server)
except AttributeError as error:
    print('Server pravdepodobne neexistuje.')
else:
    access = get_switch_port(server_id, 'eth')
    mgmt =  get_switch_port(server_id, 'mgmt')
    print(f'MOTHER:\n\tSERVER:\t{server}\n\tRACK:\t{server_rack}\n\tPORT:\t{access}\n\tMGMT:\t{mgmt}')

# COUNT - OK
#all = session.query(func.count(Machines.name)).all()
#print(all)

# UPDATE - OK -> update 1 prvku
#server = session.query(Machines).filter_by(name='server-name1').first()
#server.name = 'server-name2'
#session.commit() 

# DELETE -> OK
#server = session.query(Machines).filter_by(name='server-name2').first()
#session.delete(server)
#session.commit()

# INSERT - OK -> pridani nove machine
#server = Machines(name='server-name', server_type_id='147', snmp_community='dads', spc='dad', switch_port=10, state_id='1', site_id=2,cpu='2', serial_number='xxx-xxx',inventory='HAHAH', type_id='1', maintainer_id = '21', notes='asdfadsfa')
#session.add(server)
#session.commit()