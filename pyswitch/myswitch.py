#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# INFO: script na zobrazeni informaci ze switche a upraveni jeho configurace
# KDO: iceman
# KDY: @ 10/2021

import os
#import pynetwork as net
import pydb as db
import argparse
import configparser
import pyswitch as sw
from termcolor import colored
import pyconfig as conf


# MAIN
def main():
    os.system('clear')
    print(colored('##################################################', 'green'))
    #s = sw.Switch('AB13.TTC', '10.33.240.43', '26')
    #cmd = 'display version'
    #s.get_info(cmd)
    # OK
    server = 'bbbe1'
    mix = db.session.query(db.Subnet).join(db.Interface).join(db.Machine).filter(db.Machine.name == server).first()
    print(f'VLAN_id={mix.vlan_id}')
    mix2 = db.session.query(db.Vlan).filter(db.Vlan.id == mix.vlan_id).first()
    print(f'Vlan-name:\t{mix2.name}\nVlan-cislo:\t{mix2.id_vlan}')


if __name__ == "__main__":
    main()











#def main():
#    os.system('clear')


# MAIN
#if __name__ == "__main__":
#   main()