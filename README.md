# Loon Calculator Hyper-Captiosus 🧮⚡

An advanced, hybrid computational and symbolic calculator engine combining high-performance **C** backend binaries (`loon1.c`, `control_pad.c`) with a feature-rich, modular **Python** GUI and analytics suite (`smart_calculator.py`).

---

## 📂 Project Architecture

```text
loon/
│
├── __pycache__/                  # Compiled Python cache modules
├── scratch/                      # Experimental tests & synthesizer suites
│   ├── test_full_synthesizer_suite.py
│   ├── test_pure_curve.py
│   └── test_user_complaints_resolved.py
│
├── smart_calculator.py           # Core Python calculator & intelligence frontend
├── loon1.c / loon1.exe           # Primary C computational engine / compiled binary
├── control_pad.c / control_pad.exe # Interactive control pad interface / compiled binary
│
├── append_modal.py               # Modal extension/appending utility
├── gen_plot.ps1                  # PowerShell script for automated math plot generation
├── test_24.ps1                   # Automation & validation test script
├── test_maclaurin.py             # Maclaurin series expansion test suite
│
├── math_plot.bmp                 # Exported graphical math output
├── learned_patterns.json         # Adaptive pattern learning/recognition state
├── locker_dossier.txt            # Secure logs / profile configuration records
├── smart_gui_state.json          # Persistent GUI window/session layout states
├── smart_locker.json             # Encrypted/secured user preference vault
└── smart_profile.json            # User profile and personalization state
