# TriTBFit – Physics-Aware Tight-Binding Bandstructure Fitter (Pass 1)

**TriTBFit** is a lightweight, modular pipeline for fitting tight-binding (TB) models  
to reference bandstructures using **CMA-ES** (Covariance Matrix Adaptation).

🔧 **Pass 1** performs global RMS energy minimization.  
🚀 Later stages (e.g., dispersion weighting, curvature fitting, effective mass penalties)  
can be layered on using the same API and infrastructure.

Designed for extensibility, precision, and integration with real-world TB solvers.

---

## 1. Directory layout

<pre>

TriTBFit/
├── data/                     # Reference bandstructure CSV files (ignored by Git)
├── myvenv/                   # Local virtual environment (ignored)
├── requirements.txt          # Python dependencies
└── src/                      # Core source code
    ├── main.py                  # Entry point for running the fitter
    ├── user.py                  # Command-line interface and user config
    ├── data_loader.py           # Bandstructure data loader class
    ├── full_dispersion_fitter.py# Fitting logic for Pass 1
    └── visualizer.py            # Plotting and overlay of fitted bands
</pre>

---

## 2. Quick-start (macOS/Linux)

<pre>
```bash
# 1. Clone and enter the repository
git clone https://github.com/yourlab/TriTBFit.git
cd TriTBFit

# 2. Set up a Python 3.9 virtual environment
python3.9 -m venv myvenv
source myvenv/bin/activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Run the Pass-1 fitter (example: silicon reference)
python src/main.py \
    --ref_csv data/Si_reference.csv \
    --out_dir results \
    --popsize 16 --max_iter 200
```
</pre>

### What this command does

- 📥 Loads the reference CSV file specified by `--ref_csv`
- 🧬 Runs the CMA-ES optimiser with a population size of 16 for up to 200 generations
- 💾 Saves output files to the `--out_dir` folder:
  - `best_params_pass1.npy` — best-fit parameter vector
  - `band_fit_overlay.png` — side-by-side plot of reference vs. fitted bands


---

### 3. CSV Format

Each row corresponds to the eigen-energies at a single k-point along a high-symmetry path.

**Column layout:**

| Index | Description                                         |
|-------|-----------------------------------------------------|
| 0     | High-symmetry label (`Γ`, `X`, `L`, `W`, `K`, `U`) |
| 1     | Cumulative k-distance                               |
| 2–4   | k-vector components (ignored by the fitter)         |
| 5…    | Eigen-energies (in eV)                              |

**Example (first two rows):**
```
L,0.000000,0.578562,0.578562,0.578562,-10.220681,-6.656591,…,28.704354
none,0.000100,0.578504,0.578504,0.578504,-10.220681,-6.656591,…,28.704354
```

> **Note:** Supported high-symmetry labels include:  
> `Γ`, `X`, `L`, `W`, `K`, `U` — as defined by their fractional coordinates.



---
### 4. Plug in Your Own Tight-Binding Solver

The file `src/main.py` currently uses a placeholder `dummy_tb_solver`.

To use your own TB engine (written in C++, Fortran, or Python), replace this with a wrapper function that:

- Accepts a parameter vector `params`
- Accepts a k-point path `kpath` (shape: `[N_k, 3]`)
- Returns a NumPy array of energies with shape `[N_k, N_bands]`, matching the format of your reference CSV

**Example:**

```python
from my_cpp_wrapper import evaluate_tb  # Your custom backend

def tb_solver(params: np.ndarray, kpath: np.ndarray) -> np.ndarray:
    return evaluate_tb(params, kpath)
```

⚠️ **Note:** Make sure that `params.size` matches the number of Slater–Koster integrals you're fitting.  
If needed, update `BandStructureFitter.dim` accordingly.

---

### 5. Extending Beyond Pass 1

Once you’ve completed the initial RMS fitting (Pass 1), you can build on the same infrastructure to refine your model:

- 📉 **Pass 2 — Dispersion Weighting**  
  Modify `BandStructureFitter._loss()` to add a k-dependent weighting term (e.g., penalise curvature mismatches more heavily).

- 🧮 **Pass 3 — Effective Mass Matching**  
  Add a penalty based on finite-difference curvature of the fitted bands.  
  Compute numerical second derivatives from your solver output.

- 🧩 **Custom Extensions — Curvature, g-factor, Strain, etc.**  
  Inject additional loss terms directly into `_loss()`  
  No need to modify the CLI, data loader, or solver interface.

This modular setup allows you to layer in physics-aware objectives without disrupting the core pipeline.





---

### 7. Requirements

Install dependencies via `pip install -r requirements.txt`, or ensure the following packages are available:

- `numpy`
- `pandas`
- `matplotlib`
- `cma` (Covariance Matrix Adaptation Evolution Strategy)

✅ Tested with **Python 3.9.13** (CPython)

---

### 📄 License

This project is released under the **MIT License** with the following additional academic condition:

> 📚 If you use this code or methodology in an academic setting (e.g., publication, thesis, or presentation), **you must cite the author**:

**Sarinle Yusuf**  
[https://github.com/yourlab/TriTBFit](https://github.com/yourlab/TriTBFit)

A formal BibTeX entry will be provided in a future release.


