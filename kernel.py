"""
AEMET temperature track project
Marco A. Villena, PhD.
2023
"""

# ****** dunder variables ******
__project_name__ = "AEMET temperature track - KERNEL"
__author__ = "Marco A. Villena"
__email__ = "mavillenas@proton.me"
__version__ = "0.1"
__project_date__ = '2023'

# ****** Modules ******
import os
import json
import numpy as np
import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from datetime import datetime, timedelta
from time import sleep


# ****** Functions ******
def load_json(in_file):
    try:
        with open(in_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print('ERROR: ' + in_file + ' file not found.')
        return False
    except json.JSONDecodeError as err:
        print('JSON decoding error:', err)
        return False
    except Exception as err:
        print('ERROR reading historical file:', err)
        return False


def check_time(in_last_report, in_elapse):
    delta = datetime.today() - datetime.strptime(in_last_report, "%Y-%m-%d")
    if delta > timedelta(days=in_elapse):
        return True
    else:
        return False


def update_setup(in_json, in_id, in_new_parameter, in_path):
    in_json[in_id] = in_new_parameter

    with open(in_path, 'w') as file:
        json.dump(in_json, file, indent=2)

    return in_json


def calculate_mean_values(in_path, out_path):
    # --- Read the historical file
    historical_data = load_json(in_path)
    if historical_data is False:
        exit()

    # --- Initialize all variable
    tmax = np.zeros(365)
    tmed = np.zeros(365)
    tmin = np.zeros(365)
    prec = np.zeros(365)
    divider_max = np.full(365, len(historical_data))
    divider_med = np.full(365, len(historical_data))
    divider_min = np.full(365, len(historical_data))
    divider_prec = np.full(365, len(historical_data))

    # --- Collect the data and calculate values
    for reg in historical_data:
        # Clean the None values
        for index in range(365):
            if reg['tmax'][index] is None:
                reg['tmax'][index] = 0
                divider_max[index] -= 1

            if reg['tmed'][index] is None:
                reg['tmed'][index] = 0
                divider_med[index] -= 1

            if reg['tmin'][index] is None:
                reg['tmin'][index] = 0
                divider_min[index] -= 1

            if reg['prec'][index] is None:
                reg['prec'][index] = 0
                divider_prec[index] -= 1

        tmax = tmax + np.array(reg['tmax'])
        tmed = tmed + np.array(reg['tmed'])
        tmin = tmin + np.array(reg['tmin'])
        prec = prec + np.array(reg['prec'])

    # --- Calculate the mean value
    tmax = tmax / divider_max
    tmed = tmed / divider_med
    tmin = tmin / divider_min
    prec = prec / divider_prec

    # --- Generate JSON structure and save it in file
    json_output = {'tmax': tmax.tolist(), 'tmed': tmed.tolist(), 'tmin': tmin.tolist(), 'prec': prec.tolist()}

    try:
        with open(out_path, 'w') as file:
            json.dump(json_output, file)

        return True
    except Exception as ferr:
        print('ERROR saving summary.json file:', ferr)
        return False


def generate_url(in_year, in_station):  # OBSOLETE
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


def get_current_data(in_url, in_api_key, in_year):
    data_json = get_data_from_url(in_url, in_api_key)
    sleep(1)

    if len(data_json) == 366:
        leap_year = True
    else:
        leap_year = False

    if len(data_json) < 365:
        complete = False
    else:
        complete = True

    tmax_list = []
    tmed_list = []
    tmin_list = []
    prec_list = []
    for item in data_json:
        current_date = item['fecha'].split('-')
        if [int(current_date[1]), int(current_date[2])] != [2, 29]:
            try:
                tmax_list.append(float(item['tmax'].replace(',', '.')))
            except:
                tmax_list.append(None)

            try:
                tmed_list.append(float(item['tmed'].replace(',', '.')))
            except:
                tmed_list.append(None)

            try:
                tmin_list.append(float(item['tmin'].replace(',', '.')))
            except:
                tmin_list.append(None)

            try:
                prec_list.append(float(item['prec'].replace(',', '.')))
            except:
                prec_list.append(None)

    return {'year': in_year, 'completeYear': complete, 'leapYear': leap_year, 'tmax': tmax_list, 'tmed': tmed_list, 'tmin': tmin_list, 'prec': prec_list}


def download_year_data(in_year, in_station, in_api_key):
    # Generate the query url according to the input data
    url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{dateIniStr}/fechafin/{dateEndStr}/estacion/{stationid}"
    date_ini = str(in_year) + '-01-01T00%3A00%3A00UTC'  # Initial date (format: YYYY-MM-DDTHH%3AMM%3ASSUTC)
    date_end = str(in_year) + '-12-31T00%3A00%3A00UTC'  # Final date (format: AAAA-MM-DDTHH%3AMM%3ASSUTC)

    url = url.format(dateIniStr=date_ini, dateEndStr=date_end, stationid=in_station)

    # Get url of the output of the query
    data_url = get_data_from_url(url, in_api_key)
    if data_url['estado'] == 200:
        return get_current_data(data_url['datos'], in_api_key, in_year)
    else:
        print('ERROR')  # TODO: Identify the error
        return False


def plot_result(in_summary, in_current, in_parameters):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=tuple(in_parameters['figureSize']), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
    plt.subplots_adjust(hspace=0.05)  # Define the space between plots

    # Top panel: Temperature
    days = np.arange(len(in_summary['tmax']))
    days_current = np.arange(len(in_current['tmax']))
    ax1.plot(days_current, in_current['tmax'], color='red', linewidth=1, linestyle='dotted', label='Max. temperature')
    ax1.plot(days_current, in_current['tmin'], color='blue', linewidth=1, linestyle='dotted', label='Min. temperature')
    historical_label = 'Historical ' + str(in_parameters['firstYear']) + ' - ' + str(in_parameters['lastYear'])
    ax1.fill_between(days, in_summary['tmin'], in_summary['tmax'], color='blue', alpha=0.1, label=historical_label)
    ax1.plot(days, in_summary['tmed'], color='purple', linewidth=1, label='Mean historical')
    ax1.set_ylabel('Temperature (°C)', fontsize=14)
    ax1.legend(fontsize=12)
    ax1.set_title('Data from ' + in_parameters['stationName'])

    limit_max = max([max(in_summary['tmax']), max(in_current['tmax'])])
    limit_min = min([min(in_summary['tmin']), min(in_current['tmin'])])
    ax1.axis([0, 364, limit_min - 2, limit_max + 2])
    ax1.yaxis.set_major_locator(MultipleLocator(2))
    ax1.tick_params(axis='y', labelsize=12)

    ax1.grid(color='lightgray', linestyle='--', linewidth=0.5)

    if in_parameters['figureColor'][0]:  # Add color to the background of Temperature plot
        gradient = np.linspace(1, 0, 256).reshape(1, -1)
        gradient = np.vstack((gradient, gradient)).transpose()
        ax1.imshow(gradient, aspect='auto', cmap='jet', alpha=0.025, extent=ax1.get_xlim() + ax1.get_ylim())

    # Bottom panel: Rain
    ax2.bar(days, in_summary['prec'], color='green', label=historical_label)
    ax2.scatter(days_current, in_current['prec'], marker='_', color='blue', label='Current year')
    ax2.set_ylabel('Rain (mm)', fontsize=14)
    ax2.legend(fontsize=12)

    tick = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    plt.xticks(tick, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax2.tick_params(axis='both', labelsize=12)

    # Calculate the y-axis limit
    if None in in_summary['prec']:
        summary_max = max(value for value in in_summary['prec'] if value is not None)
    else:
        summary_max = max(in_summary['prec'])

    if None in in_current['prec']:
        current_max = max(value for value in in_current['prec'] if value is not None)
    else:
        current_max = max(in_current['prec'])
    limit_max = max([summary_max, current_max])
    ax2.axis([0, 364, -0.2, limit_max + 2])

    ax2.grid(axis='x', color='lightgray', linestyle='--', linewidth=0.5)

    if in_parameters['figureColor'][1]:  # Add color to the background of Rain plot
        ax2.set_facecolor('#f0fdff')

    # Show figure
    plt.show()

    return True
