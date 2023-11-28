# AEMET3
*Author: [**Marco A. Villena**](https://www.marcoavillena.com/)*

[AEMET3](https://github.com/Marcophy/AEMET3) (*[AEMET](https://www.aemet.es/en/portada) temperature track*) generates two graphs where the year temperature and the rain are tracked in a specific location of Spain.
To do that, the meteorologic information is downloaded using the API of [AEMET open data](https://opendata.aemet.es/centrodedescargas/inicio).

## How to use AEMET3
The purpose of this script is to be included as one of the startup apps of your OS. In this way, the temperature and rain report will
periodically (see *timeElapse* parameter from *config.json* file) be shown when you start your computer.

First, you must follow these steps:
1. Get your **API KEY** from the [AEMET open data](https://opendata.aemet.es/centrodedescargas/inicio) website.
2. Save your **API KEY** in an environment file **.env** as *APIKEY = "< your api key >"* in the main folder of this script.
3. Define all setup parameters in the **config.json** file (see section below).
4. Include the **aemet3_main.py** script in your startup list
   1. In Windows 11, create a shortcut of *aemet3_main.py* and paste it on *Win+r -> shell:startup* 

### Config.json file description
The setup parameters of this project are defined by the *JSON* file called <**config.json**>. This is the description of all parameters:

-  **workDay**: Day of the week in which the graph is displayed. Write *All* to always show the result.
   -  *Format: String*
   -  *Valid cases: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday, All* 
-  **firstYear**: First year of the historical data.
   -  *Format: Integer*
-  **lastYear**: Last year of the historical data. Typically, it should be one year before the current year.
   -  *Format: Integer*
-  **stationId**: ID number of the meteorological station. Check the documentation in [AEMET open data documentation](https://opendata.aemet.es/dist/index.html?).
   -  *Format: Integer*
-  **stationName**: Custom name used to identify the meteorological station.
   -  *Format: String*
-  **showMean**: Display/hide the historical mean temperature line in the output figure.
   -  *Format: Bool* 
-  **showRecords**: Display/hide the max/min historical records in the output figure. It also highlights the new records.
   - *Format: Bool*
-  **figureSize**: Size parameter for the figure generated.
   -  *Format: List [int, int]*
-  **figureColor**: Enable/disable the background color of each plot.
   -  *Format: List [bool, bool]*
-  **lastReport**: Date of the last report generated by the script.
    -  *Format: string "YYYY-MM-DD"*

### Dependencies
AMAT3 was developed using [Python v3.10](https://www.python.org/downloads/release/python-3100/). This is the list of non-standard libraries used by this code.
- [Numpy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [Dotenv](https://pypi.org/project/python-dotenv/)
- [Requests](https://requests.readthedocs.io/en/latest/)

