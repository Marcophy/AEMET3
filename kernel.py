"""
AEMET temperature track project
Marco A. Villena, PhD.
2023
"""

# ****** dunder variables ******
__project_name__ = "AEMET temperature track - KERNEL"
__author__ = "Marco A. Villena"
__email__ = "mavillena@ugr.es"
__version__ = "2.0"
__project_date__ = '2023'

# ****** Modules ******
import json
import copy
import numpy as np
import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from datetime import datetime, timedelta
from time import sleep


# ****** Functions ******
def load_json(in_file):
    """
    Open a JSON file.

    Args:
        in_file (str): Path of the JSON file

    Returns:
        Dict: The information loaded from the JSON file.
    """

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


def check_day(in_workday):
    """
        Check if the current week day
    Args:
        in_workday (str): The day to check against the current week day.

    Returns:
        bool: True if the input day matches the current week day or if 'All' is provided, False otherwise.
    """

    week_day = datetime.now().strftime("%A")
    if in_workday == 'All':
        return True
    elif in_workday == week_day:
        return True
    else:
        return False


def update_setup(in_json, in_id, in_new_parameter, in_path):
    """
    Update the setup JSON file with a new parameter value.

    Args:
        in_json (dict): The original JSON dictionary.
        in_id (str): The ID of the parameter to be updated.
        in_new_parameter (any): The new value for the parameter.
        in_path (str): The path to the JSON file.

    Returns:
        dict: The updated JSON dictionary.
    """

    updated_json = copy.deepcopy(in_json)
    updated_json[in_id] = in_new_parameter

    if updated_json.get(in_id) != in_json.get(in_id):
        with open(in_path, 'w') as file:
            json.dump(updated_json, file, indent=2)

    return updated_json


def post_process_data(in_path, out_path):
    """
    Calculate the mean values of temperature and precipitation from historical data.

    Args:
        in_path (str): The path to the input JSON file.
        out_path (str): The path to save the output JSON file.

    Returns:
        bool: True if the calculation and saving are successful, False otherwise.
    """

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

    tmax_record = np.full(365, -100)
    tmin_record = np.full(365, 100)

    # --- Collect the data and calculate values
    for reg in historical_data:
        # Clean the None values
        for index in range(365):
            if reg['tmax'][index] is None:
                reg['tmax'][index] = 0
                divider_max[index] -= 1
            else:  # Calculate maximum temperature record
                if reg['tmax'][index] > tmax_record[index]:
                    tmax_record[index] = reg['tmax'][index]

            if reg['tmed'][index] is None:
                reg['tmed'][index] = 0
                divider_med[index] -= 1

            if reg['tmin'][index] is None:
                reg['tmin'][index] = 0
                divider_min[index] -= 1
            else:  # Calculate minimum temperature record
                if reg['tmin'][index] < tmin_record[index]:
                    tmin_record[index] = reg['tmin'][index]

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
    json_output = {'tmax': tmax.tolist(), 'tmed': tmed.tolist(), 'tmin': tmin.tolist(), 'recordMax': tmax_record.tolist(), 'recordMin': tmin_record.tolist(), 'prec': prec.tolist()}

    try:
        with open(out_path, 'w') as file:
            json.dump(json_output, file)

        return True
    except Exception as ferr:
        print('ERROR saving summary.json file:', ferr)
        return False


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
    """
    Retrieve current data for a given year from a URL using an API key.

    Args:
        in_url (str): The URL to retrieve data from.
        in_api_key (str): The API key to authenticate the request.
        in_year (int): The year for which data is being retrieved.

    Returns:
        dict: A dictionary containing the data for the specified year, including temperature and precipitation values, and flags for leap year and completeness.
    """

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
            except ValueError:
                tmax_list.append(None)

            try:
                tmed_list.append(float(item['tmed'].replace(',', '.')))
            except ValueError:
                tmed_list.append(None)

            try:
                tmin_list.append(float(item['tmin'].replace(',', '.')))
            except ValueError:
                tmin_list.append(None)

            try:
                prec_list.append(float(item['prec'].replace(',', '.')))
            except ValueError:
                prec_list.append(None)

    return {'year': in_year, 'completeYear': complete, 'leapYear': leap_year, 'tmax': tmax_list, 'tmed': tmed_list, 'tmin': tmin_list, 'prec': prec_list}


def download_year_data(in_year, in_station, in_api_key):
    """
    Downloads daily climatological data for a specific year and station using the AEMET API. The AEMET API does not allow to download more
    than 6 months in only one shoot, for this reason the year is downloaded in two times.

    Args:
        in_year (int): The year for which data is being downloaded.
        in_station (str): The station ID for the data retrieval.
        in_api_key (str): The API key for authentication.

    Returns:
        dict: A dictionary containing temperature and precipitation values for the year, with leap year and completeness flags.
    """

    # Generate the query url according to the input data
    url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{dateIniStr}/fechafin/{dateEndStr}/estacion/{stationid}"
    date_ini = str(in_year) + '-01-01T00%3A00%3A00UTC'  # Initial date (format: YYYY-MM-DDTHH%3AMM%3ASSUTC)
    date_mid1 = str(in_year) + '-06-30T00%3A00%3A00UTC'  # Initial date (format: YYYY-MM-DDTHH%3AMM%3ASSUTC)
    date_mid2 = str(in_year) + '-07-01T00%3A00%3A00UTC'  # Initial date (format: YYYY-MM-DDTHH%3AMM%3ASSUTC)
    date_end = str(in_year) + '-12-31T00%3A00%3A00UTC'  # Final date (format: AAAA-MM-DDTHH%3AMM%3ASSUTC)

    url_first = url.format(dateIniStr=date_ini, dateEndStr=date_mid1, stationid=in_station)
    url_second = url.format(dateIniStr=date_mid2, dateEndStr=date_end, stationid=in_station)

    # Get url of the output of the query
    # First part of the year
    data_url = get_data_from_url(url_first, in_api_key)
    if data_url is not None and data_url.get('estado') == 200:
        first_part = get_current_data(data_url.get('datos'), in_api_key, in_year)
    else:
        print('ERROR: Data cannot be downloaded from API.')
        print('\tDescription:', data_url['description'])
        return False

    # Second part of the year
    data_url = get_data_from_url(url_second, in_api_key)
    if data_url is not None and data_url.get('estado') == 200:
        second_part = get_current_data(data_url.get('datos'), in_api_key, in_year)
    else:
        print('ERROR: Data cannot be downloaded from API.')
        print('\tDescription:', data_url['description'])
        return False

    # Concatenate the two parts of the year
    first_part['tmax'] = first_part['tmax'] + second_part['tmax']
    first_part['tmed'] = first_part['tmed'] + second_part['tmed']
    first_part['tmin'] = first_part['tmin'] + second_part['tmin']
    first_part['prec'] = first_part['prec'] + second_part['prec']

    return first_part


def get_new_record(in_current, in_summary):
    """
    Calculate new temperature records based on current data and historical records.

    Args:
        in_current (dict): Dictionary containing current temperature data including 'tmax' and 'tmin'.
        in_summary (dict): Dictionary containing historical temperature records including 'recordMax' and 'recordMin'.

    Returns:
        tuple: Two lists containing indices and corresponding temperatures for new maximum and minimum temperature records.
    """

    maxs = []
    mins = []

    for i in range(len(in_current['tmax'])):
        if in_current['tmax'][i] > in_summary['recordMax'][i]:
            maxs.append([i, in_current['tmax'][i]])

        if in_current['tmin'][i] < in_summary['recordMin'][i]:
            mins.append([i, in_current['tmin'][i]])

    return maxs, mins


def plot_result(in_summary, in_current, in_parameters):
    """
    Plot the temperature and precipitation data for a specific location over time. Customize the plot
    appearance based on input parameters such as figure size, color, and data display options. Show historical
    records, mean temperature line, and highlight new maximum and minimum temperature records. Display the
    data in two panels: one for temperature and the other for precipitation. The x-axis represents days of
    the year, and the y-axes show temperature in degrees Celsius and rainfall in millimeters. Return True
    after displaying the plot.

    Args:
        in_summary (dict): A dictionary containing summary temperature and precipitation data.
        in_current (dict): A dictionary containing current temperature and precipitation data.
        in_parameters (dict): A dictionary containing parameters for customizing the plot.

    Returns:
        bool: True if the plot is displayed successfully.

    Note:
        - `in_summary` and `in_current` should have keys: 'tmax', 'tmin', 'prec', 'recordMax', 'recordMin', 'tmed'.
        - `in_parameters` should have keys: 'figureSize', 'firstYear', 'lastYear', 'showRecords', 'showMean', 'stationName', 'figureColor'.
        - The plot consists of two panels: one for temperature and the other for precipitation.
        - The temperature panel shows maximum and minimum temperature data along with historical records and mean temperature line.
        - The precipitation panel displays historical precipitation data and current year's precipitation data.
        - The x-axis represents days of the year, and the y-axes show temperature in degrees Celsius and rainfall in millimeters.
        - The plot appearance can be customized using the input parameters.
    """

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=tuple(in_parameters['figureSize']), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
    plt.subplots_adjust(hspace=0.05)  # Define the space between plots

    # Top panel: Temperature
    days = np.arange(len(in_summary['tmax']))
    days_current = np.arange(len(in_current['tmax']))
    ax1.plot(days_current, in_current['tmax'], color='red', alpha=0.5, linewidth=1, label='Max. temperature')
    ax1.plot(days_current, in_current['tmin'], color='blue', alpha=0.5, linewidth=1, label='Min. temperature')

    historical_label = 'Historical ' + str(in_parameters['firstYear']) + ' - ' + str(in_parameters['lastYear'])
    ax1.fill_between(days, in_summary['tmin'], in_summary['tmax'], color='#c1c1ff', alpha=0.5, label=historical_label)
    if in_parameters['showRecords']:  # Show the historical records
        ax1.plot(days, in_summary['recordMax'], color='red', alpha=0.2, linewidth=1, linestyle='dashed', label='Max. temp. record')
        ax1.plot(days, in_summary['recordMin'], color='blue', alpha=0.2, linewidth=1, linestyle='dashed', label='Min. temp. record')

    if in_parameters['showMean']:  # Show the historical mean temperature line
        ax1.plot(days, in_summary['tmed'], color='purple', alpha=0.6, linewidth=0.75, label='Historical mean temp.')

    if in_parameters['showRecords']:  # Highlight the new max/min temperature record
        new_max, new_min = get_new_record(in_current, in_summary)
        if new_max:
            ax1.scatter(*zip(*new_max), color='red', alpha=0.7, s=10, label='New record (max.)')
        if new_min:
            ax1.scatter(*zip(*new_min), color='blue', alpha=0.7, s=10, label='New record (min.)')

    ax1.set_ylabel('Temperature (°C)', fontsize=14)
    ax1.legend(fontsize=12)
    ax1.set_title('Data from ' + in_parameters['stationName'])

    if in_parameters['showRecords']:  # Y-axis limit with records
        limit_max = max([max(in_summary['recordMax']), max(in_current['tmax'])])
        limit_min = min([min(in_summary['recordMin']), min(in_current['tmin'])])
    else:  # Y-axis limit without records
        limit_max = max([max(in_summary['tmax']), max(in_current['tmax'])])
        limit_min = min([min(in_summary['tmin']), min(in_current['tmin'])])

    ax1.axis([0, 364, limit_min - 3, limit_max + 3])
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

