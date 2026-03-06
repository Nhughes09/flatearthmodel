import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

print("Task 3.2: North Magnetic Pole Drift...")
# Correctly parse lon, lat, year
df_np = pd.read_csv('NP.xy', sep=r'\s+', comment='#', names=['lon', 'lat', 'year'])

# Unwrap longitude to prevent discontinuity jumps during fitting
# np.unwrap works on radians
unwrapped_lon = np.unwrap(np.radians(df_np['lon']))
df_np['lon_unwrapped'] = np.degrees(unwrapped_lon)

pre_1990 = df_np[df_np['year'] <= 1990].copy()
post_1990_years = df_np[df_np['year'] >= 1990].copy()

# Linear fit: lon = a + b * t
def lin_model(t, a, b):
    return a + b * (t - 1590)

popt_lin, _ = curve_fit(lin_model, pre_1990['year'], pre_1990['lon_unwrapped'])

# Exponential acceleration: lon(t) = c + d * exp(k * (t - 1990))
def exp_model(t, c, d, k):
    return c + d * np.exp(k * (t - 1990))

# For p0, look at the values. The longitude is unwrapped. At 1990, it's roughly the unwrapped value.
c0 = post_1990_years['lon_unwrapped'].iloc[0]
popt_exp, _ = curve_fit(exp_model, post_1990_years['year'], post_1990_years['lon_unwrapped'], p0=[c0, 10, 0.05], maxfev=10000)

print(f"Pre-1990 Linear Fit: lon(t) = {popt_lin[0]:.2f} + {popt_lin[1]:.4f} * (t - 1590)")
print(f"Post-1990 Exp Fit: lon(t) = {popt_exp[0]:.2f} + {popt_exp[1]:.2f} * exp({popt_exp[2]:.4f} * (t - 1990))")

# Deviation from 120E for latest year (2025)
# Note: 120E is strictly 120 in mod 360 space. 
latest_lon = df_np.loc[df_np['year'] == 2025, 'lon'].values[0]
# Normalise both to 0-360 to find shortest deviation
latest_lon_360 = latest_lon % 360
dev_from_120 = 120 - latest_lon_360
if dev_from_120 < -180: dev_from_120 += 360
if dev_from_120 > 180: dev_from_120 -= 360
print(f"2025 Longitude: {latest_lon_360:.2f}°E")
print(f"Deviation from 120°E: {dev_from_120:.2f}°")

# Plot mapping trajectory
plt.figure(figsize=(10, 8))

# Wrap coordinates back to -180 to 180 for standard map plotting
def wrap180(lon):
    return (lon + 180) % 360 - 180

plot_lon = wrap180(df_np['lon'])
plt.plot(plot_lon, df_np['lat'], 'b.-', label='Historical Path (1590-2025)', markersize=4)

# Plot the 120E Meridian line
plt.axvline(120, color='r', linestyle='--', label='120°E meridian')

plt.xlabel('Longitude (°E)')
plt.ylabel('Latitude (°N)')
plt.xlim(-180, 180)
plt.ylim(60, 90)
plt.title('North Magnetic Pole Drift (Task 3.2)')
plt.grid(True)
plt.legend()
plt.savefig('np_drift_3_2.png', dpi=300)
print("Saved np_drift_3_2.png")

# Append to master CSV
master_csv = 'dome_v46_master_data.csv'
master_df = pd.read_csv(master_csv)

new_rows = []
new_rows.append({'dataset': 'north_pole_noaa', 'year': 2025, 'parameter': 'deviation_120E', 'value': dev_from_120, 'unit': 'deg', 'source': 'NOAA', 'notes': 'Deviation from mapped asymptote'})
new_rows.append({'dataset': 'north_pole_noaa', 'year': 1990, 'parameter': 'pre1990_lin_a', 'value': popt_lin[0], 'unit': 'coeff', 'source': 'scipy', 'notes': 'Linear fit param (unwrapped)'})
new_rows.append({'dataset': 'north_pole_noaa', 'year': 1990, 'parameter': 'pre1990_lin_b', 'value': popt_lin[1], 'unit': 'coeff', 'source': 'scipy', 'notes': 'Linear fit param (unwrapped)'})
new_rows.append({'dataset': 'north_pole_noaa', 'year': 1990, 'parameter': 'post1990_exp_c', 'value': popt_exp[0], 'unit': 'coeff', 'source': 'scipy', 'notes': 'Exp fit param (unwrapped)'})
new_rows.append({'dataset': 'north_pole_noaa', 'year': 1990, 'parameter': 'post1990_exp_d', 'value': popt_exp[1], 'unit': 'coeff', 'source': 'scipy', 'notes': 'Exp fit param (unwrapped)'})
new_rows.append({'dataset': 'north_pole_noaa', 'year': 1990, 'parameter': 'post1990_exp_k', 'value': popt_exp[2], 'unit': 'coeff', 'source': 'scipy', 'notes': 'Exp fit param (unwrapped)'})

new_df = pd.DataFrame(new_rows)
pd.concat([master_df, new_df]).to_csv(master_csv, index=False)
print("Task 3.2 completed, master CSV updated.")
