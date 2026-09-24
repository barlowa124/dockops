# Docking backend setup

`VinaEngine` and PDBQT conversion are stubbed pending these dependencies.

## Install

```bash
pip install -e .[vina]    # vina (AutoDock Vina python bindings) + meeko
```

`vina` ships wheels for Linux and macOS; if a wheel is unavailable for the
target platform, use the Docker image or conda-forge (`conda install -c
conda-forge vina meeko`).

## Ligand prep (to_pdbqt)

Use `meeko.MoleculePreparation` on the RDKit-embedded mol from
`ligands.embed_smiles`:

```python
from meeko import MoleculePreparation, PDBQTWriterLegacy
preparator = MoleculePreparation()
mol_setup = preparator.prepare(mol)[0]
pdbqt_string = PDBQTWriterLegacy.write_string(mol_setup)[0]
```

## Receptor prep (one-time per target)

- Convert a cleaned receptor PDB to PDBQT with `mk_prepare_receptor.py`
  (Meeko) or ADFR's `prepare_receptor`; keep protonation/tautomers explicit
  and record the prep tool + version in provenance.
- Box: center on the co-crystallized ligand centroid; ~22.5 Å cube default.
- Add the receptor path + box to `config/config.yaml` under `targets:`.

## VinaEngine sketch

```python
v = Vina(sf_name="vina", seed=seed)
v.set_receptor(target.receptor_pdbqt)
v.set_ligand_from_string(pdbqt_string)
v.compute_vina_maps(center=target.box_center, box_size=target.box_size)
v.dock(exhaustiveness=8, n_poses=1)
score = v.energies()[0][0]
```

Record vina version, exhaustiveness, seed, and receptor hash in provenance.
