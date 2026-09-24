"""Docking engine interface and backends.

DockingEngine is the seam every backend implements. MockEngine is real code
with fake physics: deterministic pseudo-scores seeded by (smiles, target),
used so the pipeline, API, and tests run without a docking binary. Its scores
are labeled engine="mock" everywhere and must never be presented as docking
results. VinaEngine is the intended real backend — currently a stub pending
receptor prep + meeko (docs/engine-setup.md).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Protocol

from dockops.targets import TargetSpec


@dataclass(frozen=True)
class DockResult:
    score: float | None
    status: str  # "ok" | "error" | "unprepared"
    engine: str
    detail: dict = field(default_factory=dict)


class DockingEngine(Protocol):
    name: str

    def dock(self, smiles: str, target: TargetSpec) -> DockResult: ...


class MockEngine:
    """Deterministic pseudo-scores in a plausible Vina range (-12..-3).

    Score is derived from sha256(smiles|target|engine) — stable across runs,
    meaningless as physics.
    """

    name = "mock"

    def dock(self, smiles: str, target: TargetSpec) -> DockResult:
        digest = hashlib.sha256(
            f"{smiles}|{target.name}|{self.name}".encode()
        ).digest()
        score = -3.0 - 9.0 * (int.from_bytes(digest[:8]) / 2**64)
        return DockResult(
            score=round(score, 3), status="ok", engine=self.name, detail={}
        )


class VinaEngine:
    """AutoDock Vina backend.

    TODO: implement — ligand PDBQT via dockops.ligands.to_pdbqt (meeko),
    Vina(sf_name='vina'), set_receptor(target.receptor_pdbqt),
    compute_vina_maps(box_center, box_size), dock, energies()[0].
    Install: pip install .[vina]  (see docs/engine-setup.md)
    """

    name = "vina"

    def __init__(self) -> None:
        try:
            import vina  # noqa: F401
        except ImportError as e:
            raise RuntimeError(
                "vina package not installed — see docs/engine-setup.md"
            ) from e

    def dock(self, smiles: str, target: TargetSpec) -> DockResult:
        raise NotImplementedError("TODO: implement Vina docking backend")


def get_engine(name: str) -> DockingEngine:
    if name == "mock":
        return MockEngine()
    if name == "vina":
        return VinaEngine()
    raise ValueError(f"unknown engine: {name!r}")
