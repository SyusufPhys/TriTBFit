# src/data_loader.py

from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd


class BandStructureData:
    """
    Load reference CSV and expose k-points & energy matrix.

    CSV layout (no header):
        col 0  : high-symmetry label (string) or "none"
        col 1  : cumulative k-path distance (float)
        col 2-4: raw kx, ky, kz (ignored here)
        col 5… : eigen-energies (float)
    """

    def __init__(self, csv_path: Path) -> None:
        if not csv_path.is_file():
            raise FileNotFoundError(csv_path)
        self.raw_df = pd.read_csv(csv_path, header=None)

        # Extract basic arrays ----------------------------------------------------
        # Use Python list for labels
        self.labels: List[str] = self.raw_df.iloc[:, 0].tolist()
        self.kpath: np.ndarray = self.raw_df.iloc[:, 1].to_numpy(float)
        self.energies: np.ndarray = self.raw_df.iloc[:, 5:].to_numpy(float)  # shape (N_k, N_bands)

    def high_symmetry_points(self) -> Tuple[np.ndarray, List[str]]:
        """
        Return x-positions & labels of high-symmetry points for plotting.
        """
        mask = self.raw_df.iloc[:, 0] != "none"
        x_positions = self.kpath[mask.values]
        labels = self.raw_df.loc[mask, 0].tolist()
        return x_positions, labels