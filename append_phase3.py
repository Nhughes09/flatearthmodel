import pandas as pd

master_csv = 'dome_v46_master_data.csv'
df = pd.read_csv(master_csv)

new_rows = []

# Task 3.3: Telluric Data
new_rows.append({'dataset': 'telluric_spectrum', 'year': 2025, 'parameter': 'frequency_peak', 'value': 12.0, 'unit': 'Hz', 'source': 'Literature/Online', 'notes': 'Earth current resonance intervals reported at ~12Hz'})
new_rows.append({'dataset': 'telluric_spectrum', 'year': 2025, 'parameter': 'receiver_band_edge', 'value': 11.7, 'unit': 'Hz', 'source': 'Geometrics/MT', 'notes': '100kHz to 11.7Hz is a standard MT receiver spec limit'})

# Task 3.4: Deep Seismic Reflections
new_rows.append({'dataset': 'seismic_reflections', 'year': 2025, 'parameter': 'deepest_boundary', 'value': 5150.0, 'unit': 'km', 'source': 'Mainstream Seismology', 'notes': 'Inner Core Boundary is deepest recognized reflection. 12700km not cataloged.'})

# Task 3.5: Schumann Resonance Drift
new_rows.append({'dataset': 'schumann_drift', 'year': 2025, 'parameter': 'fundamental_range', 'value': 7.8, 'unit': 'Hz', 'source': 'Literature', 'notes': 'Varies 7.5 to 8.1 Hz daily. Long term solar/climate drift observed.'})
new_rows.append({'dataset': 'schumann_drift', 'year': 2025, 'parameter': 'predicted_drift_compatibility', 'value': 0.01, 'unit': 'Hz/decade', 'source': 'Dome Model', 'notes': '0.01 Hz/decade is plausible within mainstream noise margins.'})

# Task 3.6: Eclipse Gravity Anomalies
new_rows.append({'dataset': 'eclipse_gravity', 'year': 1997, 'parameter': 'gravity_anomaly_mohe', 'value': -6.5, 'unit': 'microGal', 'source': 'Chinese Academy of Sciences', 'notes': '6 to 7 microGal decrease at first/last contacts'})
new_rows.append({'dataset': 'eclipse_gravity', 'year': 1999, 'parameter': 'gravity_anomaly_europe', 'value': 11.0, 'unit': 'microGal', 'source': 'Various', 'notes': '10-12 microGal unexplainable change'})
new_rows.append({'dataset': 'eclipse_gravity', 'year': 1994, 'parameter': 'gravity_anomaly_montreal', 'value': 2.4, 'unit': 'microGal', 'source': 'Various', 'notes': '2.4 microgal anomaly recorded'})

new_df = pd.DataFrame(new_rows)
master_df = pd.concat([df, new_df], ignore_index=True)

master_df.to_csv(master_csv, index=False)
print("Phase 3 datasets correctly appended to dome_v46_master_data.csv")
