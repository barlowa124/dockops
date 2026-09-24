"""Ligand preparation: SMILES -> 3D conformer.

Implemented: RDKit ETKDG embedding + MMFF94 minimization -> SDF block.
TODO: PDBQT conversion via meeko (or Open Babel) for the Vina backend —
see docs/engine-setup.md.
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


def to_pdbqt(smiles: str, seed: int = 0) -> str:
    """TODO: 3D mol -> PDBQT via meeko MoleculePreparation.

    Raises until the meeko dependency (pip extra: dockops[vina]) and the
    conversion are implemented; the mock engine does not need PDBQT.
    """
    raise NotImplementedError(
        "PDBQT conversion requires meeko — see docs/engine-setup.md"
    )
