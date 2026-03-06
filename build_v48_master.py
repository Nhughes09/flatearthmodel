import pandas as pd
import json
import glob
from datetime import datetime

# Load existing V47 database
df_v47 = pd.read_csv('dome_v47_master_data.csv')

# Prepare new records from V48 JSONs
new_records = []

# 1. Parallax Wobble Results
try:
    with open('V48_Validation_Suite/results/parallax_results_20260306_175721.json', 'r') as f:
        parallax_data = json.load(f)
        new_records.extend([
            {
                'dataset': 'v48_parallax_wobble',
                'year': 2026,
                'parameter': 'target_parallax',
                'value': parallax_data['target_parallax_arcsec'],
                'unit': 'arcsec',
                'source': 'Dome Model V48',
                'notes': 'Target stellar parallax to mimic'
            },
            {
                'dataset': 'v48_parallax_wobble',
                'year': 2026,
                'parameter': 'derived_firmament_offset_km',
                'value': parallax_data['derived_offset_km'],
                'unit': 'km',
                'source': 'Dome Model V48',
                'notes': 'Required physical offset of firmament rotation axis from center'
            }
        ])
except FileNotFoundError:
    print("Parallax JSON not found.")

# 2. Annual Aberration Results
try:
    with open('V48_Validation_Suite/results/annual_aberration_results_20260306_175717.json', 'r') as f:
        aberration_data = json.load(f)
        new_records.extend([
            {
                'dataset': 'v48_annual_aberration',
                'year': 2026,
                'parameter': 'target_aberration',
                'value': aberration_data['target_aberration_arcsec'],
                'unit': 'arcsec',
                'source': 'Dome Model V48',
                'notes': 'Target Bradley stellar aberration'
            },
            {
                'dataset': 'v48_annual_aberration',
                'year': 2026,
                'parameter': 'aether_refractive_alpha',
                'value': aberration_data['derived_alpha'],
                'unit': 'gradient coefficient',
                'source': 'Dome Model V48',
                'notes': 'Aether refractive index gradient per solar zenith angle cycle'
            }
        ])
except FileNotFoundError:
    print("Aberration JSON not found.")

# 3. Eclipse 2026 Predictions
try:
    with open('V48_Validation_Suite/predictions/2026_eclipse_predictions_20260306_175644.json', 'r') as f:
        eclipse_data = json.load(f)
        for loc in eclipse_data:
            new_records.extend([
                {
                    'dataset': 'v48_eclipse_2026_prediction',
                    'year': 2026,
                    'parameter': f"{loc['location']}_predicted_magnetic_z_drop",
                    'value': loc['predictions']['magnetic_anomaly_z_nT']['value'],
                    'unit': 'nT',
                    'source': 'Dome Model V48',
                    'notes': 'Predicted Z-component trough during totality'
                },
                {
                    'dataset': 'v48_eclipse_2026_prediction',
                    'year': 2026,
                    'parameter': f"{loc['location']}_predicted_spring_gravity_drop",
                    'value': loc['predictions']['gravity_anomaly_spring_microGal']['value'],
                    'unit': 'microGal',
                    'source': 'Dome Model V48',
                    'notes': 'Predicted gravity anomaly for unshielded instruments'
                }
            ])
except FileNotFoundError:
    print("Eclipse predictions JSON not found.")

# Combine into master dataframe
if new_records:
    df_new = pd.DataFrame(new_records)
    df_master = pd.concat([df_v47, df_new], ignore_index=True)
else:
    df_master = df_v47

# Clean up column names and grouping for Claude prompt readability
df_master = df_master.sort_values(by=['dataset', 'year'])

# Save huge master file
master_filename = 'DOME_COSMOLOGY_V48_MASTER_DATABASE.csv'
df_master.to_csv(master_filename, index=False)

print(f"Successfully compiled {len(df_master)} mathematical datapoints into {master_filename}.")
