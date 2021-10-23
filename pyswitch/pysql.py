#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# HELP
# https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#common-filter-operators
# https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#building-a-relationship

import os, sys
from sqlalchemy import Date, Column, ForeignKey, Integer, String, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

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


def get_server_switch_port(server_name):
    server = session.query(Machines).filter(Machines.name == server_name).filter(Machines.site_id == 1).first()
    return server.switch_port

def get_server_rack(server_name):
    server = session.query(Machines).filter(Machines.name == server_name).filter(Machines.site_id == 1).first()
    #print(server.rack_id)
    rack = session.query(Rack).filter(Rack.id == server.rack_id).first()
    return rack.name

def set_server_age(server_name, server_age):
    server = session.query(Machines).filter(Machines.name == server_name).filter(Machines.site_id == 1).first()
    server.age = server_age
    session.commit()

# MAIN

# QUERY
#print(get_servers(1))
#print(get_choice())
#print(get_server_age('bbhp1'))
server = 'gmmr1'
print(f'Server: {server} ma na switch {get_server_rack(server)} port: {get_server_switch_port(server)}')

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
