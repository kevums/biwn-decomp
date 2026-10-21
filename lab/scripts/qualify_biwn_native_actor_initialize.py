"""Target-binary no-body, helper-X and original-root-delegation negatives."""
import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_actor_initialize as e

def main():
 out=e.ROOT/'verification/native-actor-initialize-negatives'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();case=e.vectors()[0];reference=(e.ND/'actor-initialize-reference.c').read_text();native=e.Native();controls=[]
 try:
  for name,source in [('no_body','#include "actor-initialize-native.h"\nvoid biwn_native_actor_initialize_body(uint32_t*r){(void)r;}\n'),('wrong_helper_X',reference.replace('biwn_native_actor_initialize_outside_capture(r);','r[16]^=16u;biwn_native_actor_initialize_outside_capture(r);'))]:
   src=out/(name+'.c');src.write_text(source);build=out/name;p=subprocess.run(['make','-f',str(e.ND/'Makefile.actor-initialize'),'actor-initialize','BUILD='+str(build),'INITIALIZE_SOURCE='+str(src)],capture_output=True,text=True);(out/(name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
   binary=build/'actor-initialize.bin';elf=build/'actor-initialize.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
   left=e.execute(snapshot,case,payload,symbols,False);right=e.execute(snapshot,case,payload,symbols,True);differences=[k for k in ['ram','registers','trace']if left[k]!=right[k]]
   if name=='no_body':assert differences;detail=dict(rejected_by=differences)
   else:
    assert not differences,'X control must reach native SR comparison'
    a=e.replay(native,snapshot,case,payload,symbols,False,left);b=e.replay(native,snapshot,case,payload,symbols,True,right);assert a!=b
    diff=[(i,x['SR'],y['SR'])for i,(x,y)in enumerate(zip(a['events'],b['events']))if x!=y]
    assert diff and all((x^y)==16 for _,x,y in diff)
    assert all({k:v for k,v in x.items()if k!='SR'}=={k:v for k,v in y.items()if k!='SR'}for x,y in zip(a['events'],b['events']))
    detail=dict(rejected_by='Native original-helper input SR/X',helper_SR_differences=diff)
   controls.append(dict(name=name,rejected=True,binary=str(binary),binary_sha256=e.g.sha(binary),source=str(src),source_sha256=e.g.sha(src),**detail))
  proof=e.g.read(e.ROOT/'verification/native-actor-initialize-current.json');payload=bytearray(Path(proof['binary']).read_bytes());symbols=proof['symbols'];at=symbols['biwn_native_actor_initialize_body']-e.BASE;payload[at:at+6]=b'\x4e\xf9'+(0x134e0).to_bytes(4,'big');mutated=out/'delegates_original_134e0.bin';mutated.write_bytes(payload)
  try:e.execute(snapshot,case,bytes(payload),symbols,True)
  except AssertionError as error:
   assert error.args==(('Original initializer instruction reached','0x134e0'),),error.args
   controls.append(dict(name='delegate_original_root_body_after_entry',rejected=True,guard_PC='0x134e0',binary=str(mutated),binary_sha256=e.g.sha(mutated)))
  else:raise AssertionError('Original root delegation escaped executable-address guard')
  paths=[Path(__file__),Path(e.__file__),e.ND/'actor-initialize-reference.c',e.ND/'actor-initialize-native.h',e.ND/'actor-initialize-shim.S',e.ND/'actor-initialize.ld',e.ND/'Makefile.actor-initialize',Path(proof['binary'])]
  state=dict(status='terminal_native_actor_initialize_three_negatives_rejected',directory=str(out),controls=controls,source_sha256={str(p):e.g.sha(p)for p in paths},scope=__doc__,new_predictions=0,disc_integrated=False)
  e.g.save(out/'protocol.json',state);e.g.save(e.ROOT/'verification/native-actor-initialize-negatives-current.json',state);print(json.dumps(dict(status=state['status'],controls=[x['name']for x in controls])))
 finally:native.close()

if __name__=='__main__':main()
