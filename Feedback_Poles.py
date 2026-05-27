import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# ============================================================
# Closed-Loop Polynomial Visualizer (Post Pole-Zero Cancellation)
# ============================================================
# This script plots the characteristic polynomial of a closed-loop
# control system AFTER the pole-zero cancellation RF*CF = L/RL has
# been applied. Five sliders let the user tune the circuit
# parameters and observe how the polynomial and its roots change
# in real time.
# ============================================================

# X-axis range used to evaluate and plot the polynomial.
# Spans a wide symmetric interval so both real roots are visible.
x = np.linspace(-1e7, 1e7, 3000)

# ===== INITIAL PARAMETER VALUES =====
# Default values for the five circuit components. These set the
# starting position of every slider when the figure opens.
R3_0 = 1000      # Resistor R3 [Ohm]
RL_0 = 0.2       # Load resistance RL [Ohm]
C1_0 = 100e-12   # Capacitor C1 [F]
Cf_0 = 1e-9      # Feedback capacitor Cf [F]
Rf_0 = 50e3      # Feedback resistor Rf [Ohm]

# ===== POLYNOMIAL COEFFICIENTS =====
# Returns the (a, b, c) coefficients of the quadratic
#     a*x^2 + b*x + c
# that represents the closed-loop characteristic polynomial AFTER
# the pole-zero cancellation has been enforced.
# The factor 10 comes from a fixed gain/divider stage in the loop.
def calcular_coeficientes(R3, RL, C1, Cf, Rf):
    a = 10 * Cf * Rf * R3 * RL * C1   # Quadratic (s^2) coefficient
    b = (C1 + Cf) * 10 * R3 * RL      # Linear (s) coefficient
    c = 1                             # Constant term
    return a, b, c

# ===== ROOT CALCULATION =====
# Solves the quadratic analytically using the discriminant.
# Returns (None, None) when the discriminant is negative,
# meaning the system has complex-conjugate poles (no real roots).
def calcular_raices(a, b, c):
    discriminante = b**2 - 4*a*c
    if discriminante < 0:
        return None, None
    x1 = (-b + np.sqrt(discriminante)) / (2*a)
    x2 = (-b - np.sqrt(discriminante)) / (2*a)
    return x1, x2

# ===== INITIAL EVALUATION =====
# Compute the polynomial and its roots with the default values
# so the figure has something to display on startup.
a, b, c = calcular_coeficientes(R3_0, RL_0, C1_0, Cf_0, Rf_0)
y = a*x**2 + b*x + c
x1, x2 = calcular_raices(a, b, c)

# ===== FIGURE SETUP =====
# Create the figure and main axes. Reserve room at the bottom
# of the figure to fit all five sliders.
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.40)

# Main curve: the quadratic polynomial.
(linea,) = ax.plot(x, y)

# Red markers placed on the x-axis at the location of the roots.
# If there are no real roots, an empty list is supplied.
raices_plot, = ax.plot(
    [x1, x2] if x1 is not None else [],
    [0, 0] if x1 is not None else [],
    'ro',
    markersize=10
)

# Text box (top-left of the axes) that prints the numerical
# values of the roots, or "No real roots" when applicable.
texto_raices = ax.text(
    0.02, 0.95, "",
    transform=ax.transAxes,
    verticalalignment='top'
)

# Cosmetic axis configuration: grid, limits, and dynamic title
# showing the current polynomial coefficients.
ax.grid()
ax.set_xlim(-1e7, 1e7)
ax.set_ylim(np.min(y) - 0.5, np.max(y) + 0.5)
titulo = ax.set_title(f"y = {a:.3e}x² + {b:.3e}x + {c:.3e}")

# ===== SLIDERS =====
# Each slider is placed in its own axes (a narrow horizontal
# strip at the bottom of the figure) and binds to a single
# circuit parameter.
ax_R3 = plt.axes([0.15, 0.28, 0.7, 0.03])
ax_RL = plt.axes([0.15, 0.23, 0.7, 0.03])
ax_C1 = plt.axes([0.15, 0.18, 0.7, 0.03])
ax_Cf = plt.axes([0.15, 0.13, 0.7, 0.03])
ax_Rf = plt.axes([0.15, 0.08, 0.7, 0.03])

# Slider widgets with min, max, and initial value for each parameter.
s_R3 = Slider(ax_R3, "R3", 1, 10000, valinit=R3_0)
s_RL = Slider(ax_RL, "RL", 0.01, 5, valinit=RL_0)
s_C1 = Slider(ax_C1, "C1", 1e-12, 200e-12, valinit=C1_0)
s_Cf = Slider(ax_Cf, "Cf", 100e-12, 10e-9, valinit=Cf_0)
s_Rf = Slider(ax_Rf, "Rf", 1e3, 100e3, valinit=Rf_0)

# ===== UPDATE CALLBACK =====
# Called automatically whenever any slider changes value.
# Reads the current slider values, recomputes coefficients,
# polynomial, and roots, and refreshes the plot.
def actualizar(val):
    # Read current slider values.
    R3 = s_R3.val
    RL = s_RL.val
    C1 = s_C1.val
    Cf = s_Cf.val
    Rf = s_Rf.val

    # Recompute coefficients and polynomial values.
    a, b, c = calcular_coeficientes(R3, RL, C1, Cf, Rf)
    y = a*x**2 + b*x + c

    # Update the curve and title text.
    linea.set_ydata(y)
    titulo.set_text(f"y = {a:.3e}x² + {b:.3e}x + {c:.3e}")

    # Update the displayed roots (or show a message if none).
    x1, x2 = calcular_raices(a, b, c)
    if x1 is not None:
        raices_plot.set_data([x1, x2], [0, 0])
        texto_raices.set_text(f"x1 = {x1:.3e}\nx2 = {x2:.3e}")
    else:
        raices_plot.set_data([], [])
        texto_raices.set_text("No real roots")

    # Rescale the y-axis so the new curve fits comfortably.
    ax.set_ylim(np.min(y) - 0.5, np.max(y) + 0.5)
    fig.canvas.draw_idle()

# Bind the update callback to every slider's change event.
s_R3.on_changed(actualizar)
s_RL.on_changed(actualizar)
s_C1.on_changed(actualizar)
s_Cf.on_changed(actualizar)
s_Rf.on_changed(actualizar)

# Launch the interactive figure window.
plt.show()
