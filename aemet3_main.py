"""
AEMET temperature track project
Marco A. Villena, PhD.
2023
"""

# ****** dunder variables ******
__project_name__ = "AEMET temperature track"
__author__ = "Marco A. Villena"
__email__ = "mavillenas@proton.me"
__version__ = "0.1"
__project_date__ = '2023'

# ****** Modules ******
import kernel
import os
from dotenv import load_dotenv
import datetime

# ****** MAIN ******
# --- Check the integrity of the structure file
# Checking setup file
setup_path = os.path.join(os.getcwd(), 'setup.json')
if os.path.exists(setup_path):
    setup_parameters = kernel.load_json(setup_path)
    if setup_parameters is False:
        exit()
else:
    print('ERROR: setup.json file not found.')
    exit()

# Checking data folder
files_control = {'historical': True, 'summary': True}  # Control if the historical and the summary file exist
if os.path.exists(os.path.join(os.getcwd(), 'data')):  # Checking <data> folder
    if os.path.exists(os.path.join(os.getcwd(), 'data', 'historical.json')):  # Checking <historical.json> file inside the <data> folder
        if not os.path.exists(os.path.join(os.getcwd(), 'data', 'summary.json')):  # Checking <summary.json> file inside the <data> folder
            files_control['summary'] = False
    else:
        files_control['historical'] = False
        files_control['summary'] = False
else:
    os.mkdir('data')
    files_control['historical'] = False
    files_control['summary'] = False

# Regenerate files in case of any problem
if files_control['historical'] is False:
    pass

if files_control['summary'] is False and files_control['historical'] is True:
    if kernel.calculate_mean_values(os.path.join(os.getcwd(), 'data'), setup_parameters['outputHistorical']):
        files_control['summary'] = True
    else:
        exit()

# --- Load data from summary file and API
# Load summary file data
if files_control['summary']:
    summary_data = kernel.load_json(os.path.join(os.getcwd(), 'data', 'summary.json'))
    if summary_data is False:
        exit()

# Load the APIKEY from enviroment
load_dotenv()
api_key = os.getenv("APIKEY")

# Download current year data from AEMET API
request_url = kernel.generate_url(datetime.date.today().year, setup_parameters['starionId'])
data_url = kernel.get_data_from_url(request_url, api_key)
if data_url['estado'] == 200:
    current_data = kernel.get_current_data(data_url['datos'], api_key)
else:
    print('ERROR')
    exit()

# --- Plot resutl
kernel.plot_result(summary_data, current_data)

print('END')
