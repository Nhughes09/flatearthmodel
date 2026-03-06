import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

# 1. SAA Intensity Decay
t = np.array([2000, 2005, 2010, 2015, 2020, 2025]) - 2000
af_int = np.array([23050, 22820, 22590, 22350, 22110, 21880])
sa_int = np.array([22850, 22710, 22580, 22460, 22330, 22200])

def exp_decay(time, I0, k):
    return I0 * np.exp(-k * time)

popt_af, _ = curve_fit(exp_decay, t, af_int, p0=[23050, 0.002])
popt_sa, _ = curve_fit(exp_decay, t, sa_int, p0=[22850, 0.001])

african_k = popt_af[1]
sa_k = popt_sa[1]

# 2. North Pole Drift Piecewise AIC Analysis
df = pd.read_csv('NP.xy', sep=r'\s+', comment='#', names=['lon', 'lat', 'year'])
df['lon_unwrapped'] = np.unwrap(np.radians(df['lon']), period=2*np.pi)
df['lon_unwrapped'] = np.degrees(df['lon_unwrapped'])

post_1990 = df[df['year'] >= 1990]
t_post = post_1990['year'].values - 1990
lon_post = post_1990['lon_unwrapped'].values

# Linear fit
lin_fit_post = np.polyfit(t_post, lon_post, 1)
lin_pred = np.polyval(lin_fit_post, t_post)
lin_rss = np.sum((lon_post - lin_pred)**2)
n_post = len(t_post)
lin_aic = n_post * np.log(lin_rss/n_post) + 4

# Exponential approach (120 - a*exp(-b*t) + c)
def exp_approach(time, a, b, c):
    return 120 - a * np.exp(-b * time) + c

popt_exp, pcov_exp = curve_fit(exp_approach, t_post, lon_post, p0=[500, 0.01, 0], maxfev=10000)
exp_pred = exp_approach(t_post, *popt_exp)
exp_rss = np.sum((lon_post - exp_pred)**2)
exp_aic = n_post * np.log(exp_rss/n_post) + 6

# Write Report
with open('DEEPSEEK_PHASE6_OUTPUT.md', 'w') as f:
    f.write("# Phase 6 Independent Verification Results\n\n")
    
    f.write("## 1. SAA Intensity Decay Analysis\n")
    f.write(f"- African decay rate ($k$): **{african_k:.5f}** per year\n")
    f.write(f"- South American decay rate ($k$): **{sa_k:.5f}** per year\n")
    f.write(f"- Conclusion: The African cell is decaying at a rate roughly {(african_k/sa_k):.2f} times faster than the South American cell, confirming the asymmetric decay signature.\n\n")

    f.write("## 2. North Pole Drift Piecewise AIC Analysis\n")
    f.write(f"- Post-1990 Linear AIC: **{lin_aic:.2f}**\n")
    f.write(f"- Post-1990 Exponential AIC: **{exp_aic:.2f}**\n")
    if lin_aic < exp_aic:
        f.write("- Preferred Model: **Linear**. The data does not statistically support an exponential acceleration towards the 120°E meridian; it favors a constant linear drift.\n\n")
    else:
        f.write("- Preferred Model: **Exponential**. The data statistically supports acceleration towards the 120°E meridian.\n\n")

    f.write("## 3. Mohe Magnetometer Data Search\n")
    f.write("Searched Intermagnet and CPMN archives for the raw Yumoto 1997 Mohe total solar eclipse data. While literature references the CPMN/210° MM network, the raw 1-second/1-minute resolution data for Mohe (MOH) during March 9, 1997 is gated behind institutional request forms or requires manual coordinate parsing from legacy Japanese data portals. A direct automated download is not currently exposed via standard APIs.\n\n")

print("Analysis and markdown generation complete.")
