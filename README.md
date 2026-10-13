# VSG Virtual Inertia Estimation Simulation

This repository contains a preliminary Python simulation designed to estimate the **virtual inertia constant (H)** of a grid-connected Virtual Synchronous Generator (VSG) inverter from an external frequency ramp. It also evaluates how measurement quality—specifically **ADC resolution (bits), measurement noise, and sampling rates**—affects the accuracy of the estimate.

> ⚠️ **Disclaimer:** This is a simplified mathematical model intended for learning, prototyping, and educational purposes only. It is highly recommended to rebuild this model in professional tools like PLECS or Simulink before citing or using results in academic/professional research.

# How-Low-Cost-Sensor-Errors-Propagate-to-PV-Forecasting-Battery-Operation-and-Battery-Sizing
To see, on a simple model, how errors of low-cost sensors (bias, noise, drift, limited resolution) affect day-ahead PV forecasts and, through them, the operation and sizing of a small solar-battery system.
Setup (all data synthetic)
Data: one year of hourly synthetic PV output (3 kWp, latitude 23.8°N, monsoon and dry seasons) and household load
(about 8 kWh/day). Sensor error on the measured PV series, in three illustrative levels (gain bias / noise / drift over the
year): low (0 / 2% / 0), medium (+5% / 5% / 3%), high (+10% / 10% / 8%), plus 0.02 kW resolution. Forecast: day-ahead
hourly PV from measured data only: persistence and gradient boosting (trained on 200 days, tested on 165). Operation:
grid-connected, 6 kWh battery, time-of-use tariff, off-peak grid pre-charge planned from the forecast, compared with no
forecast and a perfect (oracle) forecast. Sizing: designed by simulating the measured year, then evaluated on the true
data: (i) on-grid, minimum annual cost; (ii) off-grid (4.8 kWp), smallest battery with loss of supply ≤ 5%. 10 Monte Carlo
runs per error level.
result: 
<img width="1700" height="1088" alt="image" src="https://github.com/user-attachments/assets/0e42b469-32b1-4182-9478-4b14c38d817d" />
(a) day-ahead forecast error; (b) grid cost over 165 test days (dotted: no forecast and oracle forecast); (c) on-grid battery size chosen from
measured data; (d) true loss of supply of the off-grid design chosen from measured data (dotted: 5% target).
1. Forecast error rises with sensor error: day-ahead nRMSE from 5.8% to 6.1% (gradient boosting) and from 6.5%
to 7.7% (persistence).
• 2. Operation cost rises by about 3–4% (36.5 to 37.7 USD with gradient boosting, 33.3 to 34.6 USD with
persistence), between the no-forecast (38.9) and oracle (33.0) costs. A lower nRMSE did not mean a lower cost:
persistence was cheaper than gradient boosting.
• 3. Cost-based on-grid sizing was not affected: 3 kWh in all cases, because the cost curve is flat.
• 4. Reliability-based off-grid sizing was affected: a design from over-reading sensors picks a smaller battery (14
kWh with true data; 12, 10 and about 9.8 kWh for low, medium and high error), so the true loss of supply rises from
4.3% to 5.1%, 6.1% and 6.3% against the 5% target.
Error level nRMSE ML / persist. (%) Op. cost ML / persist. (USD) Off-grid battery (kWh) True loss of supply (%)
none 5.8 / 6.5 36.5 / 33.2 14 4.3
low 5.8 / 6.5 36.5 / 33.3 12 5.1
medium 5.9 / 6.9 37.3 / 33.9 10 6.1
high 6.1 / 7.7 37.7 / 34.6 9.8 ± 0.6 6.3 ± 0.4

Limitations:

Synthetic data and illustrative error levels, not measured sensor errors; a simple weather model, tariff and battery model;
coarse battery-size steps (2 kWh off-grid); single synthetic year. The results are indicative only and show that the question
is meaningful, not that the effect holds in practice.

Planned next steps:

Replace the assumed errors with errors measured by my ESP32 monitoring node against a reference instrument; use real
irradiance, PV and load data; test further forecasting models and design criteria; confirm the research gap through a
systematic literature review.


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
