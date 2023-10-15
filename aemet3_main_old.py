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
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import requests
from dotenv import load_dotenv
import datetime
from time import sleep
import kernel


# ****** Functions ******
def load_setup(in_path):
    try:
        with open(in_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print('XXXX file not found')  # TODO: Modify the script to addapt the message to the file name
        return False
    except json.JSONDecodeError as err:
        print('JSON decoding error:', err)
        return False
    except Exception as err:
        print('ERROR reading historical file:', err)
        return False


def plot_result(in_tmax, in_tmed, in_tmin, in_current_tmax, in_current_tmed, in_current_tmin):
    x = np.arange(len(in_tmax))
    x_current = np.arange(len(in_current_tmax))

    # Create the graph
    plt.figure(figsize=(20, 11))
    plt.plot(x_current, in_current_tmax, color='red', linewidth=1, linestyle='dotted', label='Max. temperature')
    plt.plot(x_current, in_current_tmin, color='blue', linewidth=1, linestyle='dotted', label='Min. temperature')

    plt.plot(x, in_tmed, color='purple', linewidth=1, label='Mean historical')
    plt.fill_between(x, in_tmin, in_tmax, color='blue', alpha=0.1, label='Historical')

    # Labels and legend
    plt.ylabel('Temperature (°C)')
    plt.title('Daily Temperature')
    plt.legend()

    tick = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    plt.xticks(tick, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax = plt.gca()
    ax.axis([0, 364, -10, 45])

    # Add grid
    plt.grid(axis='x', color='lightgray', linestyle='--')

    # Show the graph
    plt.show()


def generate_url(in_year, in_station):
    """
    Generate a URL for retrieving climatological data from AEMET API.

    Args:
        in_year (int): The year for which the data is requested.
        in_station (str): The ID of the weather station.

    Returns:
        str: The generated URL.

    Raises:
        ValueError: If the input format is invalid.
    """

    if not isinstance(in_year, int) or not isinstance(in_station, str):
        raise ValueError("Invalid input format")

    url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{dateIniStr}/fechafin/{dateEndStr}/estacion/{stationid}"
    date_ini = str(in_year) + '-01-01T00%3A00%3A00UTC'  # Initial date (format: YYYY-MM-DDTHH%3AMM%3ASSUTC)
    date_end = str(in_year) + '-12-31T00%3A00%3A00UTC'  # Final date (format: AAAA-MM-DDTHH%3AMM%3ASSUTC)

    url = url.format(dateIniStr=date_ini, dateEndStr=date_end, stationid=in_station)

    return url


def get_data_from_url(in_url, in_api_key):
    """
    Retrieves data from a given URL using an API key.

    Args:
        in_url (str): The URL to retrieve data from.
        in_api_key (str): The API key to authenticate the request.

    Returns:
        dict or None: The response data in JSON format, or None if an error occurs.
    """
    headers = {'cache-control': "no-cache", 'api_key': in_api_key}
    querystring = {"api_key": in_api_key}

    with requests.get(in_url, headers=headers, params=querystring, timeout=10) as response:
        if response.status_code == 200:
            try:
                response_json = response.json()
                return response_json
            except ValueError as ferr:
                print('ERROR in the json conversion:', ferr)
                return None
        else:
            print('Status code: ', response.status_code)
            return None


# ****** Main ******
# --- Load setup parameters
setup = load_setup('setup.json')

# --- Load the APIKEY from enviroment
load_dotenv()
api_key = os.getenv("APIKEY")

# --- Get data from AEMET database
request_url = generate_url(datetime.date.today().year, setup['starionId'])
data_url = get_data_from_url(request_url, api_key)

if data_url['estado'] == 200:
    data_json = get_data_from_url(data_url['datos'], api_key)
    sleep(1)

    if len(data_json) == 366:
        leap_year = True
    else:
        leap_year = False

    tmax_list = []
    tmed_list = []
    tmin_list = []
    for item in data_json:
        if leap_year and item != 59:
            print('Leap year. Data ignored.')
        else:
            try:
                tmax_list.append(float(item['tmax'].replace(',', '.')))
            except:
                tmax_list.append(None)
                complete = False

            try:
                tmed_list.append(float(item['tmed'].replace(',', '.')))
            except:
                tmed_list.append(None)
                complete = False

            try:
                tmin_list.append(float(item['tmin'].replace(',', '.')))
            except:
                tmin_list.append(None)
                complete = False

    current_record = {'tmax': tmax_list, 'tmed': tmed_list, 'tmin': tmin_list}

# --- Process the historical data
file_path = os.getcwd() + '\\data\\' + setup['outputHistorical']
max_temp, mean_temp, min_temp, prec = kernel.calculate_mean_values(file_path)

# --- Plot results
plot_result(max_temp, mean_temp, min_temp, current_record['tmax'], current_record['tmed'], current_record['tmin'])


print('END\n')
