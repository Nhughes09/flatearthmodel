import chaosmagpy as cp
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

print("Loading CHAOS-7.18 model...")
model = cp.load_CHAOS_matfile('CHAOS-7.18.mat')
print("Model loaded successfully.")

years = [2000, 2005, 2010, 2015, 2020, 2025]
res = 0.5
lats = np.arange(-50, 0, res)

# Regions defined by DeepSeek
lons_africa = np.arange(-20, 60, res) 
lons_sa = np.arange(270, 330, res)

colats = 90.0 - lats
radius = 6371.2 # km Earth surface

# Create meshgrids
theta_a_grid, phi_a_grid = np.meshgrid(colats, lons_africa)
lat_a_grid = 90.0 - theta_a_grid
theta_a_flat = theta_a_grid.flatten()
phi_a_flat = phi_a_grid.flatten()
lat_a_flat = lat_a_grid.flatten()
# Wrap phi for Africa if it's negative
phi_a_wrap = np.where(phi_a_flat < 0, phi_a_flat + 360, phi_a_flat)

theta_sa_grid, phi_sa_grid = np.meshgrid(colats, lons_sa)
lat_sa_grid = 90.0 - theta_sa_grid
theta_sa_flat = theta_sa_grid.flatten()
phi_sa_flat = phi_sa_grid.flatten()
lat_sa_flat = lat_sa_grid.flatten()

results_saa = []

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # km
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi/2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return np.degrees(c)

for year in years:
    time_mjd = cp.data_utils.mjd2000(year, 1, 1)
    
    # African cell tracking
    B_r_a, B_theta_a, B_phi_a = model.synth_values_tdep(time_mjd, radius, theta_a_flat, phi_a_wrap)
    F_a = np.sqrt(B_r_a**2 + B_theta_a**2 + B_phi_a**2)
    min_idx_a = np.argmin(F_a)
    min_lon_africa = phi_a_flat[min_idx_a]
    min_lat_africa = lat_a_flat[min_idx_a]
    
    # South American cell tracking
    B_r_sa, B_theta_sa, B_phi_sa = model.synth_values_tdep(time_mjd, radius, theta_sa_flat, phi_sa_flat)
    F_sa = np.sqrt(B_r_sa**2 + B_theta_sa**2 + B_phi_sa**2)
    min_idx_sa = np.argmin(F_sa)
    min_lon_sa = phi_sa_flat[min_idx_sa]
    min_lat_sa = lat_sa_flat[min_idx_sa]
                
    # Separation
    lon_sep = (min_lon_africa - min_lon_sa) % 360
    gc_sep = haversine(min_lat_africa, min_lon_africa, min_lat_sa, min_lon_sa)

    results_saa.append({
        'year': year,
        'africa_lon': min_lon_africa,
        'africa_lat': min_lat_africa,
        'sa_lon': min_lon_sa,
        'sa_lat': min_lat_sa,
        'lon_separation': lon_sep,
        'great_circle_separation': gc_sep
    })

df = pd.DataFrame(results_saa)
print(df)

# Fit exponential D(t) = a * exp(k * (t - 2000)) + c
def exp_model(t, a, k, c):
    return a * np.exp(k * (t - 2000)) + c

popt_lon, _ = curve_fit(exp_model, df['year'], df['lon_separation'], maxfev=10000, p0=[1, 0.05, 50])
popt_gc, _ = curve_fit(exp_model, df['year'], df['great_circle_separation'], maxfev=10000, p0=[1, 0.05, 50])

print(f"\nLongitudinal Fit: {popt_lon[0]:.2f} * exp({popt_lon[1]:.4f}*(t-2000)) + {popt_lon[2]:.2f}")
print(f"Great Circle Fit: {popt_gc[0]:.2f} * exp({popt_gc[1]:.4f}*(t-2000)) + {popt_gc[2]:.2f}")

# Append to master CSV
master_csv = 'dome_v46_master_data.csv'
master_df = pd.read_csv(master_csv)

new_rows = []
for _, row in df.iterrows():
    y = row['year']
    new_rows.append({'dataset': 'igrf_saa_highres', 'year': y, 'parameter': 'africa_lon', 'value': row['africa_lon'], 'unit': 'deg', 'source': 'CHAOS7', 'notes': 'high-resolution 0.5deg'})
    new_rows.append({'dataset': 'igrf_saa_highres', 'year': y, 'parameter': 'africa_lat', 'value': row['africa_lat'], 'unit': 'deg', 'source': 'CHAOS7', 'notes': 'high-resolution 0.5deg'})
    new_rows.append({'dataset': 'igrf_saa_highres', 'year': y, 'parameter': 'sa_lon', 'value': row['sa_lon'], 'unit': 'deg', 'source': 'CHAOS7', 'notes': 'high-resolution 0.5deg'})
    new_rows.append({'dataset': 'igrf_saa_highres', 'year': y, 'parameter': 'sa_lat', 'value': row['sa_lat'], 'unit': 'deg', 'source': 'CHAOS7', 'notes': 'high-resolution 0.5deg'})
    new_rows.append({'dataset': 'igrf_saa_highres', 'year': y, 'parameter': 'lon_separation', 'value': row['lon_separation'], 'unit': 'deg', 'source': 'CHAOS7', 'notes': 'computed'})
    new_rows.append({'dataset': 'igrf_saa_highres', 'year': y, 'parameter': 'great_circle_separation', 'value': row['great_circle_separation'], 'unit': 'deg', 'source': 'CHAOS7', 'notes': 'computed'})

# Add fits
new_rows.append({'dataset': 'igrf_saa_highres', 'year': 2000, 'parameter': 'lon_fit_a', 'value': popt_lon[0], 'unit': 'coeff', 'source': 'scipy', 'notes': 'exp model'})
new_rows.append({'dataset': 'igrf_saa_highres', 'year': 2000, 'parameter': 'lon_fit_k', 'value': popt_lon[1], 'unit': 'coeff', 'source': 'scipy', 'notes': 'exp model'})
new_rows.append({'dataset': 'igrf_saa_highres', 'year': 2000, 'parameter': 'lon_fit_c', 'value': popt_lon[2], 'unit': 'coeff', 'source': 'scipy', 'notes': 'exp model'})

new_df = pd.DataFrame(new_rows)
pd.concat([master_df, new_df]).to_csv(master_csv, index=False)

# Plotting SAA High Res
plt.figure(figsize=(10, 6))
plt.scatter(df['year'], df['lon_separation'], color='blue', label='Actual CHAOS-7 Lon. Separation')
plt.scatter(df['year'], df['great_circle_separation'], color='green', label='Actual CHAOS-7 Great Circle Separation')

t_plot = np.linspace(2000, 2060, 100)
plt.plot(t_plot, exp_model(t_plot, *popt_lon), 'b--', label='Exponential Fit (Longitudinal)')
plt.plot(t_plot, exp_model(t_plot, *popt_gc), 'g--', label='Exponential Fit (Great Circle)')
v42_predictions = {2025: 95.6, 2030: 122.6, 2035: 143.4, 2040: 157.4, 2050: 171.7, 2060: 176.9}
plt.scatter(list(v42_predictions.keys()), list(v42_predictions.values()), color='red', marker='x', s=100, label='V42/Dome Predictions')
plt.xlabel('Year'); plt.ylabel('Separation (Degrees)')
plt.title('High-Res CHAOS-7 SAA Bifurcation (2000-2060)')
plt.grid(True); plt.legend(); plt.tight_layout()
plt.savefig('saa_chaos7_plot.png', dpi=300)
print("\nCompleted Task 3.1!")
