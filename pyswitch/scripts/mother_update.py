#!/usr/bin/python

import os
import sys
from datetime import datetime

sys.path.append('/root/mother/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mother.settings")

from django.db import models
from  mother.machines.models import Machine

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
	if stype == 'cpu':
        	Machine.objects.filter(name=server).update(cpu=value)
	elif stype == 'ram':
		Machine.objects.filter(name=server).update(ram=value)
	elif stype == 'os':
		Machine.objects.filter(name=server).update(os=value)
	elif stype == 'inventory': # musi byt unique
		Machine.objects.filter(name=server).update(inventory=value)
	elif stype == 'HeliosID': # musi byt unique
		Machine.objects.filter(name=server).update(HeliosID=value)
	elif stype == 'purchase_date':
		Machine.objects.filter(name=server).update(purchase_date=value)
	elif stype == 'qr_code': # musi byt unique
		Machine.objects.filter(name=server).update(qr_code=value)
	elif stype == 'age':
		Machine.objects.filter(name=server).update(age=value)
	elif stype == 'serial_number': # musi byt unique
		Machine.objects.filter(name=server).update(serial_number=value)
	elif stype == 'rack_id':
		Machine.objects.filter(name=server).update(rack_id=value)
	elif stype == 'rack_position':
	        Machine.objects.filter(name=server).update(rack_position=value)
	elif stype == 'maintainer':
	        Machine.objects.filter(name=server).update(maintainer=value)
	elif stype == 'machinegroups':
                Machine.objects.filter(name=server).update(machinegroups=value)
        elif stype == 'switch_port':
                Machine.objects.filter(name=server).update(switch_port=value)
	elif stype == 'name':
		Machine.objects.filter(name=server).update(name=value)

	print('Update was successfully completed.')
#	elif stype == 'state': # mail storages dell 730 -> 132
#		Machine.objects.filter(name=server).update(state_id=value)
	

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
	f = open('/root/mother/mother/machines/mother.log', 'a')
	text = td + ' ' + str(vstup) + '\n'
	f.write(text)
	f.close

   else:
       print('Usage: ./server_update.py SERVER_NAME TYPE TYPE_VALUE')
       exit(0)
