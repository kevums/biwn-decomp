"""Actual scene-to-scene busy-fallback nesting through an injected helper JSR.
The nested original caller sees mode zero. Explicit component fixture, not a
natural game call, arbitrary reentry or IRQ proof. Original clear/rotation run;
other services and mode/completion reads retain declared fixtures.
"""
import os
from datetime import datetime,timezone
from pathlib import Path
import check_scene17_wait_bridge_v1 as b
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
base=b.base

def main():
 gate=read(V/'scene17-wait-bridge-v1-current.json')
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 payload=Path(gate['payload']).read_bytes();syms=gate['symbols'];out=V/'scene17-wait-reentry-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='checking',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,game_image_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();runtime=b.support.Runtime(V/'scene17-structured-host-v1/20261020T230553.352177Z/libscene-draw-cpu.dylib',mapping['instructions_decoded']);core=runtime.core;rows=[]
 def seed(s):base.lifecycle.seed_cpu(runtime,s)
 def run(ram,case,slot,native):
  runtime.reset(ram,case,0)
  for target in base.queue.SCRIPTS:runtime.device.direct(target,2,0x4e75)
  for off,val in enumerate(b'\x4e\xb9\x00\x01\x7e\x0e\x4e\x75'):runtime.device.direct(0xe0a6+off,1,val)
  if native:
   for off,val in enumerate(b'\x4e\xf9'+syms['biwn_v4_scene'].to_bytes(4,'big')+b'\x4e\x71'*2):runtime.device.direct(0x17e0e+off,1,val)
  seed(base.queue.make_cpu(case));injected=False;inner=False;protected=None;stack=[];entries=fallbacks=returns=0
  for step in range(20000):
   current=runtime.cpu();pc=current.pc
   if pc==base.STOP:break
   if native:
    entries+=pc==syms['biwn_v4_scene'];fallbacks+=pc==syms['biwn_v4_scene_original_fallback'];returns+=pc==syms['biwn_v4_scene_return']
   if pc==0xe0a6:
    assert not injected;injected=True;inner=True;runtime.device.direct(0x49c60,2,0)
    memory=runtime.device.ram();protected=(memory[slot+144:slot+262],memory[slot+608:slot+816]);core.m68k_execute(1);continue
   if pc==0xe0ac:
    assert inner;inner=False;memory=runtime.device.ram()
    if native:assert protected==(memory[slot+144:slot+262],memory[slot+608:slot+816]),'suspended context/stack changed'
    runtime.device.direct(0x49c60,2,1);current.pc=0xe0a6;runtime.scripted(current,0xe0a6);current.pc=0xe0ac;seed(current);core.m68k_execute(1);continue
   if native and pc in [syms['r16'],syms['r32']]:runtime.inject(runtime.device.read(current.registers[15]+8,4),2 if pc==syms['r16']else 4)
   if pc in base.queue.SCRIPTS:
    runtime.scripted(current,pc)
    for r in [0,1,8,9]:core.m68k_set_reg(r,current.registers[r])
    core.m68k_set_reg(17,current.sr)
   elif pc in runtime.rows:
    if pc in base.queue.ENTRIES:
     row=dict(target=pc,actual_body=True,incoming=base.cd.scheduler.cpu_dict(current));runtime.calls.append(row);stack.append(row)
    if pc in base.queue.RETURNS and stack:stack.pop()['return']=base.cd.scheduler.cpu_dict(current)
    if not inner and pc in [0x17e18,0x17e34,0x17e6e,0x17ef8]:runtime.inject(0x49c60,2)
    if pc in [0x17e5c,0x17ed6]:runtime.inject(0x10a684,4)
   else:assert native and b.CODE<=pc<b.CODE+len(payload),hex(pc)
   core.m68k_execute(1)
   if pc==0xe03e:
    q=runtime.queues.get((0xf02238,4))
    if q:core.m68k_set_reg(0,q.pop(0))
  else:raise AssertionError('nested scene bound')
  assert injected and not inner and not stack
  memory=bytearray(runtime.device.ram());arena=bytes(memory[b.ARENA:b.ARENA+101*1024])
  if native:assert (entries,fallbacks,returns)==(2,1,1),(entries,fallbacks,returns)
  memory[b.ARENA:b.ARENA+101*1024]=ram[b.ARENA:b.ARENA+101*1024]
  for target in base.queue.SCRIPTS:memory[target:target+2]=ram[target:target+2]
  memory[0xe0a6:0xe0ae]=ram[0xe0a6:0xe0ae];memory[0x17e0e:0x17e18]=ram[0x17e0e:0x17e18]
  return bytes(memory),runtime.cpu(),list(runtime.calls),dict(instructions=step,entries=entries,fallbacks=fallbacks,native_returns=returns,arena=arena)
 try:
  template=base.cases()[257]
  assert template['initial'][0]or template
  for i in range(64):
   task=b.POOL+[0,1,6,100][i%4]*1024;slot=b.ARENA+task-b.POOL;sp=task+[0x3c0,0x3be,0x200][i%3]
   case=dict(template,body=False,SR=(0x2000 if i>=32 else 0)|(i%32));case['registers']=list(template['registers']);case['registers'][15]=sp;case['usp']=0x170000 if i>=32 else sp;case['ssp']=sp if i>=32 else 0x1d0000
   memory=bytearray(base.fixture(snapshot,case));memory[sp-256:sp+32]=memory[base.SP-256:base.SP+32];memory[b.CODE:b.CODE+len(payload)]=payload;memory[b.ARENA:b.ARENA+101*1024]=bytes([0xa5])*(101*1024)
   for n in range(101):
    for offset in [16,144,272]:memory[b.ARENA+n*1024+offset+114:b.ARENA+n*1024+offset+118]=bytes(4)
   memory[0xc0920:0xc0924]=task.to_bytes(4,'big');ram=bytes(memory)
   expected,cpu,calls,_=run(ram,case,slot,False);actual,got,observed,details=run(ram,case,slot,True)
   if expected!=actual or bytes(cpu)!=bytes(got)or calls!=observed:
    save(out/'counterexample.json',dict(case=i,original_CPU=base.cd.scheduler.cpu_dict(cpu),native_CPU=base.cd.scheduler.cpu_dict(got),RAM_differences=[hex(a)for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32],original_calls=calls,native_calls=observed));raise AssertionError(out/'counterexample.json')
   arena=details.pop('arena');old=ram[b.ARENA:b.ARENA+101*1024];relative=slot-b.ARENA;allowed=set(range(relative+144,relative+262))|set(range(relative+608,relative+816));assert all(j in allowed or u==old[j]for j,u in enumerate(arena))
   assert arena[relative+258:relative+262]==bytes(4)
   rows.append(dict(case=i,CCR=i%32,supervisor=i>=32,task=hex(task),guest_SP=hex(sp),suspended_context_and_C_stack_preserved=True,full_CPU_nonarena_RAM_helpers_match=True,**details));state['completed']=len(rows);mark()
   if len(rows)%16==0:print('nested scene',len(rows),flush=True)
 finally:runtime.close()
 save(out/'cases.json',rows);state.update(status='terminal_scene17_actual_JSR_busy_fallback_nested_match',completed=len(rows),source_sha256={str(p):sha(p)for p in [Path(__file__),Path(b.__file__),V/'scene17-wait-bridge-v1-current.json',Path(gate['payload']),out/'cases.json']},scope=__doc__+'64cases coverallCCR/bothbanks,4taskslots and3guestSPdepths. Exactly2native rootentries,1originalbusyfallback and1native outerreturn;118bytecontextand208byteCstack protected while inner executes. Onlyprivatearena,root10byteJMP and declaredhelperstubs normalized.');mark();save(V/'scene17-wait-reentry-v1-current.json',state);print(state['status'],len(rows))
if __name__=='__main__':main()
