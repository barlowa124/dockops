"""Receptor-side helpers: derive the search-space box from a co-crystallized
ligand rather than hand-typed coordinates.

Docking boxes in published benchmarks are almost always defined around the
bound ligand; encoding that derivation in code removes an unverifiable
constant from config.
"""

from __future__ import annotations

from dockops.pdb import records


def ligand_atoms(pdb_path: str, resname: str) -> list[tuple[float, float, float]]:
    """3D coordinates of all HETATM atoms belonging to resname."""
    coords = [
        tuple(r["coords"])
        for r in records(pdb_path, kinds=("HETATM",))
        if r["resname"] == resname
    ]
    if not coords:
        raise ValueError(f"no HETATM atoms for resname {resname!r} in {pdb_path}")
    return coords


def box_from_ligand(
    pdb_path: str, resname: str, padding: float = 5.0
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """(center, size) of a box around the ligand, padded by `padding` Å."""
    coords = ligand_atoms(pdb_path, resname)
    mins = [min(c[i] for c in coords) for i in range(3)]
    maxs = [max(c[i] for c in coords) for i in range(3)]
    center = tuple(round((lo + hi) / 2, 3) for lo, hi in zip(mins, maxs))
    size = tuple(round(hi - lo + 2 * padding, 3) for lo, hi in zip(mins, maxs))
    return center, size
