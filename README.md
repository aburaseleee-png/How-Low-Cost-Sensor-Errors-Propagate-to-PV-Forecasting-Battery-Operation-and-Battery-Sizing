# How-Low-Cost-Sensor-Errors-Propagate-to-PV-Forecasting-Battery-Operation-and-Battery-Sizing
To see, on a simple model, how errors of low-cost sensors (bias, noise, drift, limited resolution) affect day-ahead PV forecasts and, through them, the operation and sizing of a small solar-battery system.
# VSG Virtual Inertia Estimation Simulation

This repository contains a preliminary Python simulation designed to estimate the **virtual inertia constant (H)** of a grid-connected Virtual Synchronous Generator (VSG) inverter from an external frequency ramp. It also evaluates how measurement quality—specifically **ADC resolution (bits), measurement noise, and sampling rates**—affects the accuracy of the estimate.

> ⚠️ **Disclaimer:** This is a simplified mathematical model intended for learning, prototyping, and educational purposes only. It is highly recommended to rebuild this model in professional tools like PLECS or Simulink before citing or using results in academic/professional research.

---

## 📌 Project Overview

The simulation models a grid-connected VSG using the classic **swing equation** (expressed in per-unit system):

\[\frac{d(\delta)}{dt} = \omega_0 \cdot (\Delta\omega - \Delta\omega_g) \quad [\text{rad/s}]\]

\[M \cdot \frac{d(\Delta\omega)}{dt} = -K_s \cdot \delta - D \cdot \Delta\omega \quad (\text{where } M = 2H)\]

\[\Delta P_e = K_s \cdot \delta \quad (\text{output power deviation})\]

### The Naive Fitting Bias
Under steady ramp tracking, a naive least-squares fit on \(\Delta P_e\) over a post-transient window will under-read the value of M due to the system damping and synchronizing power coefficients:
\[\text{Bias Offset} = \frac{D^2}{K_s \cdot \omega_0}\]
This script demonstrates how to identify, predict, and mathematically correct this analytical bias while simultaneously assessing hardware constraints (ADC bit-depth and noise floor).

---

## ⚙️ Key Technical Features

- **Swing Equation Simulator:** A discrete time-step ODE loop solving VSG dynamics during a grid RoCoF (Rate of Change of Frequency) event.
- **Hardware Error Emulation:** Simulates quantization errors based on specified ADC bit resolution (e.g., 8, 10, 12, 14 bits) and continuous Gaussian measurement noise.
- **Monte Carlo Analysis:** Runs multiple iterations (200 runs per configuration) across variable sampling frequencies (\(f_s\)) and ADC depths to plot parameter variance (μ ± σ).
- **Automated Plotting:** Generates clear comparative visualizations showing the power response profile alongside error bars for hardware precision limits.

---

## 🚀 How to Run the Simulation

### Prerequisites
Make sure you have Python installed along with the required libraries:
```bash
pip install numpy matplotlib
```

### Execution
Run the simulation script directly from your terminal:
```bash
python vsg.py
```
*(Note: Replace `vsg_inertia_sim.py` with the exact name you save your script file as).*

---

## 📊 Outputs & Results

Upon running, the script prints a performance log directly to the terminal and automatically generates a figure saved at `/mnt/user-data/outputs/vsg_inertia_result.png` (or your local directory depending on your path configuration).

### Sample Analytical Observations
- **True H Value:** `2.00 s`
- **Naive Noise-Free Estimate:** Under-reads the true value due to the mathematical steady-ramp offset.
- **Corrected Estimate:** Perfectly recovers the true parameter when D and \(K_s\) are known.
- **Hardware Trade-offs:** Higher sampling rates (\(f_s = 10 \text{ kHz}\)) combined with high ADC resolution (≥ 12-bit) drastically suppress the standard deviation introduced by sensor noise.

---
