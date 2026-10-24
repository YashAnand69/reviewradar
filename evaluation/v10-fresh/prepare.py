"""Capture fresh inputs in predeclared fixed search order; no model calls."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

from reviewradar.github import fetch_github_snapshot
from reviewradar.schemas import normalize_snapshot

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/upgrade/evaluation'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    target=OUT/'selection-log.json'
    if target.exists(): raise SystemExit('Selection already captured; preserve it.')
    records=json.loads((OUT/'search-selection.json').read_text())
    prior={'fossasia/eventyay#6104','fossasia/visdom#1864','fossasia/visdom#1872','fossasia/voxbento#718'}
    selected=[]; log=[]
    for rank,record in enumerate(records):
        repo=record['repository']['nameWithOwner']; pid=f"{repo}#{record['number']}"
        item={'rank':rank,'pr_id':pid,'url':record['url']}
        if pid in prior or repo.split('/')[0].lower()=='yashanand69':
            item['status']='excluded_prior_or_self'; log.append(item); continue
        stem=pid.replace('/','-').replace('#','-')
        try:
            raw=fetch_github_snapshot([record['url']],'YashAnand69')
            snap=normalize_snapshot(raw)
            path=OUT/f'{stem}-snapshot.json'; path.write_text(snap.model_dump_json(indent=2)+'\n')
            pr=snap.prs[0]
            humans=[c for c in pr.comments if not c.is_bot and c.author.lower()!=pr.author.lower() and c.body.strip()]
            item.update(snapshot_id=snap.id,sha256=digest(path),path=str(path.relative_to(ROOT)),complete=snap.complete,sources=len(pr.comments),reviewer_sources=len(humans),fetched_at=snap.fetched_at)
            item['status']='selected' if snap.complete and humans else 'excluded_incomplete_or_no_human_review'
            if item['status']=='selected': selected.append(item)
        except Exception as exc:
            item.update(status='intake_error',error_type=type(exc).__name__,reason=str(exc))
        log.append(item)
        target.write_text(json.dumps({'captured_at':datetime.now(timezone.utc).isoformat(),'search_sha256':digest(OUT/'search-selection.json'),'protocol_sha256':digest(ROOT/'evaluation/v10-fresh/PROTOCOL.md'),'records':log,'selected':selected},indent=2)+'\n')
        print(pid,item['status'],item.get('reviewer_sources'),flush=True)
        if len(selected)==8: break

if __name__=='__main__':main()
