"""13C9A source negatives: missing body, helper X, lowWORD result, delegation."""
import subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_actor_move as e

def main():
 out=e.ROOT/'verification/native-actor-move-negatives'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();proof=e.g.read(e.ROOT/'verification/native-actor-move-final-current.json');payload=Path(proof['binary']).read_bytes();symbols=proof['symbols'];reference=(e.ND/'actor-move-reference.c').read_text();cases=e.vectors();negative_view=next(c for c in cases if any(a==0x80000+192 and v==0xffff for a,w,v in c['initial']));rollback=None
 for c in cases:
  if c['returns'][str(0x13b5a)]not in [0x10000,0x80000000]:continue
  a=e.execute(snapshot,c,payload,symbols,False)
  if any(step['pc']in[0x13b5a,0x13bb0]for step in a['machine']):rollback=c;break
 assert rollback is not None
 rows=[];n=e.Native()
 try:
  badX=reference.replace('((w&0x8000u)?16u:0u)','0u');assert badX!=reference
  badroll=reference.replace('if(!(uint16_t)s.r[3])','if(!s.r[0])');assert badroll!=reference
  controls=[('no_body','#include "actor-move-native.h"\nvoid biwn_native_actor_move_body(uint32_t*r){(void)r;}\n',cases[0]),('wrong_direction_helper_X',badX,negative_view),('full_D0_instead_of_low_WORD',badroll,rollback)]
  for name,source,case in controls:
   src=out/(name+'.c');src.write_text(source);build=out/name;p=subprocess.run(['make','-f',str(e.ND/'Makefile.actor-move'),'actor-move','BUILD='+str(build),'MOVE_SOURCE='+str(src)],capture_output=True,text=True);(out/(name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
   binary=build/'actor-move.bin';elf=build/'actor-move.elf';code=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);syms={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};a=e.execute(snapshot,case,code,syms,False);b=e.execute(snapshot,case,code,syms,True);diff=[k for k in ['ram','registers','trace']if a[k]!=b[k]];detail=dict(rejected_by=diff)
   if name=='wrong_direction_helper_X':
    assert not diff;an=e.replay(n,snapshot,case,code,syms,False,a);bn=e.replay(n,snapshot,case,code,syms,True,b);assert an!=bn
    mismatch=[(i,x['target'],x['SR'],y['SR'])for i,(x,y)in enumerate(zip(an['events'],bn['events']))if x!=y];assert mismatch and all(target==0x13440 and(x^y)==16 for _,target,x,y in mismatch);assert all({k:v for k,v in x.items()if k!='SR'}=={k:v for k,v in y.items()if k!='SR'}for x,y in zip(an['events'],bn['events']));detail=dict(rejected_by='native direction helper-entry X only',differences=mismatch)
   else:assert diff
   rows.append(dict(name=name,rejected=True,case=case,source=str(src),source_sha256=e.g.sha(src),binary=str(binary),binary_sha256=e.g.sha(binary),**detail))
  code=bytearray(payload);at=symbols['biwn_native_actor_move_body']-e.BASE;code[at:at+6]=b'\x4e\xf9'+(0x13c9e).to_bytes(4,'big');p=out/'delegates_original_13c9e.bin';p.write_bytes(code)
  try:e.execute(snapshot,cases[0],bytes(code),symbols,True)
  except AssertionError as error:
   assert error.args==(('Original movement instruction reached','0x13c9e'),),error.args;rows.append(dict(name='delegate_original_root_after_entry',rejected=True,guard_PC='0x13c9e',binary=str(p),binary_sha256=e.g.sha(p)))
  else:raise AssertionError('Original delegation escaped executable address guard')
  paths=[Path(__file__),Path(e.__file__),Path(e.g.__file__),e.ND/'actor-move-reference.c',e.ND/'actor-move-native.h',e.ND/'actor-move-shim.S',e.ND/'actor-move.ld',e.ND/'Makefile.actor-move',Path(proof['binary'])];state=dict(status='terminal_native_actor_move_four_negatives_rejected',directory=str(out),controls=rows,source_sha256={str(p):e.g.sha(p)for p in paths},disc_integrated=False,new_predictions=0,scope=__doc__);e.g.save(out/'protocol.json',state);e.g.save(e.ROOT/'verification/native-actor-move-negatives-current.json',state);print(state['status'],len(rows))
 finally:n.close()
if __name__=='__main__':main()
