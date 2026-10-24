"""Freeze an extended search and capture the first eligible novel sources; no inference."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from reviewradar.github import fetch_github_snapshot
from reviewradar.schemas import normalize_snapshot

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/upgrade/v15-unseen"
QUERY = ["gh", "search", "prs", "--author", "YashAnand69", "--sort", "updated", "--order", "desc", "--limit", "160", "--json", "createdAt,number,repository,state,title,updatedAt,url"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    search = OUT / "search-selection.json"
    target = OUT / "selection-log.json"
    if search.exists() or target.exists():
        raise SystemExit("Capture already started; preserve first artifacts.")
    OUT.mkdir(parents=True, exist_ok=True)
    old_search = ROOT / "outputs/upgrade/evaluation/search-selection.json"
    prior = {f"{x['repository']['nameWithOwner']}#{x['number']}" for x in json.loads(old_search.read_text())}
    prior.update({"fossasia/eventyay#6104", "fossasia/visdom#1864", "fossasia/visdom#1872", "fossasia/voxbento#718"})
    exclusions = {str(old_search.relative_to(ROOT)): digest(old_search)}
    for path in sorted((ROOT / "outputs/upgrade").glob("**/selection-log.json")):
        if path == target:
            continue
        value = json.loads(path.read_text())
        prior.update(x['pr_id'] for x in value.get('records', []) if 'pr_id' in x)
        exclusions[str(path.relative_to(ROOT))] = digest(path)
    for path in sorted((ROOT / "evaluation").glob("**/freeze-manifest.json")):
        value = json.loads(path.read_text())
        prior.update(x['pr_id'] for x in value.get('selected', []) if 'pr_id' in x)
        exclusions[str(path.relative_to(ROOT))] = digest(path)
    result = subprocess.run(QUERY, check=True, capture_output=True, text=True, timeout=60)
    records = json.loads(result.stdout)
    search.write_text(json.dumps(records, indent=2) + "\n")
    capture = dict(search_frozen_at=datetime.now(timezone.utc).isoformat(), query=QUERY, search_sha256=digest(search), protocol_sha256=digest(ROOT / "evaluation/v15-unseen/PROTOCOL.md"), prior_artifacts=exclusions, prior_identity_count=len(prior), novel_screened=0, records=[], selected=[])
    target.write_text(json.dumps(capture, indent=2) + "\n")
    for rank, record in enumerate(records):
        repo = record['repository']['nameWithOwner']
        pid = f"{repo}#{record['number']}"
        item = dict(rank=rank, pr_id=pid, url=record['url'])
        if pid in prior or repo.split('/')[0].casefold() == 'yashanand69':
            item['status'] = 'excluded_prior_or_self'
        elif capture['novel_screened'] >= 80:
            break
        else:
            capture['novel_screened'] += 1
            try:
                snap = normalize_snapshot(fetch_github_snapshot([record['url']], 'YashAnand69'))
                path = OUT / (pid.replace('/', '-').replace('#', '-') + '-snapshot.json')
                path.write_text(snap.model_dump_json(indent=2) + '\n')
                pr = snap.prs[0]
                humans = [c for c in pr.comments if not c.is_bot and c.author.casefold() != pr.author.casefold() and c.body.strip()]
                item.update(snapshot_id=snap.id, sha256=digest(path), path=str(path.relative_to(ROOT)), complete=snap.complete, sources=len(pr.comments), reviewer_sources=len(humans), fetched_at=snap.fetched_at)
                item['status'] = 'selected' if snap.complete and humans else 'excluded_incomplete_or_no_human_review'
                if item['status'] == 'selected':
                    capture['selected'].append(item)
            except Exception as exc:
                item.update(status='intake_error', error_type=type(exc).__name__, reason=str(exc))
        capture['records'].append(item)
        capture['updated_at'] = datetime.now(timezone.utc).isoformat()
        target.write_text(json.dumps(capture, indent=2) + '\n')
        print(item['status'], capture['novel_screened'], len(capture['selected']), flush=True)
        if len(capture['selected']) == 6:
            break


if __name__ == '__main__':
    main()
