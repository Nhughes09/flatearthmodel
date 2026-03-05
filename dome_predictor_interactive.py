#!/usr/bin/env python3
"""
DOME SKY PREDICTOR — Interactive Version
Enter a latitude and date to see full sky predictions with ASCII map.
"""
import math
from datetime import date

ALT_MIN = -0.833
PH = 6500.0

def sun_dec(d):
    days = (d - date(2026,1,1)).days
    return 23.44 * math.sin(2*math.pi*(days-79)/365.25)

def jup_dec(d):
    days = (d - date(2026,1,1)).days
    return 23.175 - 0.018 * days

def moon_dec(d):
    days = (d - date(2026,1,1)).days
    return 28.6 * math.sin(2*math.pi*days/27.3 + 1.2)

def mars_dec(d):
    days = (d - date(2026,1,1)).days
    return -14.5 + 0.02 * days

def venus_dec(d):
    days = (d - date(2026,1,1)).days
    return -20.0 + 0.1 * days

def transit_elev(lat, dec): return min(90, 90 - abs(lat - dec))
def transit_az(lat, dec):
    d = lat - dec
    if abs(d) < 0.5: return "ZENITH"
    return "S (180°)" if d > 0 else "N (0°)"
def day_len(lat, dec):
    lr,dr,ar = math.radians(lat), math.radians(dec), math.radians(ALT_MIN)
    c = (math.sin(ar)-math.sin(lr)*math.sin(dr))/(math.cos(lr)*math.cos(dr))
    c = max(-1,min(1,c))
    h = 2*math.degrees(math.acos(c))/15
    if h >= 24: return "24:00 (Polar Day)"
    if h <= 0: return "0:00 (Polar Night)"
    hrs = int(h); mins = int((h-hrs)*60)
    return f"{hrs}:{mins:02d}"
def rise_az(lat, dec):
    c = math.sin(math.radians(dec))/math.cos(math.radians(lat))
    return math.degrees(math.acos(max(-1,min(1,c))))
def is_cp(lat, dec): return abs(dec) > (90 - abs(lat))

def ascii_sky_map(lat, d, bodies):
    """Generate ASCII cross-section sky map (N-S meridian)"""
    lines = []
    lines.append("")
    lines.append(f"  DOME SKY MAP — Lat {lat:.1f}° — {d}")
    lines.append(f"  {'='*52}")
    
    # Map: vertical = elevation (0-90), horizontal = N-S direction
    HEIGHT = 12
    WIDTH = 50
    grid = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT+1)]
    
    # Place bodies
    for name, elev, direction in bodies:
        if elev <= 0: continue
        row = HEIGHT - int(elev / 90 * HEIGHT)
        row = max(0, min(HEIGHT, row))
        if direction == "S" or direction == "S (180°)":
            col = WIDTH//4
        elif direction == "N" or direction == "N (0°)":
            col = 3*WIDTH//4
        else:  # zenith
            col = WIDTH//2
        
        # Place label
        label = f"{name[:3]}({elev:.0f}°)"
        for j, ch in enumerate(label):
            if col+j < WIDTH:
                grid[row][col+j] = ch
    
    # Draw
    lines.append(f"  90°{'─'*22}┬{'─'*22} Zenith")
    for r in range(1, HEIGHT):
        elev = 90 - r * (90/HEIGHT)
        row_str = ''.join(grid[r])
        if r == HEIGHT//2:
            lines.append(f"  {elev:3.0f}°  {row_str}")
        else:
            lines.append(f"       {row_str}")
    lines.append(f"   0°{'━'*22}┿{'━'*22} Horizon")
    lines.append(f"       {'SOUTH':^22} │ {'NORTH':^22}")
    lines.append(f"       {'(180°)':^22} │ {'(0°)':^22}")
    
    return '\n'.join(lines)

def predict(lat, d=None):
    if d is None: d = date.today()
    
    sd = sun_dec(d); jd = jup_dec(d); md = moon_dec(d)
    mrd = mars_dec(d); vd = venus_dec(d)
    
    print(f"\n{'='*56}")
    print(f"  FIRMAMENT DOME PREDICTIONS")
    print(f"  Location: {lat:.2f}° {'N' if lat>=0 else 'S'}")
    print(f"  Date: {d}")
    print(f"{'='*56}")
    
    print(f"\n  POLARIS:")
    pe = abs(lat)
    vis = "Visible" if lat > 0 else "Below horizon"
    print(f"    Elevation: {pe:.1f}° ({vis})")
    
    print(f"\n  SUN (dec={sd:.1f}°):")
    se = transit_elev(lat, sd)
    print(f"    Transit elevation: {se:.1f}°")
    print(f"    Transit azimuth:   {transit_az(lat, sd)}")
    print(f"    Day length:        {day_len(lat, sd)}")
    ra = rise_az(lat, sd)
    print(f"    Sunrise azimuth:   {ra:.1f}°")
    print(f"    Sunset azimuth:    {360-ra:.1f}°")
    
    bodies_for_map = [("Sun", se, transit_az(lat, sd))]
    
    for name, dec_val in [("Jupiter", jd), ("Moon", md), ("Mars", mrd), ("Venus", vd)]:
        e = transit_elev(lat, dec_val)
        a = transit_az(lat, dec_val)
        cp = "circumpolar" if is_cp(lat, dec_val) else ""
        print(f"\n  {name.upper()} (dec={dec_val:.1f}°):")
        print(f"    Transit elevation: {e:.1f}°")
        print(f"    Transit azimuth:   {a} {cp}")
        if e > 0:
            bodies_for_map.append((name, e, a))
    
    # Polaris
    if lat > 0:
        bodies_for_map.append(("Pol", pe, "N (0°)"))
    
    print(ascii_sky_map(lat, d, bodies_for_map))

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        lat = float(sys.argv[1])
        d = date.fromisoformat(sys.argv[2]) if len(sys.argv) >= 3 else date.today()
    else:
        lat = 35.91  # Chapel Hill default
        d = date(2026, 3, 4)
    predict(lat, d)
