"""
AEMET temperature track project - Calculate Data
Marco A. Villena, PhD.
2023
"""

# ****** dunder variables ******
__project_name__ = "AEMET3 - Calculate data"
__author__ = "Marco A. Villena"
__email__ = "mavillenas@proton.me"
__version__ = "0.1"
__project_date__ = '2023'

# ****** Modules ******
import json
import numpy as np
import matplotlib.pyplot as plt

# ****** Main ******
input_file = 'historical.json'

try:
    with open(input_file, 'r') as file:
        historical_data = json.load(file)

except FileNotFoundError:
    print('Historical file not found')
except json.JSONDecodeError as err:
    print('JSON decoding error:', err)
except Exception as err:
    print('ERROR reading historical file:', err)

tmax = np.zeros(365)
tmed = np.zeros(365)
tmin = np.zeros(365)
divider_max = np.ones(365) * len(historical_data)
divider_med = np.ones(365) * len(historical_data)
divider_min = np.ones(365) * len(historical_data)

for reg in historical_data:
    print('Year:', reg['year'])
    if reg['leapYear']:  # Remove the extra data measured the February 29th
        reg['tmax'].pop(59)
        reg['tmed'].pop(59)
        reg['tmin'].pop(59)

    if not reg['completeYear']:  # Define as 0 all None values and discount one value per None for the maen calculation
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

    tmax = tmax + np.array(reg['tmax'])
    tmed = tmed + np.array(reg['tmed'])
    tmin = tmin + np.array(reg['tmin'])

# --- Calculate the mean value
tmax = tmax / divider_max
tmed = tmed / divider_med
tmin = tmin / divider_min


# ----------------------------------------------------------------------
# Create an array of indices for the x-axis (you can use dates or other real values)
x = np.arange(len(tmax))

# Create the graph
plt.plot(x, tmax, color='red', linewidth=0.5, label='Tmax')
plt.plot(x, tmed, color='purple', linewidth=1, label='Tmed')
plt.plot(x, tmin, color='blue', linewidth=0.5, label='Tmin')
plt.fill_between(x, tmin, tmax, color='blue', alpha=0.1)

# Labels and legend
plt.ylabel('Temperature (°C)')
plt.title('Daily Temperature')
plt.legend()

tick = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
plt.xticks(tick, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax = plt.gca()
ax.axis([0, 365, -5, 45])

# Add grid
plt.grid(axis='x', color='lightgray', linestyle='--')

# Show the graph
plt.show()



print('END\n')
