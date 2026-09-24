"""Target registry: receptor + search-space box, config-driven.

A TargetSpec is everything a docking engine needs that isn't the ligand.
Real receptors are prepared to PDBQT offline (see docs/engine-setup.md);
the mock engine does not require the file to exist.
"""

from __future__ import annotations

from dataclasses import dataclass

from dockops.util import load_config


@dataclass(frozen=True)
class TargetSpec:
    name: str
    receptor_pdbqt: str
    box_center: tuple[float, float, float]
    box_size: tuple[float, float, float]
    description: str = ""


def get_target(name: str, config_path: str = "config/config.yaml") -> TargetSpec:
    targets = load_config(config_path).get("targets", {})
    if name not in targets:
        raise KeyError(f"unknown target: {name!r} (known: {sorted(targets)})")
    t = targets[name]
    return TargetSpec(
        name=name,
        receptor_pdbqt=t["receptor_pdbqt"],
        box_center=tuple(t["box_center"]),
        box_size=tuple(t["box_size"]),
        description=t.get("description", ""),
    )


def list_targets(config_path: str = "config/config.yaml") -> list[str]:
    return sorted(load_config(config_path).get("targets", {}))
