"""
p_helper.py
===========

Module-scope helpers so that multiprocessing workers can be started with
the 'forkserver' method (or 'spawn' on non-Linux machines).  All callable
objects sent to workers must be pickle-able – hence nothing is nested.
"""

from pathlib import Path
import tempfile
from typing import Dict, List

import numpy as np

from src.param_handler import ParamHandler
from src.sim_handler import SimHandler
from src.data_loader import BandStructureData

# ─────────────────────────────────────────────────────────────────────
# Parameter tags that constitute the optimisation vector
# ─────────────────────────────────────────────────────────────────────
FREE_TAGS: List[str] = [
    # On-site energies
    "E_s_a", "E_s_c", "E_p_a", "E_p_c", "E_d", "E_sstar",
    # Two-centre integrals (sp3d5s*)
    "ss_sigma", "sstar_sstar_sigma",
    "sa_star_sc_sigma", "sa_sc_star_sigma",
    "sa_pc_sigma",      "sc_pa_sigma",
    "sa_star_pc_sigma", "sc_star_pa_sigma",
    "sa_dc_sigma",      "sc_da_sigma",
    "sa_star_dc_sigma", "sc_star_da_sigma",
    "pp_sigma", "pp_pi",
    "pa_dc_sigma", "pc_da_sigma",
    "pa_dc_pi",   "pc_da_pi",
    "dd_sigma", "dd_pi", "dd_delta"]

# ─────────────────────────────────────────────────────────────────────
# Globals that each worker sets exactly once in worker_init()
# ─────────────────────────────────────────────────────────────────────
CFG         = None   # UserConfig instance (paths, CLI flags)
REF_ENERGY  = None   # reference energies ndarray (Nk, Nb)

# ---------------------------------------------------------------------
def vector_to_updates(vec: np.ndarray) -> Dict[str, float]:
    """Convert a NumPy vector to {XML tag: value} mapping."""
    return {tag: float(val) for tag, val in zip(FREE_TAGS, vec)}

# ---------------------------------------------------------------------
def worker_init(cfg_obj, ref_energies):
    """
    Executed once per worker process.  Stores shared read-only objects
    in module-level globals so subsequent calls are fast.
    """
    global CFG, REF_ENERGY
    CFG        = cfg_obj
    REF_ENERGY = ref_energies

# ---------------------------------------------------------------------
def energies_from_params(beta: np.ndarray) -> np.ndarray:
    """
    Launch a single tight-binding solver run and return the (Nk, Nb)
    energies array.
    """
    with tempfile.TemporaryDirectory(dir=CFG.out_dir) as tmp:
        tmp = Path(tmp)
        trial_xml = tmp / "mat.xml"

        # Write one-material XML containing the candidate parameters
        ParamHandler(CFG.materials_xml).update_and_save(
            "Silicon",
            vector_to_updates(beta),
            trial_xml,
            keep_only=True,
        )

        csv_path = SimHandler(
            solver_exe    = CFG.solver_exe,
            base_user_xml = CFG.user_input_xml,
            save_root     = tmp,
        ).run("Silicon", trial_xml)

        return BandStructureData(csv_path).energies

# ---------------------------------------------------------------------
def fitness(beta: np.ndarray) -> float:
    """
    Root-mean-square energy error (in eV) between TB prediction and the
    cached reference bandstructure.
    """
    ener = energies_from_params(beta)
    return float(np.sqrt(((ener - REF_ENERGY) ** 2).mean()))