# Docking backend setup

`VinaEngine` and `ligands.to_pdbqt` (meeko) are implemented. What remains
environment-specific is installing `vina` and preparing a receptor.

## Install

```bash
pip install -e .[vina]    # vina (AutoDock Vina python bindings) + meeko + gemmi
```

**Platform note:** `vina` ships manylinux and macOS x86_64 wheels only — on
Apple Silicon the pip build needs Boost headers and fails. Use the Dockerfile
(Linux), conda-forge (`conda install -c conda-forge vina meeko`), or an
x86_64 environment. `meeko` alone is pure Python and installs everywhere —
ligand prep works on macOS.

## Receptor prep (one-time per target)

- Convert a cleaned receptor PDB to PDBQT with `mk_prepare_receptor.py`
  (Meeko) or ADFR's `prepare_receptor`; keep protonation/tautomers explicit
  and record the prep tool + version in provenance.
- Box: center on the co-crystallized ligand centroid; ~22.5 Å cube default.
- Add the receptor path + box to `config/config.yaml` under `targets:`, then
  set `engine: vina` (with `engine_params` for exhaustiveness/seed).

## What VinaEngine does

Per ligand: SMILES → RDKit ETKDG+MMFF 3D → meeko PDBQT →
`Vina(sf_name="vina", seed)` → `set_receptor` → `compute_vina_maps(box)` →
`dock(exhaustiveness, n_poses=1)` → `energies()[0][0]` affinity. Missing
receptor files and unembeddable ligands return error/unprepared statuses —
they do not raise.
