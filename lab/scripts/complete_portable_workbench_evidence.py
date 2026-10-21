"""Copy the exact declared evidence closure needed by the three BIWN workbenches.
Preserve raw receipt bytes; the installed adapter only rebases paths in memory.
"""
import hashlib, json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def main():
    v=ROOT/'verification';package=Path(json.loads((v/'portable-sdk-workbench-current.json').read_text())['package'])
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=v/'portable-workbench-evidence'/stamp;out.mkdir(parents=True)
    seeds=['m68k-fact-validation-current.json','m68k-fact-packet-current.json','native-string-source-certificate-current.json','native-string-ccr-certificate-current.json']
    queue=[v/x for x in seeds];seen=set()
    def paths(value):
        if isinstance(value,str) and value.startswith(str(ROOT)+'/'):
            path=Path(value)
            if path.is_file():yield path
        elif isinstance(value,list):
            for item in value:yield from paths(item)
        elif isinstance(value,dict):
            for key,item in value.items():yield from paths(key);yield from paths(item)
    while queue:
        source=queue.pop()
        if source in seen:continue
        seen.add(source)
        if source.suffix=='.json' and source.stat().st_size<2000000:
            try:queue.extend(paths(json.loads(source.read_text())))
            except (ValueError,UnicodeError):pass
    rows=[]
    for source in sorted(seen):
        relative=source.relative_to(ROOT);target=package/'workbench'/relative;digest=sha(source);backup=None
        if target.is_file() and sha(target)==digest:action='existing_exact'
        else:
            if target.exists() or target.is_symlink():
                backup=package/'backups'/('evidence-'+stamp)/relative;backup.parent.mkdir(parents=True,exist_ok=True);os.rename(target,backup)
            target.parent.mkdir(parents=True,exist_ok=True)
            subprocess.run(['/bin/cp','-cL',str(source),str(target)],check=True)
            assert sha(target)==digest
            action='copied'
        rows.append(dict(relative=str(relative),bytes=source.stat().st_size,sha256=digest,action=action,previous_copy_backup=str(backup)if backup else None))
    save(out/'files.json',rows);save(package/'portable-workbench-evidence-files.json',rows)
    result=dict(status='terminal_exact_declared_workbench_evidence_closure_copied_pending_tool_checks',pid=os.getpid(),directory=str(out),package=str(package),files=len(rows),bytes=sum(x['bytes']for x in rows),copied=sum(x['action']=='copied'for x in rows),raw_historical_JSON_rewritten=False,new_predictions=0,new_training=False,scope=__doc__)
    save(out/'protocol.json',result);save(v/'portable-workbench-evidence-current.json',result);print(json.dumps(result))
if __name__=='__main__':main()
