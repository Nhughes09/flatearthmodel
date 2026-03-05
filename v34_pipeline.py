#!/usr/bin/env python3
"""
V34: LUNAR SPECTRAL FINGERPRINT
Task 1: Moon vs Sun emission spectra — anomalous lines?
Task 2: Lunar polarization curve — reflector or emitter?
Task 3: Opposition surge — geometric or energetic?
"""
import warnings; warnings.filterwarnings("ignore")
import math, numpy as np, pandas as pd

out=[]; master=[]
def log(s=""): print(s); out.append(s)
def mr(s,ss,p,v,u,src,n):
    master.append({'SECTION':s,'SUBSECTION':ss,'PARAMETER':p,
                   'VALUE':str(v),'UNIT':u,'SOURCE':src,'NOTES':n})

# ============================================================
# TASK 1: LUNAR SPECTROSCOPY — EMISSION vs REFLECTION
# ============================================================
log("="*70)
log("TASK 1: LUNAR SPECTROSCOPY — DOES MOONLIGHT = SUNLIGHT?")
log("="*70)

log(f"""
  QUESTION: Does moonlight contain any emission lines that are
  ABSENT in sunlight? If so, the Moon is an independent source.
  If not, it is a reflector.

  WHAT THE DATA SHOWS:
  ═══════════════════
""")

spectral_data = [
    ("Fraunhofer H (Ca II)", 396.8, "present in Sun", "present in Moon",
     "IDENTICAL", "absorption line — Moon reproduces Sun's spectrum"),
    ("Fraunhofer K (Ca II)", 393.4, "present in Sun", "present in Moon",
     "IDENTICAL", "same depth ratio as sunlight"),
    ("Fraunhofer G (Fe I + Ca I)", 430.8, "present in Sun", "present in Moon",
     "IDENTICAL", "iron/calcium absorption"),
    ("Fraunhofer D (Na I)", 589.0, "present in Sun", "present in Moon",
     "IDENTICAL", "sodium doublet — same ratio"),
    ("Fraunhofer C (Hα)", 656.3, "present in Sun", "present in Moon",
     "IDENTICAL", "hydrogen – same equivalent width"),
    ("Fraunhofer F (Hβ)", 486.1, "present in Sun", "present in Moon",
     "IDENTICAL", "hydrogen – same equivalent width"),
    ("Fraunhofer b (Mg I)", 518.4, "present in Sun", "present in Moon",
     "IDENTICAL", "magnesium triplet"),
    ("O₂ A-band", 760.0, "ABSENT in Sun (above atm)", "present in Moon",
     "EARTH ATMOSPHERE", "telluric absorption — proves moonlight traverses same atmosphere"),
    ("H₂O bands", 940.0, "ABSENT in Sun (above atm)", "present in Moon",
     "EARTH ATMOSPHERE", "water vapor — same path through atmosphere"),
    ("Lunar emission lines", "N/A", "NONE found", "NONE found",
     "NOT DETECTED", "no emission lines unique to Moon in any published study"),
]

log(f"  {'Feature':<28} {'λ (nm)':>8} {'Sun':>16} {'Moon':>16} {'Match'}")
log(f"  {'-'*85}")
for feat, wl, sun, moon, match, notes in spectral_data:
    log(f"  {feat:<28} {str(wl):>8} {sun:>16} {moon:>16} {match}")
    mr("SPECTRAL",feat,f"lambda={wl}nm",f"Sun:{sun[:20]}|Moon:{moon[:20]}",
       "nm",match,notes)

log(f"""
  KEY RESULTS:
  
  1. ALL solar Fraunhofer lines appear in moonlight at the SAME 
     wavelengths and SAME relative depths. This is the fingerprint
     of reflected sunlight.
     
  2. Moonlight contains ADDITIONAL absorption features (O₂, H₂O)
     that are TERRESTRIAL — they come from Earth's atmosphere as
     moonlight passes through it. These are ABSENT in sunlight
     measured above the atmosphere (by satellites).
     → This proves moonlight takes the same atmospheric path as
       any other external light source.
     
  3. NO emission lines unique to the Moon have been found in any
     published spectroscopic study. An independent luminary MUST
     have emission lines from whatever process generates its light
     (thermal emission → blackbody + element lines, plasma → strong
     emission lines, phosphorescence → characteristic bands).
     
  ⚡ DOME: If Moon is a local emitter, it would need to
  coincidentally reproduce the Sun's EXACT absorption line spectrum
  (hundreds of lines matching to <0.01 nm) while adding none of its own.
  This requires the Moon to be made of the SAME elements as the Sun
  AND have the same temperature/pressure profile. Extremely unlikely.
  
  🌍 GLOBE: Moonlight = sunlight reflected off silicate regolith.
  The spectrum matches because it IS the same light, modified only
  by the Moon's surface albedo curve (slight reddening ~5%).
  
  ⚠️ VERDICT: GLOBE. The spectral evidence is overwhelming.
  The Moon's spectrum IS the Sun's spectrum with:
    a) slight reddening from surface albedo
    b) telluric absorption from Earth's atmosphere
    c) ZERO unique emission lines
  A self-luminous body cannot produce this spectrum.
""")

mr("SPECTRAL","VERDICT","emission_lines_found","ZERO",
   "count","literature search","no unique lunar emissions in any study")
mr("SPECTRAL","VERDICT","fraunhofer_match","ALL lines identical",
   "100%","spectroscopy","same wavelengths same depths")
mr("SPECTRAL","VERDICT","mechanism","reflected sunlight",
   "conclusion","overwhelming evidence","GLOBE wins this test")

# ============================================================
# TASK 2: LUNAR POLARIZATION
# ============================================================
log("\n" + "="*70)
log("TASK 2: LUNAR POLARIZATION — REFLECTOR SIGNATURE")
log("="*70)

log(f"""
  QUESTION: Does the Moon's polarization curve match a silicate
  reflector, or something else (plasma, crystal, emitter)?
  
  WHAT POLARIZATION TELLS US:
  - Reflected light is partially polarized
  - The polarization % depends on the surface material
  - Each material has a characteristic polarization-vs-phase curve
  - An independent emitter (plasma, lamp) has DIFFERENT polarization
""")

polarization_data = [
    ("New Moon (0°)", 0, "N/A", "not visible"),
    ("Waxing crescent (45°)", 45, "~2-5%", "low, increasing"),
    ("First quarter (90°)", 90, "~8-12%", "MAXIMUM — characteristic of fine silicate dust"),
    ("Waxing gibbous (135°)", 135, "~3-6%", "declining"),
    ("Full Moon (180°)", 180, "<1%", "near zero — backscatter depolarization"),
    ("Negative polarization (5-20°)", 10, "-0.5 to -2%", "NEGATIVE branch — diagnostic of regolith"),
]

log(f"  {'Phase':<28} {'Angle':>6} {'Polarization':>14} {'Notes'}")
log(f"  {'-'*65}")
for phase, angle, pol, notes in polarization_data:
    log(f"  {phase:<28} {angle:>6}° {pol:>14} {notes}")
    mr("POLARIZATION",phase,f"angle={angle}deg",pol,"percent","lunar observations",notes)

log(f"""
  KEY DIAGNOSTIC: NEGATIVE POLARIZATION BRANCH
  
  At very small phase angles (5-20°), moonlight shows NEGATIVE 
  polarization — meaning the polarization direction is rotated
  90° from what simple Fresnel reflection predicts.
  
  This negative branch is DIAGNOSTIC of:
  ✅ Fine particulate material (regolith, dust)
  ✅ Multiple scattering in a rough surface
  ❌ NOT produced by plasma emission
  ❌ NOT produced by thermal blackbody emission
  ❌ NOT produced by phosphorescence
  
  The Moon's polarization curve matches:
  ✅ Laboratory measurements of silicate powders
  ✅ Other asteroids and rocky surfaces
  ✅ Returned lunar soil samples (Apollo — controversial source for FDM)
  
  It does NOT match:
  ❌ Gas discharge (plasma) emission
  ❌ Thermal emission from hot surface
  ❌ Crystal luminescence
  
  ⚡ DOME: Would need the Moon's emission process to coincidentally
  produce the exact same polarization curve as powdered silicate rock
  — including the negative branch, which is a particle-scattering 
  phenomenon that doesn't occur in emission sources.
  
  🌍 GLOBE: Reflected sunlight off silicate regolith. Polarization
  curve matches laboratory powders exactly. Well-understood since
  Lyot 1929, confirmed by every subsequent measurement.
  
  ⚠️ VERDICT: GLOBE. The polarization curve is a material fingerprint.
  The Moon's curve matches "fine silicate dust" and nothing else.
""")

mr("POLARIZATION","NEGATIVE_BRANCH","at 5-20deg","-0.5 to -2%","percent",
   "Lyot 1929 + subsequent","diagnostic of particulate surface — NOT emission")
mr("POLARIZATION","MAX_AT_90","first quarter","8-12%","percent",
   "standard observations","matches powdered silicates exactly")
mr("POLARIZATION","VERDICT","material match","silicate regolith",
   "conclusion","overwhelming","GLOBE — reflector confirmed by polarimetry")

# ============================================================
# TASK 3: OPPOSITION SURGE (SEELIGER EFFECT)
# ============================================================
log("\n" + "="*70)
log("TASK 3: OPPOSITION SURGE — GEOMETRIC OR ENERGETIC?")
log("="*70)

# The Moon's brightness at full phase (opposition) is anomalously high
# A Lambertian reflector at full would be ~3.3x brighter than half
# The Moon is actually ~11x brighter than half (magnitude difference ~2.6)

log(f"""
  THE OBSERVATION:
  ================
  
  Half Moon (quarter phase):     apparent magnitude ~-10.0
  Full Moon (opposition):        apparent magnitude ~-12.7
  
  Magnitude difference: -2.7
  Brightness ratio: 10^(2.7/2.5) = 11.5x
  
  But geometrically, the illuminated area ratio is only:
  Full/Half area ratio = 2.0
  A perfect Lambertian reflector: ~3.3x (accounting for angle)
  
  ACTUAL: ~11.5x = 3.5x brighter than geometry predicts
  
  This extra brightness near opposition is the "OPPOSITION SURGE"
""")

# Opposition surge models
opposition_models = [
    ("Shadow Hiding (SHOE)", "At exact opposition, shadows are hidden behind their casters",
     "geometric (verified in lab)", "Hapke 1986",
     "Reproduces surge shape to first order. Requires porous regolith."),
    ("Coherent Backscatter (CBOE)", "Constructive interference of counter-propagating light paths",
     "wave optics (verified in lab)", "Muinonen 1990",
     "Sharp spike within 2° of opposition. Confirmed in lab with powders."),
    ("SHOE + CBOE combined", "Both effects operate simultaneously at different angular scales",
     "quantitative fit achieved", "Hapke 2002; Shkuratov et al. 2011",
     "Best fit to full-phase curve. Used for ALL rocky bodies."),
    ("Active energy surge (FDM)", "Moon increases output energy at resonance",
     "no mathematical model", "hypothesis only",
     "Would need: trigger mechanism, energy source, frequency dependence."),
]

log(f"  {'Model':<28} {'Mechanism':<35} {'Status'}")
log(f"  {'-'*80}")
for name, mech, status, src, notes in opposition_models:
    log(f"  {name:<28} {mech[:34]:<35} {status[:25]}")
    mr("OPPOSITION",name,mech[:40],status,src,"",notes)

log(f"""
  CRITICAL TEST — DOES THE SURGE FIT REFLECTION OR EMISSION?
  
  1. SHOE (Shadow Hiding):
     ✅ Predicted mathematically before observed on other bodies
     ✅ Reproduced in laboratory with powdered materials
     ✅ Same effect seen on ALL rocky bodies (Mercury, Mars, asteroids)
     ✅ Angular width matches predicted porosity of regolith
     VERDICT: CONFIRMED mechanism
  
  2. CBOE (Coherent Backscatter):
     ✅ Sharp spike within <2° — matches wave optics prediction
     ✅ Reproduced in lab with fine powders
     ✅ Wavelength-dependent as predicted (stronger at shorter λ)
     ✅ Polarization changes as predicted at opposition
     VERDICT: CONFIRMED mechanism
  
  3. Active Energy Surge (FDM hypothesis):
     ❌ No mathematical model predicting the angular shape
     ❌ No explanation for why the surge matches SHOE+CBOE math
     ❌ No explanation for same surge on OTHER bodies (asteroids, Mars)
     ❌ Would need to explain phase-dependent polarization changes
     ❌ Energy source unspecified
     VERDICT: HYPOTHESIS ONLY — no supporting evidence
  
  ⚡ DOME: The surge COULD be energetic, but has no mathematical model.
  It would need to coincidentally match SHOE+CBOE predictions exactly.
  And explain why asteroids (which FDM doesn't claim are luminaries)
  show the SAME opposition surge.
  
  🌍 GLOBE: SHOE + CBOE model fits Moon, Mercury, Mars, and asteroids.
  Confirmed in laboratory with powder samples. Standard physics.
  
  ⚠️ VERDICT: GLOBE. The opposition surge is well-explained by
  two confirmed mechanisms (shadow hiding + coherent backscatter).
  Active emission hypothesis has no model, no lab confirmation,
  and can't explain the same effect on other bodies.
""")

mr("OPPOSITION","BRIGHTNESS","full_vs_half","11.5x (vs geometric 3.3x)",
   "ratio","observations","3.5x excess = SHOE + CBOE")
mr("OPPOSITION","SHOE_LAB","confirmed","reproduced with powders",
   "verified","Hapke 1986","geometric shadow hiding")
mr("OPPOSITION","CBOE_LAB","confirmed","reproduced with fine particles",
   "verified","Muinonen 1990","coherent backscatter")
mr("OPPOSITION","ON_OTHER_BODIES","same surge","Mercury Mars asteroids",
   "universal","all rocky bodies","FDM can't explain these")
mr("OPPOSITION","VERDICT","reflection_mechanisms","SHOE+CBOE fit completely",
   "conclusion","standard physics","GLOBE — active surge has no model")

# ============================================================
# HONEST SUMMARY
# ============================================================
log("\n" + "="*70)
log("V34 COMPREHENSIVE VERDICT")
log("="*70)

log(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                V34 — LUNAR SPECTRAL FINGERPRINT                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  TEST 1: SPECTROSCOPY                                                ║
║  Result: Moon reproduces ALL solar Fraunhofer lines exactly          ║
║  Unique emission lines found: ZERO                                   ║
║  Verdict: GLOBE ● (reflected sunlight confirmed)                     ║
║                                                                      ║
║  TEST 2: POLARIZATION                                                ║
║  Result: Negative branch matches silicate dust, not emission         ║
║  Max polarization at quarter: 8-12% (typical regolith)              ║
║  Verdict: GLOBE ● (particulate surface confirmed)                    ║
║                                                                      ║
║  TEST 3: OPPOSITION SURGE                                            ║
║  Result: SHOE + CBOE reproduce surge exactly                         ║
║  Same surge on Mercury, Mars, asteroids                              ║
║  Verdict: GLOBE ● (reflection mechanisms confirmed in lab)           ║
║                                                                      ║
║  V34 RESULT: All three tests favor reflected sunlight model          ║
║  Moon-as-emitter hypothesis has no spectral, polarimetric,           ║
║  or photometric evidence in its favor.                               ║
║                                                                      ║
║  UPDATED SCORECARD (V1-V34, 40 tests):                              ║
║  TIE:       25                                                       ║
║  GLOBE:      9  (+3: spectroscopy, polarization, opposition)        ║
║  DOME:       4  (magnetic convergence, asymmetry, Miller, jerks)    ║
║  CONTESTED:  2                                                       ║
║                                                                      ║
║  STRATEGIC NOTE:                                                     ║
║  The Moon tests went clearly to Globe. This is important to          ║
║  acknowledge — the same honesty that made the magnetic findings      ║
║  credible requires accepting losses too.                             ║
║  The dome model's strengths are MAGNETIC, not lunar.                 ║
║  Focus firepower on: convergence, asymmetry, jerks, Miller.         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# Scorecard
mr("SCORECARD","spectroscopy","GLOBE","no emission lines","test","V34","reflected sunlight")
mr("SCORECARD","polarization","GLOBE","matches silicate dust","test","V34","negative branch diagnostic")
mr("SCORECARD","opposition","GLOBE","SHOE+CBOE confirmed","test","V34","same on other bodies")
mr("SCORECARD","TOTAL_V34","40_tests","TIE=25|GLOBE=9|DOME=4|CONTESTED=2",
   "count","V1-V34","dome strengths are magnetic not lunar")

# Save
df = pd.DataFrame(master)
df.to_csv('v34_master_results.csv', index=False)
log(f"\nSaved v34_master_results.csv ({len(master)} rows)")

# Structured output
log(f"\n{'='*70}")
log("SECTION,SUBSECTION,PARAMETER,VALUE,UNIT,SOURCE,NOTES")
log("SPECTRAL,fraunhofer_match,all_lines,IDENTICAL,100%,spectroscopy,same wavelengths same depths")
log("SPECTRAL,emission_lines,unique_to_moon,ZERO,count,literature_search,no published findings")
log("SPECTRAL,telluric_lines,O2+H2O,present_in_moonlight,absorption,atmosphere,proves external path")
log("SPECTRAL,verdict,mechanism,reflected_sunlight,conclusion,overwhelming,GLOBE")
log("POLARIZATION,negative_branch,-0.5_to_-2%,at_5-20deg,percent,Lyot_1929,diagnostic_of_dust")
log("POLARIZATION,max_at_quarter,8-12%,at_90deg_phase,percent,standard,matches_silicates")
log("POLARIZATION,verdict,material,silicate_regolith,conclusion,confirmed,GLOBE")
log("OPPOSITION,brightness_ratio,11.5x,full_vs_half,ratio,observations,3.5x_above_geometric")
log("OPPOSITION,SHOE,confirmed,reproduced_in_lab,verified,Hapke_1986,shadow_hiding")
log("OPPOSITION,CBOE,confirmed,reproduced_in_lab,verified,Muinonen_1990,coherent_backscatter")
log("OPPOSITION,other_bodies,same_surge,Mercury_Mars_asteroids,universal,all_rocky,no_emission_model")
log("OPPOSITION,verdict,mechanism,SHOE+CBOE,conclusion,standard_physics,GLOBE")
log("SCORECARD,V34_total,40_tests,TIE=25|GLOBE=9|DOME=4|CONT=2,count,updated,dome=magnetic globe=lunar")
log(f"MODEL_STATUS,V34_complete,TRUE,2026-03-05,HIGH,ready_for_V35")

log(f"\n{'='*70}")
log("V34 COMPLETE")
log("="*70)
log("Files: v34_master_results.csv")
log("DONE")
