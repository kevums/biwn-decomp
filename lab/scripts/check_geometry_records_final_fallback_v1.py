"""Real scene-entry bridge fallback with invalid task IDs and busy alias frame.
Original scene/records/copy/clear/rotation bodies execute; GPU mailbox busy/ack/completion reads
are declared fixtures. No natural nesting/IRQ/disc gameplay claim.
"""
import ctypes as c,os
from scene_gpu_family_bridge_events_v1 import Events
from datetime import datetime,timezone
from pathlib import Path
import check_scene17_geometry_records_final_bridge_v1 as bridge
import check_geometry_records_structured_host_v1 as records
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
import scene17_display_list_runtime_v1 as display
display.install(bridge)
base=bridge.base

def main():
 gate=read(V/'scene17-geometry-records-final-bridge-v1-current.json')
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 payload=Path(gate['payload']).read_bytes();syms=gate['symbols'];out=V/'geometry-records-final-fallback-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='checking',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,game_image_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json');mapping['instructions_decoded']+=read(session/'geometry-records-fullCPU-generation.json')['instructions_decoded']+[x for x in read(session/'resource-fullCPU-generation.json')['instructions_decoded']if 0xe3e0<=x['address']<0xe4aa];snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();runtime=bridge.support.Runtime(V/'scene17-structured-host-v1/20261020T230553.352177Z/libscene-draw-cpu.dylib',mapping['instructions_decoded']);core=runtime.core;rows=[]
 faults=[('zero',0,False),('byte_misaligned',bridge.POOL+1,False),('bit8_misaligned',bridge.POOL+256,False),('bit9_misaligned',bridge.POOL+512,False),('past_pool',bridge.POOL+101*1024,False),('input_face_scene_busy',bridge.POOL,True)]
 try:
  for fault,task,busy in faults:
   for i in range(64):
    case0=base.cases()[256+i];case=dict(case0,body=False,SR=(case0['SR']&~0x201f)|(0x2000 if i>=32 else 0)|(i%32));case['usp']=0x170000 if case['SR']&0x2000 else base.SP;case['ssp']=base.SP if case['SR']&0x2000 else 0x1d0000
    memory=bytearray(base.fixture(records.fixture(snapshot,records.cases()[0]),case));memory[bridge.CODE:bridge.CODE+len(payload)]=payload;memory[bridge.ARENA:bridge.ARENA+101*1024]=bytes([0xa5])*(101*1024);memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
    if busy:memory[bridge.ARENA+258:bridge.ARENA+262]=(1).to_bytes(4,'big')
    ram=bytes(memory);expected,cpu,original=runtime.native(ram,case,set());runtime.reset(ram,case,0)
    for target in base.queue.SCRIPTS:runtime.device.direct(target,2,0x4e75)
    initial=base.queue.make_cpu(case);initial.pc=syms['biwn_v4_scene'];base.lifecycle.seed_cpu(runtime,initial);stack=[];fallbacks=0;events=Events(bridge,runtime,gate,bridge.ARENA)
    for step in range(10000):
     current=runtime.cpu();pc=current.pc
     if pc==base.STOP:break
     events.before(current,False)
     if pc==syms['biwn_v4_scene_original_fallback']:fallbacks+=1
     if pc in base.queue.SCRIPTS:
      current=runtime.cpu();runtime.scripted(current,pc)
      for r in [0,1,8,9]:core.m68k_set_reg(r,current.registers[r])
      core.m68k_set_reg(17,current.sr)
     elif pc in runtime.rows:
      if pc in base.queue.ENTRIES and pc not in bridge.support.GPU_ENTRIES:
       row=dict(target=pc,actual_body=True,incoming=base.cd.scheduler.cpu_dict(runtime.cpu()));runtime.calls.append(row);stack.append(row)
      if pc in base.queue.RETURNS and pc not in bridge.support.GPU_ENTRIES.values() and stack:stack.pop()['return']=base.cd.scheduler.cpu_dict(runtime.cpu())
      if pc in [0x17e18,0x17e34,0x17e6e,0x17ef8]:runtime.inject(0x49c60,2)
      if pc in [0x17e5c,0x17ed6]:runtime.inject(0x10a684,4)
     else:assert bridge.CODE<=pc<bridge.CODE+len(payload),hex(pc)
     core.m68k_execute(1)
     events.after(pc)
     if pc==0xe03e:
      q=runtime.queues.get((0xf02238,4))
      if q:core.m68k_set_reg(0,q.pop(0))
    else:raise AssertionError('fallback bound')
    actual=bytearray(runtime.device.ram())
    for target in base.queue.SCRIPTS:actual[target:target+2]=ram[target:target+2]
    events.complete();got=runtime.cpu();assert not stack and fallbacks==1
    if expected!=bytes(actual)or bytes(cpu)!=bytes(got)or original['calls']!=runtime.calls:
     save(out/'counterexample.json',dict(fault=fault,case=i,original_CPU=base.cd.scheduler.cpu_dict(cpu),native_CPU=base.cd.scheduler.cpu_dict(got),RAM_differences=[hex(a)for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32],original_calls=original['calls'],native_calls=runtime.calls));raise AssertionError(out/'counterexample.json')
    assert actual[bridge.ARENA:bridge.ARENA+101*1024]==ram[bridge.ARENA:bridge.ARENA+101*1024]
    rows.append(dict(fault=fault,case=i,CCR=i%32,supervisor=i>=32,full_CPU_all_RAM_helpers_match=True,entire_arena_unchanged=True,original_fallback_entries=fallbacks));state['completed']=len(rows);mark()
   print(fault,len(rows),flush=True)
 finally:runtime.close()
 save(out/'cases.json',rows);state.update(status='terminal_scene17_invalid_task_and_busy_fallback_match',completed=len(rows),source_sha256={str(p):sha(p)for p in [*display.dependencies(),Path(__import__('scene_gpu_family_bridge_events_v1').__file__),Path(bridge.support.__file__),Path(records.__file__),Path(__file__),Path(bridge.__file__),V/'scene17-geometry-records-final-bridge-v1-current.json',Path(gate['payload']),out/'cases.json']},scope=__doc__+' Sixfaults*64CCR/bankcases;busyframe118bytes plus Cstack208bytes and all101private slots stay byteidentical. This force-busy test is separate from actual outer/inner nesting.');mark();save(V/'geometry-records-final-fallback-v1-current.json',state);print(state['status'],len(rows))
if __name__=='__main__':main()
