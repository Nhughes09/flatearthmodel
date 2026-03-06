#!/usr/bin/env python3
"""
Dome Cosmology V48 - Deep Seismic Reflection Search
Purpose: Search for reflections from 12,700 km depth (foundations)
"""

import numpy as np
import matplotlib.pyplot as plt
import obspy
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import json
from datetime import datetime
import os

# Initialize IRIS client
client = Client("IRIS")

# Parameters
target_depth = 12700  # km
vp_avg = 10.0  # km/s (average P-wave velocity)
travel_time_2way = 2 * target_depth / vp_avg  # seconds
print(f"Predicted 2-way travel time: {travel_time_2way:.0f} seconds ({travel_time_2way/60:.1f} minutes)")

# Search for large earthquakes (M > 7) in last 10 years
endtime = UTCDateTime.now()
starttime = endtime - 10 * 365 * 24 * 3600

print(f"Searching for earthquakes from {starttime} to {endtime}...")
catalog = client.get_events(starttime=starttime, endtime=endtime, minmagnitude=7, limit=10)

results = {
    'search_parameters': {
        'target_depth_km': target_depth,
        'predicted_travel_time_s': float(travel_time_2way),
        'vp_avg_km_s': vp_avg,
        'starttime': str(starttime),
        'endtime': str(endtime)
    },
    'earthquakes_found': [],
    'analysis_status': 'placeholder',
    'notes': 'Requires downloading waveform data and stacking. This script sets up the search.',
    'timestamp': datetime.now().isoformat()
}

for i, event in enumerate(catalog):
    if event.preferred_origin():
        origin = event.preferred_origin()
        mag = event.preferred_magnitude()
        results['earthquakes_found'].append({
            'id': i,
            'time': str(origin.time),
            'lat': origin.latitude,
            'lon': origin.longitude,
            'depth_km': origin.depth/1000,
            'magnitude': mag.mag if mag else None
        })

# Save results
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'V48_Validation_Suite/results/seismic_search_{timestamp}.json'
with open(filename, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Found {len(results['earthquakes_found'])} earthquakes")
print(f"To complete analysis: download waveforms and stack for arrivals at {travel_time_2way:.0f}s")

# Create waveform download script
download_script = f"""#!/bin/bash
# Waveform download script for deep reflection search
# Created: {datetime.now().isoformat()}

mkdir -p V48_Validation_Suite/waveforms

# Download waveforms for each earthquake
# Example for first event:
# obspy_download -c IRIS -t "{results['earthquakes_found'][0]['time']}" -d 3600 -s "ANMO" -o V48_Validation_Suite/waveforms/event1.mseed

echo "Run this script after installing obspy"
"""

with open('V48_Validation_Suite/code/download_waveforms.sh', 'w') as f:
    f.write(download_script)

os.system("chmod +x V48_Validation_Suite/code/download_waveforms.sh")

# Git commit
os.system(f"git add {filename} V48_Validation_Suite/code/download_waveforms.sh")
os.system(f'git commit -m "Add seismic reflection search - {timestamp}"')

print(f"Results saved to {filename}")
