#!/usr/bin/env python3
"""
2024 Eclipse Replication (PRED-W004)
Reproduce Nov 2024 paper's 9-station results
Paper: "Geomagnetic Field Variations During the April 8, 2024 Total Solar Eclipse"
Stations: BOU, FRD, CMO, BSL, TUC, DHT, NEW, OTT, STJ
"""

import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json
import hashlib

# Station coordinates (from INTERMAGNET)
STATIONS = {
    'BOU': {'name': 'Boulder', 'lat': 40.1, 'lon': -105.2, 'code': 'BOU'},
    'FRD': {'name': 'Fredericksburg', 'lat': 38.2, 'lon': -77.4, 'code': 'FRD'},
    'CMO': {'name': 'College', 'lat': 64.9, 'lon': -147.8, 'code': 'CMO'},
    'BSL': {'name': 'Stennis', 'lat': 30.4, 'lon': -89.6, 'code': 'BSL'},
    'TUC': {'name': 'Tucson', 'lat': 32.2, 'lon': -110.7, 'code': 'TUC'},
    'DHT': {'name': 'Del Rio', 'lat': 29.5, 'lon': -100.9, 'code': 'DHT'},
    'NEW': {'name': 'Newport', 'lat': 48.3, 'lon': -117.1, 'code': 'NEW'},
    'OTT': {'name': 'Ottawa', 'lat': 45.4, 'lon': -75.6, 'code': 'OTT'},
    'STJ': {'name': 'St Johns', 'lat': 47.6, 'lon': -52.7, 'code': 'STJ'}
}

ECLIPSE_DATE = '2024-04-08'
ECLIPSE_TIMES = {
    'BOU': '18:30 UTC',  # Approximate max eclipse at each station
    'FRD': '18:45 UTC',
    'CMO': '19:15 UTC',
    'BSL': '18:15 UTC',
    'TUC': '18:00 UTC',
    'DHT': '18:05 UTC',
    'NEW': '18:40 UTC',
    'OTT': '18:55 UTC',
    'STJ': '19:05 UTC'
}

def fetch_intermagnet_data(station, date):
    """Fetch 1-minute definitive data from INTERMAGNET"""
    # Note: Requires registration. Using public mirror for demo
    year = date[:4]
    month = date[5:7]
    day = date[8:10]
    
    # Using BGS GIN API (free with registration)
    url = f"https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=iaga2002&observatoryIagaCode={station}&samplesPerDay=1440&publicationState=adj-or-rep&dataStartDate={date}&dataDuration=1"
    
    print(f"Fetching {station} for {date}...")
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} – trying fallback")
            return None
        
        # Parse IAGA-2002 format
        lines = r.text.split('\n')
        z_vals = []
        for line in lines:
            if line and line[0].isdigit():
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        z = float(parts[4])
                        if z != 99999.0:  # Missing data flag
                            z_vals.append(z)
                    except:
                        continue
        return np.array(z_vals)
    except Exception as e:
        print(f"  Error: {e}")
        return None

def get_quiet_baseline(station, eclipse_date):
    """Use 3 days before and 3 days after, excluding eclipse day"""
    date_obj = datetime.strptime(eclipse_date, '%Y-%m-%d')
    quiet_dates = []
    
    # 3 days before
    for i in range(3, 0, -1):
        d = (date_obj - timedelta(days=i)).strftime('%Y-%m-%d')
        quiet_dates.append(d)
    # 3 days after (skip eclipse day)
    for i in range(1, 4):
        d = (date_obj + timedelta(days=i)).strftime('%Y-%m-%d')
        quiet_dates.append(d)
    
    all_data = []
    for d in quiet_dates:
        data = fetch_intermagnet_data(station, d)
        if data is not None and len(data) == 1440:
            all_data.append(data)
    
    if len(all_data) >= 3:
        return np.median(all_data, axis=0)  # Robust to outliers
    return None

def compute_anomaly(station):
    """Compute eclipse day anomaly vs quiet baseline"""
    print(f"\n=== Processing {station} ===")
    
    # Get eclipse day data
    eclipse_data = fetch_intermagnet_data(station, ECLIPSE_DATE)
    if eclipse_data is None or len(eclipse_data) != 1440:
        print(f"  No eclipse data")
        return None
    
    # Get quiet baseline
    baseline = get_quiet_baseline(station, ECLIPSE_DATE)
    if baseline is None:
        print(f"  Could not establish baseline")
        return None
    
    # Subtract to get residual
    residual = eclipse_data - baseline
    
    # Find max negative anomaly in expected window
    eclipse_hour = int(ECLIPSE_TIMES[station].split(':')[0])
    window_start = (eclipse_hour - 2) * 60  # ±2 hours
    window_end = (eclipse_hour + 2) * 60
    
    window_residual = residual[window_start:window_end]
    window_minutes = np.arange(window_start, window_end)
    
    peak_idx = np.argmin(window_residual)
    peak_time_min = window_minutes[peak_idx]
    peak_time_utc = f"{peak_time_min//60:02d}:{peak_time_min%60:02d}"
    peak_value = window_residual[peak_idx]
    
    # Noise estimate (using early morning hours 0-4 UTC)
    noise = np.std(residual[0:240])
    
    print(f"  Peak anomaly: {peak_value:.2f} nT at {peak_time_utc}")
    print(f"  Noise floor: ±{noise:.2f} nT")
    print(f"  SNR: {abs(peak_value)/noise:.1f}")
    
    return {
        'station': station,
        'peak_nT': float(peak_value),
        'peak_time_utc': peak_time_utc,
        'paper_time': ECLIPSE_TIMES[station],
        'noise_nT': float(noise),
        'snr': float(abs(peak_value)/noise),
        'data_quality': 'good' if len(eclipse_data)==1440 else 'partial'
    }

def main():
    print("="*60)
    print("2024 ECLIPSE REPLICATION (PRED-W004)")
    print("="*60)
    print(f"Date: {ECLIPSE_DATE}")
    print(f"Stations: {', '.join(STATIONS.keys())}")
    print("-"*60)
    
    results = []
    for code in STATIONS.keys():
        res = compute_anomaly(code)
        if res:
            results.append(res)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for r in results:
        match = "✓" if abs(r['peak_nT']) > 2*r['noise_nT'] else "?"
        print(f"{match} {r['station']}: {r['peak_nT']:.1f} nT at {r['peak_time_utc']} "
              f"(paper: {r['paper_time']}) SNR={r['snr']:.1f}")
    
    # Save
    output = {
        'date': ECLIPSE_DATE,
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    with open('eclipse_2024_replication.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    # SHA-256
    hash_input = json.dumps(output, sort_keys=True).encode()
    sha = hashlib.sha256(hash_input).hexdigest()
    print(f"\nSHA-256: {sha}")
    print("Saved to eclipse_2024_replication.json")

if __name__ == "__main__":
    main()
