"""A shallower initializer frame passes alone but corrupts a native caller frame."""
import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_actor_initialize as single
import check_biwn_native_actor_dispatch_initialize_joint as joint

def main():
 out=joint.ROOT/'verification/joint-actor-frame-overlap-negative'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 shim=out/'actor-initialize-small-gap-shim.S';shim.write_text((single.ND/'actor-initialize-shim.S').read_text().replace('INIT_PRIVATE_RESERVE,448','INIT_PRIVATE_RESERVE,320'))
 make=out/'Makefile.negative';text=(single.ND/'Makefile.actor-initialize').read_text();text=text.replace('ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../../../..)','ROOT := '+str(joint.ROOT));text=text.replace('SOURCE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))','SOURCE_DIR := '+str(single.ND)+'/');text=text.replace('"$(SOURCE_DIR)/actor-initialize-shim.S"','"'+str(shim)+'"');make.write_text(text)
 build=out/'build';p=subprocess.run(['make','-f',str(make),'actor-initialize','BUILD='+str(build)],capture_output=True,text=True);(out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 binary=build/'actor-initialize.bin';elf=build/'actor-initialize.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(joint.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};snapshot=(joint.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=single.Native();isolated=0
 try:
  for case in single.vectors()[:16]:
   a=single.execute(snapshot,case,payload,symbols,False);b=single.execute(snapshot,case,payload,symbols,True);assert all(a[k]==b[k]for k in ['ram','registers','trace']);an=single.replay(native,snapshot,case,payload,symbols,False,a);bn=single.replay(native,snapshot,case,payload,symbols,True,b);assert an==bn;isolated+=1
 finally:native.close()
 proof=joint.g.read(joint.ROOT/'verification/native-actor-dispatch-initialize-joint-current.json');dispatch=Path(proof['binary']).read_bytes();dispatch_symbols=proof['symbols'];joint.INIT_PAYLOAD=payload;joint.INIT_SYMBOLS=symbols;case=next(c for c in joint.vectors()if c['params'][0]==0 and any(a==0x4208c and v==1 for a,w,v in c['initial']))
 left=joint.execute(snapshot,case,dispatch,dispatch_symbols,False)
 try:
  right=joint.execute(snapshot,case,dispatch,dispatch_symbols,True)
  assert any(left[k]!=right[k]for k in ['ram','registers','trace']),'Bad composed frame unexpectedly matched'
  evidence=dict(rejected_by='Original/C joint state mismatch')
 except Exception as error:
  evidence=dict(rejected_by=type(error).__name__,error=str(error))
 # Original child-entrySP=rootSP-36; child prologue32+gap320; context76bytes.
 # Its[SP-388,SP-312) overwrites caller capture returnPC[SP-344,SP-340).
 state=dict(status='terminal_isolated_valid_small_gap_rejected_when_nested',directory=str(out),isolated_native_cases_passed=isolated,joint_rejected=True,child_context_relative_interval=[-388,-312],caller_capture_return_PC_interval=[-344,-340],known_overlap=True,negative_shim=str(shim),binary=str(binary),binary_sha256=joint.g.sha(binary),evidence=evidence,source_sha256={str(p):joint.g.sha(p)for p in [Path(__file__),Path(single.__file__),Path(joint.__file__),single.ND/'actor-initialize-shim.S',single.ND/'actor-initialize-reference.c',single.ND/'actor-initialize-native.h',make,shim,elf]},scope=__doc__,disc_integrated=False,new_predictions=0)
 joint.g.save(out/'protocol.json',state);joint.g.save(joint.ROOT/'verification/joint-actor-frame-overlap-negative-current.json',state);print(json.dumps({k:state[k]for k in ['status','isolated_native_cases_passed','evidence']}))

if __name__=='__main__':main()
