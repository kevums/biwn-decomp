"""Actual CPU data-bus order over input globals/descriptors;helpers declared.
Guest/private stacks and instruction fetches are outside watched ranges.
Recorder lacks width; CPU semantic gates and decoded operations cover widths.
"""
import ctypes as c,importlib.util,json,os
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from check_native_scene_reset_core_bus_v1 import Event
def main():
 out=V/'scene17-clear-input-public-bus-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='checking',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False)
 def mark():save(out/'review.json',state);save(V/'scene17-clear-input-public-bus-v1-current.json',state)
 mark();script=ROOT/'scripts/check_native_deck_retained_scene17_clear_v1.py';spec=importlib.util.spec_from_file_location('input_bus_prototype',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.configure('input')
 # Use an already completed preflight build; no build/checker is modified.
 gp=V/'native-deck-retained-scene17-clear-v1-current.json';g=read(gp);assert g['completed']==4992
 for p,h in g['source_sha256'].items():assert sha(p)==h,p
 payload=Path(g['payload']).read_bytes();assert sha(g['payload'])==g['payload_sha256'];syms=g['symbols'];engine=m.Engine('input');core=engine.core;rows=[]
 core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
 def arm():
  core.vjtrace_disarm();core.vjtrace_watch_clear()
  for low,high in [(0x40000,0x4ffff),(0x80000,0x900ff)]:assert core.vjtrace_watch_add(low,high,3)>=0
  start=core.vjtrace_ring_head();core.vjtrace_arm();return start
 def collect(start):
  core.vjtrace_disarm();end=core.vjtrace_ring_head();events=[]
  for i in range(start,end):
   e=Event();assert core.vjtrace_ring_read(i,c.byref(e))
   if e.type in [11,12]:events.append(dict(kind='r'if e.type==11 else'w',address=e.addr,value=e.value,PC=hex(e.pc)))
  return events
 try:
  for i,(ram,initial,case)in enumerate(m.fixtures('input')):
   if i not in [0,32,128,160,256,288,384,416,511,767,1023,1535,2047]:continue
   memory=bytearray(ram);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=bytes([0xa5])*(m.SLOTS*m.STRIDE)
   for slot in range(m.SLOTS):
    for _,off,_,_ in m.LAYOUT.values():memory[m.ARENA+slot*m.STRIDE+off+114:m.ARENA+slot*m.STRIDE+off+118]=bytes(4)
   task=m.POOL+(i%m.SLOTS)*m.STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3];memory[0xc0920:0xc0924]=task.to_bytes(4,'big');memory[sp-256:sp+32]=memory[m.SP-256:m.SP+32];initial=m.CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
   if initial.sr&0x2000:initial.ssp=sp
   else:initial.usp=sp
   ram=bytes(memory);case=dict(case,payload=payload);start=arm();expected,cpu,entries,*_=engine.reference(ram,initial,case);original=collect(start);start=arm();actual,got,observed,details=engine.compiled(ram,initial,case,syms,entries);compiled=collect(start)
   assert expected==actual and m.cpu_dict(cpu)==m.cpu_dict(got)and entries==observed
   normal=lambda seq:[(x['kind'],x['address'],x['value'])for x in seq]
   save(out/f'case-{i}.json',dict(original=original,compiled=compiled))
   if normal(original)!=normal(compiled):
    save(out/'mismatch.json',dict(case=i,original_events=len(original),compiled_events=len(compiled),first_mismatch=next((n for n,(a,b)in enumerate(zip(normal(original),normal(compiled)))if a!=b),min(len(original),len(compiled)))));raise AssertionError(('public bus order',i,len(original),len(compiled)))
   rows.append(dict(case=i,events=len(original),CPU_RAM_helper_entries_and_order_match=True));state['completed']=len(rows);mark()
  assert len(rows)==13
 except BaseException as error:state.update(status='terminal_public_input_bus_order_failed',error=repr(error));mark();raise
 finally:core.vjtrace_disarm();engine.native.close()
 paths=[Path(__file__),script,gp,Path(g['payload']),*out.glob('case-*.json')];state.update(status='terminal_13_actual_input_public_bus_orders_match',cases=rows,payload_sha256=g['payload_sha256'],source_sha256={str(p):sha(p)for p in paths},scope=__doc__+'Read hook records0ratherthan operand data;onlyreadaddress/orderandwritevaluesarecompared.13selected input cases including reset/nonreset,bothbanks and face selections. Actual original reset in reference;compiled reset in native. Public record/poll/texture helpers remain declared effects. No trace RAM/CPUmutation,IRQ,physical console or fresh-gameplay proof.');mark();print(state['status'],flush=True)
if __name__=='__main__':main()
