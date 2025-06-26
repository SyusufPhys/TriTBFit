"""CMA‑ES wrapper for Pass‑1 fitting (Python 3.9‑compatible)."""

from typing import Callable, Optional

import numpy as np
import cma

from src.data_loader import BandStructureData
from src.user import UserConfig


class BandStructureFitter:
    """Treat TB solver as a black‑box and fit via CMA‑ES.

    Parameters
    ----------
    data        : reference band‑structure (k‑path & energies)
    tb_solver   : callable ``(params, k_grid) -> energies``
    init_params : initial parameter vector; if ``None`` → random normal
    cfg         : CLI‑derived optimiser hyper‑parameters
    """

    def __init__(
        self,
        data: BandStructureData,
        tb_solver: Callable[[np.ndarray, np.ndarray], np.ndarray],
        init_params: Optional[np.ndarray],
        cfg: UserConfig,
    ) -> None:
        self.data = data
        self.tb_solver = tb_solver
        self.cfg = cfg
        self.dim = init_params.size if init_params is not None else 20  # default size

        # ── CMA‑ES initialisation ───────────────────────────────────────────
        x0 = init_params if init_params is not None else np.random.randn(self.dim)
        sigma0 = 0.3 * np.linalg.norm(x0) / np.sqrt(self.dim)
        self.es = cma.CMAEvolutionStrategy(
            x0,
            sigma0,
            {
                "popsize": cfg.popsize,
                "seed": cfg.seed,
                "maxiter": cfg.max_iter,
            },
        )

    # ------------------------------------------------------------------
    def _loss(self, params: np.ndarray) -> float:
        """Root‑mean‑square energy mismatch over all k‑points & bands."""
        pred = self.tb_solver(params, self.data.kpath)  # type: ignore[arg-type]
        if pred.shape != self.data.energies.shape:
            raise ValueError("TB solver returned array of wrong shape")
        return float(np.sqrt(((pred - self.data.energies) ** 2).mean()))

    # ------------------------------------------------------------------
    def fit(self) -> np.ndarray:
        """Run CMA‑ES until termination; return best parameter vector."""
        while not self.es.stop():
            population = self.es.ask()
            losses = [self._loss(p) for p in population]
            self.es.tell(population, losses)
            self.es.disp()
        best = self.es.result.xbest

        # Save best parameters
        out_path = self.cfg.out_dir / "best_params_pass1.npy"
        np.save(out_path, best)
        print(f"[INFO] Saved best parameters to {out_path}")
        return best
