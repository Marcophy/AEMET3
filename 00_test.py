import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from matplotlib import cm

# Datos de ejemplo
x = [1, 2, 3, 4, 5]
y = [10, 20, 25, 30, 35]

# Crear una figura y un eje
fig, ax = plt.subplots()

# Crear una matriz de colores para el fondo de degradado
gradient = np.linspace(1, 0, 256).reshape(1, -1)
gradient = np.vstack((gradient, gradient)).transpose()

# Configurar los datos de la gráfica
ax.plot(x, y, label='Datos de ejemplo')

# Cambiar el fondo de la gráfica a un degradado desde rojo a azul
ax.imshow(gradient, aspect='auto', cmap='jet', alpha=0.1, extent=ax.get_xlim() + ax.get_ylim())

# Cambiar el tamaño de la fuente para los labels y los ticks labels
ax.set_xlabel('Eje X', fontsize=12)
ax.set_ylabel('Eje Y', fontsize=12)

ax.tick_params(axis='both', labelsize=10)

# Agregar un grid gris claro solo en el eje X
ax.grid(axis='x', color='lightgray', linestyle='--', linewidth=0.5)

# Configurar los ticks del eje Y para que aparezcan cada incremento de dos
ax.yaxis.set_major_locator(MultipleLocator(2))

# Agregar una leyenda
ax.legend()

# Mostrar la gráfica
plt.show()
