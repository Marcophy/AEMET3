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


def calculate_mean_values(in_path, in_file):
    file_path = os.path.join(in_path, in_file)
    # --- Read the historical file
    historical_data = load_json(file_path)
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

    # --- Collect the data and calcutate values
    for reg in historical_data:
        if reg['leapYear']:  # Remove the extra data measured the February 29th
            reg['tmax'].pop(59)
            reg['tmed'].pop(59)
            reg['tmin'].pop(59)
            reg['prec'].pop(59)

        if reg['completeYear'] is False:  # Define as 0 all None values and discount one value per None for the mean calculation
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

    output_path = os.path.join(in_path, 'summary.json')
    try:
        with open(output_path, 'w') as file:
            json.dump(json_output, file)

        return True
    except Exception as ferr:
        print('ERROR saving summary.json file:', ferr)
        return False


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


def get_current_data(in_url, in_api_key):
    data_json = get_data_from_url(in_url, in_api_key)

    if len(data_json) == 366:
        leap_year = True
    else:
        leap_year = False

    tmax_list = []
    tmed_list = []
    tmin_list = []
    prec_list = []
    for item in data_json:
        if leap_year and item != 59:
            pass
        else:
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

    return {'tmax': tmax_list, 'tmed': tmed_list, 'tmin': tmin_list, 'prec': prec_list}


def plot_result(in_summary, in_current):
    # TODO: Automatic adjustment of y-axis limits
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 11), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
    plt.subplots_adjust(hspace=0.05)  # Define the space between plots

    # Top panel: Temperature
    days = np.arange(len(in_summary['tmax']))
    days_current = np.arange(len(in_current['tmax']))
    ax1.plot(days_current, in_current['tmax'], color='red', linewidth=1, linestyle='dotted', label='Max. temperature')
    ax1.plot(days_current, in_current['tmin'], color='blue', linewidth=1, linestyle='dotted', label='Min. temperature')
    ax1.plot(days, in_summary['tmed'], color='purple', linewidth=1, label='Mean historical')
    ax1.fill_between(days, in_summary['tmin'], in_summary['tmax'], color='blue', alpha=0.1, label='Historical')
    ax1.set_ylabel('Temperature (°C)')
    ax1.legend()
    ax1.axis([0, 364, -10, 45])

    # Botton panel: Rain
    ax2.bar(days, in_summary['prec'], color='green', label='Historical')
    ax2.scatter(days_current, in_current['prec'], marker='_', color='blue', label='Current year')
    ax2.set_xlabel('Days')
    ax2.set_ylabel('Rain (mm)')
    ax2.legend()

    tick = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    plt.xticks(tick, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax2.axis([0, 364, -0.2, 15])

    # Show figure
    plt.show()

    return True
