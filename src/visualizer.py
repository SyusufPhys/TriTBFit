"""Plotting utilities for TriTBFit.

Implements a `BandStructurePlot` class that overlays reference and fitted
bands in a dark style. Call `.draw(Path)` to write a PNG, or `.draw()` to
show interactively.
"""
from pathlib import Path
from typing import Optional

import numpy as np
from matplotlib import pyplot as plt

from src.data_loader import BandStructureData


class BandStructurePlot:
    """Overlay reference vs. fitted bands in a dark-style plot."""

    def __init__(self, data: BandStructureData, fitted: np.ndarray) -> None:
        self.data = data
        self.fitted = fitted
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(6, 3.5))

    # ------------------------------------------------------------------
    def draw(self, save_path: Optional[Path] = None) -> None:
        """Render the overlay and optionally save it.

        Parameters
        ----------
        save_path : Path or None
            If provided, write the figure to this file; otherwise show.
        """
        x = self.data.kpath

        # Reference bands – solid blue
        for i, band in enumerate(self.data.energies.T):
            self.ax.plot(x, band, "b-", lw=0.6, label="Reference" if i == 0 else None)

        # Fitted bands – red dotted
        for i, band in enumerate(self.fitted.T):
            self.ax.plot(x, band, "r:", lw=0.6, label="Fitted" if i == 0 else None)

        # High-symmetry ticks
        hs_x, hs_lbl = self.data.high_symmetry_points()
        self.ax.set_xticks(hs_x)
        self.ax.set_xticklabels(hs_lbl)

        self.ax.set_ylabel("Energy (eV)")
        self.ax.set_title("Bandstructure: reference vs. fitted (Pass 1)")
        self.ax.grid(True, color="gray", lw=0.3)
        self.ax.legend()

        if save_path is not None:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            self.fig.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"[INFO] Plot saved to {save_path}")
        else:
            plt.show()