

# ****** Modules ******
import os
import json
import numpy as np
import requests
from dotenv import load_dotenv
import datetime
from time import sleep


# ****** Functions ******


# ****** Main ******

try:
    with open('setup.json', 'r') as file:
        setup_data = json.load(file)
except FileNotFoundError:
    print('Historical file not found')
except json.JSONDecodeError as err:
    print('JSON decoding error:', err)
except Exception as err:
    print('ERROR reading historical file:', err)

# --- Year update
report_date = setup_data['lastReport'].split('-')

if datetime.date.today().month > int(report_date[1]):
    print('Mostrar datos')

if datetime.date.today().month > int(report_date[0]):
    print('Actualizar year')

print('END\n')
