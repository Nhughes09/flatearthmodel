import pandas as pd

master_csv = 'dome_v46_master_data.csv'
df = pd.read_csv(master_csv)

new_rows = []

# Task 4.2: Predict 2026 Eclipse Anomaly
new_rows.append({'dataset': 'eclipse_gravity_compilation', 'year': 2026, 'parameter': 'prediction_mohe_replica', 'value': -7.5, 'unit': 'microGal', 'source': 'Dome Model V46', 'notes': 'Predicted symmetric aetheric pressure trough at first/last contacts for Aug 12 2026'})

# Task 4.4: Schumann Corrections Ad-Hoc
new_rows.append({'dataset': 'schumann_corrections', 'year': 1960, 'parameter': 'ideal_cavity_theoretical', 'value': 10.59, 'unit': 'Hz', 'source': 'Schumann Original', 'notes': 'Raw geometric mathematical derivation'})
new_rows.append({'dataset': 'schumann_corrections', 'year': 1960, 'parameter': 'empirical_measurement', 'value': 7.83, 'unit': 'Hz', 'source': 'Various', 'notes': 'Actual atmospheric measurement'})
new_rows.append({'dataset': 'schumann_corrections', 'year': 1960, 'parameter': 'fudge_factor_conductivity', 'value': 1.0, 'unit': 'bool', 'source': 'Mainstream Physics', 'notes': 'Ad-hoc finite conductivity curve (knee) added to lower f1'})
new_rows.append({'dataset': 'schumann_corrections', 'year': 1960, 'parameter': 'dome_theoretical_match', 'value': 11.78, 'unit': 'Hz', 'source': 'Dome Model', 'notes': 'Pure geometric resonance matches ground tellurics without ad-hoc conductivity corrections'})

# Task 4.5: Longitudinal Wave Faraday Penetration
new_rows.append({'dataset': 'longitudinal_wave_experiments', 'year': 2000, 'parameter': 'meyl_scalar_penetration', 'value': 1.0, 'unit': 'bool', 'source': 'Prof K. Meyl', 'notes': 'Demonstrated unattenuated signal penetration through Faraday cage shielding'})
new_rows.append({'dataset': 'longitudinal_wave_experiments', 'year': 1900, 'parameter': 'tesla_magnifying_transmitter', 'value': 1.0, 'unit': 'bool', 'source': 'Nikola Tesla', 'notes': 'Longitudinal ground compression wave transmission'})

new_df = pd.DataFrame(new_rows)
master_df = pd.concat([df, new_df], ignore_index=True)

master_df.to_csv(master_csv, index=False)
print("Phase 4 tasks 4.2, 4.4, and 4.5 correctly appended to dome_v46_master_data.csv")
