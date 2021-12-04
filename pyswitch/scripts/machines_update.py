#!/usr/bin/python

import os
import sys
import base64
from datetime import datetime

sys.path.append('/root/mother/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mother.settings")

from django.db import models
from  mother.machines.models import Machine

#print(Machine._meta.get_all_field_names())

# VARS
LOG_FILE = '/root/mother/mother/machines/machines.log'

# FUNC
def server_create():
	##m = Machine.objects.create(name='a-server6', serial_number='ABCEFGHIJK', project_id_id=1, inventory='testovaci6', cpu=4, ram=16, os='d10', HeliosID='123123', qr_code='12312346', type_id=132, state_id=1, site_id=1)
	pass

def server_update(vstup):
	server = vstup[1]
	stype = vstup[2]
	value = vstup[3]
	data_in = 'Vstupy: ' + str(server) + ',' + str(stype) + ',' + str(value)
	print(data_in)
	if stype == 'cpu':
		try:
	        	Machine.objects.filter(name=server).update(cpu=value)
		except Exception, e:
			print('ERR: ' + str(e))
		else:
			print('OK: Hodnota CPU uspesne aktualizovana.')
        elif stype == 'project_id':
                Machine.objects.filter(name=server).update(project_id=value)
	elif stype == 'ram':
		Machine.objects.filter(name=server).update(ram=value)
	elif stype == 'os':
		Machine.objects.filter(name=server).update(os=value)
	elif stype == 'type':
	        Machine.objects.filter(name=server).update(type=value)
        elif stype == 'state':
                Machine.objects.filter(name=server).update(state=value)
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
	elif stype == 'rack':
		Machine.objects.filter(name=server).update(rack=value)
	elif stype == 'rack_position':
	        Machine.objects.filter(name=server).update(rack_position=value)
	elif stype == 'maintainer':
		try:
		        Machine.objects.filter(name=server).update(maintainer=value)
		except Exception, e:
			print('ERR: ' + str(e))
		else:
			print('OK: Maintainer byl aktualizovan.')

#	elif stype == 'machinegroups':
#                MachineGroup_machine.objects.filter(name=server).update(machinegroups=value)
        elif stype == 'switch_port':
                Machine.objects.filter(name=server).update(switch_port=value)
	elif stype == 'name':
		try:
			Machine.objects.filter(name=server).update(name=value)
		except Exception, e:
			print(e)
		else:
			print('OK: Server uspesne prejmenovan.')
        elif stype == 'notes':
		# decode notes
	        base64_message = value
        	base64_bytes = base64_message.encode('ascii')
	        message_bytes = base64.b64decode(base64_bytes)
        	value = message_bytes.decode('ascii')
		#print(value)
		# read current note
		note = Machine.objects.filter(name=server).get()
		note_current = note.notes
		if note_current != '':
			note_new = value + '\n' + note_current
		else:
			note_new = value
                Machine.objects.filter(name=server).update(notes=note_new)
	

def user_add():
	pass
    #m = Machine.objects.update(name=''
    #from django.contrib.auth.models import User
    #user = User.objects.create_user('aaaa','aaaa@xyz.com','sn@pswrd')
    #user.save()


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
	f = open(LOG_FILE, 'a')
	text = td + ' ' + str(vstup) + '\n'
	f.write(text)
	f.close

   else:
       print('Usage: ./machines_update.py SERVER_NAME TYPE TYPE_VALUE')
       exit(0)
