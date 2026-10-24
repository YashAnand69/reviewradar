#!/usr/bin/env python3
"""Run the frozen fresh v10 cases exactly once. No tuning or automatic accuracy claim.

Run from project root: PYTHONPATH=backend .venv/bin/python evaluation/v10-fresh/run.py
Full histories and model artifacts remain ignored under outputs/upgrade/evaluation.
"""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
from datetime import datetime, timezone

from reviewradar.analysis import run_analysis, validate_bound_analysis
from reviewradar.config import Settings
from reviewradar.model import LINK_PROMPT, PROMPT_VERSION, SYSTEM_PROMPT
from reviewradar.schemas import normalize_snapshot

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / 'evaluation/v10-fresh'
OUT = ROOT / 'outputs/upgrade/evaluation/first-run'


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def main():
    manifest=json.loads((FROZEN/'freeze-manifest.json').read_text())
    for path,expected in [(FROZEN/'labels.json',manifest['labels_sha256']),(FROZEN/'PROTOCOL.md',manifest['protocol_sha256']),(ROOT/'backend/reviewradar/model.py',manifest['model_implementation_sha256'])]:
        if sha(path)!=expected:raise SystemExit(f'Frozen file changed: {path.relative_to(ROOT)}')
    for item in manifest['selected']:
        if sha(ROOT/item['path'])!=item['sha256']:raise SystemExit(f"Frozen source changed: {item['pr_id']}")
    OUT.mkdir(parents=True,exist_ok=True)
    runpath=OUT/'run-manifest.json'
    if runpath.exists() or list(OUT.glob('*-model.json')):raise SystemExit('First-run artifacts exist. Do not rerun or select a better prediction.')
    settings=Settings()
    config=json.loads((ROOT/'.runtime/services/config.json').read_text())
    run={'started_at':datetime.now(timezone.utc).isoformat(),'protocol':'human-review-passages-v10-fresh-1','freeze_manifest_sha256':sha(FROZEN/'freeze-manifest.json'),'labels_sha256':manifest['labels_sha256'],'model_implementation_sha256':manifest['model_implementation_sha256'],'prompt_version':PROMPT_VERSION,'prompt_sha256':hashlib.sha256((SYSTEM_PROMPT+LINK_PROMPT).encode()).hexdigest(),'model_sha256':sha(Path(config['model'])),'runtime_sha256':sha(Path(config['runtime'])),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'platform':platform.platform(),'python':platform.python_version(),'settings':{'model':settings.model_name,'context':settings.model_context,'max_output':settings.model_output,'margin':settings.model_margin,'timeout_seconds':settings.model_timeout,'temperature':0},'results':[],'complete':False}
    runpath.write_text(json.dumps(run,indent=2)+'\n')
    for item in manifest['selected']:
        stem=item['pr_id'].replace('/','-').replace('#','-')
        snapshot=normalize_snapshot(json.loads((ROOT/item['path']).read_text()))
        record={'pr_id':item['pr_id'],'snapshot_id':snapshot.id,'started_at':datetime.now(timezone.utc).isoformat()}
        started=time.monotonic()
        try:
            analysis=run_analysis(snapshot,'model',settings)
            (OUT/f'{stem}-model.json').write_text(analysis.model_dump_json(indent=2)+'\n')
            try:
                validate_bound_analysis(analysis,snapshot)
                record['mechanical_bound_validation']='pass'
            except ValueError as exc:
                record['mechanical_bound_validation']='fail'; record['validation_error']=str(exc)
            record.update(analysis_id=analysis.id,complete=analysis.complete,model_cards=len(analysis.cards),reported_elapsed_seconds=analysis.stats.elapsed_seconds,coverage=[x.model_dump() for x in analysis.coverage])
        except Exception as exc:
            # Preserve the failed attempt; no retry. Do not dump request headers/credentials.
            record.update(complete=False,error_type=type(exc).__name__)
        record['wall_seconds']=round(time.monotonic()-started,3)
        chronology=run_analysis(snapshot,'baseline',settings)
        validate_bound_analysis(chronology,snapshot)
        (OUT/f'{stem}-baseline.json').write_text(chronology.model_dump_json(indent=2)+'\n')
        record['baseline_cards']=len(chronology.cards)
        record['baseline_elapsed_seconds']=chronology.stats.elapsed_seconds
        run['results'].append(record)
        runpath.write_text(json.dumps(run,indent=2)+'\n')
        print(json.dumps(record),flush=True)
    run['finished_at']=datetime.now(timezone.utc).isoformat()
    run['complete']=len(run['results'])==len(manifest['selected'])
    runpath.write_text(json.dumps(run,indent=2)+'\n')

if __name__=='__main__':main()
