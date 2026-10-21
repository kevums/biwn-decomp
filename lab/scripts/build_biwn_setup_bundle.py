"""One-bundle setup57 candidate with actual compiled state/bus ABI checks."""
import ctypes as c,hashlib,json,os,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from biwn_material_bundle import PartialState
from biwn_frame_OP_GPU import R32,W32,OBS
ROOT=Path(__file__).resolve().parents[1]
class SetupBus(c.Structure):
    _fields_=[('read32',R32),('write32',W32),('observe_PC',OBS),('context',c.c_void_p)]
def main():
    out=ROOT/'verification/setup-bundle-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    original=ROOT/'projects/black-ice-white-noise/restoration';stem='biwn_gpu_setup57';body=(original/(stem+'.c')).read_text();assert body.count('while(budget--)')==1
    body=body.replace(stem+'_run(',stem+'_bundle_run(').replace('while(budget--){unsigned delayed=pending;','while(budget||pending){unsigned delayed=pending;if(!delayed)budget--;')
    end='return BIWN_GPU_SETUP57_WORK_LIMIT;}';assert body.count(end)==1;body=body.replace(end,'*state=s;return BIWN_GPU_SETUP57_OK;}')
    (out/(stem+'.c')).write_text(body);(out/(stem+'.h')).write_bytes((original/(stem+'.h')).read_bytes());library=out/'libsetup-bundle.dylib';environment={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/(stem+'.c')),'-o',str(library)],capture_output=True,text=True,env=environment);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'gpu-render-57a0-overlay/initial-linear-decode.json').read_text());cases={int(x,16)for x in re.findall(r'case (0x[0-9a-fA-F]+)u?:',body)};rows=[x for x in mapping['rows']if x['address']in cases];assert len(rows)==len(cases)
    lines=['#include <stddef.h>','#include <stdio.h>','#include "biwn_gpu_setup57.h"','int main(void){'];expected={}
    for kind,typ in [('state',PartialState),('bus',SetupBus)]:
        cname='struct '+stem+'_'+kind;lines.append('printf("'+kind+' size %zu\\n",sizeof('+cname+'));');expected[(kind,'size')]=c.sizeof(typ)
        for field,_ in typ._fields_:lines.append('printf("'+kind+' '+field+' %zu\\n",offsetof('+cname+','+field+'));');expected[(kind,field)]=getattr(typ,field).offset
    lines.append('return 0;}');(out/'ABI.c').write_text('\n'.join(lines)+'\n');subprocess.run(['clang','-std=c99','-Wall','-Wextra','-Werror',str(out/'ABI.c'),'-o',str(out/'ABI')],check=True,env=environment);layout=subprocess.check_output([str(out/'ABI')],text=True);(out/'ABI-layout.txt').write_text(layout);checks=[]
    for line in layout.splitlines():
        kind,field,value=line.split();assert expected[(kind,field)]==int(value);checks.append(dict(kind=kind,field=field,value=int(value)))
    report=dict(status='compiled_ABI_checked_unverified',directory=str(out),library=str(library),instructions_decoded=rows,ABI_checks=checks,source_sha256=hashlib.sha256(body.encode()).hexdigest(),parent_source_sha256=hashlib.sha256((original/(stem+'.c')).read_bytes()).hexdigest(),whole_game_complete=False,new_training=False,coordinator_authored_bridge=True,case_bodies_origin='Earlier local-model source; unchanged except outer-budget loop conversion.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/setup-bundle-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out,len(checks),len(rows))
if __name__=='__main__':main()
