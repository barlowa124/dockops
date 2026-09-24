from dockops.ligands import embed_smiles, to_pdbqt
import pytest


def test_embed_valid_smiles():
    mol = embed_smiles("CC(=O)Oc1ccccc1C(=O)O")
    assert mol is not None
    assert mol.GetNumConformers() == 1


def test_embed_invalid_smiles_returns_none():
    assert embed_smiles("not_a_smiles") is None


def test_pdbqt_is_stubbed_until_meeko():
    with pytest.raises(NotImplementedError):
        to_pdbqt("CCO")
