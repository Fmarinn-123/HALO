# Closed-Loop Polynomial Visualizer

An interactive Python tool that plots the **characteristic polynomial of a closed-loop control system** after the pole-zero cancellation `RF·CF = L/RL` has been applied. Five sliders let you tune the circuit parameters and watch the polynomial and its roots update in real time.

## Purpose

In the design of analog and power-electronics feedback loops, a common compensation technique is to cancel a slow plant pole with a zero introduced by the controller. When the condition

```
RF · CF = L / RL
```

is enforced, the closed-loop transfer function collapses into a second-order polynomial whose roots determine the stability and dynamic response (damping, overshoot, settling time) of the resulting system.

This visualizer is meant to help during that design stage by letting you:

- See the resulting quadratic `a·x² + b·x + c` as a curve.
- See its real roots highlighted as red dots on the x-axis (or be told when they become complex).
- Sweep the five circuit parameters and develop intuition about how each one moves the poles.

It is intended as a **design and tuning aid**, not a full SPICE replacement.

## How It Works

1. **Coefficients.** From the five circuit parameters, the script computes the coefficients of the post-cancellation closed-loop polynomial:
   - `a = 10 · Cf · Rf · R3 · RL · C1`
   - `b = (C1 + Cf) · 10 · R3 · RL`
   - `c = 1`

   The constant `10` factor comes from a fixed gain/divider stage of the specific loop this tool was derived for. If your loop has a different gain, edit it inside the `calcular_coeficientes` function.

2. **Polynomial.** The polynomial is evaluated on a wide symmetric x-range (`±1e7`) and plotted as a blue curve.

3. **Roots.** Roots are computed analytically with the quadratic formula. When the discriminant `b² − 4ac` is negative, the roots become a complex-conjugate pair and the message *"No real roots"* is shown instead of markers.

4. **Interactivity.** Each slider is wired to an update callback (`actualizar`) that recalculates the coefficients, redraws the curve, repositions the root markers, refreshes the printed values, and rescales the y-axis to fit.

## Parameters

| Symbol | Description           | Default | Slider Range     |
| ------ | --------------------- | ------- | ---------------- |
| R3     | Resistor R3 [Ω]       | 1000    | 1 – 10 000       |
| RL     | Load resistance [Ω]   | 0.2     | 0.01 – 5         |
| C1     | Capacitor C1 [F]      | 100 pF  | 1 pF – 200 pF    |
| Cf     | Feedback capacitor [F]| 1 nF    | 100 pF – 10 nF   |
| Rf     | Feedback resistor [Ω] | 50 kΩ   | 1 kΩ – 100 kΩ    |

## Requirements

- Python 3.8 or newer
- NumPy
- Matplotlib

Install dependencies with:

```bash
pip install numpy matplotlib
```

## Usage

Run the script from a terminal:

```bash
python closed_loop_polynomial.py
```

A figure window opens showing:

- The polynomial curve in the main plot area.
- Red dots on the x-axis at the locations of the real roots.
- A small text label (top-left) listing the numerical values of the roots.
- A title showing the current coefficients in scientific notation.
- Five sliders at the bottom of the window.

Drag any slider and the entire view updates immediately.

## Important Notes

- **The cancellation condition must hold.** The polynomial that this tool plots is only valid when `RF · CF = L / RL`. If you change `Rf` or `Cf` independently, in the real circuit the cancellation will be broken; this script does **not** model what happens in that broken-cancellation case. It always shows the *idealized post-cancellation* polynomial.
- **The constant `10` factor** in the coefficients is loop-specific. Adjust it inside `calcular_coeficientes` if your gain/divider chain differs.
- **No real roots = complex poles.** When the message *"No real roots"* appears, the closed loop has a complex-conjugate pole pair, which generally corresponds to an underdamped response.

## File Structure

```
closed_loop_polynomial.py   # Main script with the interactive plot
README.md                   # This file
```

## License

Free to use and modify for educational and engineering purposes.
