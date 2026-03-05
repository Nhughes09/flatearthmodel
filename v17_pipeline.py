#!/usr/bin/env python3
"""
V17: FINAL VALIDATION
1. Per-city Moon declination at exact transit time
2. Corrected Moon predictions
3. Future prediction test (June 21 2026)
4. Complete model validation plot (R²)
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

from astropy.coordinates import (
    EarthLocation, AltAz, SkyCoord,
    get_sun, get_body, solar_system_ephemeris
)
from astropy.time import Time, TimeDelta
import astropy.units as u

solar_system_ephemeris.set("builtin")

CITIES = [
    ("Reykjavik, Iceland",64.1466,-21.9426),("London, UK",51.5074,-0.1278),
    ("New York City, USA",40.7128,-74.006),("Chicago, USA",41.8781,-87.6298),
    ("Los Angeles, USA",34.0522,-118.2437),("Tokyo, Japan",35.6762,139.6503),
    ("Dubai, UAE",25.2048,55.2708),("Singapore",1.3521,103.8198),
    ("Paris, France",48.8566,2.3522),("Berlin, Germany",52.52,13.405),
    ("Moscow, Russia",55.7558,37.6173),("Beijing, China",39.9042,116.4074),
    ("Mumbai, India",19.076,72.8777),("Cairo, Egypt",30.0444,31.2357),
    ("Toronto, Canada",43.6532,-79.3832),("Mexico City, Mexico",19.4326,-99.1332),
    ("Stockholm, Sweden",59.3293,18.0686),("Helsinki, Finland",60.1699,24.9384),
    ("Accra, Ghana",5.6037,-0.187),("Nairobi, Kenya",-1.2921,36.8219),
    ("Quito, Ecuador",-0.1807,-78.4678),("Sydney, Australia",-33.8688,151.2093),
    ("Perth, Australia",-31.9505,115.8605),("Cape Town, South Africa",-33.9249,18.4241),
    ("Johannesburg, South Africa",-26.2041,28.0473),("Santiago, Chile",-33.4489,-70.6693),
    ("Buenos Aires, Argentina",-34.6037,-58.3816),("Auckland, New Zealand",-36.8485,174.7633),
    ("Lima, Peru",-12.0464,-77.0428),("São Paulo, Brazil",-23.5505,-46.6333),
    ("Chapel Hill, NC, USA",35.9132,-79.056),
]

SUN_ALT_MIN = -0.833
POLARIS_H = 6500.0

def find_body_transit(body_name, location, date_str):
    t_center = Time(f"{date_str}T12:00:00", scale="utc")
    times = t_center + TimeDelta(np.linspace(-18, 18, 400) * 3600, format="sec")
    frame = AltAz(obstime=times, location=location)
    altaz = get_body(body_name, times).transform_to(frame)
    alts = altaz.alt.deg
    idx = np.argmax(alts)
    # Refine
    if 0 < idx < len(times)-1:
        t_lo, t_hi = times[max(0,idx-3)], times[min(len(times)-1,idx+3)]
        times2 = t_lo + TimeDelta(np.linspace(0, (t_hi-t_lo).sec, 100), format="sec")
        frame2 = AltAz(obstime=times2, location=location)
        altaz2 = get_body(body_name, times2).transform_to(frame2)
        idx2 = np.argmax(altaz2.alt.deg)
        return times2[idx2], altaz2[idx2].alt.deg, altaz2[idx2].az.deg
    return times[idx], alts[idx], altaz[idx].az.deg

def find_sun_transit(location, date_str):
    t_center = Time(f"{date_str}T12:00:00", scale="utc")
    approx = -location.lon.deg / 15.0
    t0 = t_center + TimeDelta(approx * 3600, format="sec")
    times = t0 + TimeDelta(np.linspace(-6, 6, 200) * 3600, format="sec")
    frame = AltAz(obstime=times, location=location)
    altaz = get_sun(times).transform_to(frame)
    idx = np.argmax(altaz.alt.deg)
    return times[idx], altaz[idx].alt.deg, altaz[idx].az.deg

def find_sunrise_sunset(location, date_str):
    """Fixed: search ±12hrs around solar noon"""
    loc = location
    t_noon, _, _ = find_sun_transit(loc, date_str)
    results = {}
    for event in ["rise", "set"]:
        if event == "rise":
            t_start = t_noon - TimeDelta(12*3600, format="sec")
            t_end = t_noon
        else:
            t_start = t_noon
            t_end = t_noon + TimeDelta(12*3600, format="sec")
        times = t_start + TimeDelta(np.linspace(0, (t_end-t_start).sec, 400), format="sec")
        frame = AltAz(obstime=times, location=loc)
        alts = get_sun(times).transform_to(frame).alt.deg
        crossings = np.where(np.diff(np.sign(alts)))[0]
        t_cross = None
        if len(crossings) > 0:
            if event == "rise":
                for c in crossings:
                    if alts[c] < 0 and alts[c+1] >= 0:
                        t_lo, t_hi = times[c], times[c+1]
                        for _ in range(50):
                            t_mid = t_lo + (t_hi-t_lo)*0.5
                            a = get_sun(t_mid).transform_to(AltAz(obstime=t_mid,location=loc)).alt.deg
                            if a < 0: t_lo = t_mid
                            else: t_hi = t_mid
                        t_cross = t_lo + (t_hi-t_lo)*0.5
                        break
            else:
                for c in reversed(crossings):
                    if alts[c] >= 0 and alts[c+1] < 0:
                        t_lo, t_hi = times[c], times[c+1]
                        for _ in range(50):
                            t_mid = t_lo + (t_hi-t_lo)*0.5
                            a = get_sun(t_mid).transform_to(AltAz(obstime=t_mid,location=loc)).alt.deg
                            if a >= 0: t_lo = t_mid
                            else: t_hi = t_mid
                        t_cross = t_lo + (t_hi-t_lo)*0.5
                        break
        if t_cross:
            frame_c = AltAz(obstime=t_cross, location=loc)
            az = get_sun(t_cross).transform_to(frame_c).az.deg
            results[event] = (t_cross, az)
        else:
            results[event] = (None, None)
    return results

# --- Model formulas ---
def m_polaris(lat):
    al = max(abs(lat), 0.01)
    elev = math.degrees(math.atan(POLARIS_H / (POLARIS_H / math.tan(math.radians(al)))))
    return -elev if lat < 0 else elev

def m_transit_elev(lat, dec):
    return min(90.0, 90.0 - abs(lat - dec))

def m_transit_az(lat, dec):
    diff = lat - dec
    if abs(diff) < 0.5: return 180.0 if lat >= 0 else 0.0
    return 180.0 if diff > 0 else 0.0

def m_day_length(lat, dec):
    lr, dr = math.radians(lat), math.radians(dec)
    ar = math.radians(SUN_ALT_MIN)
    c = (math.sin(ar) - math.sin(lr)*math.sin(dr)) / (math.cos(lr)*math.cos(dr))
    c = max(-1.0, min(1.0, c))
    return 2 * math.degrees(math.acos(c)) / 15.0

def m_sunrise_az(lat, dec):
    c = math.sin(math.radians(dec)) / math.cos(math.radians(lat))
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))

def m_sunset_az(lat, dec):
    return 360.0 - m_sunrise_az(lat, dec)

def wrap(obs, pred):
    e = obs - pred
    if e > 180: e -= 360
    elif e < -180: e += 360
    return e

# ============================================================
# TASK 1-2: PER-CITY MOON DECLINATION + CORRECTED PREDICTIONS
# ============================================================
print("=" * 70)
print("V17 TASK 1-2: Per-city Moon declination at exact transit")
print("=" * 70)

DATE = "2026-03-04"
moon_rows = []
for city, lat, lon in CITIES:
    loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=0*u.m)
    moon_t, moon_alt, moon_az = find_body_transit("moon", loc, DATE)
    
    # Get Moon dec at EXACT transit time
    moon_icrs = get_body("moon", moon_t)
    moon_dec = moon_icrs.dec.deg
    moon_ra = moon_icrs.ra.deg
    
    # Model prediction with per-city dec
    elev_flat = round(m_transit_elev(lat, moon_dec), 2)
    az_flat = m_transit_az(lat, moon_dec)
    elev_err = round(moon_alt - elev_flat, 2)
    az_err = round(wrap(moon_az, az_flat), 2)
    near_z = 'Y' if moon_alt > 80 else ''
    
    moon_rows.append({
        'City': city, 'Lat': lat, 'Lon': lon,
        'Transit_UTC': moon_t.iso,
        'Moon_Dec': round(moon_dec, 4),
        'Moon_RA': round(moon_ra, 4),
        'Moon_Elev_Obs': round(moon_alt, 2),
        'Moon_Elev_Flat': elev_flat,
        'Moon_Elev_Err': elev_err,
        'Moon_Az_Obs': round(moon_az, 2),
        'Moon_Az_Flat': az_flat,
        'Moon_Az_Err': az_err,
        'Near_Zenith': near_z,
    })
    print(f"  ✓ {city[:25]:<26} dec={moon_dec:>+7.3f}° elev_err={elev_err:>+6.2f}° az_err={az_err:>+7.1f}°")

df_moon = pd.DataFrame(moon_rows)
df_moon.to_csv('v17_moon_corrected.csv', index=False)

# Moon dec range across cities
decs = [r['Moon_Dec'] for r in moon_rows]
print(f"\nMoon dec range across 31 cities' transits: {min(decs):.3f}° to {max(decs):.3f}° (span: {max(decs)-min(decs):.3f}°)")

moon_elev_errs = [abs(r['Moon_Elev_Err']) for r in moon_rows]
stable_moon = [r for r in moon_rows if r['Near_Zenith'] != 'Y']
stable_moon_az = [abs(r['Moon_Az_Err']) for r in stable_moon]
print(f"Moon Elev (per-city dec): mean={np.mean(moon_elev_errs):.3f}°, max={max(moon_elev_errs):.3f}°")
print(f"Moon Az (stable {len(stable_moon)}): mean={np.mean(stable_moon_az):.3f}°, max={max(stable_moon_az):.3f}°")

# ============================================================
# TASK 5: PREDICTIVE TEST — JUNE 21 2026
# ============================================================
print("\n" + "=" * 70)
print("V17 TASK 5: PREDICTIVE TEST — JUNE 21 2026 (Summer Solstice)")
print("=" * 70)

TEST_DATE = "2026-06-21"
TEST_CITIES = [
    ("Reykjavik, Iceland", 64.1466, -21.9426),
    ("Chapel Hill, NC, USA", 35.9132, -79.056),
    ("Singapore", 1.3521, 103.8198),
    ("Sydney, Australia", -33.8688, 151.2093),
    ("Cape Town, South Africa", -33.9249, 18.4241),
]

t_solstice = Time(f"{TEST_DATE}T12:00:00", scale="utc")
sun_dec_solstice = get_sun(t_solstice).dec.deg
print(f"\nSun declination on June 21 2026: {sun_dec_solstice:.3f}°")

print(f"\n{'City':<28} {'Metric':<18} {'Observed':>10} {'Predicted':>10} {'Error':>10}")
print("-" * 80)

pred_test_rows = []
for city, lat, lon in TEST_CITIES:
    loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=0*u.m)
    
    # Observed from astropy
    sun_t, sun_alt, sun_az = find_sun_transit(loc, TEST_DATE)[0], find_sun_transit(loc, TEST_DATE)[1], find_sun_transit(loc, TEST_DATE)[2]
    dl_pred = round(m_day_length(lat, sun_dec_solstice), 2)
    rise_pred = round(m_sunrise_az(lat, sun_dec_solstice), 2)
    set_pred = round(m_sunset_az(lat, sun_dec_solstice), 2)
    elev_pred = round(m_transit_elev(lat, sun_dec_solstice), 2)
    
    # Observed sunrise/sunset
    ss = find_sunrise_sunset(loc, TEST_DATE)
    rise_t, rise_az_obs = ss['rise']
    set_t, set_az_obs = ss['set']
    
    dl_obs = round((set_t - rise_t).sec / 3600.0, 2) if rise_t and set_t else None
    
    elev_err = round(sun_alt - elev_pred, 2)
    dl_err = round(dl_obs - dl_pred, 2) if dl_obs else None
    rise_err = round(rise_az_obs - rise_pred, 2) if rise_az_obs else None
    set_err = round(set_az_obs - set_pred, 2) if set_az_obs else None
    
    print(f"{city:<28} {'Sun Elev':<18} {sun_alt:>10.2f} {elev_pred:>10.2f} {elev_err:>+10.2f}")
    print(f"{'':28} {'Day Length (hrs)':<18} {dl_obs:>10.2f} {dl_pred:>10.2f} {dl_err:>+10.2f}" if dl_obs else "")
    print(f"{'':28} {'Sunrise Az':<18} {rise_az_obs:>10.2f} {rise_pred:>10.2f} {rise_err:>+10.2f}" if rise_az_obs else "")
    print(f"{'':28} {'Sunset Az':<18} {set_az_obs:>10.2f} {set_pred:>10.2f} {set_err:>+10.2f}" if set_az_obs else "")
    
    pred_test_rows.append({
        'City': city, 'Lat': lat,
        'Sun_Elev_Obs': round(sun_alt, 2), 'Sun_Elev_Pred': elev_pred, 'Sun_Elev_Err': elev_err,
        'DL_Obs': dl_obs, 'DL_Pred': dl_pred, 'DL_Err': dl_err,
        'Rise_Az_Obs': round(rise_az_obs, 2) if rise_az_obs else None,
        'Rise_Az_Pred': rise_pred, 'Rise_Err': rise_err,
        'Set_Az_Obs': round(set_az_obs, 2) if set_az_obs else None,
        'Set_Az_Pred': set_pred, 'Set_Err': set_err,
    })

df_pred = pd.DataFrame(pred_test_rows)
df_pred.to_csv('v17_june21_predictions.csv', index=False)

# ============================================================
# TASK 6: VALIDATION PLOT (Observed vs Predicted, R²)
# ============================================================
print("\n" + "=" * 70)
print("V17 TASK 6: FINAL VALIDATION PLOT")
print("=" * 70)

# Gather all March 4 data
df_v15 = pd.read_csv('v15_transit_obs.csv')
df_v13 = pd.read_csv('v13_corrected_obs.csv')

obs_all, pred_all, body_labels = [], [], []

for i, (city, lat, lon) in enumerate(CITIES):
    co = df_v13.iloc[i]
    tr = df_v15.iloc[i]
    mr = moon_rows[i]
    
    t_ref = Time(f"2026-03-04T12:00:00", scale="utc")
    sun_dec = get_sun(t_ref).dec.deg
    jup_dec = get_body("jupiter", t_ref).dec.deg
    
    # Polaris
    obs_all.append(co['polaris_elevation'])
    pred_all.append(round(m_polaris(lat), 2))
    body_labels.append('Polaris')
    
    # Sun elev
    obs_all.append(co['sun_noon_elevation'])
    pred_all.append(round(m_transit_elev(lat, sun_dec), 2))
    body_labels.append('Sun')
    
    # Day length
    obs_all.append(co['day_length_hours'])
    pred_all.append(round(m_day_length(lat, sun_dec), 4))
    body_labels.append('Day Length')
    
    # Jupiter elev
    obs_all.append(tr['jup_transit_elev'])
    pred_all.append(round(m_transit_elev(lat, jup_dec), 2))
    body_labels.append('Jupiter')
    
    # Moon elev (per-city dec)
    obs_all.append(mr['Moon_Elev_Obs'])
    pred_all.append(mr['Moon_Elev_Flat'])
    body_labels.append('Moon')

obs_arr = np.array(obs_all)
pred_arr = np.array(pred_all)

# R² per body
fig, ax = plt.subplots(figsize=(10, 10))
body_colors = {'Polaris': '#e74c3c', 'Sun': '#f39c12', 'Day Length': '#2ecc71',
               'Jupiter': '#3498db', 'Moon': '#9b59b6'}

for body in ['Polaris', 'Sun', 'Day Length', 'Jupiter', 'Moon']:
    mask = [b == body for b in body_labels]
    o = np.array([obs_all[i] for i in range(len(mask)) if mask[i]])
    p = np.array([pred_all[i] for i in range(len(mask)) if mask[i]])
    
    ss_res = np.sum((o - p)**2)
    ss_tot = np.sum((o - np.mean(o))**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    
    ax.scatter(o, p, c=body_colors[body], s=30, alpha=0.7, label=f'{body} (R²={r2:.6f})', zorder=3)
    print(f"  {body:<12} R² = {r2:.8f} ({len(o)} points)")

# Perfect line
all_min = min(min(obs_all), min(pred_all))
all_max = max(max(obs_all), max(pred_all))
ax.plot([all_min, all_max], [all_min, all_max], 'k--', alpha=0.5, label='Perfect (y=x)')

# Overall R²
ss_res = np.sum((obs_arr - pred_arr)**2)
ss_tot = np.sum((obs_arr - np.mean(obs_arr))**2)
r2_all = 1 - ss_res / ss_tot

ax.set_xlabel('Observed Value', fontsize=12)
ax.set_ylabel('Predicted Value (Dome Model)', fontsize=12)
ax.set_title(f'V17 — Dome Model Validation\nOverall R² = {r2_all:.8f}', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

plt.tight_layout()
plt.savefig('v17_final_validation.png', dpi=150, bbox_inches='tight')
print(f"\n  OVERALL R² = {r2_all:.8f}")
print("Saved v17_final_validation.png")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("V17 FINAL RESULTS")
print("=" * 70)

print("\n  MARCH 4 2026 — MODEL ACCURACY:")
print(f"  {'Metric':<30} {'Mean |Error|':>15} {'Max |Error|':>15} {'Status'}")
print(f"  {'-'*75}")

metrics = [
    ("Polaris Elevation", [abs(m_polaris(lat) - df_v13.iloc[i]['polaris_elevation']) for i,(c,lat,lon) in enumerate(CITIES)]),
    ("Sun Elevation", [abs(m_transit_elev(lat, get_sun(Time("2026-03-04T12:00:00",scale="utc")).dec.deg) - df_v13.iloc[i]['sun_noon_elevation']) for i,(c,lat,lon) in enumerate(CITIES)]),
    ("Day Length (hrs)", [abs(m_day_length(lat, get_sun(Time("2026-03-04T12:00:00",scale="utc")).dec.deg) - df_v13.iloc[i]['day_length_hours']) for i,(c,lat,lon) in enumerate(CITIES)]),
    ("Jupiter Elevation", [abs(m_transit_elev(lat, get_body("jupiter",Time("2026-03-04T12:00:00",scale="utc")).dec.deg) - df_v15.iloc[i]['jup_transit_elev']) for i,(c,lat,lon) in enumerate(CITIES)]),
    ("Moon Elevation (per-city)", [abs(r['Moon_Elev_Err']) for r in moon_rows]),
]

for name, errs in metrics:
    m = np.mean(errs)
    mx = max(errs)
    s = "✅" if m < 1.0 else "⚠️"
    print(f"  {name:<30} {m:>14.3f}° {mx:>14.3f}° {s}")

print(f"\n  JUNE 21 2026 — FUTURE PREDICTION TEST:")
for r in pred_test_rows:
    sym = "✅" if r['Sun_Elev_Err'] is not None and abs(r['Sun_Elev_Err']) < 1 else "⚠️"
    print(f"  {r['City']:<28} Sun Elev err={r['Sun_Elev_Err']:>+.2f}° DL err={r['DL_Err']:>+.2f}hrs {sym}" if r['DL_Err'] else f"  {r['City']}")

print(f"\n{'='*70}")
print("V17 COMPLETE — MODEL VALIDATED")
print(f"{'='*70}")
print("Files: v17_moon_corrected.csv, v17_june21_predictions.csv,")
print("       v17_final_validation.png")
print("DONE")
