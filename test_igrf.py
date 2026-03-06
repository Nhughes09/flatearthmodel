import numpy as np
import pandas as pd
import ppigrf
import time

print("Testing single year evaluation speed...")
start = time.time()

year = 2025
lats = np.arange(-50, 0, 5)    # reduced resolution
lons = np.arange(0, 360, 5)    # reduced resolution
lon_grid, lat_grid = np.meshgrid(lons, lats)

lon_flat = lon_grid.flatten()
lat_flat = lat_grid.flatten()
h_flat = np.zeros_like(lon_flat)

dates = pd.to_datetime([f'{year}-01-01'] * len(lon_flat))

# Vectorized call
Be, Bn, Bu = ppigrf.igrf(lon_flat, lat_flat, h_flat, dates)

print(f"Computed {len(lon_flat)} points in {time.time() - start:.2f} seconds")
