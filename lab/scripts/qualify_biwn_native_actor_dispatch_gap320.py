"""Seeded no-body and wrong-child-X controls through actual native dispatcher gates."""
import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_native_actor_dispatch_gap320 as e

def main():
    out=e.ROOT/'verification/native-actor-dispatch-gap320-negatives'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();case=e.vectors()[0];reference=(e.ND/'actor-dispatch-gap320-reference.c').read_text();controls=[];native=e.Native()
    try:
        for name,source in [('no_body','#include "actor-dispatch-gap320-native.h"\nvoid biwn_native_actor_dispatch_body(uint32_t*r){(void)r;}\n'),('wrong_child_X',reference.replace('biwn_native_actor_dispatch_sprite_capture(r);','r[16]^=16u;biwn_native_actor_dispatch_sprite_capture(r);'))]:
            src=out/(name+'.c');src.write_text(source);build=out/name;p=subprocess.run(['make','-f',str(e.ND/'Makefile.actor-dispatch-gap320'),'actor-dispatch','BUILD='+str(build),'DISPATCH_SOURCE='+str(src)],capture_output=True,text=True);(out/(name+'.log')).write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
            binary=build/'actor-dispatch.bin';elf=build/'actor-dispatch.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
            a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True)
            differences=[k for k in ['ram','registers','trace']if a[k]!=b[k]]
            if name=='no_body':assert differences;detail=dict(rejected_by=differences)
            else:
                assert not differences,'The X control should specifically reach the native SR check'
                an=e.replay(native,snapshot,case,payload,symbols,False,a);bn=e.replay(native,snapshot,case,payload,symbols,True,b)
                assert an!=bn;diff=[(i,x['SR'],y['SR'])for i,(x,y)in enumerate(zip(an['events'],bn['events']))if x!=y]
                assert diff and all(x['target']==y['target']and x['registers']==y['registers']and x['SP']==y['SP']and x['args']==y['args']for x,y in zip(an['events'],bn['events']))
                assert all((sr1^sr2)==16 for _,sr1,sr2 in diff);detail=dict(rejected_by='native child-entry SR/X',child_event_SR_differences=diff)
            controls.append(dict(name=name,rejected=True,source=str(src),source_sha256=e.g.sha(src),binary=str(binary),binary_sha256=e.g.sha(binary),**detail))
        inputs=[Path(__file__),Path(e.__file__),e.ND/'actor-dispatch-gap320-reference.c',e.ND/'actor-dispatch-gap320-native.h',e.ND/'actor-dispatch-gap320-shim.S',e.ND/'actor-dispatch.ld',e.ND/'Makefile.actor-dispatch-gap320']
        state=dict(status='terminal_native_actor_dispatch_noop_and_wrong_X_rejected',directory=str(out),controls=controls,source_sha256={str(p):e.g.sha(p)for p in inputs},scope=__doc__,disc_integrated=False,new_predictions=0)
        e.g.save(out/'protocol.json',state);e.g.save(e.ROOT/'verification/native-actor-dispatch-gap320-negatives-current.json',state);print(json.dumps(state,indent=2))
    finally:native.close()

if __name__=='__main__':main()
