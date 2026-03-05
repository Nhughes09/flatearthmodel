#!/usr/bin/env python3
"""
V14: Jupiter + Moon dome model predictions
- Uses observed data from v13_corrected_obs.csv
- Fits dome height H and orbital radius R for Jupiter and Moon
- Compares predicted vs observed az/elev for all 31 cities
"""
import warnings
warnings.filterwarnings("ignore")

import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.optimize import minimize

# Load corrected observations
df = pd.read_csv('v13_corrected_obs.csv')

# ============================================================
# FLAT MAP GEOMETRY
# ============================================================
# AE projection: city at polar coords (r, lon) on flat plane
# r = 6500 / tan(|lat|), angle = longitude (degrees)
# Body orbits at height H, radius R from center, at angle theta

POLARIS_H = 6500.0

def city_xy(lat, lon):
    """Map city to (x, y) on flat plane. North pole = (0, 0)."""
    abs_lat = max(abs(lat), 0.01)
    r = POLARIS_H / math.tan(math.radians(abs_lat))
    # Use longitude as angular position (radians, measured from +x axis)
    theta = math.radians(lon)
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y, r

def body_position(R, theta_deg):
    """Body orbital position on flat plane at radius R, angle theta."""
    theta = math.radians(theta_deg)
    return R * math.cos(theta), R * math.sin(theta)

def predict_elev_az(city_lat, city_lon, body_R, body_theta, body_H):
    """
    Predict elevation and azimuth of a dome body from a city.
    Returns (elevation_deg, azimuth_deg).
    """
    cx, cy, cr = city_xy(city_lat, city_lon)
    bx, by = body_position(body_R, body_theta)
    
    # Horizontal distance
    dx = bx - cx
    dy = by - cy
    horiz_dist = math.sqrt(dx**2 + dy**2)
    if horiz_dist < 1:
        horiz_dist = 1
    
    # Elevation
    elev = math.degrees(math.atan(body_H / horiz_dist))
    
    # Azimuth: angle from north (toward center) measured clockwise
    # For northern cities, "north" points toward center (0,0)
    # Direction to center from city
    to_center_x = -cx
    to_center_y = -cy
    center_dist = math.sqrt(to_center_x**2 + to_center_y**2)
    if center_dist < 1:
        center_dist = 1
    
    # Normalize
    nc_x = to_center_x / center_dist
    nc_y = to_center_y / center_dist
    
    # Direction to body
    body_dist = horiz_dist
    nb_x = dx / body_dist
    nb_y = dy / body_dist
    
    # Azimuth = angle from north-to-center direction, clockwise
    # Using atan2 for proper quadrant handling
    # Cross product for sign, dot product for angle
    dot = nc_x * nb_x + nc_y * nb_y
    cross = nc_x * nb_y - nc_y * nb_x
    az = math.degrees(math.atan2(cross, dot))
    
    # For southern hemisphere, observer faces outward (away from center)
    # so we flip the reference direction
    if city_lat < 0:
        az = (az + 180) % 360
    else:
        az = az % 360
    
    return elev, az

def wrap_az_err(obs, pred):
    e = obs - pred
    if e > 180: e -= 360
    elif e < -180: e += 360
    return e

# ============================================================
# OPTIMIZATION: Find best H, R, theta for Jupiter
# ============================================================
print("=" * 60)
print("V14: FITTING JUPITER DOME PARAMETERS")
print("=" * 60)

def jupiter_cost(params):
    H, R, theta = params
    total = 0
    for _, row in df.iterrows():
        pred_e, pred_a = predict_elev_az(row['latitude'], row['longitude'], R, theta, H)
        obs_e = row['jupiter_elevation']
        obs_a = row['jupiter_azimuth']
        elev_err = pred_e - obs_e
        az_err = wrap_az_err(obs_a, pred_a)
        # Weight elevation more since it's more geometrically constrained
        total += elev_err**2 + (az_err * 0.3)**2
    return total

# Try multiple starting points
best_jup = None
best_jup_cost = float('inf')
for H0 in [3000, 5000, 8000, 12000]:
    for R0 in [5000, 10000, 20000, 40000]:
        for th0 in [0, 90, 180, 270]:
            try:
                res = minimize(jupiter_cost, [H0, R0, th0], method='Nelder-Mead',
                              options={'maxiter': 5000, 'xatol': 1, 'fatol': 0.1})
                if res.fun < best_jup_cost:
                    best_jup_cost = res.fun
                    best_jup = res.x
            except:
                pass

H_jup, R_jup, theta_jup = best_jup
print(f"  Best fit: H_jupiter = {H_jup:.0f} km, R_jupiter = {R_jup:.0f} km, θ_jupiter = {theta_jup:.1f}°")
print(f"  Cost: {best_jup_cost:.1f}")

# ============================================================
# OPTIMIZATION: Find best H, R, theta for Moon
# ============================================================
print("\n" + "=" * 60)
print("V14: FITTING MOON DOME PARAMETERS")
print("=" * 60)

def moon_cost(params):
    H, R, theta = params
    total = 0
    for _, row in df.iterrows():
        pred_e, pred_a = predict_elev_az(row['latitude'], row['longitude'], R, theta, H)
        obs_e = row['moon_elevation']
        obs_a = row['moon_azimuth']
        elev_err = pred_e - obs_e
        az_err = wrap_az_err(obs_a, pred_a)
        total += elev_err**2 + (az_err * 0.3)**2
    return total

best_moon = None
best_moon_cost = float('inf')
for H0 in [3000, 5000, 8000, 15000]:
    for R0 in [5000, 10000, 20000, 40000]:
        for th0 in [0, 90, 180, 270]:
            try:
                res = minimize(moon_cost, [H0, R0, th0], method='Nelder-Mead',
                              options={'maxiter': 5000, 'xatol': 1, 'fatol': 0.1})
                if res.fun < best_moon_cost:
                    best_moon_cost = res.fun
                    best_moon = res.x
            except:
                pass

H_moon, R_moon, theta_moon = best_moon
print(f"  Best fit: H_moon = {H_moon:.0f} km, R_moon = {R_moon:.0f} km, θ_moon = {theta_moon:.1f}°")
print(f"  Cost: {best_moon_cost:.1f}")

# ============================================================
# BUILD COMPARISON TABLE
# ============================================================
print("\n" + "=" * 60)
print("V14: FULL COMPARISON TABLE")
print("=" * 60)

results = []
for _, row in df.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    
    jup_e_pred, jup_a_pred = predict_elev_az(lat, lon, R_jup, theta_jup, H_jup)
    moon_e_pred, moon_a_pred = predict_elev_az(lat, lon, R_moon, theta_moon, H_moon)
    
    jup_e_obs = row['jupiter_elevation']
    jup_a_obs = row['jupiter_azimuth']
    moon_e_obs = row['moon_elevation']
    moon_a_obs = row['moon_azimuth']
    moon_phase_obs = row['moon_phase_fraction']
    
    near_zenith = 'YES' if row['sun_noon_elevation'] > 80 else 'no'
    
    results.append({
        'City': row['city'],
        'Lat': lat,
        'Lon': lon,
        'Jup_Az_Obs': round(jup_a_obs, 2),
        'Jup_Az_Flat': round(jup_a_pred, 2),
        'Jup_Az_Err': round(wrap_az_err(jup_a_obs, jup_a_pred), 2),
        'Jup_Elev_Obs': round(jup_e_obs, 2),
        'Jup_Elev_Flat': round(jup_e_pred, 2),
        'Jup_Elev_Err': round(jup_e_obs - jup_e_pred, 2),
        'Moon_Az_Obs': round(moon_a_obs, 2),
        'Moon_Az_Flat': round(moon_a_pred, 2),
        'Moon_Az_Err': round(wrap_az_err(moon_a_obs, moon_a_pred), 2),
        'Moon_Elev_Obs': round(moon_e_obs, 2),
        'Moon_Elev_Flat': round(moon_e_pred, 2),
        'Moon_Elev_Err': round(moon_e_obs - moon_e_pred, 2),
        'Moon_Phase_Obs': moon_phase_obs,
        'Near_Zenith': near_zenith,
    })

df_results = pd.DataFrame(results)
df_results.to_csv('v14_results.csv', index=False)

# Print table
print(f"\n{'City':<28} {'Lat':>6} {'JupElOb':>7} {'JupElFl':>7} {'JupElEr':>7} {'JupAzEr':>7} {'MnElOb':>7} {'MnElFl':>7} {'MnElEr':>7} {'MnAzEr':>7}")
print("-" * 110)
for r in results:
    print(f"{r['City'][:27]:<28} {r['Lat']:>6.1f} {r['Jup_Elev_Obs']:>7.1f} {r['Jup_Elev_Flat']:>7.1f} {r['Jup_Elev_Err']:>7.1f} {r['Jup_Az_Err']:>7.1f} "
          f"{r['Moon_Elev_Obs']:>7.1f} {r['Moon_Elev_Flat']:>7.1f} {r['Moon_Elev_Err']:>7.1f} {r['Moon_Az_Err']:>7.1f}")

# ============================================================
# ERROR CHARTS
# ============================================================
print("\n" + "=" * 60)
print("GENERATING ERROR CHARTS...")
print("=" * 60)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('V14 — Jupiter & Moon Dome Model Errors vs Latitude', fontsize=14, fontweight='bold')

lats = [r['Lat'] for r in results]
zenith_mask = [r['Near_Zenith'] == 'YES' for r in results]
colors = ['red' if z else 'steelblue' for z in zenith_mask]

panels = [
    (axes[0,0], [r['Jup_Az_Err'] for r in results], 'Jupiter Azimuth Error (°)'),
    (axes[0,1], [r['Jup_Elev_Err'] for r in results], 'Jupiter Elevation Error (°)'),
    (axes[1,0], [r['Moon_Az_Err'] for r in results], 'Moon Azimuth Error (°)'),
    (axes[1,1], [r['Moon_Elev_Err'] for r in results], 'Moon Elevation Error (°)'),
]

for ax, errs, title in panels:
    ax.scatter(lats, errs, c=colors, s=40, zorder=3)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Latitude (°)')
    ax.set_ylabel('Error (°)')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)

legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue', markersize=8, label='Stable'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Near-Zenith'),
]
fig.legend(handles=legend_elements, loc='upper right', fontsize=10)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('v14_errors.png', dpi=150, bbox_inches='tight')
print("Saved v14_errors.png")

# ============================================================
# SUMMARY STATS
# ============================================================
print("\n" + "=" * 60)
print("V14 SUMMARY")
print("=" * 60)

def stat(label, vals, threshold=2.0):
    abs_vals = [abs(v) for v in vals]
    m = np.mean(abs_vals)
    mx = max(abs_vals)
    flag = " ⚠️  NEEDS WORK" if m > threshold else " ✅"
    print(f"  {label:<30} mean|err| = {m:>7.2f}°  max|err| = {mx:>7.2f}°{flag}")
    return m

print("\nALL 31 CITIES:")
stat("Jupiter Azimuth", [r['Jup_Az_Err'] for r in results])
stat("Jupiter Elevation", [r['Jup_Elev_Err'] for r in results])
stat("Moon Azimuth", [r['Moon_Az_Err'] for r in results])
stat("Moon Elevation", [r['Moon_Elev_Err'] for r in results])

stable = [r for r in results if r['Near_Zenith'] == 'no']
print(f"\nSTABLE ({len(stable)} non-zenith):")
stat("Jupiter Azimuth", [r['Jup_Az_Err'] for r in stable])
stat("Jupiter Elevation", [r['Jup_Elev_Err'] for r in stable])
stat("Moon Azimuth", [r['Moon_Az_Err'] for r in stable])
stat("Moon Elevation", [r['Moon_Elev_Err'] for r in stable])

print("\n" + "=" * 60)
print("DOME GEOMETRY SUMMARY")
print("=" * 60)
print(f"\n  {'Body':<12} {'Height (km)':>12} {'Orbital R (km)':>16} {'Angle (°)':>10}")
print(f"  {'-'*54}")
print(f"  {'Polaris':<12} {'6500':>12} {'0 (fixed)':>16} {'N/A':>10}")
print(f"  {'Sun':<12} {'~7250*':>12} {'~15800*':>16} {'var':>10}")
print(f"  {'Jupiter':<12} {H_jup:>12.0f} {R_jup:>16.0f} {theta_jup:>10.1f}")
print(f"  {'Moon':<12} {H_moon:>12.0f} {R_moon:>16.0f} {theta_moon:>10.1f}")
print(f"\n  * Sun values from V11 geometric fit (not used in calibrated model)")

print("\n" + "=" * 60)
print("V14 COMPLETE")
print("=" * 60)
print("Files: v14_results.csv, v14_errors.png")
print("DONE")
