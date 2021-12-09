#!/usr/bin/python

import os
import sys
import base64
from datetime import datetime

sys.path.append('/root/mother/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mother.settings")

from django.db import models
from  mother.networking.models import Interface

#print(Machine._meta.get_all_field_names())

def server_create():
	##m = Machine.objects.create(name='a-server6', serial_number='ABCEFGHIJK', project_id_id=1, inventory='testovaci6', cpu=4, ram=16, os='d10', HeliosID='123123', qr_code='12312346', type_id=132, state_id=1, site_id=1)
	pass

def server_update(vstup):
	server = vstup[1]
	stype = vstup[2]
	value = vstup[3]
	print(server)
	print(stype)
	print(value)
	if stype == 'mgmt' or 'eth' or 'e1' or 'e2' or 'e3':
		print(value)
		mac_addr = value.split('-')[0]
		sw_port = value.split('-')[1]
		try:
		        Interface.objects.create(machine_id=server, type=stype, mac=mac_addr, port=sw_port)
		except ValueError, e:
			print('ERR: Zaznam nebyl aktualizovan.' + str(e))
		else:
			print('OK: Zaznam byl aktualizovan.')
	else:
		pass
	

def user_add():
    #m = Machine.objects.update(name=''
    #from django.contrib.auth.models import User
    #user = User.objects.create_user('aaaa','aaaa@xyz.com','sn@pswrd')
    #user.save()
    pass


# MAIN
os.system('clear')
try:
    vstup = sys.argv
except:
    print('Nejsou zadane vsechny parametry!')
else:
   if len(vstup) > 3:
   	server_update(vstup)
        now = datetime.now()
        td = now.strftime("%d-%m-%Y %H:%M:%S")
	f = open('/root/mother/mother/networking/interfaces.log', 'a')
	text = td + ' ' + str(vstup) + '\n'
	f.write(text)
	f.close

   else:
       print('Usage: ./interfaces_update.py SERVER_ID TYPE TYPE_VALUE')
       exit(0)
