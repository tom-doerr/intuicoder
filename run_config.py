#!/usr/bin/env python3

import yaml

CONFIG_FILE_NAME = 'ic_config.yaml'

TEMPLATE_CONFIG = '''run_command:
'''

# check if the file exists
def config_file_exists():
    try:
        with open(CONFIG_FILE_NAME, 'r') as file:
            return True
    except FileNotFoundError:
        return False

def create_config_file():
    with open(CONFIG_FILE_NAME, 'w') as file:
        file.write(TEMPLATE_CONFIG)

if not config_file_exists():
    create_config_file()

def load_config():
    with open(CONFIG_FILE_NAME, 'r') as file:
        return yaml.safe_load(file)

config = load_config()


