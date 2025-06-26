# src/sim_handler.py
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union

class SimHandler:
    """Wrapper for launching the compiled `sdt tight-binding` solver."""

    def __init__(
        self,
        solver_exe: Union[str, Path],
        base_user_xml: Union[str, Path],
        save_root: Union[str, Path] = "results",
        env_vars: Optional[Dict[str, str]] = None,
        modules: Optional[List[str]] = None,
    ) -> None:
        self.solver_exe   = Path(solver_exe).resolve()
        self.base_user_xml = Path(base_user_xml).resolve()
        self.save_root    = Path(save_root).resolve()

        # default environment & module settings
        self.env_vars = env_vars or {
            "SLEPC_DIR": "...",
            "PETSC_DIR": "...",
            "PETSC_ARCH": "...",
            "TRILINOS_DIR": "...",
        }
        self.modules = modules or [
            "openmpi/4.0.2", "intel-compiler/2020", "intel-mkl/2020", 
            # etc.
        ]

        if not self.solver_exe.is_file() or not self.base_user_xml.is_file():
            raise FileNotFoundError("Solver or XML template missing")
        self.save_root.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        material_name: str,
        material_db: Union[str, Path],
        extra_flags: Optional[Dict[str, str]] = None,
    ) -> Path:
        """Run one tight-binding solve and return the bandstructure CSV path."""
        scratch = Path(tempfile.mkdtemp(prefix="tbf_", dir=self.save_root))
        user_xml = scratch / "user_input.xml"
        self._write_user_xml(material_name, material_db, user_xml)

        cli = [
            str(self.solver_exe),
            "tight-binding",
            f"--user_input={user_xml}",
            f"--save_dir={scratch}",
        ]
        if extra_flags:
            cli += [f"--{k}={v}" for k, v in extra_flags.items()]

        bash_cmd = f'bash -lc "{" ".join(cli)}"'
        subprocess.run(bash_cmd, shell=True, check=True, executable="/bin/bash",
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        csv_path = scratch / "bandstructure.csv"
        if not csv_path.is_file():
            raise FileNotFoundError(csv_path)
        return csv_path

    def _write_user_xml(
        self,
        material_name: str,
        db_path: Union[str, Path],
        out_path: Path,
    ) -> None:
        tree = ET.parse(self.base_user_xml)
        root = tree.getroot()

        mat_node = root.find("./material")
        mat_node.text = material_name

        db_node = root.find("./material_db_path")
        db_node.text = str(Path(db_path).resolve())

        out_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(out_path, encoding="utf-8", xml_declaration=True)