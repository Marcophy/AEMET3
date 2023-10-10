import requests
import json
import os
from dotenv import load_dotenv


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
    url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{dateIniStr}/fechafin/{dateEndStr}/estacion/{stationid}"
    date_ini = str(in_year) + '-01-01T00%3A00%3A00UTC'  # Initial date (format: YYYY-MM-DDTHH%3AMM%3ASSUTC)
    date_end = str(in_year) + '-12-31T00%3A00%3A00UTC'  # Final date (format: AAAA-MM-DDTHH%3AMM%3ASSUTC)

    url = url.replace('{dateIniStr}', date_ini)
    url = url.replace('{dateEndStr}', date_end)
    url = url.replace('{stationid}', in_station)

    return url


# --- Get the API KEY from enviroment variable ---
load_dotenv()
api_key = os.getenv("APIKEY")

# Define the URL for request
station_id = '5514'  # ID of the metheorologic station
data_clean = []

for year in range(2000, 2005):
    print('Year:', year)
    request_url = generate_url(year, station_id)
    # print('Request url:', request_url)
    data_url = get_data_from_url(request_url, api_key)

    # --- Main script ---
    if data_url['estado'] == 200:
        # print('Data url:', data_url['datos'])
        data_json = get_data_from_url(data_url['datos'], api_key)
        # print(data_json)

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
            tmax_list.append(float(item['tmax'].replace(',', '.')))
            tmed_list.append(float(item['tmed'].replace(',', '.')))
            tmin_list.append(float(item['tmin'].replace(',', '.')))

        aux = {'year': year, 'completeYear': complete, 'leapYear': leap_year, 'tnax': tmax_list, 'tmed': tmed_list, 'tmin': tmin_list}
        data_clean.append(aux)

    else:
        print('Status:', data_url['estado'])
        print('Description:', data_url['descripcion'])


# --- Save result ---
with open('output.json', 'w') as file:
    json.dump(data_clean, file)

print('END')
