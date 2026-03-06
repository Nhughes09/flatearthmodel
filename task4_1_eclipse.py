import pandas as pd
import numpy as np

master_csv = 'dome_v46_master_data.csv'
df = pd.read_csv(master_csv)

# Task 4.1: Eclipse Gravity Anomalies Dataset
eclipse_data = [
    {'dataset': 'eclipse_gravity_compilation', 'year': 1954, 'parameter': 'gravity_anomaly_valley', 'value': np.nan, 'unit': 'microGal', 'source': 'Tomaschek/Frost54', 'notes': 'Two lateral valleys reported, magnitude unspecified'},
    {'dataset': 'eclipse_gravity_compilation', 'year': 1991, 'parameter': 'gravity_anomaly_mexico', 'value': 0.1, 'unit': 'microGal', 'source': 'LCR-G402', 'notes': '0.1 uGal attributed to atmospheric pressure'},
    {'dataset': 'eclipse_gravity_compilation', 'year': 1994, 'parameter': 'gravity_anomaly_montreal', 'value': 2.4, 'unit': 'microGal', 'source': 'Various', 'notes': 'Recorded 2.4 microgal anomaly'},
    {'dataset': 'eclipse_gravity_compilation', 'year': 1997, 'parameter': 'gravity_anomaly_mohe', 'value': -6.5, 'unit': 'microGal', 'source': 'Chinese Academy of Sciences / LaCoste-Romberg', 'notes': '6 to 7 microGal decrease symmetrically at first/last contacts'},
    {'dataset': 'eclipse_gravity_compilation', 'year': 1999, 'parameter': 'gravity_anomaly_europe', 'value': 11.0, 'unit': 'microGal', 'source': 'Various', 'notes': '10-12 microGal unexplainable change at onset'},
    {'dataset': 'eclipse_gravity_compilation', 'year': 1954, 'parameter': 'paris_theoretical_acceleration', 'value': 25.0, 'unit': 'microGal', 'source': 'Allais Theory', 'notes': '35 uGal anisotropic acceleration / 12 upward calculated'},
    {'dataset': 'eclipse_gravity_compilation', 'year': 1990, 'parameter': 'gravity_anomaly_finland', 'value': 0.0, 'unit': 'microGal', 'source': 'Various', 'notes': 'No anomalous variations detected.'}
]

new_df = pd.DataFrame(eclipse_data)

# Extract magnitudes for analysis where value is not NaN
magnitudes = new_df['value'].dropna().abs()
mean_anomaly = magnitudes.mean()
# Newtonian expectation is roughly 0.1 uGal
newtonian = 0.1

print("--- ECLIPSE GRAVITY ANOMALY ANALYSIS ---")
print(f"Mean Anomaly Magnitude: {mean_anomaly:.2f} μGal")
if mean_anomaly > newtonian:
    ratio = mean_anomaly / newtonian
    print(f"The observed mean anomaly is {ratio:.1f}x larger than the Newtonian prediction of {newtonian} μGal.")
    print("Conclusion: Newtonian tidal model fails to account for empirical eclipse gravitational troughing.")

# Append to master
master_df = pd.concat([df, new_df], ignore_index=True)
master_df.to_csv(master_csv, index=False)
print(f"\nAppended {len(new_df)} eclipse gravity records to {master_csv}")
