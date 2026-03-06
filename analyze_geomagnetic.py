import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import ppigrf

# --- MASTER CSV AGGREGATOR ---
master_data = []

def add_to_master(dataset, year, parameter, value, unit, source, notes):
    master_data.append({
        'dataset': dataset,
        'year': year,
        'parameter': parameter,
        'value': round(value, 5) if isinstance(value, float) else value,
        'unit': unit,
        'source': source,
        'notes': notes
    })

# Add Task 1.1 & 1.3 Data
add_to_master('tesla_patent', 1905, 'round_trip_time', 0.08484, 's', 'US787412', 'from patent text')
add_to_master('tesla_patent', 1905, 'frequency', 11.787, 'Hz', 'US787412', 'derived from 1/0.08484')
add_to_master('schumann_synthetic', 2025, 'atmospheric_peak', 7.83, 'Hz', 'synthetic', 'based on literature')
add_to_master('schumann_synthetic', 2025, 'atmospheric_peak', 14.3, 'Hz', 'synthetic', 'based on literature')
add_to_master('schumann_synthetic', 2025, 'ground_peak', 11.78, 'Hz', 'synthetic', 'based on Meyl/Tesla telluric')
add_to_master('schumann_synthetic', 2025, 'ground_peak', 7.83, 'Hz', 'synthetic', 'leakage from atmosphere')

# --- Task 2.1 & 2.3: SAA SEPARATION ANALYSIS (Real IGRF Data) ---
print("Task 2.1 & 2.3: Computing SAA separation from real IGRF data (Optimized target zones)...")

years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025]
lats = np.arange(-50, 0, 2)

# Only calculate longitudes where the cells exist
lons_africa = np.arange(0, 62, 2)
lons_sa = np.arange(280, 342, 2)

results_saa = []

for year in years:
    date = pd.to_datetime(f'{year}-01-01')
    
    # African cell
    min_f_africa = np.inf
    min_lon_africa = None
    for lat in lats:
        for lon in lons_africa:
            Be, Bn, Bu = ppigrf.igrf(lon, lat, 0, date)
            B = np.sqrt(Be.item()**2 + Bn.item()**2 + Bu.item()**2)
            if B < min_f_africa:
                min_f_africa = B
                min_lon_africa = lon
                
    # South American cell
    min_f_sa = np.inf
    min_lon_sa = None
    for lat in lats:
        for lon in lons_sa:
            Be, Bn, Bu = ppigrf.igrf(lon, lat, 0, date)
            B = np.sqrt(Be.item()**2 + Bn.item()**2 + Bu.item()**2)
            if B < min_f_sa:
                min_f_sa = B
                min_lon_sa = lon
    
    # Separation distance
    sep = (min_lon_africa - min_lon_sa) % 360
    
    add_to_master('igrf_saa', year, 'africa_cell_lon', float(min_lon_africa), 'deg', 'IGRF13', 'computed via ppigrf')
    add_to_master('igrf_saa', year, 'sa_cell_lon', float(min_lon_sa), 'deg', 'IGRF13', 'computed via ppigrf')
    add_to_master('igrf_saa', year, 'separation_deg', float(sep), 'deg', 'IGRF13', 'computed via ppigrf')
    
    results_saa.append({
        'year': year, 'africa_lon': min_lon_africa, 'sa_lon': min_lon_sa, 'separation_deg': sep
    })

df_saa = pd.DataFrame(results_saa)
print(df_saa[['year', 'africa_lon', 'sa_lon', 'separation_deg']])

# Fit
def exp_model(t, a, k, c):
    return a * np.exp(k * (t - 1990)) + c

popt, _ = curve_fit(exp_model, df_saa['year'].values, df_saa['separation_deg'].values, p0=(10, 0.05, 50), maxfev=10000)
a_fit, k_fit, c_fit = popt

add_to_master('igrf_saa', 1990, 'fitted_theta_0', float(a_fit), 'coeff', 'scipy', 'Exponential fit param')
add_to_master('igrf_saa', 1990, 'fitted_kappa', float(k_fit), 'coeff', 'scipy', 'Exponential fit param')
add_to_master('igrf_saa', 1990, 'fitted_C', float(c_fit), 'coeff', 'scipy', 'Exponential fit param')

print(f"Fitted model: Delta(t) = {a_fit:.2f} * exp({k_fit:.4f} * (t-1990)) + {c_fit:.2f}")

# Plotting SAA
plt.figure(figsize=(10, 6))
plt.scatter(df_saa['year'], df_saa['separation_deg'], color='blue', label='Actual IGRF13 Separation')
t_plot = np.linspace(1990, 2060, 100)
plt.plot(t_plot, exp_model(t_plot, *popt), 'b--', label='Exponential Fit to IGRF')
v42_predictions = {2025: 95.6, 2030: 122.6, 2035: 143.4, 2040: 157.4, 2050: 171.7, 2060: 176.9}
plt.scatter(list(v42_predictions.keys()), list(v42_predictions.values()), color='red', marker='x', s=100, label='V42/Dome Predictions')
plt.xlabel('Year'); plt.ylabel('Longitudinal Separation (Degrees)')
plt.title('South Atlantic Anomaly: Bifurcation and Cell Separation (1990-2060)')
plt.grid(True); plt.legend(); plt.tight_layout()
plt.savefig('saa_separation_plot.png', dpi=300)

# --- Task 2.2: NORTH MAGNETIC POLE DRIFT ---
print("\nTask 2.2: North Magnetic Pole Drift...")
df_np = pd.read_csv('NP.xy', delim_whitespace=True, comment='#', names=['year', 'lat', 'lon'])

recent = df_np[df_np['year'] >= 1990].copy()
for _, row in recent.iterrows():
    add_to_master('north_pole', row['year'], 'latitude', row['lat'], 'deg', 'NOAA', 'from NP.xy')
    add_to_master('north_pole', row['year'], 'longitude', row['lon'], 'deg', 'NOAA', 'from NP.xy')

dlat, dlon = np.diff(df_np['lat']), np.diff(df_np['lon'])
velocities = np.sqrt(dlat**2 + dlon**2) / np.diff(df_np['year'])
years_vel = df_np['year'].values[1:]

post_1990_vel = pd.DataFrame({'year': years_vel, 'vel': velocities}).query('year >= 1990')

def exp_accel(t, a, k): 
    return a * np.exp(k * (t - 1990))

try:
    popt_v, _ = curve_fit(exp_accel, post_1990_vel['year'], post_1990_vel['vel'], p0=(0.1, 0.05))
    add_to_master('north_pole', 1990, 'accel_theta_0', float(popt_v[0]), 'coeff', 'scipy', 'Exponential velocity fit')
    add_to_master('north_pole', 1990, 'accel_kappa', float(popt_v[1]), 'coeff', 'scipy', 'Exponential velocity fit')
except:
    pass

# Plotting NP Draft
plt.figure(figsize=(10, 10))
plt.plot(df_np['lon'], df_np['lat'], 'b.-', label='Historical Path (1590-2025)', markersize=3)
recent_2000 = df_np[df_np['year'] >= 2000]
plt.plot(recent_2000['lon'], recent_2000['lat'], 'rx', label='Recent (2000-2025)', markersize=8)
plt.axvline(120, color='red', linestyle='--', linewidth=2, label='120°E Meridian')
plt.xlim(-180, 180); plt.ylim(60, 90)
plt.xlabel('Longitude (°E)'); plt.ylabel('Latitude (°N)')
plt.title('North Magnetic Pole Drift Trajectory')
plt.grid(True); plt.legend(); plt.tight_layout()
plt.savefig('north_pole_trajectory.png', dpi=300)

# SAVE MASTER
df_master = pd.DataFrame(master_data)
df_master.to_csv('dome_v46_master_data.csv', index=False)
print("\nGenerated dome_v46_master_data.csv")
