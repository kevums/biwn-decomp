"""Compare compiled header layouts with ctypes; refuses shifted GPU local RAM."""
import ctypes as c,json,os,subprocess
from pathlib import Path
from biwn_renderer_bundle import State,GeometryState,Bus,OverlayBus
ROOT=Path(__file__).resolve().parents[1]
def main():
    candidate=json.loads((ROOT/'verification/renderer-bundle-candidate.json').read_text());folder=Path(candidate['directory'])
    rows=[];lines=['#include <stddef.h>','#include <stdio.h>']
    entries=[('resident',State,Bus),('geometry',GeometryState,OverlayBus),('projection',State,OverlayBus)]
    for name,_,_ in entries:lines.append('#include "biwn_gpu_'+name+'.h"')
    lines.append('int main(void){')
    for name,state,bus in entries:
        for kind,typ in [('state',state),('bus',bus)]:
            cname='struct biwn_gpu_'+name+'_'+kind
            lines.append('printf("'+name+' '+kind+' size %zu\\n",sizeof('+cname+'));')
            for field,_ in typ._fields_:lines.append('printf("'+name+' '+kind+' '+field+' %zu\\n",offsetof('+cname+','+field+'));')
    lines.append('return 0;}');source=folder/'ABI.c';source.write_text('\n'.join(lines)+'\n');exe=folder/'ABI'
    subprocess.run(['clang','-std=c99','-Wall','-Wextra','-Werror',str(source),'-o',str(exe)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    output=subprocess.check_output([str(exe)],text=True);(folder/'ABI-layout.txt').write_text(output)
    expected={(name,kind,field):getattr(typ,field).offset for name,state,bus in entries for kind,typ in [('state',state),('bus',bus)]for field,_ in typ._fields_}
    expected.update({(name,kind,'size'):c.sizeof(typ)for name,state,bus in entries for kind,typ in [('state',state),('bus',bus)]})
    for line in output.splitlines():
        name,kind,field,value=line.split();assert int(value)==expected[(name,kind,field)],line;rows.append(dict(name=name,kind=kind,field=field,offset_or_size=int(value)))
    report=dict(status='compiled_headers_match_ctypes',checks=len(rows),directory=str(folder),rows=rows)
    (ROOT/'verification/renderer-bundle-ABI-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['checks'])
if __name__=='__main__':main()
