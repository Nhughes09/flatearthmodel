#!/usr/bin/env python3
"""
Dome Cosmology V48 - Annual Aberration Model
Purpose: Derive aether refractive gradient from 20.5" aberration
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import json
from datetime import datetime
import os

# Constants
c = 299792458  # m/s
arcsec_to_rad = np.pi / (180 * 3600)
aberration_arcsec = 20.5
aberration_rad = aberration_arcsec * arcsec_to_rad

# Dome geometry
H_firm = 9086e3  # m (firmament height)
R_disc = 20015e3  # m (disc radius)

# Model: refractive index gradient with solar zenith angle
# n(θ) = n0 + α * (θ/π) where θ = solar zenith angle (changes annually)
# Aberration angle δ = (1/n) * dn/dθ * L / c
# L = path length through aether ~ H_firm

def solve_for_alpha(alpha):
    """Compute aberration given alpha and compare to target"""
    n0 = 1.0  # baseline refractive index
    # dn/dθ = α/π (since θ ranges 0 to π)
    dn_dtheta = alpha / np.pi
    
    # Average path length (zenith to horizon)
    L_avg = H_firm  # approximate
    
    # Aberration angle
    delta = (1/n0) * dn_dtheta * L_avg / c
    return delta - aberration_rad

# Solve for alpha
alpha_guess = 1e-12  # initial guess
alpha_solution = fsolve(solve_for_alpha, alpha_guess)[0]

# Compute resulting dn/dθ
dn_dtheta = alpha_solution / np.pi

# Compute physical plausibility
# α represents change in refractive index over full annual cycle
# Should be small (<< 1)
plausible = abs(alpha_solution) < 0.1

results = {
    'parameter': 'aether_refractive_gradient',
    'target_aberration_arcsec': aberration_arcsec,
    'target_aberration_rad': aberration_rad,
    'derived_alpha': float(alpha_solution),
    'derived_dn_dtheta': float(dn_dtheta),
    'physical_plausibility': bool(plausible),
    'notes': 'α is change in refractive index over full annual cycle',
    'threshold': 'α < 0.1 considered physically plausible',
    'timestamp': datetime.now().isoformat()
}

# Save results
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'V48_Validation_Suite/results/annual_aberration_results_{timestamp}.json'
with open(filename, 'w') as f:
    json.dump(results, f, indent=2)

# Generate plot
theta = np.linspace(0, np.pi, 100)
n = 1.0 + alpha_solution * theta / np.pi
delta = (1/1.0) * (alpha_solution/np.pi) * H_firm / c * np.ones_like(theta)
delta_arcsec = delta / arcsec_to_rad

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(theta * 180/np.pi, n)
ax1.set_xlabel('Solar Zenith Angle (degrees)')
ax1.set_ylabel('Refractive Index n')
ax1.set_title('Aether Refractive Index vs Solar Angle')
ax1.grid(True)

ax2.plot(theta * 180/np.pi, delta_arcsec)
ax2.axhline(aberration_arcsec, color='r', linestyle='--', label=f'Target: {aberration_arcsec}"')
ax2.set_xlabel('Solar Zenith Angle (degrees)')
ax2.set_ylabel('Aberration (arcsec)')
ax2.set_title('Predicted Annual Aberration')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plot_file = f'V48_Validation_Suite/plots/annual_aberration_{timestamp}.png'
plt.savefig(plot_file, dpi=150)

print(f"Results saved to {filename}")
print(f"Plot saved to {plot_file}")
print(f"Derived α = {alpha_solution:.2e}")
print(f"Plausible: {plausible}")

# Git commit
os.system(f"git add {filename} {plot_file}")
os.system(f'git commit -m "Add annual aberration model - {timestamp}"')
