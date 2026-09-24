"""FastAPI job service for docking requests.

POST /jobs {smiles, target} -> runs the configured engine, returns the
DockResult plus a provenance block. GET /jobs/{id} retrieves past results.
GET /targets lists configured targets.

State is in-memory — this is a single-process demonstration service, not a
production queue.
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from dockops.engine import get_engine
from dockops.provenance import manifest
from dockops.targets import get_target, list_targets
from dockops.util import load_config

CONFIG_PATH = "config/config.yaml"

app = FastAPI(title="dockops", version="0.1.0")
_jobs: dict[str, dict] = {}


class JobRequest(BaseModel):
    smiles: str
    target: str


def _engine():
    return get_engine(load_config(CONFIG_PATH).get("engine", "mock"))


@app.get("/targets")
def targets() -> list[str]:
    return list_targets(CONFIG_PATH)


@app.post("/jobs", status_code=201)
def submit_job(req: JobRequest) -> dict:
    try:
        target = get_target(req.target, CONFIG_PATH)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e
    engine = _engine()
    res = engine.dock(req.smiles, target)
    job_id = uuid.uuid4().hex[:12]
    record = {
        "job_id": job_id,
        "smiles": req.smiles,
        "target": req.target,
        "score": res.score,
        "status": res.status,
        "engine": res.engine,
        "provenance": manifest([], CONFIG_PATH, res.engine),
    }
    _jobs[job_id] = record
    return record


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    if job_id not in _jobs:
        raise HTTPException(404, f"unknown job: {job_id}")
    return _jobs[job_id]
