#!/usr/bin/env python3
"""
V13 Full Pipeline:
1. Fix day length bug (search ±12hrs around solar noon)
2. Re-run full model comparison
3. Plot error charts
4. Test southern Polaris fix
5. Add sunrise/sunset azimuth predictions
6. Summary stats
"""
import warnings
warnings.filterwarnings("ignore")

import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from astropy.coordinates import EarthLocation, AltAz, get_sun, get_body, solar_system_ephemeris
from astropy.time import Time, TimeDelta
import astropy.units as u

solar_system_ephemeris.set("builtin")

# ============================================================
# TASK 1: Fix day length bug — search ±12hrs around solar noon
# ============================================================

CITIES = [
    ("Reykjavik, Iceland",        64.1466, -21.9426),
    ("London, UK",                51.5074,  -0.1278),
    ("New York City, USA",        40.7128, -74.0060),
    ("Chicago, USA",              41.8781, -87.6298),
    ("Los Angeles, USA",          34.0522, -118.2437),
    ("Tokyo, Japan",              35.6762, 139.6503),
    ("Dubai, UAE",                25.2048,  55.2708),
    ("Singapore",                  1.3521, 103.8198),
    ("Paris, France",             48.8566,   2.3522),
    ("Berlin, Germany",           52.5200,  13.4050),
    ("Moscow, Russia",            55.7558,  37.6173),
    ("Beijing, China",            39.9042, 116.4074),
    ("Mumbai, India",             19.0760,  72.8777),
    ("Cairo, Egypt",              30.0444,  31.2357),
    ("Toronto, Canada",           43.6532, -79.3832),
    ("Mexico City, Mexico",       19.4326, -99.1332),
    ("Stockholm, Sweden",         59.3293,  18.0686),
    ("Helsinki, Finland",         60.1699,  24.9384),
    ("Accra, Ghana",               5.6037,  -0.1870),
    ("Nairobi, Kenya",            -1.2921,  36.8219),
    ("Quito, Ecuador",            -0.1807, -78.4678),
    ("Sydney, Australia",        -33.8688, 151.2093),
    ("Perth, Australia",         -31.9505, 115.8605),
    ("Cape Town, South Africa",  -33.9249,  18.4241),
    ("Johannesburg, South Africa",-26.2041, 28.0473),
    ("Santiago, Chile",          -33.4489, -70.6693),
    ("Buenos Aires, Argentina",  -34.6037, -58.3816),
    ("Auckland, New Zealand",    -36.8485, 174.7633),
    ("Lima, Peru",               -12.0464, -77.0428),
    ("São Paulo, Brazil",        -23.5505, -46.6333),
    ("Chapel Hill, NC, USA",      35.9132, -79.0560),
]

DATE_STR = "2026-03-04"

def find_transit(location):
    """Find solar noon by sampling sun altitude over 24hrs."""
    # Use approximate noon based on longitude
    approx_noon_utc = 12.0 - (location.lon.deg / 15.0)
    t0 = Time(f"{DATE_STR}T00:00:00", scale="utc") + TimeDelta(approx_noon_utc * 3600, format="sec")
    # Search ±6 hours around approximate noon
    times = t0 + TimeDelta(np.linspace(-6, 6, 200) * 3600, format="sec")
    frame = AltAz(obstime=times, location=location)
    sun_altaz = get_sun(times).transform_to(frame)
    idx = np.argmax(sun_altaz.alt.deg)
    return times[idx]

def find_horizon_crossing_fixed(location, t_noon, event="rise", n_coarse=400, n_fine=60):
    """
    FIXED: Search ±12 hours around solar noon instead of 00:00-24:00 UTC.
    This fixes the date-boundary inversion bug.
    """
    if event == "rise":
        # Search from noon-12h to noon
        t_start = t_noon - TimeDelta(12 * 3600, format="sec")
        t_end = t_noon
    else:
        # Search from noon to noon+12h
        t_start = t_noon
        t_end = t_noon + TimeDelta(12 * 3600, format="sec")
    
    times = t_start + TimeDelta(np.linspace(0, (t_end - t_start).sec, n_coarse), format="sec")
    frame = AltAz(obstime=times, location=location)
    alts = get_sun(times).transform_to(frame).alt.deg
    
    crossings = np.where(np.diff(np.sign(alts)))[0]
    if len(crossings) == 0:
        return None
    
    if event == "rise":
        for c in crossings:
            if alts[c] < 0 and alts[c + 1] >= 0:
                t_lo, t_hi = times[c], times[c + 1]
                break
        else:
            return None
    else:
        for c in reversed(crossings):
            if alts[c] >= 0 and alts[c + 1] < 0:
                t_lo, t_hi = times[c], times[c + 1]
                break
        else:
            return None
    
    # Bisection refinement
    for _ in range(n_fine):
        t_mid = t_lo + (t_hi - t_lo) * 0.5
        alt_mid = get_sun(t_mid).transform_to(
            AltAz(obstime=t_mid, location=location)
        ).alt.deg
        if (event == "rise" and alt_mid < 0) or (event == "set" and alt_mid >= 0):
            t_lo = t_mid
        else:
            t_hi = t_mid
    return t_lo + (t_hi - t_lo) * 0.5

print("=" * 60)
print("TASK 1: Recalculating observations with fixed day lengths...")
print("=" * 60)

polaris = from_coords = None
from astropy.coordinates import SkyCoord
polaris = SkyCoord(ra="02h31m49.09s", dec="+89d15m50.8s", frame="icrs")

obs_rows = []
for city_name, lat, lon in CITIES:
    loc = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=0 * u.m)
    
    t_noon = find_transit(loc)
    frame_noon = AltAz(obstime=t_noon, location=loc)
    
    sun_noon = get_sun(t_noon).transform_to(frame_noon)
    polaris_noon = polaris.transform_to(frame_noon)
    jupiter_noon = get_body("jupiter", t_noon).transform_to(frame_noon)
    moon_noon = get_body("moon", t_noon).transform_to(frame_noon)
    
    sun_ec = get_sun(t_noon)
    moon_ec = get_body("moon", t_noon)
    elongation = sun_ec.separation(moon_ec)
    moon_phase = (1 - np.cos(elongation.rad)) / 2.0
    
    # FIXED: search around solar noon
    t_rise = find_horizon_crossing_fixed(loc, t_noon, event="rise")
    t_set = find_horizon_crossing_fixed(loc, t_noon, event="set")
    
    if t_rise is not None:
        frame_rise = AltAz(obstime=t_rise, location=loc)
        sun_rise = get_sun(t_rise).transform_to(frame_rise)
        sunrise_alt = round(sun_rise.alt.deg, 4)
        sunrise_az = round(sun_rise.az.deg, 4)
    else:
        sunrise_alt = sunrise_az = None
    
    if t_set is not None:
        frame_set = AltAz(obstime=t_set, location=loc)
        sun_set = get_sun(t_set).transform_to(frame_set)
        sunset_alt = round(sun_set.alt.deg, 4)
        sunset_az = round(sun_set.az.deg, 4)
    else:
        sunset_alt = sunset_az = None
    
    if t_rise is not None and t_set is not None:
        day_length = round((t_set - t_rise).sec / 3600.0, 4)
    else:
        day_length = None
    
    obs_rows.append({
        'city': city_name, 'latitude': lat, 'longitude': lon,
        'date': DATE_STR, 'solar_noon_utc': t_noon.iso,
        'polaris_elevation': round(polaris_noon.alt.deg, 4),
        'polaris_azimuth': round(polaris_noon.az.deg, 4),
        'sun_noon_elevation': round(sun_noon.alt.deg, 4),
        'sun_noon_azimuth': round(sun_noon.az.deg, 4),
        'sunrise_elevation': sunrise_alt, 'sunrise_azimuth': sunrise_az,
        'sunset_elevation': sunset_alt, 'sunset_azimuth': sunset_az,
        'day_length_hours': day_length,
        'jupiter_elevation': round(jupiter_noon.alt.deg, 4),
        'jupiter_azimuth': round(jupiter_noon.az.deg, 4),
        'moon_elevation': round(moon_noon.alt.deg, 4),
        'moon_azimuth': round(moon_noon.az.deg, 4),
        'moon_phase_fraction': round(moon_phase, 4),
    })
    print(f"  ✓ {city_name} — DL: {day_length:.2f} hrs" if day_length else f"  ✓ {city_name} — polar")

df_obs = pd.DataFrame(obs_rows)
df_obs.to_csv('v13_corrected_obs.csv', index=False)
print(f"\nSaved v13_corrected_obs.csv ({len(df_obs)} rows)")

# ============================================================
# TASKS 2, 4, 5: Full model comparison + Polaris V2 + Sunrise/Sunset Az
# ============================================================
print("\n" + "=" * 60)
print("TASKS 2-5: Full model comparison...")
print("=" * 60)

POLARIS_H = 6500.0
SUN_DEC = -6.4
SUN_ALT_MIN = -0.833

def polaris_r_v1(lat):
    """Original: north tuned, south 2.5x multiplier"""
    if lat > 0:
        return POLARIS_H / math.tan(math.radians(lat))
    else:
        al = abs(lat)
        if al > 0.5:
            return (POLARIS_H / math.tan(math.radians(al))) * 2.5
        else:
            return 750000 * 2.5

def polaris_r_v2(lat):
    """V2 fix: same formula north and south, no multiplier"""
    al = abs(lat) if abs(lat) > 0.01 else 0.01
    return POLARIS_H / math.tan(math.radians(al))

def pred_polaris(lat, r_func):
    r = r_func(lat)
    elev = math.degrees(math.atan(POLARIS_H / r))
    if lat < 0:
        elev = -elev
    return round(elev, 2)

def pred_sun_az(lat):
    return 180.0 if lat >= 0 else 0.0

def pred_sun_elev(lat, dec=SUN_DEC):
    return round(min(90.0, 90.0 - abs(lat - dec)), 2)

def pred_day_length(lat, dec=SUN_DEC):
    lat_r = math.radians(lat)
    dec_r = math.radians(dec)
    alt_r = math.radians(SUN_ALT_MIN)
    cos_H0 = (math.sin(alt_r) - math.sin(lat_r) * math.sin(dec_r)) / \
             (math.cos(lat_r) * math.cos(dec_r))
    cos_H0 = max(-1.0, min(1.0, cos_H0))
    H0 = math.degrees(math.acos(cos_H0))
    return round(2 * H0 / 15.0, 4)

def pred_sunrise_az(lat, dec=SUN_DEC):
    """Sunrise azimuth from hour angle formula"""
    lat_r = math.radians(lat)
    dec_r = math.radians(dec)
    # At sunrise, altitude = 0 (approx), so:
    # cos(az) = sin(dec) / cos(lat)  [when alt=0]
    cos_az = math.sin(dec_r) / math.cos(lat_r)
    cos_az = max(-1.0, min(1.0, cos_az))
    az = math.degrees(math.acos(cos_az))
    return round(az, 2)

def pred_sunset_az(lat, dec=SUN_DEC):
    return round(360.0 - pred_sunrise_az(lat, dec), 2)

def wrap_az_err(obs, pred):
    e = obs - pred
    if e > 180: e -= 360
    elif e < -180: e += 360
    return round(e, 2)

results = []
for _, row in df_obs.iterrows():
    lat = row['latitude']
    elev_obs = row['sun_noon_elevation']
    near_zenith = 'YES' if elev_obs > 80 else 'no'
    
    pol_v1 = pred_polaris(lat, polaris_r_v1)
    pol_v2 = pred_polaris(lat, polaris_r_v2)
    
    az_flat = pred_sun_az(lat)
    az_obs = row['sun_noon_azimuth']
    az_err = wrap_az_err(az_obs, az_flat)
    
    elev_flat = pred_sun_elev(lat)
    
    dl_obs = row['day_length_hours']
    dl_flat = pred_day_length(lat)
    
    rise_az_flat = pred_sunrise_az(lat)
    set_az_flat = pred_sunset_az(lat)
    rise_az_obs = row['sunrise_azimuth']
    set_az_obs = row['sunset_azimuth']
    
    results.append({
        'City': row['city'],
        'Lat': lat,
        'Pol_Obs': row['polaris_elevation'],
        'Pol_Flat_V1': pol_v1,
        'Pol_Err_V1': round(row['polaris_elevation'] - pol_v1, 2),
        'Pol_Flat_V2': pol_v2,
        'Pol_Err_V2': round(row['polaris_elevation'] - pol_v2, 2),
        'Az_Obs': az_obs,
        'Az_Flat': az_flat,
        'Az_Err': az_err,
        'Elev_Obs': elev_obs,
        'Elev_Flat': elev_flat,
        'Elev_Err': round(elev_obs - elev_flat, 2),
        'DL_Obs': dl_obs,
        'DL_Flat': dl_flat,
        'DL_Err': round(dl_obs - dl_flat, 4),
        'Rise_Az_Obs': rise_az_obs,
        'Rise_Az_Flat': rise_az_flat,
        'Rise_Az_Err': round(rise_az_obs - rise_az_flat, 2) if rise_az_obs else None,
        'Set_Az_Obs': set_az_obs,
        'Set_Az_Flat': set_az_flat,
        'Set_Az_Err': round(set_az_obs - set_az_flat, 2) if set_az_obs else None,
        'Near_Zenith': near_zenith,
    })

df_results = pd.DataFrame(results)
df_results.to_csv('v13_results.csv', index=False)

# Print table
print(f"\n{'City':<30} {'Lat':>6} {'PolErrV1':>8} {'PolErrV2':>8} {'AzErr':>6} {'ElvErr':>7} {'DL_Obs':>7} {'DL_Flat':>7} {'DLErr':>7} {'RiseAzE':>8} {'SetAzE':>8} {'Zen'}")
print("-" * 140)
for r in results:
    rae = f"{r['Rise_Az_Err']:>8.2f}" if r['Rise_Az_Err'] is not None else "    N/A "
    sae = f"{r['Set_Az_Err']:>8.2f}" if r['Set_Az_Err'] is not None else "    N/A "
    print(f"{r['City'][:29]:<30} {r['Lat']:>6.2f} {r['Pol_Err_V1']:>8.2f} {r['Pol_Err_V2']:>8.2f} {r['Az_Err']:>6.2f} {r['Elev_Err']:>7.2f} {r['DL_Obs']:>7.2f} {r['DL_Flat']:>7.2f} {r['DL_Err']:>7.4f} {rae} {sae} {r['Near_Zenith']}")

# ============================================================
# TASK 3: Error charts
# ============================================================
print("\n" + "=" * 60)
print("TASK 3: Generating error charts...")
print("=" * 60)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Firmament Model V13 — Error Analysis vs Latitude', fontsize=14, fontweight='bold')

lats = [r['Lat'] for r in results]
zenith_mask = [r['Near_Zenith'] == 'YES' for r in results]
stable_mask = [not z for z in zenith_mask]

# Panel 1: Polaris error (V2)
ax = axes[0, 0]
pol_errs_v2 = [r['Pol_Err_V2'] for r in results]
colors = ['red' if z else 'steelblue' for z in zenith_mask]
ax.scatter(lats, pol_errs_v2, c=colors, s=40, zorder=3)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Latitude (°)')
ax.set_ylabel('Polaris Error (°)')
ax.set_title('Polaris Elevation Error (V2)')
ax.grid(True, alpha=0.3)

# Panel 2: Sun Az error
ax = axes[0, 1]
az_errs = [r['Az_Err'] for r in results]
ax.scatter(lats, az_errs, c=colors, s=40, zorder=3)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Latitude (°)')
ax.set_ylabel('Sun Az Error (°)')
ax.set_title('Sun Noon Azimuth Error')
ax.grid(True, alpha=0.3)

# Panel 3: Sun Elev error
ax = axes[1, 0]
elev_errs = [r['Elev_Err'] for r in results]
ax.scatter(lats, elev_errs, c=colors, s=40, zorder=3)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Latitude (°)')
ax.set_ylabel('Sun Elev Error (°)')
ax.set_title('Sun Noon Elevation Error')
ax.grid(True, alpha=0.3)

# Panel 4: Day Length error
ax = axes[1, 1]
dl_errs = [r['DL_Err'] for r in results]
ax.scatter(lats, dl_errs, c=colors, s=40, zorder=3)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Latitude (°)')
ax.set_ylabel('Day Length Error (hrs)')
ax.set_title('Day Length Error (CORRECTED data)')
ax.grid(True, alpha=0.3)

# Legend
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue', markersize=8, label='Stable'),
                   Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Near-Zenith (>80°)')]
fig.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('v13_errors.png', dpi=150, bbox_inches='tight')
print("Saved v13_errors.png")

# ============================================================
# TASK 6: Summary stats
# ============================================================
print("\n" + "=" * 60)
print("TASK 6: SUMMARY STATS")
print("=" * 60)

stable_results = [r for r in results if r['Near_Zenith'] == 'no']

def stat(label, vals, unit="°", threshold=1.0):
    vals = [v for v in vals if v is not None]
    abs_vals = [abs(v) for v in vals]
    mean_e = np.mean(abs_vals)
    max_e = max(abs_vals)
    flag = " ⚠️  NEEDS WORK" if mean_e > threshold else " ✅"
    print(f"  {label:<30} mean|err| = {mean_e:>7.3f}{unit}  max|err| = {max_e:>7.3f}{unit}{flag}")
    return mean_e

print("\nALL 31 CITIES:")
stat("Polaris (V1 — original)", [r['Pol_Err_V1'] for r in results])
stat("Polaris (V2 — symmetric)", [r['Pol_Err_V2'] for r in results])
stat("Sun Noon Azimuth", [r['Az_Err'] for r in results])
stat("Sun Noon Elevation", [r['Elev_Err'] for r in results])
stat("Day Length", [r['DL_Err'] for r in results], unit=" hrs", threshold=0.5)
stat("Sunrise Azimuth", [r['Rise_Az_Err'] for r in results])
stat("Sunset Azimuth", [r['Set_Az_Err'] for r in results])

print(f"\nSTABLE ({len(stable_results)} non-zenith cities):")
stat("Polaris (V2 — symmetric)", [r['Pol_Err_V2'] for r in stable_results])
stat("Sun Noon Azimuth", [r['Az_Err'] for r in stable_results])
stat("Sun Noon Elevation", [r['Elev_Err'] for r in stable_results])
stat("Day Length", [r['DL_Err'] for r in stable_results], unit=" hrs", threshold=0.5)
stat("Sunrise Azimuth", [r['Rise_Az_Err'] for r in stable_results])
stat("Sunset Azimuth", [r['Set_Az_Err'] for r in stable_results])

print("\n" + "=" * 60)
print("V13 PIPELINE COMPLETE")
print("=" * 60)
print("Files saved:")
print("  v13_corrected_obs.csv     — Fixed astropy observations")
print("  v13_results.csv           — Full model comparison")
print("  v13_errors.png            — 4-panel error chart")
print("\nDONE")
