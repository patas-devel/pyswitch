#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
from typing import Counter, NewType
from sqlalchemy import Date, Column, ForeignKey, Integer, String, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import interfaces, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.sqltypes import DECIMAL, VARCHAR
import ipaddress

Base = declarative_base()
# DB
mysql_pass_local = ''
mysql_pass_prod = ''
# INIT CONNECTION ans SESSIONS
# DB LOCAL
conn_str = 'mysql://root:' + mysql_pass_local + '@127.0.0.1/mother'
engine = create_engine(conn_str, echo=False)
conn = engine.connect()
DBSession = sessionmaker(bind=engine)
session = DBSession()

class Domain(Base):
    __tablename__ = 'domains'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255))
    type = Column(VARCHAR(6))
    notified_serial = Column(Integer)
    master = Column(VARCHAR(128))
    last_check = Column(Integer)
    account = Column(VARCHAR(40))

class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer)
    name = Column(VARCHAR(255))
    type = Column(VARCHAR(6))
    content = Column(VARCHAR(255))
    ttl = Column(Integer)
    prio = Column(Integer)
    change_date = Column(Integer)
    interface_id = Column(Integer)

class Machine(Base):
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

class Rack(Base):
    __tablename__ = 'machines_rack'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(128))
    spc_sockets = Column(Integer)
    network_ports = Column(Integer) 
    management_ports = Column(Integer)
    filled_positions = Column(VARCHAR(255))
    location_id = Column(Integer)
    migration = Column(Integer)

class Location(Base):
    __tablename__ = 'machines_location'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(128))

class Interface(Base):
    __tablename__ = 'networking_interface'
    id = Column(Integer, primary_key=True)
    ip = Column(DECIMAL(39,0))
    subnet_id = Column(Integer, ForeignKey('networking_subnet.id'), nullable=False)
    machine_id = Column(Integer, ForeignKey('machines_machine.id'), nullable=False)
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
    dhcp_template = Column(VARCHAR(128))
    notes = Column(VARCHAR(128)) 
    domain_id = Column(Integer)
    # Text(4294000000) as longtext
    rev_domain_id = Column(Integer)
    
class Vlan(Base):
    __tablename__ = 'networking_vlan'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(128))
    id_vlan = Column(Integer)
    notes = Column(VARCHAR(128))




# MAIN - BASIC OPERATION
#os.system('clear')
#server_name = 'vmadb1'
#
##MACHINE
#srv = session.query(Machine).filter(Machine.name == server_name and Machine.site_id ==1).first()
#server_id = srv.id
#print(f'Server:\t\t{srv.name}')
#
## INTERFACE
#int = session.query(Interface).filter(Interface.machine_id == server_id).first()
##print(f'mac={int.mac}, type={int.type}, port={int.port}, subnet={int.subnet_id}')
#subnet_id = int.subnet_id
##print(f'interface_id:\t{subnet_id}')
#
## RACK
#rk = session.query(Rack).filter(Rack.id == srv.rack_id).first()
#print(f'rack:\t\t{rk.name}')
#
#
## SUBNET
#t1 = session.query(Subnet).filter(Subnet.id == subnet_id).first()
##print(f'subnet:\t{t1.vlan_id}')
#vlan_id = t1.vlan_id
#ip = round((t1.ip))
#ipv = str(ipaddress.IPv4Address(ip))
##print(ipv)
#
## VLAN
##t2 = session.query(Vlan).filter(Vlan.id == vlan_id).first()
##print(f'Vlan_name={t2.name}, Vlan_c={t2.id_vlan}')
#
## OK
#mix = session.query(Subnet).join(Interface).join(Machine).filter(Machine.name == server_name).first()
##print(f'---Vlan_id={mix.vlan_id}')
#mix2 = session.query(Vlan).filter(Vlan.id == mix.vlan_id).first()
#print(f'Vlan-name:\t{mix2.name}\nVlan-cislo:\t{mix2.id_vlan}')

#server = srv.name + '.cent.'
#test = session.query(Record).filter(Record.content == server).all()
#for i in test:
#    print(i.content)


#INSERT INTO mother.machines_machine (name, project_id_id, project_id, server_type_id, cpu, ram, os, inventory, HeliosID, qr_kod, qr_code, purchase_date, age, type_id, serial_number, rack_id, rack_position, maintainer_id, notes, snmp_community, nagios_system_id, spc, switch_port, state_id, site_id) VALUES('', NULL, NULL, NULL, 0, NULL, NULL, '', NULL, NULL, NULL, NULL, '0', 0, '', NULL, NULL, NULL, '', '', NULL, '', '', 0, 0);