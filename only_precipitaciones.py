import os

import matplotlib.pyplot as plt

import kernel

data = kernel.load_json(os.path.join(os.getcwd(), 'data', 'historical.json'))

years = []
precipitaciones = []
for reg in data:
    years.append(reg['year'])
    long = len(reg['prec'])
    for i in range(len(reg['prec'])):
        if reg['prec'][i] is None:
            reg['prec'][i] = 0
            long -= 1

    precipitaciones.append(sum(reg['prec']) / long)

plt.bar(years, precipitaciones)
plt.show()
print('END')
