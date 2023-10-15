import matplotlib.pyplot as plt
import numpy as np

# Datos de ejemplo (asegúrate de reemplazarlos con tus listas reales)
tmax = [25, 28, 30, 32, 29, 27]
tmin = [15, 18, 20, 22, 19, 17]
prec = [5, 8, 2, 12, 6, 4]

# Crear una figura con dos paneles (altura del panel superior es el doble del panel inferior)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 11), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
plt.subplots_adjust(hspace=0.0)  # Ajustar el espacio vertical entre los paneles

# Panel superior: Área entre tmax y tmin
dias = np.arange(len(tmax))
ax1.fill_between(dias, tmin, tmax, color='lightblue', label='Tmin-Tmax Area')
ax1.set_ylabel('Temperatura (°C)')
ax1.legend()

# Panel inferior: Gráfico de barras de precipitación
ax2.bar(dias, prec, color='lightblue')
ax2.set_xlabel('Días')
ax2.set_ylabel('Precipitación (mm)')

# Mostrar la figura
plt.show()

