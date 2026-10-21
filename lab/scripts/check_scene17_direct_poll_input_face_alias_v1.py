"""Actual scene/input/face cross-root busy fallbacks in four injected directions.
One helper JSR is injected. Nested scene uses modezero;input/face helpers are
declared volatile-register/pad/record effects. Original clear/rotation execute.
CPU,nonarenaRAM,helperrecords and protected outer frame/stack compare. Not
natural calls, fresh gameplay or arbitrary IRQ/reentry proof.
"""
import os
from pathlib import Path
from datetime import datetime,timezone
import check_scene17_direct_poll_final_bridge_v1 as b
import check_native_deck_scene_reset_v1 as m
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
base=b.base
ROOTS={'scene':0x17e0e,'input':0x11b4c,'face':0x1186a}
EXTRA={0xe4c0,0x10c6e,0x10e72,0x10cb6,0x1102a}
def main():
 gp=V/'scene17-direct-poll-final-bridge-v1-current.json';gate=read(gp)
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 payload=Path(gate['payload']).read_bytes();syms=gate['symbols'];poll_sites={int(pc,16)for pc in gate['direct_poll_sites']};out=V/'scene17-direct-poll-input-face-alias-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='checking',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False)
 def mark():save(out/'protocol.json',state)
 mark();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();runtime=b.support.Runtime(V/'scene17-structured-host-v1/20261020T230553.352177Z/libscene-draw-cpu.dylib',mapping['instructions_decoded']);core=runtime.core;rows=[]
 face_ram,face_cpu,face_case=list(m.faces.fixtures())[256];_,input_cpu,input_case=m.inputs.fixtures()[256];m.scene.HELPERS=EXTRA;template=base.cases()[257]
 def seed(s):base.lifecycle.seed_cpu(runtime,s)
 def run(ram,case,slot,outer,inner,native):
  runtime.reset(ram,case,0);scripts=base.queue.SCRIPTS|EXTRA;injection=0xe0a6 if outer=='scene'else 0xe4c0 if outer=='input'else 0x10c6e
  for target in scripts:runtime.device.direct(target,2,0x4e75)
  for off,val in enumerate(b'\x4e\xb9'+ROOTS[inner].to_bytes(4,'big')+b'\x4e\x75'):runtime.device.direct(injection+off,1,val)
  if native:
   for name in [outer,inner]:
    n=10 if name=='scene'else 6
    for off,val in enumerate(b'\x4e\xf9'+syms['biwn_v4_'+name].to_bytes(4,'big')+b'\x4e\x71'*((n-6)//2)):runtime.device.direct(ROOTS[name]+off,1,val)
  seed(base.queue.make_cpu(case));injected=False;inside=False;protected=None;stack=[];counts={name:dict(entries=0,returns=0,fallbacks=0)for name in [outer,inner]}
  def effect(current,target):
   if target in EXTRA:
    row=dict(target=target,declared_input_face_effect=True,incoming=base.cd.scheduler.cpu_dict(current));runtime.calls.append(row);mem=bytearray(runtime.device.ram());kw=dict(case,variant=case['sample'],held=0,pressed=0)
    if outer=='face' or(inner=='face'and inside):m.faces.Engine.helper(None,mem,current,target,kw,len(runtime.calls)-1)
    else:m.inputs.Engine.helper(None,mem,current,target,kw,len(runtime.calls)-1)
    for a in [0x49ba4,0x49bac]:mem[a:a+4]=bytes(4)
    runtime.device.seed(bytes(mem),0);row['return']=base.cd.scheduler.cpu_dict(current)
   else:runtime.scripted(current,target)
  for step in range(20000):
   current=runtime.cpu();pc=current.pc
   if pc==base.STOP:break
   if native:
    for name,row in counts.items():
     row['entries']+=pc==syms['biwn_v4_'+name];row['returns']+=pc==syms['biwn_v4_'+name+'_return'];row['fallbacks']+=pc==syms['biwn_v4_'+name+'_original_fallback']
   if pc==injection and not injected:
    injected=True;inside=True
    if inner=='scene':runtime.device.direct(0x49c60,2,0)
    memory=runtime.device.ram();protected=(memory[slot+144:slot+262],memory[slot+608:slot+816]);core.m68k_execute(1);continue
   if pc==injection+6:
    assert inside;inside=False;memory=runtime.device.ram()
    if native:assert protected==(memory[slot+144:slot+262],memory[slot+608:slot+816]),'suspended alias frame/stack changed'
    if inner=='scene':runtime.device.direct(0x49c60,2,1)
    current.pc=injection;effect(current,injection);current.pc=injection+6;seed(current);core.m68k_execute(1);continue
   if native and pc in poll_sites:runtime.inject(0x10a684,4)
   if native and pc in [syms['r16'],syms['r32']]:runtime.inject(runtime.device.read(current.registers[15]+8,4),2 if pc==syms['r16']else 4)
   if pc in scripts:
    effect(current,pc);current.pc=injection+6 if pc==injection else pc;seed(current);core.m68k_execute(1);continue
   if pc in base.queue.ENTRIES:
    row=dict(target=pc,actual_body=True,incoming=base.cd.scheduler.cpu_dict(current));runtime.calls.append(row);stack.append(row)
   if pc in base.queue.RETURNS and stack:stack.pop()['return']=base.cd.scheduler.cpu_dict(current)
   if not(inside and inner=='scene')and pc in [0x17e18,0x17e34,0x17e6e,0x17ef8]:runtime.inject(0x49c60,2)
   if pc in [0x17e5c,0x17ed6]:runtime.inject(0x10a684,4)
   assert pc in runtime.rows or 0x1186a<=pc<0x11ad4 or 0x11b4c<=pc<0x11d1a or(native and b.CODE<=pc<b.CODE+len(payload)),hex(pc)
   core.m68k_execute(1)
   if pc==0xe03e:
    q=runtime.queues.get((0xf02238,4))
    if q:core.m68k_set_reg(0,q.pop(0))
  else:raise AssertionError(('cross alias bound',outer,inner))
  assert injected and not inside and not stack
  memory=bytearray(runtime.device.ram());arena=bytes(memory[b.ARENA:b.ARENA+101*1024])
  if native:assert counts[outer]==dict(entries=1,returns=1,fallbacks=0)and counts[inner]==dict(entries=1,returns=0,fallbacks=1),counts
  memory[b.ARENA:b.ARENA+101*1024]=ram[b.ARENA:b.ARENA+101*1024]
  for target in scripts:memory[target:target+2]=ram[target:target+2]
  memory[injection:injection+8]=ram[injection:injection+8]
  for name in [outer,inner]:
   a=ROOTS[name];n=10 if name=='scene'else 6;memory[a:a+n]=ram[a:a+n]
  return bytes(memory),runtime.cpu(),list(runtime.calls),dict(instructions=step,native_counts=counts,arena=arena)
 try:
  for outer,inner in [('scene','input'),('scene','face'),('input','scene'),('face','scene')]:
   for i in range(64):
    task=b.POOL+[0,1,6,100][i%4]*1024;slot=b.ARENA+task-b.POOL;sp=task+[0x3c0,0x3be,0x200][i%3];case=dict(template,entry=ROOTS[outer],body=False,SR=(0x2000 if i>=32 else 0)|(i%32),sample=i)
    original=base.queue.make_cpu(template)if outer=='scene'else input_cpu if outer=='input'else face_cpu;case['registers']=list(original.registers);case['registers'][15]=sp;case['usp']=0x170000 if i>=32 else sp;case['ssp']=sp if i>=32 else 0x1d0000
    memory=bytearray(base.fixture(face_ram,case));memory[0x90000:0x90090]=memory[0x80000:0x80090];memory[sp-256:sp+32]=memory[base.SP-256:base.SP+32];memory[sp:sp+4]=base.STOP.to_bytes(4,'big');memory[b.CODE:b.CODE+len(payload)]=payload;memory[b.ARENA:b.ARENA+101*1024]=bytes([0xa5])*(101*1024)
    for n in range(101):
     for offset in [16,144,272]:memory[b.ARENA+n*1024+offset+114:b.ARENA+n*1024+offset+118]=bytes(4)
    memory[0xc0920:0xc0924]=task.to_bytes(4,'big');ram=bytes(memory)
    expected,cpu,calls,_=run(ram,case,slot,outer,inner,False);actual,got,observed,details=run(ram,case,slot,outer,inner,True)
    if expected!=actual or bytes(cpu)!=bytes(got)or calls!=observed:
     save(out/'counterexample.json',dict(outer=outer,inner=inner,case=i,original_CPU=base.cd.scheduler.cpu_dict(cpu),native_CPU=base.cd.scheduler.cpu_dict(got),RAM_differences=[hex(a)for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32],original_calls=calls,native_calls=observed));raise AssertionError(out/'counterexample.json')
    arena=details.pop('arena');old=ram[b.ARENA:b.ARENA+101*1024];relative=slot-b.ARENA;allowed=set(range(relative+144,relative+262))|set(range(relative+608,relative+816));assert all(j in allowed or u==old[j]for j,u in enumerate(arena));assert arena[relative+258:relative+262]==bytes(4)
    rows.append(dict(outer=outer,inner=inner,case=i,CCR=i%32,supervisor=i>=32,task=hex(task),guest_SP=hex(sp),suspended_frame_stack_preserved=True,full_CPU_nonarena_RAM_helper_records_match=True,**details));state['completed']=len(rows);mark()
   print(outer,'to',inner,len(rows),flush=True)
 finally:runtime.close()
 save(out/'cases.json',rows);state.update(status='terminal_scene_input_face_four_direction_alias_fallbacks_match',completed=len(rows),source_sha256={str(p):sha(p)for p in [Path(__file__),Path(b.__file__),gp,Path(gate['payload']),out/'cases.json',Path(m.inputs.__file__),Path(m.faces.__file__)]},scope=__doc__+'64casesperdirection,all32CCR/bothbanks,4taskslotsand3guestSPdepths. Exactlyoneacceptedouterandonebusyinnerfallback;private118bytecontext/208byteCstackprotected.No new image or preview changes.');mark();save(V/'scene17-direct-poll-input-face-alias-v1-current.json',state);print(state['status'],len(rows))
if __name__=='__main__':main()
