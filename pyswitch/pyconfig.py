#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://wiki.python.org/moin/ConfigParserExamples

import configparser

class Config():

    SETUP_FILE = 'settings.ini'
    
    def __init__(self, source=''):
        self.source = source

    def load_config(self):
        settings_file = Config.SETUP_FILE
        self.settings = configparser.ConfigParser()
        self.settings._interpolation = configparser.ExtendedInterpolation()
        self.settings.read(settings_file)

    def get_value(self, cf_value):
        self.load_config()
        if self.source != '':
            return self.settings.get(self.source, cf_value)
        else:
            print('Neni zadano menu udat!')
        

# TEST
#test = Config()
#test.load_config()
#print(test.get_value('switch', 'user'))