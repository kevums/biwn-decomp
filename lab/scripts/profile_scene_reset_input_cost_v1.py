"""Pinned-emulator work samples for exact final-image input/reset dispatch.
Other input helpers remain declared effects. No physical or full-game timing.
"""
import importlib.util,json,struct
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
def main():
 gate=V/'native-deck-retained-scene-reset-final-v1-current.json';g=read(gate)
 for p,h in g['source_sha256'].items():assert sha(p)==h,p
 script=next(Path(p)for p in g['source_sha256']if Path(p).name=='retained.py')
 spec=importlib.util.spec_from_file_location('reset_input_cost_checked',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 payload=Path(g['payload']).read_bytes();assert sha(g['payload'])==g['payload_sha256'];syms=g['symbols'];m.configure('input');fixtures=m.fixtures('input');engine=m.Engine('input');execute=engine.core.m68k_execute
 out=V/'scene-reset-input-cost-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=[]
 try:
  for i in [0,32,128,160,256,288,384,416]:
   ram,initial,case=fixtures[i];memory=bytearray(ram);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=bytes([0xa5])*(m.SLOTS*m.STRIDE)
   for slot in range(m.SLOTS):
    for _,offset,_,_ in m.LAYOUT.values():memory[m.ARENA+slot*m.STRIDE+offset+114:m.ARENA+slot*m.STRIDE+offset+118]=bytes(4)
   task=m.POOL+(i%m.SLOTS)*m.STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3];memory[0xc0920:0xc0924]=task.to_bytes(4,'big');memory[sp-256:sp+32]=memory[m.SP-256:m.SP+32];initial=m.CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
   if initial.sr&0x2000:initial.ssp=sp
   else:initial.usp=sp
   ram=bytes(memory);case=dict(case,payload=payload);costs={}
   for lane in ['original','compiled']:
    active=False;endpc=None;endsp=None;counters=dict(instructions=0,cycles=0,reset_entries=0,reset_instructions=0,reset_cycles=0)
    def counted(cycles):
     nonlocal active,endpc,endsp
     assert cycles==1
     pc=engine.core.m68k_get_reg(None,16);sp=engine.core.m68k_get_reg(None,15)
     start=pc==0x1102a if lane=='original'else pc==syms['dispatch']and engine.native.device.read(sp+12,4)==0x1102a
     if start:
      assert not active;active=True;counters['reset_entries']+=1;endpc=0x110d2 if lane=='original'else engine.native.device.read(sp,4);endsp=None if lane=='original'else sp+4
     was_active=active;used=execute(cycles);counters['instructions']+=1;counters['cycles']+=used
     if was_active:
      counters['reset_instructions']+=1;counters['reset_cycles']+=used
      if engine.core.m68k_get_reg(None,16)==endpc and(endsp is None or engine.core.m68k_get_reg(None,15)==endsp):active=False
     return used
    engine.core.m68k_execute=counted
    if lane=='original':expected,cpu,entries,*_=engine.reference(ram,initial,case)
    else:
     actual,got,observed,details=engine.compiled(ram,initial,case,syms,entries);assert expected==actual and m.cpu_dict(cpu)==m.cpu_dict(got)and entries==observed
    engine.core.m68k_execute=execute;assert not active;costs[lane]=counters
   assert costs['original']['reset_entries']==costs['compiled']['reset_entries']==(1 if i in [128,160,384,416]else 0)
   ratio=round(costs['compiled']['reset_cycles']/costs['original']['reset_cycles'],4)if costs['original']['reset_cycles']else None
   row=dict(variant=i,supervisor=bool(initial.sr&0x2000),costs=costs,compiled_dispatch_vs_original_body_ratio=ratio,CPU_nonarena_RAM_helper_entries_match=True);rows.append(row);print(i,costs['original']['reset_cycles'],costs['compiled']['reset_cycles'],ratio,flush=True)
 finally:engine.core.m68k_execute=execute;engine.native.close()
 save(out/'cases.json',rows);paths=[Path(__file__),gate,script,Path(g['payload']),out/'cases.json']
 proof=dict(status='terminal_exact_final_input_reset_cost_samples',directory=str(out),completed=len(rows),reset_pairs=4,no_reset_pairs=4,ratios=[x['compiled_dispatch_vs_original_body_ratio']for x in rows if x['compiled_dispatch_vs_original_body_ratio']is not None],new_game_execution=False,new_predictions=0,new_training=False,disc_changed=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Eight retained input cases;four real reset andfour nonreset,bothstackbanks,exact deployed40402byte code. Counts sum actual m68k_execute(1) costs. Original reset body excludes its RTS;compiled reset service includes dispatcher guard,marker andCreturn. Ratio includes bridge/service overhead and is not an isolated Cbody or full-game cost. Wholeinput samples omit emulated costs of declared poll/record/texture effects. No inference,IRQ orphysical-console timing claim.')
 save(out/'review.json',proof);save(V/'scene-reset-input-cost-v1-current.json',proof);print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
