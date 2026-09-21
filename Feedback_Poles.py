
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, TextBox

# ===== constante fija =====
R_shunt = 0.1

# ===== valores iniciales =====
R8_0, R9_0, C2_0, C3_0 = 270, 10000, 10e-12, 10e-9
RL_0 = 0.4
L_0 = 25e-6         

# limites de sliders
R9_MIN, R9_MAX = 1000, 100000
C2_MIN, C2_MAX = 10e-12, 1000e-12
C3_MIN, C3_MAX = 100e-12, 100e-9

# colores
COL_TRAZA = "#0a9c8e"
COL_RAIZ = "#dd4636"
COL_WN = "#c07a00"

# estado (modo del eje, parametros ingresables L y RL, y lock anti-recursion)
estado = {"modo": "Auto (decadas)", "L": L_0, "RL": RL_0, "lock": False}


def Kprod():
    """Producto impuesto C3*R9 = L/RL."""
    return estado["L"] / estado["RL"]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ===== calculo =====
def coeficientes(R8, R9, C2, C3, RL):
    K = (1 / R_shunt) * R8 * RL
    a = K * C2 * C3 * R9
    b = K * (C2 + C3)
    c = 1.0
    return a, b, c


def raices(a, b, c):
    if a == 0:
        return [] if b == 0 else [-c / b]
    disc = b * b - 4 * a * c
    if disc < 0:
        return []
    r = np.sqrt(disc)
    return sorted([(-b + r) / (2 * a), (-b - r) / (2 * a)])


def ventana(rts, modo, a, c):
    """Devuelve (xmin, xmax, linthresh) para el eje symlog."""
    if modo == "+-1e7":
        return -1e7, 1e7, 1e3
    if modo == "+-2e6":
        return -2e6, 2e6, 1e2
    mags = [abs(r) for r in rts if r != 0]
    if not mags and a > 0 and c > 0:
        mags = [np.sqrt(c / a)]
    if not mags:
        return -1e7, 1e7, 1e3
    mn, mx = min(mags), max(mags)
    lt = max(mn / 60.0, 1.0)
    return -mx * 6.0, mx * 0.6, lt


def muestras(xmin, xmax, lt):
    """Muestreo denso adecuado para symlog (log en ambos signos + banda lineal)."""
    pts = {0.0, xmin, xmax}
    pts.update(np.linspace(-lt, lt, 80))
    if xmin < -lt:
        pts.update(-np.logspace(np.log10(lt), np.log10(-xmin), 700))
    if xmax > lt:
        pts.update(np.logspace(np.log10(lt), np.log10(xmax), 700))
    x = np.array(sorted(pts))
    return x[(x >= xmin) & (x <= xmax)]


# ===== figura y layout =====
fig = plt.figure(figsize=(11, 7.4))
fig.suptitle("Polinomio del denominador  (eje X log)",
             fontsize=13, fontweight="bold")

ax = fig.add_axes([0.09, 0.40, 0.56, 0.48])
ax.set_xlabel("x  (variable s)   [escala symlog]")
ax.set_ylabel("y")
ax.grid(True, which="both", alpha=0.3)
ax.axhline(0, color="0.55", lw=0.8)

(linea,) = ax.plot([], [], color=COL_TRAZA, lw=2, label="traza y(x)")
(raices_plot,) = ax.plot([], [], "o", color=COL_RAIZ, ms=9,
                         mec="white", mew=1.2, label="raices (polos)")
wn_line = ax.axvline(0, color=COL_WN, lw=1.2, ls="--", label="|wn| (polos complejos)")
wn_line.set_visible(False)
ax.legend(loc="upper center", fontsize=9, ncol=3, framealpha=0.9)

# crosshair (hover)
cursor_line = ax.axvline(0, color="0.5", lw=1, ls=":")
cursor_line.set_visible(False)
annot = ax.annotate("", xy=(0, 0), xytext=(12, 12),
                    textcoords="offset points", fontsize=9, family="monospace",
                    bbox=dict(boxstyle="round,pad=0.4", fc="white",
                              ec="0.6", alpha=0.92))
annot.set_visible(False)

# ---- celdas de texto para L y RL (parametros ingresables) ----
fig.text(0.71, 0.925, "Parametros  (C3*R9 = L / RL)", fontsize=10,
         fontweight="bold")
ax_L = fig.add_axes([0.80, 0.875, 0.10, 0.038])
ax_RL = fig.add_axes([0.80, 0.825, 0.10, 0.038])
tb_L = TextBox(ax_L, "L [H]  ", initial=f"{L_0:.3e}")
tb_RL = TextBox(ax_RL, "RL [Ohm]  ", initial=f"{RL_0:g}")

# selector de rango X
ax_radio = fig.add_axes([0.72, 0.50, 0.24, 0.24])
ax_radio.set_title("Rango eje X", fontsize=10)
radio = RadioButtons(ax_radio, ("Auto (decadas)", "+-2e6", "+-1e7"), active=0)

# panel de texto
info = fig.text(0.70, 0.42, "", va="top", ha="left", fontsize=9,
                family="monospace")

# ---- sliders ----
ax_R8 = fig.add_axes([0.30, 0.28, 0.30, 0.03])
ax_R9 = fig.add_axes([0.30, 0.23, 0.30, 0.03])
ax_C2 = fig.add_axes([0.30, 0.18, 0.30, 0.03])
ax_C3 = fig.add_axes([0.30, 0.13, 0.30, 0.03])

sR8 = Slider(ax_R8, "R8 [Ohm]", 1, 1000, valinit=R8_0, valfmt="%.0f",
             color=COL_TRAZA)
sR9 = Slider(ax_R9, "R9 [Ohm]", R9_MIN, R9_MAX, valinit=R9_0, valfmt="%.0f",
             color=COL_TRAZA)
sC2 = Slider(ax_C2, "C2 [F]", C2_MIN, C2_MAX, valinit=C2_0, valfmt="%.2e",
             color=COL_TRAZA)
sC3 = Slider(ax_C3, "C3 [F]", C3_MIN, C3_MAX, valinit=C3_0, valfmt="%.2e",
             color=COL_TRAZA)


# ===== dibujo / lecturas =====
def actualizar(_=None):
    RL = estado["RL"]
    a, b, c = coeficientes(sR8.val, sR9.val, sC2.val, sC3.val, RL)
    rts = raices(a, b, c)
    disc = b * b - 4 * a * c
    xmin, xmax, lt = ventana(rts, estado["modo"], a, c)

    ax.set_xscale("symlog", linthresh=lt, linscale=0.9)

    x = muestras(xmin, xmax, lt)
    y = a * x**2 + b * x + c
    linea.set_data(x, y)

    rx = [r for r in rts if xmin <= r <= xmax]
    raices_plot.set_data(rx, [0] * len(rx))

    if disc < 0 and a > 0 and c > 0:
        wn = np.sqrt(c / a)
        wn_line.set_xdata([-wn, -wn])
        wn_line.set_visible(-wn >= xmin)
    else:
        wn_line.set_visible(False)

    ax.set_xlim(xmin, xmax)
    # eje Y acotado a la zona de las raices (vertice de la parabola y y=0)
    yv = c - b * b / (4 * a) if a != 0 else float(y.min())
    lo, hi = min(0.0, yv), max(0.0, yv)
    if hi == lo:
        hi = lo + 1.0
    pad = (hi - lo) * 0.6
    ax.set_ylim(lo - pad, hi + pad)

    ax.set_title(f"y = {a:.3e} x^2  +  {b:.3e} x  +  {c:.3e}", fontsize=11)

    # ---- lecturas ----
    if len(rts) == 2:
        f1, f2 = abs(rts[0]) / (2 * np.pi), abs(rts[1]) / (2 * np.pi)
        rtxt = (f"x1 = {rts[0]:.3e}   ({f1:.3e} Hz)\n"
                f"x2 = {rts[1]:.3e}   ({f2:.3e} Hz)")
    elif len(rts) == 1:
        rtxt = f"x (lineal) = {rts[0]:.3e}"
    else:
        if a > 0 and c > 0:
            wn = np.sqrt(c / a)
            zeta = b / (2 * np.sqrt(a * c))
            rtxt = (f"Sin raices reales\n"
                    f"wn = {wn:.3e} rad/s ({wn/(2*np.pi):.3e} Hz)\n"
                    f"zeta = {zeta:.3f}")
        else:
            rtxt = "Sin raices reales"
    diag = ("2 polos reales negativos\n(sistema estable)" if disc >= 0
            else "complejas conjugadas\n(subamortiguado)")
    prod = sC3.val * sR9.val
    info.set_text(
        f"L       = {estado['L']:.3e} H\n"
        f"RL      = {estado['RL']:g} Ohm\n"
        f"R_shunt = {R_shunt} Ohm\n"
        f"C3*R9   = {prod:.3e}  (L/RL = {Kprod():.3e})\n"
        f"{'-'*30}\n"
        f"Polos [rad/s]:\n{rtxt}\n\n"
        f"Disc b^2-4ac = {disc:.3e}\n{diag}"
    )

    fig.canvas.draw_idle()


# ===== acoplamiento C3 <-> R9  (C3*R9 = L/RL) =====
def on_c3(_=None):
    if estado["lock"]:
        return
    estado["lock"] = True
    r9 = clamp(Kprod() / sC3.val, R9_MIN, R9_MAX)
    sR9.set_val(r9)                       # mueve el otro slider (callback bloqueado)
    estado["lock"] = False
    actualizar()


def on_r9(_=None):
    if estado["lock"]:
        return
    estado["lock"] = True
    c3 = clamp(Kprod() / sR9.val, C3_MIN, C3_MAX)
    sC3.set_val(c3)
    estado["lock"] = False
    actualizar()


def reconciliar():
    """Mantiene C3 y recalcula R9 tras cambiar L o RL."""
    estado["lock"] = True
    r9 = clamp(Kprod() / sC3.val, R9_MIN, R9_MAX)
    sR9.set_val(r9)
    estado["lock"] = False
    actualizar()


def on_L(text):
    try:
        val = float(text)
    except ValueError:
        return
    if val > 0:
        estado["L"] = val
        reconciliar()


def on_RL(text):
    try:
        val = float(text)
    except ValueError:
        return
    if val > 0:
        estado["RL"] = val
        reconciliar()


def on_radio(label):
    estado["modo"] = label
    actualizar()


def on_move(event):
    if event.inaxes is not ax or event.xdata is None:
        if annot.get_visible():
            annot.set_visible(False)
            cursor_line.set_visible(False)
            fig.canvas.draw_idle()
        return
    a, b, c = coeficientes(sR8.val, sR9.val, sC2.val, sC3.val, estado["RL"])
    xh = event.xdata
    yh = a * xh * xh + b * xh + c
    cursor_line.set_xdata([xh, xh])
    cursor_line.set_visible(True)
    annot.xy = (xh, yh)
    annot.set_text(f"x={xh:.2e}\ny={yh:.2e}")
    annot.set_visible(True)
    fig.canvas.draw_idle()


# eventos
sR8.on_changed(actualizar)
sC2.on_changed(actualizar)
sR9.on_changed(on_r9)
sC3.on_changed(on_c3)
tb_L.on_submit(on_L)
tb_RL.on_submit(on_RL)
radio.on_clicked(on_radio)
fig.canvas.mpl_connect("motion_notify_event", on_move)

# render inicial
actualizar()


if __name__ == "__main__":
    plt.show()
    
    
