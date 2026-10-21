"""Compare original,optimized coordinator and coordinator cast-profile CPU work.
Pinned emulator instruction costs,not host wall time or physical-console timing.
GPU submission is the same declared fixture;formatter/text execute original CPU.
"""
import hashlib,importlib.util,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 out=V/'native-clear-casts-cost-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=[];paths=[Path(__file__)];baseline={}
 for label,gatefile,script,clearname in [('optimized','native-Deck-debug-real-v1-current.json','check_native_deck_debug_real_v1.py','native_clear_records'),('casts','native-Deck-clear-casts-v1-current.json','check_native_deck_clear_casts_v1.py','native_clear_records')]:
  gp=V/gatefile;g=read(gp);assert g['completed']==256
  for p,h in g['source_sha256'].items():assert sha(p)==h,p
  script=ROOT/'scripts'/script;m=load('clear_cost_'+label,script);payload=Path(g['payload']).read_bytes();syms=g['symbols'];clear=next(a for n,a in syms.items()if n.startswith(clearname));e=m.Engine();e.real_dependencies=True;e.debug_out=out;execute=e.core.m68k_execute
  try:
   for ram,initial,case in m.connected.fixtures():
    i=case['variant']
    if i not in [0,1,3,12]:continue
    memory=bytearray(ram);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=bytes([0xa5])*(m.SLOTS*m.STRIDE)
    for slot in range(m.SLOTS):
     for _,off,_,_ in m.shared.LAYOUT.values():memory[m.ARENA+slot*m.STRIDE+off+114:m.ARENA+slot*m.STRIDE+off+118]=bytes(4)
    task=m.POOL+(i%m.SLOTS)*m.STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3];memory[0xc0920:0xc0924]=task.to_bytes(4,'big');memory[sp-256:sp+32]=memory[m.connected.h.SP-256:m.connected.h.SP+32];initial=m.CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
    if initial.sr&0x2000:initial.ssp=sp
    else:initial.usp=sp
    memory[0x403cc:0x403ce]=bytes(2);case=dict(case,mutate_globals=False);ram=bytes(memory);costs={}
    for lane in ['original','compiled']:
     active=False;entry_sp=None;ret=None;counters=dict(instructions=0,cycles=0,clear_instructions=0,clear_cycles=0,clear_C_stack_low=None)
     def counted(cycles):
      nonlocal active,entry_sp,ret
      pc=e.core.m68k_get_reg(None,16);at=e.core.m68k_get_reg(None,15)
      if pc==(0x10968 if lane=='original'else clear):
       assert not active;active=True;entry_sp=at;ret=e.native.device.read(at,4)
      if active and pc==ret and at==entry_sp+4:active=False
      if active and lane=='compiled':counters['clear_C_stack_low']=at-task+m.POOL-m.ARENA if counters['clear_C_stack_low']is None else min(counters['clear_C_stack_low'],at-task+m.POOL-m.ARENA)
      used=execute(cycles);counters['instructions']+=1;counters['cycles']+=used
      if active:counters['clear_instructions']+=1;counters['clear_cycles']+=used
      return used
     e.core.m68k_execute=counted
     if lane=='original':expected,cpu,entries,_,_,hardware=e.original(ram,initial,case)
     else:
      actual,got,observed,details=e.compiled(ram,initial,case,syms,payload,entries);assert expected==actual and m.cpu_dict(cpu)==m.cpu_dict(got)and entries==observed and hardware==e.native.device.registers()
     e.core.m68k_execute=execute;assert not active and counters['clear_cycles']>0;costs[lane]=counters
    if i in baseline:assert baseline[i]==costs['original'],'Original timing changed across payload seeds'
    else:baseline[i]=costs['original']
    rows.append(dict(variant=i,body=label,descriptor_faces=[0,1,2,3,6][(i//3)%5],costs=costs,CPU_RAM_entries_blitter_match=True));print(label,i,costs['compiled']['clear_cycles'],flush=True)
  finally:e.core.m68k_execute=execute;e.native.close()
  paths.extend([gp,script,Path(g['payload'])])
 comparisons=[]
 for i in [0,1,3,12]:
  old=next(x for x in rows if x['variant']==i and x['body']=='optimized');new=next(x for x in rows if x['variant']==i and x['body']=='casts');a=old['costs']['compiled'];b=new['costs']['compiled'];comparisons.append(dict(variant=i,faces=new['descriptor_faces'],original_clear_cycles=new['costs']['original']['clear_cycles'],optimized_clear_cycles=a['clear_cycles'],casts_clear_cycles=b['clear_cycles'],casts_vs_previous_clear_ratio=round(b['clear_cycles']/a['clear_cycles'],4),optimized_geometry_cycles=a['cycles'],casts_geometry_cycles=b['cycles'],casts_vs_previous_geometry_ratio=round(b['cycles']/a['cycles'],4)))
 save(out/'cases.json',rows);save(out/'comparisons.json',comparisons);paths.extend([out/'cases.json',out/'comparisons.json']);proof=dict(status='terminal_native_clear_casts_CPU_cost_samples_measured',directory=str(out),completed=len(rows),comparisons=comparisons,new_predictions=0,new_training=False,native_disc_changed=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Four fixedgeometrycases,includingbothstackbanks and0/1/6faces. Leaf costs include ownC/originalRTS butexclude callerJSR;wholegeometry includes bridges. Active debug isdisabled only for thesecostsamples;thefull256casecomponent gate separatelytests all4flag groups. No physicaltiming,freshgameplay orfidelityclaim.');save(out/'review.json',proof);save(V/'native-clear-casts-cost-v1-current.json',proof);print(json.dumps(comparisons,indent=2))
if __name__=='__main__':main()
