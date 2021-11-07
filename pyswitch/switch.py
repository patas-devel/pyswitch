#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# INFO: script na zobrazeni informaci ze switche a upraveni jeho configurace
# KDO: iceman
# KDY: @ 10/2021

import os
import pynetwork as net
import pydb as db
import argparse
import configparser
import pyswitch as switch
from termcolor import colored

def config():
    # https://wiki.python.org/moin/ConfigParserExamples
    settings_file = 'settings.ini'
    settings = configparser.ConfigParser()
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read(settings_file)
    return settings
 



# MAIN
def main():
    os.system('clear')
    print(colored('##################################################', 'green'))
    setup = config()
    sw = switch.Switch('AB13.TTC', '10.33.240.43', '26')
    sw.swuser = setup.get('switch', 'user')
    sw.swpass = setup.get('switch', 'pass')
    sw.swtype = setup.get('switch', 'type')
    cmd = 'display version'
    sw.get_info(cmd)


#sw = Switch('','AB13.TTC', '10.33.240.43', '26')
#sw.get_info('display interface brief')
#sw.get_config()
#show_config()
#mac_find('0021-5ef0-adb4')
#show_config('','')
#mac_find('00215ef0adb4')

    # OK
    server = 'bbbe1'
    mix = db.session.query(db.Subnet).join(db.Interface).join(db.Machine).filter(db.Machine.name == server).first()
    #print(f'---Vlan_id={mix.vlan_id}')
    mix2 = db.session.query(db.Vlan).filter(db.Vlan.id == mix.vlan_id).first()
    print(f'Vlan-name:\t{mix2.name}\nVlan-cislo:\t{mix2.id_vlan}')


if __name__ == "__main__":
    main()











#def main():
#    os.system('clear')


# MAIN
#if __name__ == "__main__":
#   main()