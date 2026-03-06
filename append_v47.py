import pandas as pd

# Load existing master CSV
try:
    master_df = pd.read_csv('dome_v46_master_data.csv')
except:
    master_df = pd.DataFrame(columns=['dataset', 'year', 'parameter', 'value', 'unit', 'source', 'notes'])

# New records from our analysis
new_records = [
    {
        'dataset': 'bou_magnetic_2017',
        'year': 2017,
        'parameter': 'z_component_quiet_mean_16UTC',
        'value': 47727.3,
        'unit': 'nT',
        'source': 'BOU Observatory (INTERMAGNET)',
        'notes': 'Mean of Aug 14-15 at 16:00 UTC'
    },
    {
        'dataset': 'bou_magnetic_2017',
        'year': 2017,
        'parameter': 'z_component_eclipse_16UTC',
        'value': 47718.5,
        'unit': 'nT',
        'source': 'BOU Observatory (INTERMAGNET)',
        'notes': 'Eclipse day (Aug 21) at 16:00 UTC'
    },
    {
        'dataset': 'bou_magnetic_2017',
        'year': 2017,
        'parameter': 'z_component_quiet_mean_18UTC',
        'value': 47724.7,
        'unit': 'nT',
        'source': 'BOU Observatory (INTERMAGNET)',
        'notes': 'Mean of Aug 14-15 at 18:00 UTC'
    },
    {
        'dataset': 'bou_magnetic_2017',
        'year': 2017,
        'parameter': 'z_component_eclipse_18UTC',
        'value': 47715.0,
        'unit': 'nT',
        'source': 'BOU Observatory (INTERMAGNET)',
        'notes': 'Eclipse day (Aug 21) at 18:00 UTC'
    },
    {
        'dataset': 'bou_magnetic_2017',
        'year': 2017,
        'parameter': 'z_component_residual_mean',
        'value': -9.51,
        'unit': 'nT',
        'source': 'BOU Observatory (INTERMAGNET)',
        'notes': 'Mean residual in eclipse window 16-19 UTC'
    },
    {
        'dataset': 'bou_magnetic_2017',
        'year': 2017,
        'parameter': 'z_component_residual_max',
        'value': -10.9,
        'unit': 'nT',
        'source': 'BOU Observatory (INTERMAGNET)',
        'notes': 'Maximum residual at 17.2 UTC'
    },
    {
        'dataset': 'bou_magnetic_2017',
        'year': 2017,
        'parameter': 'z_component_total_drop',
        'value': 12.0,
        'unit': 'nT',
        'source': 'BOU Observatory (INTERMAGNET)',
        'notes': 'Drop from 12:00 baseline to 18:00 trough'
    },
    {
        'dataset': 'eclipse_magnetic_gravity_coupling',
        'year': 2017,
        'parameter': 'magnetic_gravity_ratio',
        'value': 1.67,
        'unit': 'nT/µGal',
        'source': 'BOU 2017 + Mohe 1997',
        'notes': 'Ratio of magnetic anomaly to Mohe gravity anomaly'
    }
]

# Append to master
new_df = pd.DataFrame(new_records)
master_df = pd.concat([master_df, new_df], ignore_index=True)

# Save as v47
master_df.to_csv('dome_v47_master_data.csv', index=False)
print(f"Added {len(new_records)} records. Master CSV (V47) now has {len(master_df)} rows.")
