"""Reject four semantic defects using the actual native-direction comparison."""
import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_actor_direction_engine_v1 as e
ROOT=e.ROOT;V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 gate=read(V/'native-actor-direction-current.json');assert gate['cases']==2560
 out=V/'native-actor-direction-negatives'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=(e.ND/'actor-direction-reference-v2.c').read_text();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=e.Native();rows=[]
 defects=[('wrong_packed_word_offset','R16(s.r[15]+18u,z)','R16(s.r[15]+16u,z)',6),('lost_final_X','(s->r[16]&0xfff0u)','(s->r[16]&0xffe0u)',0),('wrong_signed_divisor','s.r[8]=sx16((uint16_t)s.r[1])','s.r[8]=(uint32_t)(uint16_t)s.r[1]',24),('wrong_table_endpoint','index<64','index<63',6)]
 try:
  for name,old,new,index in defects:
   assert source.count(old)==1,(name,source.count(old));folder=out/name;folder.mkdir();candidate=folder/'candidate.c';candidate.write_text(source.replace(old,new));run=subprocess.run(['make','-f',str(e.ND/'Makefile.actor-direction-v2'),'actor-direction','BUILD='+str(folder/'build'),'DIRECTION_SOURCE='+str(candidate)],capture_output=True,text=True);(folder/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
   binary=folder/'build/actor-direction.bin';elf=folder/'build/actor-direction.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3};case=e.vectors()[index]
   a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);diff=[k for k in ['ram','registers','trace']if a[k]!=b[k]];left=e.replay(native,snapshot,case,payload,symbols,False,a);right=e.replay(native,snapshot,case,payload,symbols,True,b)
   if left!=right:diff+=['native_CPU_SR_banks_or_helper_entry']
   assert diff,'Deliberate semantic defect was not rejected'
   row=dict(defect=name,index=index,rejected=True,differences=diff,original_native=left,candidate_native=right,source=str(candidate),binary_sha256=e.g.sha(binary));e.g.save(folder/'result.json',row);rows.append(row);print(name,diff,flush=True)
  e.g.save(out/'results.json',rows);decoded,_=e.g.direction.world.select.binary_tools.m68k_instructions(snapshot[0x13440:0x134dc],0x13440);sites={i['address']for i in decoded};covered=set(gate['original_sites']);unreachable={0x134be};assert sites-unreachable<=covered
  state=dict(status='terminal_four_native_direction_semantic_defects_rejected',directory=str(out),controls=4,original_reachable_sites=[len(sites-unreachable),len((sites-unreachable)&covered)],unreachable_control_flow_sites=[hex(x)for x in unreachable],results=str(out/'results.json'),new_predictions=0,new_training=False,scope=__doc__);e.g.save(out/'protocol.json',state);e.g.save(V/'native-actor-direction-negatives-current.json',state);print(json.dumps(state))
 finally:native.close()
if __name__=='__main__':main()
