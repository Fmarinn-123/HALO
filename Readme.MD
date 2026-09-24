# Closed-Loop Polynomial Visualizer

An interactive Python tool that plots the **denominator (characteristic) polynomial of the gradient-amplifier current loop** after the pole-zero cancellation `CF · RF = L / R_L` has been applied. Sliders, text boxes and a range selector let you tune the circuit and watch the polynomial, its roots and the damping figures update in real time, on a symmetric-log x-axis that keeps poles several decades apart visible at once.

Component names follow the schematic in `circuito_gradientes.svg`.

## Purpose

In analog and power-electronics feedback loops, a common compensation technique is to cancel the slow plant pole (set by the load inductance `L` and resistance `R_L`) with a zero introduced by the controller. When the condition

```
CF · RF = L / R_L
```

is enforced, the closed-loop transfer function collapses into a second-order polynomial whose roots determine the stability and dynamic response (damping, overshoot, settling time) of the resulting system.

This visualizer helps during that design stage by letting you:

- See the resulting quadratic `a·x² + b·x + c` as a curve on a log-scaled x-axis.
- See its real roots (the closed-loop poles) highlighted on the x-axis, with their values in rad/s and Hz.
- Get the natural frequency `ωn` and damping ratio `ζ` when the poles become complex.
- Sweep the circuit parameters while the tool **automatically keeps the cancellation condition satisfied**.

It is intended as a **design and tuning aid**, not a full SPICE replacement.

## Circuit it Models

The controller is the inverting stage around U1 in the schematic:

- `R3` feeds the current-feedback signal from the shunt into the summing node.
- `RF + CF` in series, in parallel with `C1`, form the feedback impedance (a PI controller with an extra high-frequency pole).
- `R4` is the current-sense shunt; the loop gain is proportional to `R4 / R3`.
- `L` and `R_L` are the gradient coil driven by the output stage.

## How It Works

1. **Coefficients.** From the circuit parameters, the script computes the coefficients of the post-cancellation closed-loop polynomial (function `coeficientes`):

   ```
   K = (1 / R4) · R3 · R_L
   a = K · C1 · CF · RF
   b = K · (C1 + CF)
   c = 1
   ```

   `R4` is the current-sense shunt, fixed at `0.1 Ω` at the top of the script, which is why the factor `1 / R4 = 10` appears in equations (1)–(3) of the poster. Change the constant if your sensing stage differs.

2. **Cancellation coupling.** The `CF` and `RF` sliders are linked. Moving one recalculates the other so that `CF · RF = L / R_L` keeps holding. Changing `L` or `R_L` in the text boxes keeps `CF` fixed and recomputes `RF`. A lock flag prevents the two slider callbacks from triggering each other recursively.

3. **Roots.** Roots are computed analytically with the quadratic formula (function `raices`). When the discriminant `b² − 4ac` is negative, the roots are a complex-conjugate pair; the tool then reports
   - `ωn = √(c / a)` [rad/s], also in Hz
   - `ζ = b / (2·√(a·c))`

   and draws a dashed vertical line at `x = −ωn`.

4. **Symlog x-axis.** Poles of a compensated loop are often decades apart, so the x-axis uses a `symlog` scale (logarithmic on both signs, linear near zero). The curve is sampled densely in log space on each side plus a linear band around zero (function `muestras`), so it stays smooth at every zoom level.

5. **Auto window.** In *Auto (decadas)* mode (function `ventana`) the x-range is fitted to the roots: from `−6·|x|max` to `+0.6·|x|max`, with the linear threshold set to `|x|min / 60` (minimum 1). If there are no real roots, `ωn` is used as the reference scale. The y-axis is always fitted to the region between `y = 0` and the parabola's vertex, so the zero crossings are clearly visible.

6. **Interactivity.** Every control is wired to `actualizar`, which recalculates the coefficients, redraws the curve, repositions the root markers and `ωn` line, rescales both axes and refreshes the info panel.

## Controls

### Sliders

| Symbol | Description                            | Default | Slider Range       |
| ------ | -------------------------------------- | ------- | ------------------ |
| R3     | Current-feedback resistor [Ω]          | 270     | 1 – 1 000          |
| RF     | Compensation resistor [Ω] *(linked to CF)* | 10 kΩ   | 1 kΩ – 100 kΩ      |
| C1     | Parallel feedback capacitor [F]        | 10 pF   | 10 pF – 1 000 pF   |
| CF     | Compensation capacitor [F] *(linked to RF)* | 10 nF   | 100 pF – 100 nF    |

### Text boxes (type a value and press **Enter**)

| Symbol | Description              | Default |
| ------ | ------------------------ | ------- |
| L      | Coil inductance [H]      | 25 µH   |
| R_L    | Coil resistance [Ω]      | 0.4     |

Values accept scientific notation (e.g. `4.7e-5`). Non-numeric or non-positive entries are ignored.

For the gradient coil used in the poster, enter `10e-6` and `0.2`.

### X-range selector

| Option             | X-range            | Linear threshold |
| ------------------ | ------------------ | ---------------- |
| Auto (decadas)     | fitted to roots    | `|x|min / 60`    |
| ±2e6               | −2·10⁶ … 2·10⁶     | 100              |
| ±1e7               | −10⁷ … 10⁷         | 1 000            |

### Mouse hover

Moving the mouse over the plot shows a crosshair and a tooltip with the cursor's `x` and the polynomial value `y(x)` at that point.

## What the Window Shows

- **Main plot:** the polynomial curve (teal), real roots as red dots on `y = 0`, and a dashed orange line at `−ωn` when the poles are complex.
- **Title:** the current polynomial `y = a x² + b x + c` in scientific notation.
- **Info panel (right):**
  - `L`, `R_L`, `R4`
  - `CF·RF` next to the target `L/R_L`, to confirm the cancellation holds
  - Pole values in rad/s and Hz, or `ωn` and `ζ` if complex
  - Discriminant `b² − 4ac` and a diagnosis: *two real negative poles (stable)* or *complex conjugates (underdamped)*

## Requirements

- Python 3.8 or newer
- NumPy
- Matplotlib (3.3+ for the `symlog` `linthresh` keyword)

Install dependencies with:

```bash
pip install numpy matplotlib
```

## Usage

Run the script from a terminal:

```bash
python closed_loop_polynomial.py
```

Drag any slider, type a new `L` or `R_L`, or change the x-range mode, and the whole view updates immediately.

## Important Notes

- **Only the post-cancellation polynomial is modeled.** The plotted polynomial is valid only while `CF · RF = L / R_L`. The tool enforces this by coupling the sliders, but it does **not** model the broken-cancellation case.
- **Slider limits can break the cancellation.** If the value required to satisfy `CF · RF = L / R_L` falls outside the other slider's range, it is clamped to the limit and the condition no longer holds exactly. Compare `CF·RF` against `L/R_L` in the info panel; if they differ, pick a different `CF` (or `RF`) or widen the limits (`RF_MIN` / `RF_MAX`, `CF_MIN` / `CF_MAX`).
- **Initial state.** The default values (`CF·RF = 1e-4`, `L/R_L = 6.25e-5`) do not satisfy the condition at startup. The coupling is applied as soon as you move `CF` or `RF`, or submit a value for `L` or `R_L`.
- **`R4` is a fixed constant** (`0.1 Ω`). Edit it at the top of the script if your current-sense resistor differs.
- **No real roots means complex poles.** A negative discriminant means the closed loop has a complex-conjugate pole pair, i.e. an underdamped response; use the reported `ζ` to judge the overshoot.
- **Stability diagnosis assumes positive coefficients.** With all components positive, `a`, `b` and `c` are positive, so real roots are always negative. The "stable" label relies on that.

## File Structure

```
closed_loop_polynomial.py   # Main script with the interactive plot
circuito_gradientes.py      # Schematic drawn with Schemdraw (source of the names)
circuito_gradientes.svg     # Rendered schematic
ecuaciones.tex              # Loop equations (1)-(3)
README.md                   # This file
```

## License

Free to use and modify for educational and engineering purposes.
