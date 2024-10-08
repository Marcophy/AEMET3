"""
AEMET temperature track project
Marco A. Villena, PhD.
2023 - 2024
"""

# ****** dunder variables ******
__project_name__ = "AEMET temperature track"
__author__ = "Marco A. Villena"
__email__ = "mavillena@ugr.es"
__version__ = "3.0"
__project_date__ = '2023 - 2024'


# ****** Modules ******
import os
import kernel
import json
from dotenv import load_dotenv
from datetime import datetime

# ****** MAIN ******
# --- Check the integrity of the structure file
files_control = {'historical': True, 'summary': True}  # Control if the historical and the summary file exist

# Definition of the files path
setup_path = os.path.join(os.getcwd(), 'config.json')
historical_path = os.path.join(os.getcwd(), 'data', 'historical.json')
summary_path = os.path.join(os.getcwd(), 'data', 'summary.json')

# Checking setup file
if os.path.exists(setup_path):
    setup_parameters = kernel.load_json(setup_path)
    if setup_parameters is False:
        exit()
    else:
        print('config.json --> OK')
else:
    print('ERROR: config.json file not found.')
    exit()

# Checking the data folder, historical, and summary files
if kernel.check_day(setup_parameters['workDay']):  # Check if today is the work day
    # Load the APIKEY from environment
    load_dotenv()
    api_key = os.getenv("APIKEY")
    if api_key is None:
        print('ERROR: API KEY cannot be loaded.')
        exit()

    # Checking data folder
    if os.path.exists(os.path.join(os.getcwd(), 'data')):  # Checking if <data> folder exists
        if os.path.exists(historical_path):  # Checking if <historical.json> file exists
            if not os.path.exists(summary_path):  # Checking <summary.json> file exists
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
        # Fix the last year as the previous year
        kernel.update_setup(setup_parameters, 'lastYear', datetime.now().year - 1, setup_path)

        # Download all historical data
        print('Generating new historical.json file. It may take some time ...')
        clean_data = []
        for year in range(setup_parameters['firstYear'], setup_parameters['lastYear'] + 1):
            print(year)
            year_data = kernel.download_year_data(year, setup_parameters['stationId'], api_key)
            if year_data is False:
                exit()
            else:
                clean_data.append(year_data)

        # Save historical.json data
        with open(historical_path, 'w') as file:
            json.dump(clean_data, file)

        files_control['historical'] = True
        print('historical.json file created.')

    else:
        # Update historical.json if it is outdated
        historical = kernel.load_json(historical_path)

        if datetime.now().year > historical[-1]['year'] + 1:
            print('Historical file outdated. Updating ...')
            current_year = kernel.download_year_data(datetime.now().year - 1, setup_parameters['stationId'], api_key)
            if current_year is False:
                exit()
            else:
                if len(current_year['tmax']) >= 365:  # If the new year has all data
                    temp_historical = kernel.load_json(historical_path)
                    temp_historical.append(current_year)
                    with open(historical_path, 'w') as file:
                        json.dump(temp_historical, file)

                    print('historical.json file updated.')
                    setup_parameters = kernel.update_setup(setup_parameters, 'lastYear', datetime.now().year - 1, setup_path)  # Update config.json
                    files_control['summary'] = False  # Force the regeneration of the summary file
        else:
            print('historical.json --> OK')

    if files_control['summary'] is False and files_control['historical'] is True:  #
        if kernel.post_process_data(historical_path, summary_path):
            print('summary.json file generated.')
            files_control['summary'] = True
        else:
            exit()
    else:
        print('summary.json --> OK')

    # --- Load data from summary file
    # Load summary file data
    if files_control['summary']:
        summary_data = kernel.load_json(summary_path)
        if summary_data is False:
            exit()

    # Download current year data from AEMET API
    current_data = kernel.download_year_data(datetime.now().year, setup_parameters['stationId'], api_key)
    if current_data is False:
        exit()
    else:
        # --- Plot result
        print('Plotting ...')
        kernel.plot_result(summary_data, current_data, setup_parameters)

    # Update the latest report date in config.json
    today = datetime.now().strftime('%Y-%m-%d')
    setup_parameters = kernel.update_setup(setup_parameters, 'lastReport', today, setup_path)


print('END')
