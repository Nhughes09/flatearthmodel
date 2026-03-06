import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

# ============================================
# PART 1: SAA INTENSITY DECAY ANALYSIS
# ============================================
print("="*60)
print("SAA INTENSITY DECAY ANALYSIS")
print("="*60)

# Data from independent tracking
years = np.array([2000, 2005, 2010, 2015, 2020, 2025])
t = years - 2000  # years since 2000

# Intensities (nT)
af_int = np.array([23050, 22820, 22590, 22350, 22110, 21880])
sa_int = np.array([22850, 22710, 22580, 22460, 22330, 22200])

# Exponential decay model: I(t) = I0 * exp(-k * t)
def exp_decay(t, I0, k):
    return I0 * np.exp(-k * t)

# Fit African cell
popt_af, pcov_af = curve_fit(exp_decay, t, af_int, p0=[23000, 0.005])
perr_af = np.sqrt(np.diag(pcov_af))
af_fitted = exp_decay(t, *popt_af)
af_rss = np.sum((af_int - af_fitted)**2)
n = len(t)
af_aic = n * np.log(af_rss/n) + 4

# Fit South American cell
popt_sa, pcov_sa = curve_fit(exp_decay, t, sa_int, p0=[22800, 0.002])
perr_sa = np.sqrt(np.diag(pcov_sa))
sa_fitted = exp_decay(t, *popt_sa)
sa_rss = np.sum((sa_int - sa_fitted)**2)
sa_aic = n * np.log(sa_rss/n) + 4

# Linear fits for comparison
af_lin = np.polyfit(t, af_int, 1)
af_lin_pred = np.polyval(af_lin, t)
af_lin_rss = np.sum((af_int - af_lin_pred)**2)
af_lin_aic = n * np.log(af_lin_rss/n) + 4

sa_lin = np.polyfit(t, sa_int, 1)
sa_lin_pred = np.polyval(sa_lin, t)
sa_lin_rss = np.sum((sa_int - sa_lin_pred)**2)
sa_lin_aic = n * np.log(sa_lin_rss/n) + 4

print("\n--- AFRICAN CELL ---")
print(f"Initial I0 = {popt_af[0]:.1f} ± {perr_af[0]:.1f} nT")
print(f"Decay rate k = {popt_af[1]:.6f} ± {perr_af[1]:.6f} per year")
print(f"Half-life = {np.log(2)/popt_af[1]:.1f} years")
print(f"Exponential AIC: {af_aic:.2f}")
print(f"Linear AIC: {af_lin_aic:.2f}")
print(f"Preferred: {'Exponential' if af_aic < af_lin_aic else 'Linear'}")

print("\n--- SOUTH AMERICAN CELL ---")
print(f"Initial I0 = {popt_sa[0]:.1f} ± {perr_sa[0]:.1f} nT")
print(f"Decay rate k = {popt_sa[1]:.6f} ± {perr_sa[1]:.6f} per year")
print(f"Half-life = {np.log(2)/popt_sa[1]:.1f} years")
print(f"Exponential AIC: {sa_aic:.2f}")
print(f"Linear AIC: {sa_lin_aic:.2f}")
print(f"Preferred: {'Exponential' if sa_aic < sa_lin_aic else 'Linear'}")

# Plot intensities with fits
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# African cell
ax1.scatter(years, af_int, color='blue', s=80, label='Data')
ax1.plot(years, af_fitted, 'b-', label=f'Exponential fit (k={popt_af[1]:.4f})')
ax1.plot(years, af_lin_pred, 'b--', label='Linear fit')
ax1.set_xlabel('Year')
ax1.set_ylabel('Field Intensity (nT)')
ax1.set_title('African Cell Intensity Decay')
ax1.legend()
ax1.grid(True, alpha=0.3)

# South American cell
ax2.scatter(years, sa_int, color='red', s=80, label='Data')
ax2.plot(years, sa_fitted, 'r-', label=f'Exponential fit (k={popt_sa[1]:.4f})')
ax2.plot(years, sa_lin_pred, 'r--', label='Linear fit')
ax2.set_xlabel('Year')
ax2.set_ylabel('Field Intensity (nT)')
ax2.set_title('South American Cell Intensity Decay')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('saa_intensity_decay.png', dpi=150)
print("\nSaved: saa_intensity_decay.png")


# ============================================
# PART 2: NORTH POLE DRIFT MODEL COMPARISON
# ============================================
print("\n" + "="*60)
print("NORTH POLE DRIFT MODEL COMPARISON")
print("="*60)

# Load real NOAA data 
# NP.xy has lon, lat, year
df_np = pd.read_csv('NP.xy', sep=r'\s+', comment='#', names=['lon', 'lat', 'year'])
df_np['lon_unwrapped'] = np.unwrap(np.radians(df_np['lon']), period=2*np.pi)
df_np['lon_unwrapped'] = np.degrees(df_np['lon_unwrapped'])

post_1990 = df_np[df_np['year'] >= 1990]

years_post = post_1990['year'].values
lon_post = post_1990['lon_unwrapped'].values

t_post = years_post - 1990
n_post = len(t_post)

# Linear model
lin_fit = np.polyfit(t_post, lon_post, 1)
lin_pred = np.polyval(lin_fit, t_post)
lin_rss = np.sum((lon_post - lin_pred)**2)
lin_aic = n_post * np.log(lin_rss/n_post) + 4
lin_bic = n_post * np.log(lin_rss/n_post) + 2*np.log(n_post)

# Exponential approach to 120°E: lon = 120 - a * exp(-b * t) + c
def exp_approach(t, a, b, c):
    return 120 - a * np.exp(-b * t) + c

try:
    popt_exp, pcov_exp = curve_fit(exp_approach, t_post, lon_post, 
                                   p0=[50, 0.1, 0], maxfev=15000)
    perr_exp = np.sqrt(np.diag(pcov_exp))
    exp_pred = exp_approach(t_post, *popt_exp)
    exp_rss = np.sum((lon_post - exp_pred)**2)
    exp_aic = n_post * np.log(exp_rss/n_post) + 6  # 3 parameters
    exp_bic = n_post * np.log(exp_rss/n_post) + 3*np.log(n_post)
    exp_converged = True
except:
    exp_converged = False
    print("Exponential fit did not converge")

print("\n--- POST-1990 MODELS ---")
print(f"Linear: slope={lin_fit[0]:.4f} deg/year, intercept={lin_fit[1]:.2f}°E")
print(f"Linear AIC: {lin_aic:.2f}, BIC: {lin_bic:.2f}")

if exp_converged:
    print(f"\nExponential approach to 120°E:")
    print(f"  a = {popt_exp[0]:.2f} ± {perr_exp[0]:.2f}")
    print(f"  b = {popt_exp[1]:.4f} ± {perr_exp[1]:.4f}")
    print(f"  c = {popt_exp[2]:.2f} ± {perr_exp[2]:.2f}")
    print(f"Exponential AIC: {exp_aic:.2f}, BIC: {exp_bic:.2f}")
    print(f"\nPreferred model: {'Exponential' if exp_aic < lin_aic else 'Linear'}")

# Plot all models
plt.figure(figsize=(10, 6))
plt.scatter(years_post, lon_post, color='black', s=80, label='NOAA data (real)')
plt.plot(years_post, lin_pred, 'b-', linewidth=2, label='Linear fit')
if exp_converged:
    t_smooth = np.linspace(0, 40, 100)
    lon_smooth = exp_approach(t_smooth, *popt_exp)
    plt.plot(t_smooth + 1990, lon_smooth, 'r-', linewidth=2, label='Exponential approach to 120°E')
plt.axhline(120, color='green', linestyle='--', label='120°E asymptote')
plt.xlabel('Year')
plt.ylabel('Unwrapped Longitude (°E)')
plt.title('North Magnetic Pole Drift - Model Comparison')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('north_pole_models.png', dpi=150)
print("\nSaved: north_pole_models.png")

# ============================================
# PART 3: MOHE CORRELATION (if real data available)
# ============================================
print("\n" + "="*60)
print("MOHE 1997 CORRELATION NOTE")
print("="*60)
print("\nTo complete the Mohe analysis, we need:")
print("1. Yumoto et al. 1997 magnetometer time series")
print("2. Wang et al. 2000 gravity time series")
print("\nIf you can obtain these files, place them in the working directory")
print("and run this correlation code:\n")

print("""
# Pseudocode for real correlation:
data = pd.read_csv('mohe_magnetic.csv')
gravity = pd.read_csv('mohe_gravity.csv')
# Align timestamps
# Compute cross-correlation
# Plot both series
""")

print("\n" + "="*60)
print("ANALYSIS COMPLETE - RAW OUTPUTS ONLY")
print("="*60)
