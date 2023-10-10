"""
AEMET temperature track project - Download Data
Marco A. Villena, PhD.
2023
"""

# ****** dunder variables ******
__project_name__ = "AEMET3 - Download data"
__author__ = "Marco A. Villena"
__email__ = "mavillenas@proton.me"
__version__ = "0.1"
__project_date__ = '2023'

# ****** Modules ******
import requests
import json
import os
from dotenv import load_dotenv
from time import sleep


# ****** Functions ******
def get_data_from_url(in_url, in_api_key):
    querystring = {"api_key": in_api_key}
    headers = {'cache-control': "no-cache"}
    response = requests.get(in_url, headers=headers, params=querystring)

    if response.status_code == 200:
        try:
            response_json = response.json()
            response.close()
            return response_json
        except ValueError as ferr:
            print('ERROR in the json conversion:', ferr)
            response.close()
            return None
    else:
        print('Status code: ', response.status_code)
        response.close()
        return None


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


# ****** Main ******
# --- Get the API KEY from environment variable ---
load_dotenv()
api_key = os.getenv("APIKEY")

station_id = '5514'  # ID of the meteorologic station
data_clean = []  # Output variable

# 1952 - 1985
for year in range(1952, 2022):

    request_url = generate_url(year, station_id)
    data_url = get_data_from_url(request_url, api_key)

    # --- Main script ---
    if data_url['estado'] == 200:
        print('Year:', year, '--> Found')
        data_json = get_data_from_url(data_url['datos'], api_key)
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
        for item in data_json:
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

        aux = {'year': year, 'completeYear': complete, 'leapYear': leap_year, 'tmax': tmax_list, 'tmed': tmed_list, 'tmin': tmin_list}
        data_clean.append(aux)

    else:
        print('Year:', year, '--> NO Found')
        print('Status:', data_url['estado'])
        print('Description:', data_url['descripcion'])

# --- Save result ---
with open('output_1952-2022.json', 'w') as file:
    json.dump(data_clean, file)

print('END')
