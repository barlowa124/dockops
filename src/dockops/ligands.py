"""Ligand preparation: SMILES -> 3D conformer -> PDBQT.

RDKit ETKDG embedding + MMFF94 minimization, then Meeko for the PDBQT
conversion Vina needs (install extra: dockops[vina]).
"""

from __future__ import annotations

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")


def embed_smiles(smiles: str, seed: int = 0) -> Chem.Mol | None:
    """Return a 3D-embedded, MMFF-minimized mol, or None on failure."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, AllChem.ETKDGv3()) != 0:
        return None
    if AllChem.MMFFHasAllMoleculeParams(mol):
        AllChem.MMFFOptimizeMolecule(mol)
    return mol


def to_sdf(smiles: str, seed: int = 0) -> str | None:
    mol = embed_smiles(smiles, seed=seed)
    return Chem.MolToMolBlock(mol) if mol is not None else None


def to_pdbqt(smiles: str, seed: int = 0) -> str | None:
    """3D-embedded mol -> PDBQT string via meeko; None on failure."""
    try:
        from meeko import MoleculePreparation, PDBQTWriterLegacy
    except ImportError as e:
        raise RuntimeError(
            "meeko not installed — pip install .[vina] "
            "(see docs/engine-setup.md)"
        ) from e
    mol = embed_smiles(smiles, seed=seed)
    if mol is None:
        return None
    setups = MoleculePreparation().prepare(mol)
    if not setups:
        return None
    out = PDBQTWriterLegacy.write_string(setups[0])
    pdbqt = out[0] if isinstance(out, tuple) else out
    return pdbqt or None
