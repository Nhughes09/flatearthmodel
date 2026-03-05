#!/usr/bin/env python3
"""
Astronomical observations calculator for 30+ cities worldwide.
Calculates Polaris, Sun, Jupiter, and Moon positions using astropy.
Exports results to observations.csv.
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from datetime import datetime, timezone

from astropy.coordinates import (
    EarthLocation, AltAz, SkyCoord,
    get_sun, get_body, solar_system_ephemeris
)
from astropy.time import Time, TimeDelta
import astropy.units as u


# ---------------------------------------------------------------------------
# 1. Define cities  (30 cities + Chapel Hill NC = 31 total)
# ---------------------------------------------------------------------------
CITIES = [
    # --- Northern Hemisphere ---
    ("Reykjavik, Iceland",        64.1466, -21.9426),
    ("London, UK",                51.5074,  -0.1278),
    ("New York City, USA",        40.7128, -74.0060),
    ("Chicago, USA",              41.8781, -87.6298),
    ("Los Angeles, USA",          34.0522, -118.2437),
    ("Tokyo, Japan",              35.6762, 139.6503),
    ("Dubai, UAE",                25.2048,  55.2708),
    ("Singapore",                  1.3521, 103.8198),
    ("Paris, France",             48.8566,   2.3522),
    ("Berlin, Germany",           52.5200,  13.4050),
    ("Moscow, Russia",            55.7558,  37.6173),
    ("Beijing, China",            39.9042, 116.4074),
    ("Mumbai, India",             19.0760,  72.8777),
    ("Cairo, Egypt",              30.0444,  31.2357),
    ("Toronto, Canada",           43.6532, -79.3832),
    ("Mexico City, Mexico",       19.4326, -99.1332),
    ("Stockholm, Sweden",         59.3293,  18.0686),
    ("Helsinki, Finland",         60.1699,  24.9384),
    # --- Equatorial ---
    ("Accra, Ghana",               5.6037,  -0.1870),
    ("Nairobi, Kenya",            -1.2921,  36.8219),
    ("Quito, Ecuador",            -0.1807, -78.4678),
    # --- Southern Hemisphere ---
    ("Sydney, Australia",        -33.8688, 151.2093),
    ("Perth, Australia",         -31.9505, 115.8605),
    ("Cape Town, South Africa",  -33.9249,  18.4241),
    ("Johannesburg, South Africa",-26.2041, 28.0473),
    ("Santiago, Chile",          -33.4489, -70.6693),
    ("Buenos Aires, Argentina",  -34.6037, -58.3816),
    ("Auckland, New Zealand",    -36.8485, 174.7633),
    ("Lima, Peru",               -12.0464, -77.0428),
    ("São Paulo, Brazil",        -23.5505, -46.6333),
    # --- Special request ---
    ("Chapel Hill, NC, USA",      35.9132, -79.0560),
]


def _find_transit(sun_coord_func, location, date_utc, n_steps=200):
    """Find solar noon (transit) by sampling the sun altitude over the day."""
    t0 = Time(f"{date_utc}T00:00:00", scale="utc")
    times = t0 + TimeDelta(np.linspace(0, 24, n_steps) * 3600, format="sec")
    frame = AltAz(obstime=times, location=location)
    sun_altaz = sun_coord_func(times).transform_to(frame)
    idx = np.argmax(sun_altaz.alt.deg)
    return times[idx]


def _find_horizon_crossing(sun_coord_func, location, date_utc, event="rise",
                           n_coarse=300, n_fine=200):
    """
    Find sunrise or sunset time by coarse-then-fine search for altitude ~ 0.
    Returns None if the sun never crosses the horizon in the requested direction.
    """
    t0 = Time(f"{date_utc}T00:00:00", scale="utc")
    times = t0 + TimeDelta(np.linspace(0, 24, n_coarse) * 3600, format="sec")
    frame = AltAz(obstime=times, location=location)
    alts = sun_coord_func(times).transform_to(frame).alt.deg

    # Look for sign changes
    crossings = np.where(np.diff(np.sign(alts)))[0]
    if len(crossings) == 0:
        return None

    if event == "rise":
        # First positive-going crossing
        for c in crossings:
            if alts[c] < 0 and alts[c + 1] >= 0:
                t_lo, t_hi = times[c], times[c + 1]
                break
        else:
            return None
    else:
        # Last negative-going crossing
        for c in reversed(crossings):
            if alts[c] >= 0 and alts[c + 1] < 0:
                t_lo, t_hi = times[c], times[c + 1]
                break
        else:
            return None

    # Refine with bisection
    for _ in range(n_fine):
        t_mid = t_lo + (t_hi - t_lo) * 0.5
        alt_mid = sun_coord_func(t_mid).transform_to(
            AltAz(obstime=t_mid, location=location)
        ).alt.deg
        if (event == "rise" and alt_mid < 0) or (event == "set" and alt_mid >= 0):
            t_lo = t_mid
        else:
            t_hi = t_mid
    return t_lo + (t_hi - t_lo) * 0.5


def compute_observations(cities, date_str):
    """Compute all requested astronomical quantities for each city."""

    # Use the built-in ephemeris (no extra download needed)
    solar_system_ephemeris.set("builtin")

    # Polaris coordinates (J2000)
    polaris = SkyCoord(ra="02h31m49.09s", dec="+89d15m50.8s", frame="icrs")

    rows = []
    for city_name, lat, lon in cities:
        loc = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=0 * u.m)

        # --- Solar noon (transit) ---
        t_noon = _find_transit(get_sun, loc, date_str)

        # --- AltAz frame at solar noon ---
        frame_noon = AltAz(obstime=t_noon, location=loc)

        # Sun at solar noon
        sun_noon = get_sun(t_noon).transform_to(frame_noon)

        # Polaris at solar noon
        polaris_noon = polaris.transform_to(frame_noon)

        # Jupiter at solar noon
        jupiter_noon = get_body("jupiter", t_noon).transform_to(frame_noon)

        # Moon at solar noon
        moon_noon = get_body("moon", t_noon).transform_to(frame_noon)

        # --- Moon phase (illumination fraction) ---
        sun_ec = get_sun(t_noon)
        moon_ec = get_body("moon", t_noon)
        elongation = sun_ec.separation(moon_ec)
        moon_phase_frac = (1 - np.cos(elongation.rad)) / 2.0

        # --- Sunrise / Sunset ---
        t_rise = _find_horizon_crossing(get_sun, loc, date_str, event="rise")
        t_set  = _find_horizon_crossing(get_sun, loc, date_str, event="set")

        if t_rise is not None:
            frame_rise = AltAz(obstime=t_rise, location=loc)
            sun_rise = get_sun(t_rise).transform_to(frame_rise)
            sunrise_alt = round(sun_rise.alt.deg, 4)
            sunrise_az  = round(sun_rise.az.deg, 4)
        else:
            sunrise_alt = None
            sunrise_az  = None

        if t_set is not None:
            frame_set = AltAz(obstime=t_set, location=loc)
            sun_set = get_sun(t_set).transform_to(frame_set)
            sunset_alt = round(sun_set.alt.deg, 4)
            sunset_az  = round(sun_set.az.deg, 4)
        else:
            sunset_alt = None
            sunset_az  = None

        # --- Day length ---
        if t_rise is not None and t_set is not None:
            day_length_hrs = round((t_set - t_rise).sec / 3600.0, 4)
        else:
            day_length_hrs = None  # polar day or polar night

        row = {
            "city":                city_name,
            "latitude":            lat,
            "longitude":           lon,
            "date":                date_str,
            "solar_noon_utc":      t_noon.iso,
            "polaris_elevation":   round(polaris_noon.alt.deg, 4),
            "polaris_azimuth":     round(polaris_noon.az.deg, 4),
            "sun_noon_elevation":  round(sun_noon.alt.deg, 4),
            "sun_noon_azimuth":    round(sun_noon.az.deg, 4),
            "sunrise_elevation":   sunrise_alt,
            "sunrise_azimuth":     sunrise_az,
            "sunset_elevation":    sunset_alt,
            "sunset_azimuth":      sunset_az,
            "day_length_hours":    day_length_hrs,
            "jupiter_elevation":   round(jupiter_noon.alt.deg, 4),
            "jupiter_azimuth":     round(jupiter_noon.az.deg, 4),
            "moon_elevation":      round(moon_noon.alt.deg, 4),
            "moon_azimuth":        round(moon_noon.az.deg, 4),
            "moon_phase_fraction": round(moon_phase_frac, 4),
        }
        rows.append(row)
        print(f"  ✓ {city_name}")

    return pd.DataFrame(rows)


def main():
    # Today's date: 2026-03-04
    date_str = "2026-03-04"

    print(f"Calculating astronomical observations for {len(CITIES)} cities on {date_str}...\n")
    df = compute_observations(CITIES, date_str)

    output_file = "observations.csv"
    df.to_csv(output_file, index=False)
    print(f"\nExported {len(df)} rows to {output_file}")
    print("DONE")


if __name__ == "__main__":
    main()
