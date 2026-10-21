"""Reject source-level missing body/wrong callback, helper-X and original delegation."""
import subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_sprite_create as e

def main():
 out=e.ROOT/'verification/native-sprite-create-negatives'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();cases=e.vectors();reference=(e.ND/'sprite-create-reference.c').read_text();n=e.Native();rows=[]
 try:
  callback_case=next(c for c in cases if c['params'][0]==104 and any(a==0x4208c+104 and value==2 for a,w,value in c['initial']) and any(0x4bd9c<=a<0x4bd9c+40*30 and value==0 for a,w,value in c['initial']))
  for name,source,case in [('no_body','#include "sprite-create-native.h"\nvoid biwn_native_sprite_create_body(uint32_t*r){(void)r;}\n',cases[0]),('wrong_helper_X',reference.replace('biwn_native_sprite_create_position_capture(r);','r[16]^=16u;biwn_native_sprite_create_position_capture(r);'),cases[0]),('wrong_callback',reference.replace('callback=0x8f54u','callback=0x8f56u'),callback_case)]:
   src=out/(name+'.c');src.write_text(source);build=out/name;p=subprocess.run(['make','-f',str(e.ND/'Makefile.sprite-create'),'sprite-create','BUILD='+str(build),'SPRITE_SOURCE='+str(src)],capture_output=True,text=True);(out/(name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
   binary=build/'sprite-create.bin';elf=build/'sprite-create.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
   a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);diffs=[k for k in ['ram','registers','trace']if a[k]!=b[k]]
   detail=dict(rejected_by=diffs)
   if name=='wrong_helper_X':
    assert not diffs;an=e.replay(n,snapshot,case,payload,symbols,False,a);bn=e.replay(n,snapshot,case,payload,symbols,True,b);assert an!=bn
    mismatches=[(i,x['SR'],y['SR'])for i,(x,y)in enumerate(zip(an['events'],bn['events']))if x!=y];assert mismatches and all((x^y)==16 for _,x,y in mismatches)
    assert all({k:v for k,v in x.items()if k!='SR'}=={k:v for k,v in y.items()if k!='SR'}for x,y in zip(an['events'],bn['events']));detail=dict(rejected_by='native helper-entry SR/X',helper_SR_differences=mismatches)
   else:assert diffs
   rows.append(dict(name=name,rejected=True,source=str(src),source_sha256=e.g.sha(src),binary=str(binary),binary_sha256=e.g.sha(binary),**detail))
  proof=e.g.read(e.ROOT/'verification/native-sprite-create-final-current.json');payload=bytearray(Path(proof['binary']).read_bytes());symbols=proof['symbols'];at=symbols['biwn_native_sprite_create_body']-e.BASE;payload[at:at+6]=b'\x4e\xf9'+(0x137e4).to_bytes(4,'big');p=out/'delegates_original_137e4.bin';p.write_bytes(payload)
  try:e.execute(snapshot,cases[0],bytes(payload),symbols,True)
  except AssertionError as error:
   assert error.args==(('Original sprite factory instruction reached','0x137e4'),),error.args;rows.append(dict(name='delegate_original_root_after_entry',rejected=True,guard_PC='0x137e4',binary=str(p),binary_sha256=e.g.sha(p)))
  else:raise AssertionError('Original-root delegation escaped address guard')
  paths=[Path(__file__),Path(e.__file__),e.ND/'sprite-create-reference.c',e.ND/'sprite-create-native.h',e.ND/'sprite-create-shim.S',e.ND/'sprite-create.ld',e.ND/'Makefile.sprite-create',Path(proof['binary'])]
  state=dict(status='terminal_native_sprite_create_four_negatives_rejected',directory=str(out),controls=rows,source_sha256={str(p):e.g.sha(p)for p in paths},scope=__doc__,new_predictions=0,disc_integrated=False);e.g.save(out/'protocol.json',state);e.g.save(e.ROOT/'verification/native-sprite-create-negatives-current.json',state);print(state['status'],len(rows))
 finally:n.close()
if __name__=='__main__':main()
