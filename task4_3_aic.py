import chaosmagpy as cp
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

print("Task 4.3: SAA Separation Error Analysis (Monte Carlo Bootstrap)")
model = cp.load_CHAOS_matfile('CHAOS-7.18.mat')

years = [2000, 2005, 2010, 2015, 2020, 2025]
res = 1.0 # use 1-deg to speed up 1000 Monte Carlo runs
lats = np.arange(-50, 0, res)
lons_africa = np.arange(-20, 60, res) 
lons_sa = np.arange(270, 330, res)

colats = 90.0 - lats
radius = 6371.2 # km Earth surface

theta_a_grid, phi_a_grid = np.meshgrid(colats, lons_africa)
lat_a_grid = 90.0 - theta_a_grid
theta_a_flat = theta_a_grid.flatten()
phi_a_flat = phi_a_grid.flatten()
lat_a_flat = lat_a_grid.flatten()
phi_a_wrap = np.where(phi_a_flat < 0, phi_a_flat + 360, phi_a_flat)

theta_sa_grid, phi_sa_grid = np.meshgrid(colats, lons_sa)
lat_sa_grid = 90.0 - theta_sa_grid
theta_sa_flat = theta_sa_grid.flatten()
phi_sa_flat = phi_sa_grid.flatten()
lat_sa_flat = lat_sa_grid.flatten()

# Standard chaos-7 uncertainty ~ 5-10 nT. We will inject normally distributed noise and bootstrap the minimum locations
n_bootstraps = 100
uncertainty_nT = 10.0

results_master = []

for year in years:
    time_mjd = cp.data_utils.mjd2000(year, 1, 1)
    
    # Base computations
    B_r_a, B_theta_a, B_phi_a = model.synth_values_tdep(time_mjd, radius, theta_a_flat, phi_a_wrap)
    F_a_base = np.sqrt(B_r_a**2 + B_theta_a**2 + B_phi_a**2)
    
    B_r_sa, B_theta_sa, B_phi_sa = model.synth_values_tdep(time_mjd, radius, theta_sa_flat, phi_sa_flat)
    F_sa_base = np.sqrt(B_r_sa**2 + B_theta_sa**2 + B_phi_sa**2)
    
    boot_seps = []
    
    for _ in range(n_bootstraps):
        noise_a = np.random.normal(0, uncertainty_nT, len(F_a_base))
        F_a_noisy = F_a_base + noise_a
        min_idx_a = np.argmin(F_a_noisy)
        min_lon_africa = phi_a_flat[min_idx_a]
        
        noise_sa = np.random.normal(0, uncertainty_nT, len(F_sa_base))
        F_sa_noisy = F_sa_base + noise_sa
        min_idx_sa = np.argmin(F_sa_noisy)
        min_lon_sa = phi_sa_flat[min_idx_sa]
        
        lon_sep = (min_lon_africa - min_lon_sa) % 360
        boot_seps.append(lon_sep)
        
    mean_sep = np.mean(boot_seps)
    std_sep = np.std(boot_seps)
    
    results_master.append({
        'year': year,
        'lon_separation_mean': mean_sep,
        'lon_separation_std': std_sep
    })

df = pd.DataFrame(results_master)
print(df)

# Regression Models
def lin_model(t, a, b):
    return a + b * (t - 2000)

def exp_model(t, a, k, c):
    return a * np.exp(k * (t - 2000)) + c

y = df['lon_separation_mean'].values
t = df['year'].values
sigma = df['lon_separation_std'].values
# Prevent div by zero if sigma is 0
sigma = np.where(sigma == 0, 0.1, sigma)

popt_lin, pcov_lin = curve_fit(lin_model, t, y, sigma=sigma, absolute_sigma=True)
popt_exp, pcov_exp = curve_fit(exp_model, t, y, p0=[1, 0.05, 30], sigma=sigma, absolute_sigma=True, maxfev=10000)

y_pred_lin = lin_model(t, *popt_lin)
y_pred_exp = exp_model(t, *popt_exp)

# Calculate AIC
# AIC = 2k + n * ln(RSS / n)
n = len(y)
rss_lin = np.sum((y - y_pred_lin)**2)
k_lin = 2
aic_lin = 2*k_lin + n * np.log(rss_lin / n)

rss_exp = np.sum((y - y_pred_exp)**2)
k_exp = 3
aic_exp = 2*k_exp + n * np.log(rss_exp / n)

print("\nModel Comparisons:")
print(f"Linear AIC: {aic_lin:.2f}")
print(f"Exponential AIC: {aic_exp:.2f}")

diff = aic_lin - aic_exp
if diff > 2:
    print(f"Result: The exponential (Dome) model is heavily preferred over the linear model (Delta AIC = {diff:.2f})")
else:
    print("Result: Linear model cannot be rejected statistically.")

# Plot
plt.figure(figsize=(10, 6))
plt.errorbar(t, y, yerr=sigma, fmt='o', capsize=5, label='CHAOS-7 Separation ± 1σ')
t_plot = np.linspace(2000, 2030, 100)
plt.plot(t_plot, lin_model(t_plot, *popt_lin), 'r--', label=f'Linear Fit (AIC {aic_lin:.1f})')
plt.plot(t_plot, exp_model(t_plot, *popt_exp), 'g-', label=f'Exp Fit (AIC {aic_exp:.1f})')
plt.xlabel('Year')
plt.ylabel('Longitudinal Separation (Degrees)')
plt.title('Statistical Comparison: Exponential Bifurcation vs Linear Core Drift')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('saa_aic_comparison.png', dpi=300)

# Save to master CSV
master_csv = 'dome_v46_master_data.csv'
master_df = pd.read_csv(master_csv)

new_rows = []
new_rows.append({'dataset': 'igrf_saa_highres', 'year': 2025, 'parameter': 'aic_linear', 'value': aic_lin, 'unit': 'aic', 'source': 'scipy', 'notes': 'Akaike Information Criterion (lower is better)'})
new_rows.append({'dataset': 'igrf_saa_highres', 'year': 2025, 'parameter': 'aic_exponential', 'value': aic_exp, 'unit': 'aic', 'source': 'scipy', 'notes': 'Akaike Information Criterion (lower is better)'})
new_rows.append({'dataset': 'igrf_saa_highres', 'year': 2025, 'parameter': 'exponential_preferred', 'value': 1 if aic_exp < aic_lin else 0, 'unit': 'bool', 'source': 'scipy', 'notes': '1 if dome exponential vortex model wins'})

new_df = pd.DataFrame(new_rows)
pd.concat([master_df, new_df]).to_csv(master_csv, index=False)
print("Updated master CSV with AIC calculations.")
