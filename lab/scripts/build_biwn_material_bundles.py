"""Isolated material/consumer single-bundle candidates; accepted renderer unchanged."""
import ctypes as c,hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from biwn_material_bundle import PartialState,MaterialBus,ConsumerBus
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'verification/material-bundle-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    original=ROOT/'projects/black-ice-white-noise/restoration';session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    rows=[];ABI=['#include <stddef.h>','#include <stdio.h>'];entries=[]
    for name in ['material6720','material69a0','material6860','material65e0','material6460','consumer6380']:
        stem='biwn_gpu_'+name;body=(original/(stem+'.c')).read_text()
        repairs=[]
        if name=='consumer6380':
            old_case='case 0xf032c6:\n    if (2 == 32)'
            assert body.count(old_case)==1
            body=body.replace(old_case,'case 0xf032c6:\n    s.c=s.registers[0][3]>>31;\n    if (2 == 32)')
            repairs.append(dict(PC='0xf032c6',instruction='SHLQ2,r3',coordinator_edit='Set carry from original register sign bit before shifting; matches pinned core.'))
        assert body.count('while(budget--)')==1
        body=body.replace(stem+'_run(',stem+'_bundle_run(').replace('while(budget--){unsigned delayed=pending;','while(budget||pending){unsigned delayed=pending;if(!delayed)budget--;')
        end='return BIWN_GPU_'+name.upper()+'_WORK_LIMIT;}'
        assert body.count(end)==1;body=body.replace(end,'*state=s;return BIWN_GPU_'+name.upper()+'_OK;}')
        (out/(stem+'.c')).write_text(body);(out/(stem+'.h')).write_bytes((original/(stem+'.h')).read_bytes())
        library=out/('lib'+name+'-bundle.dylib');command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/(stem+'.c')),'-o',str(library)]
        p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/(name+'-compiler.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        code_rows=json.loads((session/('gpu-render-'+name[-4:]+'-overlay')/'initial-linear-decode.json').read_text())['rows']
        # Only exact compiled case addresses; exclude padding or unanalyzed tail.
        import re
        cases={int(x,16)for x in re.findall(r'case (0x[0-9a-fA-F]+)u?:',body)}
        code_rows=[x for x in code_rows if x['address']in cases];assert len(code_rows)==len(cases),(name,len(code_rows),len(cases))
        rows.append(dict(coordinator_repairs=repairs,name=name,library=str(library),instructions_decoded=code_rows,source_sha256=hashlib.sha256(body.encode()).hexdigest(),parent_source_sha256=hashlib.sha256((original/(stem+'.c')).read_bytes()).hexdigest()))
        ABI.append('#include "'+stem+'.h"');entries.append((name,PartialState,MaterialBus if name.startswith('material')else ConsumerBus))
    ABI.append('int main(void){');expected={}
    for name,state,bus in entries:
        for kind,typ in [('state',state),('bus',bus)]:
            cname='struct biwn_gpu_'+name+'_'+kind;ABI.append('printf("'+name+' '+kind+' size %zu\\n",sizeof('+cname+'));');expected[(name,kind,'size')]=c.sizeof(typ)
            for field,_ in typ._fields_:
                ABI.append('printf("'+name+' '+kind+' '+field+' %zu\\n",offsetof('+cname+','+field+'));');expected[(name,kind,field)]=getattr(typ,field).offset
    ABI.append('return 0;}');(out/'ABI.c').write_text('\n'.join(ABI)+'\n')
    subprocess.run(['clang','-std=c99','-Wall','-Wextra','-Werror',str(out/'ABI.c'),'-o',str(out/'ABI')],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    layout=subprocess.check_output([str(out/'ABI')],text=True);(out/'ABI-layout.txt').write_text(layout);checks=[]
    for line in layout.splitlines():
        name,kind,field,value=line.split();assert expected[(name,kind,field)]==int(value);checks.append(dict(name=name,kind=kind,field=field,value=int(value)))
    report=dict(status='compiled_ABI_checked_unverified',directory=str(out),overlays=rows,ABI_checks=checks,whole_game_complete=False,new_training=False,coordinator_authored_bridge=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/material-bundle-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out,len(checks))
if __name__=='__main__':main()
