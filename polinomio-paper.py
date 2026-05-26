import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Rango de x
x = np.linspace(-1e7, 1e7, 3000)

# ===== VARIABLES INICIALES =====
R3_0 = 1000
RL_0 = 0.2
C1_0 = 100e-12
Cf_0 = 1e-9
Rf_0 = 50e3


# ===== COEFICIENTES =====
def calcular_coeficientes(R3, RL, C1, Cf, Rf):
    a = 10 * Cf * Rf * R3 * RL * C1
    b = (C1 + Cf) * 10 * R3 * RL
    c = 1
    return a, b, c


# ===== FUNCIÓN RAÍCES =====
def calcular_raices(a, b, c):
    discriminante = b**2 - 4*a*c
    if discriminante < 0:
        return None, None
    x1 = (-b + np.sqrt(discriminante)) / (2*a)
    x2 = (-b - np.sqrt(discriminante)) / (2*a)
    return x1, x2


# ===== VALORES INICIALES =====
a, b, c = calcular_coeficientes(R3_0, RL_0, C1_0, Cf_0, Rf_0)
y = a*x**2 + b*x + c
x1, x2 = calcular_raices(a, b, c)


# ===== FIGURA =====
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.40)

(linea,) = ax.plot(x, y)

raices_plot, = ax.plot(
    [x1, x2] if x1 is not None else [],
    [0, 0] if x1 is not None else [],
    'ro',
    markersize=10
)

texto_raices = ax.text(
    0.02, 0.95, "",
    transform=ax.transAxes,
    verticalalignment='top'
)

ax.grid()
ax.set_xlim(-1e7, 1e7)
ax.set_ylim(np.min(y) - 0.5, np.max(y) + 0.5)
titulo = ax.set_title(f"y = {a:.3e}x² + {b:.3e}x + {c:.3e}")


# ===== SLIDERS =====
ax_R3 = plt.axes([0.15, 0.28, 0.7, 0.03])
ax_RL = plt.axes([0.15, 0.23, 0.7, 0.03])
ax_C1 = plt.axes([0.15, 0.18, 0.7, 0.03])
ax_Cf = plt.axes([0.15, 0.13, 0.7, 0.03])
ax_Rf = plt.axes([0.15, 0.08, 0.7, 0.03])

s_R3 = Slider(ax_R3, "R3", 1, 10000, valinit=R3_0)
s_RL = Slider(ax_RL, "RL", 0.01, 5, valinit=RL_0)
s_C1 = Slider(ax_C1, "C1", 1e-12, 200e-12, valinit=C1_0)
s_Cf = Slider(ax_Cf, "Cf", 100e-12, 10e-9, valinit=Cf_0)
s_Rf = Slider(ax_Rf, "Rf", 1e3, 100e3, valinit=Rf_0)


# ===== ACTUALIZACIÓN =====
def actualizar(val):
    R3 = s_R3.val
    RL = s_RL.val
    C1 = s_C1.val
    Cf = s_Cf.val
    Rf = s_Rf.val

    a, b, c = calcular_coeficientes(R3, RL, C1, Cf, Rf)
    y = a*x**2 + b*x + c

    linea.set_ydata(y)
    titulo.set_text(f"y = {a:.3e}x² + {b:.3e}x + {c:.3e}")

    x1, x2 = calcular_raices(a, b, c)

    if x1 is not None:
        raices_plot.set_data([x1, x2], [0, 0])
        texto_raices.set_text(f"x1 = {x1:.3e}\nx2 = {x2:.3e}")
    else:
        raices_plot.set_data([], [])
        texto_raices.set_text("Sin raíces reales")

    ax.set_ylim(np.min(y) - 0.5, np.max(y) + 0.5)
    fig.canvas.draw_idle()


# eventos
s_R3.on_changed(actualizar)
s_RL.on_changed(actualizar)
s_C1.on_changed(actualizar)
s_Cf.on_changed(actualizar)
s_Rf.on_changed(actualizar)

plt.show()