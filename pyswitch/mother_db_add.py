#!/usr/bin/python

# POPIS: Otestovana na mother prepro stroji

import os
import sys
sys.path.append('/root/mother/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mother.settings")

from django.db import models
from  mother.machines.models import Machine

#print(Machine._meta.get_all_field_names())
os.system('clear')

m = Machine.objects.create(name='a-server6', serial_number='ABCEFGHIJK', project_id_id=1, inventory='testovaci6', cpu=4, ram=16, os='d10', HeliosID='123123', qr_code='12312346', type_id=132, state_id=1, site_id=1)
