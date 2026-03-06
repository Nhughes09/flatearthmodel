#!/usr/bin/env python3
"""
Dome Cosmology V48 - Master Predictions Document
Purpose: Compile all falsifiable predictions with timestamps
"""

import json
import os
from datetime import datetime
import glob

# Collect all prediction files
prediction_files = glob.glob('V48_Validation_Suite/predictions/*.json')
prediction_files.extend(glob.glob('V48_Validation_Suite/results/*.json'))

master = {
    'title': 'Dome Cosmology V48 - Master Predictions',
    'created': datetime.now().isoformat(),
    'version': 'V48',
    'predictions': []
}

for f in prediction_files:
    try:
        with open(f, 'r') as infile:
            data = json.load(infile)
            master['predictions'].append({
                'source_file': f,
                'data': data
            })
    except:
        pass

# Save master
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
master_file = f'V48_Validation_Suite/predictions/master_predictions_{timestamp}.json'
with open(master_file, 'w') as f:
    json.dump(master, f, indent=2)

# Create markdown version
md_file = f'V48_Validation_Suite/predictions/master_predictions_{timestamp}.md'
with open(md_file, 'w') as f:
    f.write(f"# Dome Cosmology V48 - Master Predictions\n\n")
    f.write(f"**Created:** {datetime.now().isoformat()}\n\n")
    f.write(f"**Version:** V48\n\n")
    f.write(f"## Summary\n\n")
    f.write(f"This document contains all falsifiable predictions from the Dome Cosmology model.\n")
    f.write(f"Each prediction is timestamped to establish priority of discovery.\n\n")
    
    for pred in master['predictions']:
        f.write(f"### Source: {pred['source_file']}\n")
        f.write(f"```json\n{json.dumps(pred['data'], indent=2)}\n```\n\n")

# Git commit
os.system(f"git add {master_file} {md_file}")
os.system(f'git commit -m "Add master predictions document - {timestamp}"')

print(f"Master predictions saved to {master_file}")
print(f"Markdown version saved to {md_file}")
