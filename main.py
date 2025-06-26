"""
main.py
=======

Parallel CMA-ES band-structure fitting.  Each generation’s population
is evaluated concurrently through a multiprocessing Pool whose size
equals the PBS `ncpus` request (== `--popsize`).  No mpi4py required.
"""

from multiprocessing import get_context
from pathlib import Path

import numpy as np
import cma

from src.user import UserConfig
from src.p_helper import (
    FREE_TAGS,
    worker_init,
    fitness,
    vector_to_updates,
)
from src.param_handler import ParamHandler
from src.sim_handler import SimHandler
from src.data_loader import BandStructureData
from src.visualizer import BandStructurePlot


# ────────────────────────────────────────────────────────────────────
def main() -> None:
    # ── 0.  CLI & RNG setup ─────────────────────────────────────────
    cfg     = UserConfig()
    out_dir = cfg.out_dir
    rng     = np.random.default_rng(cfg.seed)

    # ── 1.  Load reference bandstructure ────────────────────────────
    ref_data = BandStructureData(cfg.ref_csv)
    print(f"[INFO] Starting CMA-ES fitting: popsize={cfg.popsize}, "
          f"max_iter={cfg.max_iter}, seed={cfg.seed}")
          
    # ── 2.  CMA-ES initialisation (popsize, max_iter from CLI) ──────
    init_vec = rng.uniform(-20, -20, size=len(FREE_TAGS))
    es = cma.CMAEvolutionStrategy(
        init_vec,
        5.0,                     # initial σ
        {
            "popsize": cfg.popsize,
            "maxiter": cfg.max_iter,
            "verbose": -9,       # silence CMA banner; we print our own progress
            "seed":    cfg.seed,
        },
    )

    # ── 3.  Launch multiprocessing Pool (forkserver) ────────────────
    ctx = get_context("forkserver")          # safer on HPC than raw “fork”
    with ctx.Pool(
        processes=cfg.popsize,
        initializer=worker_init,
        initargs=(cfg, ref_data.energies),
    ) as pool:

        generation = 0
        while not es.stop():
            # 3.1 ask → population
            X = es.ask()
            # 3.2 evaluate fitness in parallel
            fvals = pool.map(fitness, X)
            # 3.3 tell → strategy update
            es.tell(X, fvals)
            es.disp()                        # CMA’s one-line status

            # ---------- custom progress line ------------------------
            print(f"[gen {generation+1:>3d}/{cfg.max_iter}] "
                  f"RMS best = {es.best.f:.3f} eV")

            generation += 1

    # ── 4.  Report best vector ──────────────────────────────────────
    best_vec = es.result.xbest
    print(f"[CMA-ES] Finished after {generation} generations – "
          f"best RMS error = {es.result.fbest:.6f} eV")

    # ── 5.  Re-run solver with best parameters & plot overlay ───────
    best_xml = out_dir / "materials_best.xml"
    ParamHandler(cfg.materials_xml).update_and_save(
        "Silicon",
        vector_to_updates(best_vec),
        best_xml,
        keep_only=True,
    )

    final_csv = SimHandler(
        solver_exe    = cfg.solver_exe,
        base_user_xml = cfg.user_input_xml,
        save_root     = out_dir,
    ).run("Silicon", best_xml)

    final_data = BandStructureData(final_csv)
    plot_path  = out_dir / "overlay_best_fit.png"
    BandStructurePlot(ref_data, final_data.energies).draw(plot_path)
    print(f"[main] Overlay saved to {plot_path}")


# ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()