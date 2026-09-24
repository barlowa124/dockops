# dockops

Docking as a service: a reproducible pipeline + API that turns a molecular
docking tool into a reliable scientific workflow — ligand preparation, batch
execution, benchmark evaluation, and provenance on every run.

**2-minute tour:** [Status](#status) for what is real vs. stubbed,
[Architecture](#architecture) for the moving parts, `src/dockops/engine.py`
for the backend interface, `src/dockops/benchmark.py` for the evaluation.

## Status

- **Real and tested:** ligand SMILES → 3D embedding (RDKit ETKDG + MMFF) →
  PDBQT (Meeko), batch pipeline, FastAPI job service, benchmark metrics
  (ROC-AUC, enrichment factor), provenance manifests, Snakemake DAG, tests.
- **Real benchmark staging:** `python -m dockops.fetch` pulls a DUD-E
  target's actives/decoys (EGFR by default) plus its co-crystallized
  receptor from RCSB; `receptor.box_from_ligand` derives the docking box
  from the bound ligand rather than hand-typed coordinates.
- **Deterministic mock engine:** `MockEngine` produces stable pseudo-scores
  seeded by input hash so the whole system runs end-to-end without a docking
  binary. Scores from it are pipeline-mechanics demonstrations, **not**
  docking results, and are labeled `engine: "mock"` everywhere they appear.
- **Implemented, needs an environment:** `VinaEngine` is real code (ligand
  prep → maps → dock → affinity) but `vina` has no macOS arm64 wheel — it
  runs in the Dockerfile/Linux or conda-forge; receptor PDBQT conversion
  is still needed (see `docs/engine-setup.md`).

## Why

Drug-discovery platforms need models and tools operationalized into
dependable workflows, not notebooks: versioned inputs, recorded provenance,
repeatable batch execution, and honest evaluation against benchmark sets
(actives vs. decoys). This repo is that pattern at small scale.

## Architecture

```
config/config.yaml         endpoint-neutral config: targets, box params, engine selection
workflow/Snakefile         fixture ligands -> embed -> dock (batch) -> benchmark metrics
src/dockops/
  targets.py               target registry; box derived from co-crystallized ligand
  receptor.py              ligand HETATM -> box center/size
  fetch.py                 DUD-E actives/decoys + RCSB receptor staging
  ligands.py               SMILES -> 3D conformer (ETKDG + MMFF) -> PDBQT (meeko)
  engine.py                DockingEngine protocol | MockEngine (real) | VinaEngine (stub)
  pipeline.py              batch docking -> scores.csv + provenance.json
  provenance.py            git sha, versions, input hashes, config hash
  benchmark.py             ROC-AUC + enrichment factor over actives/decoys
  api.py                   FastAPI: POST /jobs, GET /jobs/{id}, GET /targets
```

## Quickstart

```bash
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python -e .[dev]
.venv/bin/python -m snakemake --cores 2    # end-to-end on fixture + mock engine
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m uvicorn dockops.api:app --port 8000
```

```bash
curl -X POST localhost:8000/jobs \
  -H 'content-type: application/json' \
  -d '{"smiles": "CC(=O)Oc1ccccc1C(=O)O", "target": "demo_target"}'
```

## Limitations

- Mock-engine scores carry no physical meaning; the repo claims workflow
  correctness, not docking accuracy, until `VinaEngine` lands and the
  benchmark runs on a real backend against a real benchmark set.
- The bundled fixture labels are illustrative — they exercise the benchmark
  code path and are not an enrichment claim.
- Research/education only; not for any regulated or clinical use.

## License

MIT — see LICENSE.
