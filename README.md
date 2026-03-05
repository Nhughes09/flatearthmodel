# 🌍 Flat Earth Firmament Model — Research Archive

> A comprehensive computational research project exploring flat-plane and dome/firmament-based astronomical models, with 35+ iterative versions of mathematical pipelines, observational data, and falsifiable predictions.

---

## 📖 Overview

This repository contains a complete archive of an evolving astronomical model that attempts to describe celestial mechanics using flat-plane geometry and a dome/firmament architecture. The project spans **versions v8–v35** and includes:

- **28 pipeline scripts** (Python) implementing the mathematical models
- **60+ CSV data files** with observational data, predictions, and results
- **Architecture documents** describing the firmament model in detail
- **Visualization outputs** (error plots, star drift, analemma fits)
- **Honest assessments** of where the model succeeds and fails

---

## 🏗️ Firmament Architecture (V21)

```
╔═══════════════════════════════════════════════════════════════════╗
║                FIRMAMENT ARCHITECTURE — V21                      ║
╠═══════════════════════════════════════════════════════════════════╣
║ Body          Height (km)   Diameter (km)  Period      Notes     ║
╠═══════════════════════════════════════════════════════════════════╣
║ Earth plane   0             ~40,000        fixed       observer  ║
║ Moon             2,534           23.0     27.3 d      closest   ║
║ Sun              5,733           53.0    365.25 d    dome shell ║
║ Venus         ~  5,733       ~    0.2      variable    shell     ║
║ Mars          ~  5,733       ~    0.3      687 d       shell     ║
║ Jupiter       ~  5,733       ~    5.3     11.86 yr    shell     ║
║ Polaris       6,500          ~10           fixed       pole lamp ║
║ Near stars    ~1,400,000     ~0.001        fixed       firmament ║
║ Firmament     unknown        encompasses   25,772 yr   outer wall║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 📊 Key Results (Latest: V35)

### Aetheric Flow Model

| Parameter        | Value      | Unit  | Notes                       |
| ---------------- | ---------- | ----- | --------------------------- |
| Qμ (best fit)    | 0.00203851 | km²/s | Single parameter model      |
| North pole drift | 0.0007     | mm/s  | Exact match to observations |
| South pole drift | 0.0001     | mm/s  | 24% off observed            |
| Aether density   | 2.15×10⁸   | kg/m³ | ~175M × air density         |
| Wave speed       | 0.54       | m/s   | From geomagnetic jerk lag   |

### Falsifiable Predictions (2026–2035)

| Year | NMP Distance from Polaris | Radius (km) |
| ---- | ------------------------- | ----------- |
| 2026 | 3.73°                     | 415.2       |
| 2027 | 3.51°                     | 390.4       |
| 2028 | 3.27°                     | 363.9       |
| 2029 | 3.01°                     | 335.2       |
| 2030 | 2.73°                     | 303.8       |
| 2031 | 2.41°                     | 268.8       |
| 2032 | 2.05°                     | 228.5       |
| 2033 | 1.61°                     | 179.4       |
| 2034 | 1.00°                     | 111.1       |

---

## 📁 Repository Structure

```
FlatEarthModel/
├── README.md                          # This file
│
├── 📐 Core Modules
│   ├── astro_calc.py                  # Core astronomical calculation library
│   ├── firmament_model_FINAL.py       # Final firmament model implementation
│   ├── build_unified_master.py        # Unified dataset builder
│   └── dome_predictor_interactive.py  # Interactive dome predictor tool
│
├── 📜 Architecture Documents
│   ├── FIRMAMENT_ARCHITECTURE_FINAL.md  # Complete architecture with honest assessment
│   ├── FIRMAMENT_MODEL_DRAFT_2.md       # Detailed model draft (~44KB)
│   └── DOME_MODEL_DOCUMENTATION.md      # Dome model docs
│
├── 🔬 Pipeline Scripts (v13–v35)
│   ├── firmament_v8.py                # Early firmament model
│   ├── v13_pipeline.py                # Corrected observations pipeline
│   ├── v14_pipeline.py                # Error reduction iteration
│   ├── v15_pipeline.py                # Transit observations
│   ├── v16_pipeline.py                # Star dome heights + precession
│   ├── v17_pipeline.py                # Moon corrections + June predictions
│   ├── v18_pipeline.py                # Mars/Venus integration
│   ├── v19_pipeline.py                # Multi-date validation
│   ├── v20_pipeline.py                # Challenges documentation
│   ├── v21_pipeline.py                # Major: LeSage gravity, tidal model, distances
│   ├── v22_pipeline.py                # Analemma fit, equation of time
│   ├── v23_pipeline.py                # Coriolis, flight route matrix, Sigma Octantis
│   ├── v24_pipeline.py                # Live sky validation, star drift
│   ├── v25_pipeline.py                # Final scorecard, lunar power, unique predictions
│   ├── v26_pipeline.py                # Dark matter, GR comparison, Hubble tension
│   ├── v27_pipeline.py                # Layer table, outlier analysis
│   ├── v28_pipeline.py                # Gravity gradient, pole asymmetry
│   ├── v31_pipeline.py                # Full scorecard
│   ├── v32_pipeline.py                # Refined pipeline
│   ├── v33_pipeline.py                # Geomagnetic jerk analysis
│   ├── v34_pipeline.py                # Updated master results
│   ├── v34b_pipeline.py               # Moon tests
│   ├── v34c_phase_objections.py       # Phase objection analysis
│   └── v35_pipeline.py                # Latest: Aetheric flow model
│
├── 📊 Observational Data
│   ├── observations.csv               # Base observational dataset
│   ├── v13_corrected_obs.csv          # Corrected observations
│   └── v15_transit_obs.csv            # Transit observations
│
├── 📈 Results & Predictions (CSV)
│   ├── v*_master_results.csv          # Master results per version
│   ├── UNIFIED_MASTER_V1_V31.csv      # Unified dataset (v1–v31)
│   ├── UNIFIED_MASTER_V1_V33.csv      # Unified dataset (v1–v33)
│   ├── v*_results.csv                 # Per-version results
│   └── [various specialized CSVs]     # See detailed list below
│
├── 📉 Visualizations (PNG)
│   ├── v13_errors.png                 # V13 error analysis
│   ├── v14_errors.png                 # V14 error analysis
│   ├── v15_errors.png                 # V15 error analysis
│   ├── v16_errors.png                 # V16 error analysis
│   ├── v16_precession.png             # Precession visualization
│   ├── v17_final_validation.png       # V17 validation results
│   ├── v22_analemma.png               # Analemma fit
│   └── v24_star_drift.png             # Star drift analysis
│
└── 📝 Analysis Documents (TXT)
    ├── v20_challenges.txt             # Known challenges
    ├── v21_miller_experiment.txt       # Dayton Miller aether experiment
    ├── v24_firmament_height.txt        # Firmament height analysis
    ├── v26_dark_matter_failures.txt    # Dark matter comparison failures
    └── v26_hubble_tension.txt          # Hubble tension analysis
```

### Specialized CSV Data Files

| File                                | Description                                   |
| ----------------------------------- | --------------------------------------------- |
| `firmament_v8–v12_comparison.csv`   | Firmament model comparison across iterations  |
| `v16_declination_drift.csv`         | Declination drift measurements                |
| `v16_star_dome_heights.csv`         | Star dome height calculations                 |
| `v17_moon_corrected.csv`            | Corrected Moon observations                   |
| `v18_mars_venus.csv`                | Mars/Venus position data                      |
| `v19_multidate_validation.csv`      | Multi-date validation results                 |
| `v21_flat_distances.csv`            | Flat Earth distance calculations              |
| `v21_lesage_gravity_fit.csv`        | LeSage gravity model fit data                 |
| `v21_sun_height_triangulation.csv`  | Sun height triangulation from multiple cities |
| `v21_moon_height_triangulation.csv` | Moon height triangulation                     |
| `v21_southern_distances.csv`        | Southern hemisphere distances (critical test) |
| `v21_tidal_aetheric.csv`            | Aetheric tidal model data                     |
| `v21_power_beaming_comparison.csv`  | Tesla Wardenclyffe comparison                 |
| `v22_analemma_fit.csv`              | Analemma curve fitting data                   |
| `v22_equation_of_time.csv`          | Equation of time calculations                 |
| `v22_bipolar_distances.csv`         | Bipolar distance measurements                 |
| `v23_coriolis_bipolar.csv`          | Coriolis effect bipolar data                  |
| `v23_full_route_matrix.csv`         | Complete flight route matrix                  |
| `v23_sigma_octantis.csv`            | Sigma Octantis analysis                       |
| `v24_live_sky.csv`                  | Live sky validation data                      |
| `v24_worst_routes.csv`              | Worst-fitting flight routes                   |
| `v25_final_scorecard.csv`           | Final model scorecard                         |
| `v25_lunar_power.csv`               | Lunar power beaming data                      |
| `v25_pole_convergence.csv`          | Pole convergence predictions                  |
| `v25_unique_predictions.csv`        | Unique model predictions                      |
| `v25_wall_reflection.csv`           | Wall reflection data                          |
| `v26_dark_matter.csv`               | Dark matter comparison                        |
| `v26_fine_tuning.csv`               | Fine-tuning analysis                          |
| `v26_gr_vs_aether.csv`              | General Relativity vs Aether comparison       |
| `v26_young_earth_test.csv`          | Young Earth test data                         |
| `v27_layer_table.csv`               | Atmospheric layer table                       |
| `v27_outlier_layers.csv`            | Outlier layer analysis                        |
| `v27_pole_convergence.csv`          | Updated pole convergence                      |
| `v27_realtime_sky.csv`              | Real-time sky validation                      |
| `v28_gravity_gradient.csv`          | Gravity gradient measurements                 |
| `v28_pole_asymmetry.csv`            | Pole asymmetry analysis                       |
| `v31_full_scorecard.csv`            | V31 full scorecard                            |
| `v33_jerk_analysis.csv`             | Geomagnetic jerk timing analysis              |
| `v34b_moon_tests.csv`               | Moon phase/libration tests                    |
| `v35_master_results.csv`            | Latest master results with predictions        |

---

## 🔄 Version History

| Version    | Key Changes                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------------------ |
| **v8**     | Initial firmament model with dome geometry                                                             |
| **v9–v12** | Iterative firmament comparison refinements                                                             |
| **v13**    | Corrected observations, error analysis with plots                                                      |
| **v14**    | Error reduction, refined calculations                                                                  |
| **v15**    | Transit observations integration                                                                       |
| **v16**    | Star dome heights, declination drift, precession analysis                                              |
| **v17**    | Moon corrections, June 21 predictions, final validation                                                |
| **v18**    | Mars and Venus position modeling                                                                       |
| **v19**    | Multi-date validation across calendar                                                                  |
| **v20**    | Documented known challenges and limitations                                                            |
| **v21**    | **MAJOR**: LeSage gravity, tidal model, distance tests, Miller experiment, complete architecture table |
| **v22**    | Analemma fit, equation of time, southern arc distances                                                 |
| **v23**    | Coriolis analysis, full 30-route flight matrix, Sigma Octantis                                         |
| **v24**    | Live sky validation, star drift analysis, firmament height                                             |
| **v25**    | Final scorecard, lunar power, unique predictions, wall reflection                                      |
| **v26**    | Dark matter comparison, GR vs Aether, Hubble tension, young Earth test                                 |
| **v27**    | Atmospheric layer table, outlier analysis, real-time sky                                               |
| **v28**    | Gravity gradient, pole asymmetry analysis                                                              |
| **v31**    | Full scorecard with updated metrics                                                                    |
| **v32**    | Refined pipeline calculations                                                                          |
| **v33**    | Geomagnetic jerk timing analysis                                                                       |
| **v34**    | Updated master results, Moon phase tests                                                               |
| **v34b**   | Moon libration and phase objection tests                                                               |
| **v34c**   | Phase objection analysis                                                                               |
| **v35**    | **LATEST**: Aetheric flow model with Qμ parameter, 2026–2035 predictions, derived aether properties    |

---

## ⚖️ Honest Assessment

### ✅ Where the Model Works Well

- Polaris elevation: 0.30° error (R² = 0.9999)
- Sun/Moon/planet transit elevations: <0.2° error
- Day length: 8.4 min error
- Sunrise/sunset azimuths: <0.3° error
- Eclipse prediction: 10/10
- Star trail directions: 5/5
- Circumpolar stars: 10/10

### ⚠️ Works With Caveats

- Sun height triangulation gives inconsistent heights from different cities
- LeSage gravity uses same formula as Newton (different mechanism, same predictions)
- Tidal model reproduces 12.4hr cycle but can't explain amplitude variation
- Miller experiment data is real but disputed for valid reasons

### ❌ Known Failures

- **Southern hemisphere distances**: Flat AE map gives 2x too-long distances for routes like Sydney↔Cape Town. Actual flight times match globe distances.
- **Ship hull-down**: Requires ad hoc atmospheric lensing
- **Moon distance variation**: Perigee/apogee tidal effects not explained

### 🔑 Fundamental Conclusion

> The dome model's astronomical predictions work because they ARE the globe formulas. `elev = 90 - |lat - dec|` IS spherical trigonometry. Where the models make DIFFERENT predictions (southern distances, hull-down, Moon distance variation), the globe model consistently fits observations better. The dome model is a valid COORDINATE TRANSFORMATION of globe astronomy, not an alternative physics.

---

## 🚀 Running the Code

```bash
# Run the latest pipeline
python v35_pipeline.py

# Run the interactive dome predictor
python dome_predictor_interactive.py

# Build the unified master dataset
python build_unified_master.py

# Run the core astronomical calculations
python astro_calc.py
```

### Requirements

- Python 3.8+
- NumPy
- Matplotlib (for visualizations)
- SciPy (for curve fitting)

---

## 📄 License

This research archive is provided for educational and research purposes.

---

_Last updated: March 4, 2026_
