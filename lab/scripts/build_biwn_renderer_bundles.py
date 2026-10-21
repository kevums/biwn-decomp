"""Build isolated one-outer-instruction renderer with mandatory delay completion.
Generation is not runtime acceptance. Existing whole-component source unchanged.
"""
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out=ROOT/'verification/renderer-bundle-build'/stamp;out.mkdir(parents=True)
    original=ROOT/'projects/black-ice-white-noise/restoration'
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'gpu-resident-C-candidate/C-generation.json').read_text())
    source=(original/'biwn_gpu_resident.c').read_text()
    assert source.count('while(budget--)')==1
    source=source.replace('biwn_gpu_resident_run(', 'biwn_gpu_resident_bundle_run(')
    source=source.replace('while(budget--){unsigned delayed=pending;', 'while(budget||pending){unsigned delayed=pending;if(!delayed)budget--;')
    end='return BIWN_GPU_RESIDENT_WORK_LIMIT;}'
    assert source.count(end)==1
    source=source.replace(end,'*state=s;return BIWN_GPU_RESIDENT_OK;}')
    (out/'biwn_gpu_resident.c').write_text(source)
    (out/'biwn_gpu_resident.h').write_bytes((original/'biwn_gpu_resident.h').read_bytes())
    lib=out/'librenderer-bundle.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/'biwn_gpu_resident.c'),'-o',str(lib)]
    proc=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr
    report=dict(status='compiled_unverified',directory=str(out),library=str(lib),instructions_decoded=mapping['instructions_decoded'],
                source_sha256=hashlib.sha256(source.encode()).hexdigest(),parent_source_sha256=hashlib.sha256((original/'biwn_gpu_resident.c').read_bytes()).hexdigest(),
                semantics='Budget counts outer instructions; taken branch delay is completed without consuming outer budget. Commit at exhausted budget.',
                whole_game_complete=False,coordinator_authored=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'verification/renderer-bundle-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    overlays=[]
    for name,folder in [('geometry','gpu-geometry-overlay'),('projection','gpu-render-52e0-overlay')]:
        stem='biwn_gpu_'+name;body=(original/(stem+'.c')).read_text()
        assert body.count('while(budget--)')==1
        body=body.replace(stem+'_run(',stem+'_bundle_run(')
        body=body.replace('while(budget--){unsigned delayed=pending;','while(budget||pending){unsigned delayed=pending;if(!delayed)budget--;')
        end='return BIWN_GPU_'+name.upper()+'_WORK_LIMIT;}'
        assert body.count(end)==1
        body=body.replace(end,'*state=s;return BIWN_GPU_'+name.upper()+'_OK;}')
        (out/(stem+'.c')).write_text(body);(out/(stem+'.h')).write_bytes((original/(stem+'.h')).read_bytes())
        library=out/('lib'+name+'-bundle.dylib')
        cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/(stem+'.c')),'-o',str(library)]
        proc=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
        (out/(name+'-compiler.log')).write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr
        rows=json.loads((session/folder/'C-generation.json').read_text())['instructions_decoded']
        overlays.append(dict(name=name,library=str(library),instructions_decoded=rows,source_sha256=hashlib.sha256(body.encode()).hexdigest()))
    report['overlays']=overlays
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'verification/renderer-bundle-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(directory=str(out),status=report['status'],overlays=[x['name']for x in overlays])))
if __name__=='__main__':main()
