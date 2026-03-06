#!/usr/bin/env python3
"""
Dome Cosmology V48 - Parallax as Firmament Wobble Model
Purpose: Show that dome wobble produces apparent parallax matching observations
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import json
from datetime import datetime
import os

# Constants
arcsec_to_rad = np.pi / (180 * 3600)
H_firm = 9086e3  # m (firmament height)
R_disc = 20015e3  # m

# Observed parallax range for nearby stars
# Proxima Centauri: 0.7685 arcsec
# Typical range: 0.1 - 1.0 arcsec
target_parallax = 0.5  # arcsec (typical)

# Model: Firmament rotates about an axis slightly offset from center
# Offset distance d causes stars to trace small ellipses
# Apparent parallax ~ d / H_firm (in radians)

def wobble_parallax(d):
    """Compute apparent parallax for given offset d"""
    return (d / H_firm) / arcsec_to_rad

# Solve for d needed to produce target parallax
d_solution = target_parallax * arcsec_to_rad * H_firm

# Compute parallax as function of stellar "distance" on firmament
# In dome model, all stars at same distance, but wobble amplitude varies with
# position on dome due to projection
def parallax_by_position(lat, d):
    """Apparent parallax as function of observer latitude and offset d"""
    # Simple model: parallax ∝ sin(lat) * d / H_firm
    lat_rad = np.radians(lat)
    return (d / H_firm) * np.abs(np.sin(lat_rad)) / arcsec_to_rad

# Generate latitude dependence
lats = np.linspace(-90, 90, 100)
parallax_lat = parallax_by_position(lats, d_solution)

results = {
    'parameter': 'firmament_wobble_offset',
    'target_parallax_arcsec': target_parallax,
    'derived_offset_m': float(d_solution),
    'derived_offset_km': float(d_solution/1000),
    'derived_offset_as_fraction_of_R': float(d_solution/R_disc),
    'firmament_height_km': H_firm/1000,
    'predicted_parallax_range_arcsec': [float(np.min(parallax_lat)), float(np.max(parallax_lat))],
    'notes': 'Offset is physical displacement of firmament rotation axis from geometric center',
    'plausibility': 'Offset < 1% of disc radius is physically plausible',
    'timestamp': datetime.now().isoformat()
}

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Parallax vs latitude
ax1.plot(lats, parallax_lat)
ax1.set_xlabel('Observer Latitude (degrees)')
ax1.set_ylabel('Apparent Parallax (arcsec)')
ax1.set_title('Parallax vs Latitude (Firmament Wobble Model)')
ax1.grid(True)

# Wobble geometry schematic
circle = plt.Circle((0,0), 1, fill=False)
ax2.add_patch(circle)
ax2.plot([0, 0.05], [0, 0], 'r-', linewidth=2, label='Offset axis')
ax2.plot(0.05, 0, 'ro', markersize=8)
ax2.set_xlim(-1.2, 1.2)
ax2.set_ylim(-1.2, 1.2)
ax2.set_aspect('equal')
ax2.set_title('Firmament Wobble Geometry\n(Offset exaggerated)')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
plot_file = f'V48_Validation_Suite/plots/parallax_wobble_{timestamp}.png'
plt.savefig(plot_file, dpi=150)

# Save results
filename = f'V48_Validation_Suite/results/parallax_results_{timestamp}.json'
with open(filename, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to {filename}")
print(f"Plot saved to {plot_file}")
print(f"Required offset: {d_solution/1000:.2f} km")
print(f"As fraction of disc radius: {d_solution/R_disc:.4f}")

# Git commit
os.system(f"git add {filename} {plot_file}")
os.system(f'git commit -m "Add parallax wobble model - {timestamp}"')
