"""
ParamHandler – Python 3.9-compatible.

Reads a Jancu-style <materials> XML, lets you tweak tags, and writes a new file.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union


class ParamHandler:
    """Lightweight wrapper around the Jancu material database.

    Convenience method:
        • update_and_save(material, updates, out_path, keep_only=True)
    """

    # ------------------------------------------------------------------
    def __init__(self, xml_path: Union[str, Path]) -> None:
        self.path = Path(xml_path)
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()  # <materials>

    # ------------------------------------------------------------------
    def list_materials(self) -> List[str]:
        return [m.get("name") for m in self.root.findall("./material")]

    def get_params(self, material: str) -> Dict[str, float]:
        mat = self._material_node(material)
        return {child.tag: float(child.get("val")) for child in mat}

    # ------------------------------------------------------------------
    def set_params(self, material: str, updates: Dict[str, float]) -> None:
        mat = self._material_node(material)
        for tag, val in updates.items():
            node = mat.find(tag)
            if node is None:
                node = ET.SubElement(mat, tag)
            node.set("val", f"{val:.6f}")

            # keep _a/_c twins equal for diamond structures
            if tag.endswith("_a"):
                twin = tag.replace("_a", "_c")
            elif tag.endswith("_c"):
                twin = tag.replace("_c", "_a")
            else:
                twin = None

            if twin:
                twin_node = mat.find(twin)
                if twin_node is not None:
                    twin_node.set("val", f"{val:.6f}")

    # ------------------------------------------------------------------
    def write(
        self,
        out_path: Union[str, Path],
        materials: Optional[Iterable[str]] = None,
    ) -> None:
        """Serialize current tree to *out_path*.

        If *materials* is given, keep **only** those material names.
        """
        out_path = Path(out_path)
        if materials is not None:
            keep = set(materials)
            for mat in list(self.root.findall("./material")):
                if mat.get("name") not in keep:
                    self.root.remove(mat)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        self.tree.write(out_path, encoding="utf-8", xml_declaration=True)
        print(f"[ParamHandler] wrote {out_path}")

    # ------------------------------------------------------------------
    def update_and_save(
        self,
        material: str,
        updates: Dict[str, float],
        out_path: Union[str, Path],
        keep_only: bool = True,
    ) -> None:
        """Shortcut: update tags, then write to *out_path*."""
        self.set_params(material, updates)
        self.write(out_path, materials=[material] if keep_only else None)

    # ------------------------------------------------------------------
    def _material_node(self, material: str) -> ET.Element:
        node = self.root.find(f"./material[@name='{material}']")
        if node is None:
            raise KeyError(f"material <{material}> not found in {self.path}")
        return node

