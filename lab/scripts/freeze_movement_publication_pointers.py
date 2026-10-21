"""Freeze newly added migration pointer dependencies; facts and binaries unchanged."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 v=ROOT/'verification';p=v/'current-biwn-latest-publication-current.json';old=json.loads(p.read_text());assert old['facts']['experimental_build']['resident_bytes']==26220;out=v/'current-biwn-latest-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copy2(p,out/'previous-publication.json');snap=out/'snapshots';snap.mkdir();d={};aliases=dict(old.get('historical_pointer_snapshots',{}))
 for name,h in old['dependencies_sha256'].items():
  q=Path(name);assert sha(q)==h,q
  if q.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(q).encode()).hexdigest()[:12]+'-'+q.name);shutil.copy2(q,target);aliases[str(q)]=str(target);q=target
  d[str(q)]=h
 d.update({str(q):sha(q)for q in [Path(__file__),out/'previous-publication.json']});old.update(directory=str(out),dependencies_sha256=d,historical_pointer_snapshots=aliases);save(out/'publication.json',old);save(p,old);print(json.dumps(dict(status=old['status'],resident_bytes=26220,mutable_dependency_snapshots=len(list(snap.iterdir())))))
if __name__=='__main__':main()
