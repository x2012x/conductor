'''
Created on Feb 12, 2022

@author: x2012x
'''
import yaml
import os

config = yaml.safe_load(open('resources/config/application.yaml'))

__protected_config = 'resources/config/protected.yaml'

if os.path.exists(__protected_config):
    config.update(yaml.safe_load(open(__protected_config)))
