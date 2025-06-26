# src/user.py
"""Parse command-line arguments for the band-structure simulation and fitting pipeline."""

import argparse
from pathlib import Path
from typing import Optional


class UserConfig:
    """Encapsulates paths and optimisation hyperparameters provided by the user."""

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            description="Run tight-binding simulation, CMA-ES fit, and plot overlay",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        # Reference data: bandstructure CSV for comparison
        parser.add_argument(
            "--ref_csv", type=Path, required=True,
            help="Path to reference bandstructure CSV"
        )

        # Output directory for plots, fit results, and scratch runs
        parser.add_argument(
            "--out_dir", type=Path, default=Path("results"),
            help="Directory to write outputs (plots, params, scratch runs)"
        )

        # Material database: initial parameters
        parser.add_argument(
            "--materials_xml", type=Path,
            default=Path("simulator/Jancu_Materials.xml"),
            help="Path to the material DB XML file"
        )

        # User-input template for sdt
        parser.add_argument(
            "--user_input_xml", type=Path,
            default=Path("simulator/user_input_tight_binding.xml"),
            help="Path to the base user-input XML template"
        )

        # Solver executable
        parser.add_argument(
            "--solver_exe", type=Path,
            default=Path("simulator/sdt"),
            help="Path to the sdt tight-binding executable"
        )

        # CMA-ES hyperparameters
        parser.add_argument(
            "--popsize", type=int, default=32,
            help="CMA-ES population size"
        )
        parser.add_argument(
            "--max_iter", type=int, default=200,
            help="Maximum CMA-ES generations"
        )
        parser.add_argument(
            "--seed", type=int, default=0,
            help="Random seed for reproducibility"
        )

        self.args = parser.parse_args()

        # Create output directory if needed
        self.args.out_dir.mkdir(parents=True, exist_ok=True)

    @property
    def ref_csv(self) -> Path:
        return self.args.ref_csv

    @property
    def out_dir(self) -> Path:
        return self.args.out_dir

    @property
    def materials_xml(self) -> Path:
        return self.args.materials_xml

    @property
    def user_input_xml(self) -> Path:
        return self.args.user_input_xml

    @property
    def solver_exe(self) -> Path:
        return self.args.solver_exe

    # CMA-ES properties ---------------------------------------------------
    @property
    def popsize(self) -> int:
        return self.args.popsize

    @property
    def max_iter(self) -> int:
        return self.args.max_iter

    @property
    def seed(self) -> int:
        return self.args.seed
