"""Isolated movement/sprite single-bundle C candidates; no runtime acceptance."""
import ctypes as c,hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_GPU as GPU
from biwn_renderer_bundle import OverlayBus
from biwn_material_bundle import MaterialBus
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'verification/control-GPU-bundle-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    original=ROOT/'projects/black-ice-white-noise/restoration';session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);rows=[];entries=[];ABI=['#include <stddef.h>','#include <stdio.h>']
    for name,bus in [('movement',OverlayBus),('sprite',MaterialBus)]:
        stem='biwn_'+name+'_fullGPU';body=(original/(stem+'.c')).read_text();assert body.count('while(budget--)')==1
        body=body.replace(stem+'_run(',stem+'_bundle_run(').replace('while(budget--){unsigned delayed=pending;','while(budget||pending){unsigned delayed=pending;if(!delayed)budget--;')
        end='return BIWN_'+name.upper()+'_FULLGPU_WORK_LIMIT;}';assert body.count(end)==1;body=body.replace(end,'*state=s;return BIWN_'+name.upper()+'_FULLGPU_OK;}')
        (out/(stem+'.c')).write_text(body);(out/(stem+'.h')).write_bytes((original/(stem+'.h')).read_bytes());library=out/('lib'+name+'-bundle.dylib')
        p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/(stem+'.c')),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/(name+'-compiler.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        mapping=json.loads((session/('gpu-'+name+'-overlay')/'fullGPU-C-generation.json').read_text());rows.append(dict(name=name,library=str(library),function=stem+'_bundle_run',instructions_decoded=mapping['instructions_decoded'],source_sha256=hashlib.sha256(body.encode()).hexdigest(),parent_source_sha256=hashlib.sha256((original/(stem+'.c')).read_bytes()).hexdigest()));entries.append((name,stem,GPU.State,bus));ABI.append('#include "'+stem+'.h"')
    ABI.append('int main(void){');expected={}
    for name,stem,state,bus in entries:
        for kind,typ in [('state',state),('bus',bus)]:
            cname='struct '+stem+'_'+kind;ABI.append('printf("'+name+' '+kind+' size %zu\\n",sizeof('+cname+'));');expected[(name,kind,'size')]=c.sizeof(typ)
            for field,_ in typ._fields_:ABI.append('printf("'+name+' '+kind+' '+field+' %zu\\n",offsetof('+cname+','+field+'));');expected[(name,kind,field)]=getattr(typ,field).offset
    ABI.append('return 0;}');(out/'ABI.c').write_text('\n'.join(ABI)+'\n');subprocess.run(['clang','-std=c99','-Wall','-Wextra','-Werror',str(out/'ABI.c'),'-o',str(out/'ABI')],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});layout=subprocess.check_output([str(out/'ABI')],text=True);(out/'ABI-layout.txt').write_text(layout);checks=[]
    for line in layout.splitlines():
        name,kind,field,value=line.split();assert expected[(name,kind,field)]==int(value);checks.append(dict(name=name,kind=kind,field=field,value=int(value)))
    report=dict(status='compiled_ABI_checked_unverified',directory=str(out),overlays=rows,ABI_checks=checks,whole_game_complete=False,new_training=False,coordinator_authored=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/control-GPU-bundle-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out,len(checks))
if __name__=='__main__':main()
