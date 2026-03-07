#!/usr/bin/env python3
"""
Lunar Transit Magnetic Anomaly Check
Station: Huancayo, Peru (HUA)
Tests whether Z-component drops ~2 nT during Moon zenith passage
"""

from skyfield.api import load, wgs84
from datetime import datetime, timezone
import requests
import numpy as np
import json

# HUA coordinates
HUA_LAT = -12.05
HUA_LON = -75.33
HUA_ALT = 3313  # meters

def get_moon_transit_time(date_str):
    """Find UTC time of Moon's upper transit over HUA today"""
    ts = load.timescale()
    eph = load('de421.bsp')
    
    earth = eph['earth']
    moon = eph['moon']
    observer = earth + wgs84.latlon(HUA_LAT, HUA_LON, elevation_m=HUA_ALT)
    
    # Search window: today
    t0 = ts.utc(*[int(x) for x in date_str.split('-')], 0)
    t1 = ts.utc(*[int(x) for x in date_str.split('-')], 23, 59)
    
    # Find culmination (max altitude = transit)
    alts = []
    for hour in range(24):
        t = ts.utc(*[int(x) for x in date_str.split('-')], hour, 0)
        astrometric = observer.at(t).observe(moon)
        alt, az, dist = astrometric.apparent().altaz()
        alts.append((hour, alt.degrees))
    
    # Find peak
    peak_hour = max(alts, key=lambda x: x[1])
    print(f"Moon transit at HUA: ~{peak_hour[0]:02d}:00 UTC, "
          f"altitude {peak_hour[1]:.1f}°")
    return peak_hour[0]

def fetch_intermagnet_hua(date_str):
    """
    Fetch INTERMAGNET 1-minute data for HUA
    Returns Z-component array (1440 values)
    """
    # INTERMAGNET data URL pattern
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    url = (f"https://imag-data.bgs.ac.uk/GIN_V1/GINServices"
           f"?Request=GetData&format=iaga2002"
           f"&testObsys=0&observatoryIagaCode=HUA"
           f"&samplesPerDay=1440&publicationState=adj-or-rep"
           f"&dataStartDate={date_str}&dataDuration=1")
    
    print(f"Fetching HUA data for {date_str}...")
    response = requests.get(url, timeout=30)
    
    if response.status_code != 200:
        print(f"HTTP {response.status_code} - trying alternate source")
        return None
    
    # Parse IAGA-2002 format
    lines = response.text.split('\n')
    z_values = []
    
    for line in lines:
        if line.startswith(' ') or (len(line) > 0 and line[0].isdigit()):
            parts = line.split()
            if len(parts) >= 5:
                try:
                    z = float(parts[4])  # Z component
                    if z != 99999.0:     # Missing data flag
                        z_values.append(z)
                except (ValueError, IndexError):
                    continue
    
    print(f"Got {len(z_values)} Z-component readings")
    return np.array(z_values)

def compute_anomaly(z_data, transit_hour, window_minutes=60):
    """
    Subtract quiet-day baseline (polynomial fit to non-transit hours)
    Look for anomaly in ±window_minutes around transit
    """
    if z_data is None or len(z_data) < 1000:
        print("Insufficient data")
        return None
    
    minutes = np.arange(len(z_data))
    transit_minute = transit_hour * 60
    
    # Baseline: exclude ±2 hours around transit
    mask = np.abs(minutes - transit_minute) > 120
    baseline_x = minutes[mask]
    baseline_y = z_data[mask]
    
    # Fit polynomial baseline
    coeffs = np.polyfit(baseline_x, baseline_y, 3)
    baseline = np.polyval(coeffs, minutes)
    residual = z_data - baseline
    
    # Anomaly window
    window_start = transit_minute - window_minutes
    window_end = transit_minute + window_minutes
    window_mask = (minutes >= window_start) & (minutes <= window_end)
    
    window_residual = residual[window_mask]
    
    peak_anomaly = np.min(window_residual)  # Most negative
    peak_minute = minutes[window_mask][np.argmin(window_residual)]
    noise_level = np.std(residual[~window_mask])
    
    print(f"\n--- RESULTS ---")
    print(f"Transit minute: {transit_minute} ({transit_hour:02d}:00 UTC)")
    print(f"Peak anomaly: {peak_anomaly:.2f} nT at minute {peak_minute} "
          f"({peak_minute//60:02d}:{peak_minute%60:02d} UTC)")
    print(f"Noise floor: ±{noise_level:.2f} nT")
    print(f"Signal/Noise: {abs(peak_anomaly)/noise_level:.1f}x")
    
    if abs(peak_anomaly) > 2 * noise_level:
        print("RESULT: Anomaly exceeds 2σ — potentially significant")
    else:
        print("RESULT: Anomaly within noise — not significant")
    
    return {
        'peak_nT': float(peak_anomaly),
        'peak_time_utc': f"{peak_minute//60:02d}:{peak_minute%60:02d}",
        'noise_nT': float(noise_level),
        'snr': float(abs(peak_anomaly)/noise_level),
        'transit_hour': transit_hour
    }

def main():
    from datetime import date
    today = date.today().isoformat()
    
    print(f"Lunar Transit Magnetic Check — {today}")
    print(f"Station: HUA (Huancayo, Peru)")
    print("="*50)
    
    transit_hour = get_moon_transit_time(today)
    z_data = fetch_intermagnet_hua(today)
    result = compute_anomaly(z_data, transit_hour)
    
    if result:
        with open(f'lunar_transit_{today}.json', 'w') as f:
            json.dump({'date': today, 'station': 'HUA', **result}, f, indent=2)
        print(f"\nSaved to lunar_transit_{today}.json")

if __name__ == "__main__":
    main()
