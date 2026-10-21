"""Execute readable scene and real170A0 through actual shared68000 bridge.

Record copy/matrix providers execute original CPU and synchronous originalGPU4320.
Other scene GPU commands retain controlled idle/ack/completion fixtures. Finite
CPU/RAM/MMIO/helper/partition proof, not game-image or asynchronous timing proof.
"""
import argparse,ctypes as c,os,subprocess
from check_native_scene_reset_core_bus_v1 import Event
from datetime import datetime,timezone
from pathlib import Path
import geometry_records_scene_runtime_v1 as support
import check_geometry_records_structured_host_v1 as records
from check_native_deck_coordinate_v1 import symbols
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
base=support.base
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v34-record-strides-v1'
CODE=0x180000;ARENA=0x1b0000;SLOTS=101;STRIDE=1024;POOL=0xc0928
OFFSET=144;LOWER=608;TOP=816
FENCES=[(0,16),(136,144),(264,272),(400,416),(592,608),(816,832),(1008,1024)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 out=V/'scene17-geometry-records-strides-bridge-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,game_image_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();runtime=None
 try:
  build=out/'build';p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  payload=(build/'native-shared.bin').read_bytes();syms=symbols(build/'symbols.txt');assert CODE+len(payload)<ARENA
  gpu_reads,gpu_writes=support.native_sites(payload,CODE);gpu_wait_pc=syms['scene_gpu_wait_body']
  session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
  display_mapping=read(session/'display-list-fullCPU-generation.json');mapping['instructions_decoded']+=display_mapping['instructions_decoded']
  mapping['instructions_decoded']+=read(session/'geometry-records-fullCPU-generation.json')['instructions_decoded']+[x for x in read(session/'resource-fullCPU-generation.json')['instructions_decoded']if 0xe3e0<=x['address']<0xe4aa]
  base.queue.ENTRIES.add(0x185b2);base.queue.RETURNS.add(0x18852);base.queue.SCRIPTS.discard(0x185b2)
  runtime=support.Runtime(V/'scene17-structured-host-v1/20261020T230553.352177Z/libscene-draw-cpu.dylib',mapping['instructions_decoded']);core=runtime.core;rows=[];coverage=set();helper_return=syms['biwn_v4_scene_helper_return'];capture_end=syms['biwn_v4_scene_capture_end']
  device_write=runtime.device.write;cpu_execute=core.m68k_execute
  def traced_write(address,value):
   device_write(address,value)
   if address==0xf03204 and value==0x4320:core.vjtrace_arm()
  def traced_execute(count):
   assert c.c_int.in_dll(core,'vjtrace_armed').value==1,'CPU trace unexpectedly disarmed'
   return cpu_execute(count)
  runtime.device.write=traced_write;core.m68k_execute=traced_execute
  poll_opcode=bytes.fromhex('4ab90010a68466f8');poll_sites={CODE+i for i in range(0,len(payload)-7,2)if payload[i:i+8]==poll_opcode};assert 1<=len(poll_sites)<=2,poll_sites
  core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
  def symbol(name):
   if name in syms:return syms[name]
   matches=[v for k,v in syms.items()if k.startswith(name+'.lto_priv.')];assert len(matches)==1,(name,matches);return matches[0]
  callback_reads={symbol('r16'):2,symbol('r32'):4}
  def seed(s):base.lifecycle.seed_cpu(runtime,s)
  def word(a):return runtime.device.read(a,4)
  def logical_cpu():
   raw=runtime.device.ram()[slot+OFFSET+4:slot+OFFSET+4+78];state=base.CPU()
   state.registers[:]=[int.from_bytes(raw[i:i+4],'big')for i in range(0,64,4)]
   state.pc=int.from_bytes(raw[64:68],'big');state.usp=int.from_bytes(raw[68:72],'big');state.ssp=int.from_bytes(raw[72:76],'big');state.sr=int.from_bytes(raw[76:78],'big')
   # The shared frame serializes the active bank only. Read the untouched
   # inactive bank from the physical CPU; never fabricate or write guest state.
   physical=runtime.cpu()
   if state.sr&0x2000:state.usp=physical.usp
   else:state.ssp=physical.ssp

   return state

  clear_poll_sites={}
  for i in range(0,len(payload)-9,2):
   for reg in range(8):
    op=(0x2039+(reg<<9)).to_bytes(2,'big')+bytes.fromhex('00f02238')+(0xe248+reg).to_bytes(2,'big')+bytes.fromhex('64f6')
    if payload[i:i+10]==op:clear_poll_sites[CODE+i]=reg
  assert len(clear_poll_sites)==1,clear_poll_sites
  def arm():
   core.vjtrace_disarm();core.vjtrace_watch_clear()
   for lo,hi in [(0x10a684,0x10a687),(0xf02200,0xf0229f),(0xf03200,0xf0321f)]:assert core.vjtrace_watch_add(lo,hi,3)>=0
   begin=core.vjtrace_ring_head();core.vjtrace_arm();return begin
  def mmio_events(begin):
   core.vjtrace_disarm();end=core.vjtrace_ring_head();events=[]
   for n in range(begin,end):
    e=Event();assert core.vjtrace_ring_read(n,c.byref(e))
    if e.type in [11,12]and e.who==6 and(0xf02200<=e.addr<=0xf0229f or 0xf03200<=e.addr<=0xf0321f):events.append(['r'if e.type==11 else'w',e.addr,None if e.type==11 else e.value])
   return events
  vectors=base.cases()[256:]
  record_vectors=records.cases()
  for polls in [512,1024]:
   case=dict(base.cases()[257]);case['read_queues']=[q for q in case['read_queues']if q['address']!=0x10a684]+[dict(address=0x10a684,width=4,values=[1]*polls+[0])];case['long_completion_polls']=polls;vectors.append(case)
  for polls in [512,1024]:
   case=dict(base.cases()[257]);case['read_queues']=[q for q in case['read_queues']if q['address']!=0xf02238]+[dict(address=0xf02238,width=4,values=[0]*polls+[1])];case['long_clear_polls']=polls;vectors.append(case)
  if args.limit:vectors=vectors[:args.limit]
  for i,case0 in enumerate(vectors):
   task=POOL+(i%SLOTS)*STRIDE;slot=ARENA+(i%SLOTS)*STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3]
   case=dict(case0,body=False,SR=(case0['SR']&~0x201f)|(0x2000 if i%64>=32 else 0)|(i%32));case['registers']=list(case0['registers']);case['registers'][15]=sp;case['usp']=0x170000 if case['SR']&0x2000 else sp;case['ssp']=sp if case['SR']&0x2000 else 0x1d0000
   record_case=record_vectors[i%len(record_vectors)];record_snapshot=records.fixture(snapshot,record_case)
   memory=bytearray(base.fixture(record_snapshot,case));memory[sp-256:sp+32]=memory[base.SP-256:base.SP+32];memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
   for n in range(SLOTS):
    for offset in [16,144,272]:memory[ARENA+n*STRIDE+offset+114:ARENA+n*STRIDE+offset+118]=bytes(4)
   memory[0xc0920:0xc0924]=task.to_bytes(4,'big');ram=bytes(memory)
   original_begin=arm();expected,cpu,original=runtime.native(ram,case,coverage);original_mmio=mmio_events(original_begin);expected_clear_reads=sum(pc==0xe03e for pc in original['steps']);expected_clear_remaining=list(runtime.queues.get((0xf02238,4),[]));expected_poll_reads=sum(pc in [0x17e5c,0x17ed6]for pc in original['steps']);expected_queue_remaining=list(runtime.queues.get((0x10a684,4),[]))
   runtime.reset(ram,case,0)
   for target in base.queue.SCRIPTS:runtime.device.direct(target,2,0x4e75)
   begin=arm();poll_reads=0;clear_reads=0
   initial=base.queue.make_cpu(case);initial.pc=syms['biwn_v4_scene'];seed(initial);minimum=TOP;captures=0;lookups=0;last_helper_sp=None;rotation_row=None;rotation_calls=0;clear_row=None;clear_calls=0;display_row=None;display_calls=0;gpu_row=None;gpu_wait_row=None;gpu_wait_return=None;gpu_calls=0;gpu_wait_calls=0;records_row=None;record_calls=0;record_helpers=[];actual_record_helpers=0
   for step in range(2000000):
    current=runtime.cpu();pc=current.pc;physical_sp=current.registers[15]
    if pc==base.STOP:break
    if slot<=physical_sp<slot+STRIDE:
     if helper_return+12<=pc<capture_end:
      displacement={12:0,16:0,20:64}.get(pc-helper_return,4);assert physical_sp==slot+OFFSET+displacement,('capture SP',hex(pc),hex(physical_sp))
      if pc==helper_return+12:lookups+=1
     else:
      minimum=min(minimum,physical_sp-slot);assert physical_sp>=slot+LOWER,('C stack exceeds partition',i,physical_sp-slot)
    if pc==syms['biwn_v33_records_begin']:
     assert records_row is None
     logical=logical_cpu();assert logical.pc==0x170a0
     records_row=dict(target=0x170a0,actual_body=True,incoming=base.cd.scheduler.cpu_dict(logical));runtime.calls.append(records_row);record_calls+=1
    if pc==syms['biwn_v33_records_end']:
     assert records_row is not None and not record_helpers
     logical=logical_cpu();assert logical.pc==0x17324
     records_row['return']=base.cd.scheduler.cpu_dict(logical);records_row=None
    assert not 0x170a0<=pc<0x17326,('originalrecordbodymustnotexecute',hex(pc))
    if pc in [0xe3e0,0xe220]or(pc==0xe098 and(not record_helpers or record_helpers[-1]['target']!=0xe098)):
     assert records_row is not None
     row=dict(target=pc,actual_body=True,incoming=base.cd.scheduler.cpu_dict(current));runtime.calls.append(row);record_helpers.append(row);actual_record_helpers+=1
     if pc in [0xe3e0,0xe220]:
      assert word(physical_sp)==helper_return;last_helper_sp=physical_sp
    if pc in [0xe4a8,0xe26a,0xe0a4]:
     assert record_helpers;record_helpers.pop()['return']=base.cd.scheduler.cpu_dict(current)
    if pc==0xe098:runtime.inject(0xf03200,4)
    if gpu_wait_return is not None and pc==gpu_wait_return:
     logical=logical_cpu();assert logical.pc==0xe0a4
     gpu_wait_row['return']=base.cd.scheduler.cpu_dict(logical);gpu_wait_row=None;gpu_wait_return=None
    if pc==syms['biwn_v30_gpu_begin']:
     assert gpu_row is None
     logical=logical_cpu();assert logical.pc in support.GPU_ENTRIES
     gpu_row=dict(target=logical.pc,actual_body=True,incoming=base.cd.scheduler.cpu_dict(logical));runtime.calls.append(gpu_row);gpu_calls+=1
    if pc==gpu_wait_pc and gpu_row is not None and gpu_row['target']!=0xe098:
     assert gpu_wait_row is None
     logical=logical_cpu();assert logical.pc==0xe098
     gpu_wait_return=word(physical_sp);assert CODE<=gpu_wait_return<CODE+len(payload)
     gpu_wait_row=dict(target=0xe098,actual_body=True,incoming=base.cd.scheduler.cpu_dict(logical));runtime.calls.append(gpu_wait_row);gpu_wait_calls+=1
    if pc==syms['biwn_v30_gpu_end']:
     assert gpu_row is not None and gpu_wait_row is None
     logical=logical_cpu();assert logical.pc==support.GPU_ENTRIES[gpu_row['target']]
     gpu_row['return']=base.cd.scheduler.cpu_dict(logical);gpu_row=None
    assert not 0xe0a6<=pc<0xe220,('Original scene GPU mailbox helper executed in native scene',hex(pc))
    if pc==syms['biwn_v27_display_begin']:
     assert display_row is None
     logical=logical_cpu();assert logical.pc==0x185b2
     display_row=dict(target=0x185b2,actual_body=True,incoming=base.cd.scheduler.cpu_dict(logical));runtime.calls.append(display_row);display_calls+=1
    if pc==syms['biwn_v27_display_end']:
     assert display_row is not None
     logical=logical_cpu();assert logical.pc==0x18852
     display_row['return']=base.cd.scheduler.cpu_dict(logical);display_row=None
    assert not 0x185b2<=pc<=0x18852,('originaldisplaylistmustnotexecute',hex(pc))
    if pc==syms['biwn_v26_clear_begin']:
     assert clear_row is None
     logical=logical_cpu();assert logical.pc==0xe03a
     clear_row=dict(target=0xe03a,actual_body=True,incoming=base.cd.scheduler.cpu_dict(logical));runtime.calls.append(clear_row);clear_calls+=1
    if pc==syms['biwn_v26_clear_end']:
     assert clear_row is not None
     logical=logical_cpu();assert logical.pc==0xe096
     clear_row['return']=base.cd.scheduler.cpu_dict(logical);clear_row=None
    assert not 0xe03a<=pc<=0xe096,('originalclearmustnotexecute',hex(pc))
    if pc in clear_poll_sites:clear_reads+=1
    if pc==syms['biwn_v25_rotation_begin']:
     assert rotation_row is None
     logical=logical_cpu()
     assert logical.pc==0x17f14,(i,hex(logical.pc),hex(slot),base.cd.scheduler.cpu_dict(logical))
     rotation_row=dict(target=0x17f14,actual_body=True,incoming=base.cd.scheduler.cpu_dict(logical));runtime.calls.append(rotation_row);rotation_calls+=1
    if pc==syms['biwn_v25_rotation_end']:
     assert rotation_row is not None
     logical=logical_cpu()
     assert logical.pc==0x17f66
     rotation_row['return']=base.cd.scheduler.cpu_dict(logical);rotation_row=None
    assert not 0x17f14<=pc<=0x17f66,('originalrotationmustnotexecute',hex(pc))
    if pc==helper_return:captures+=1;assert physical_sp==last_helper_sp+4
    if pc in poll_sites:runtime.inject(0x10a684,4);poll_reads+=1
    if pc in callback_reads:
     address=word(physical_sp+8);assert address!=0x10a684,('completionflagmustusephysicalTST',i);runtime.inject(address,callback_reads[pc])
    if pc in base.queue.SCRIPTS:
     assert word(physical_sp)==helper_return;last_helper_sp=physical_sp
     runtime.scripted(current,pc);seed(current);core.m68k_execute(1);continue
    assert CODE<=pc<CODE+len(payload)or 0xe3e0<=pc<0xe4aa or 0xe220<=pc<0xe26c or 0xe098<=pc<0xe0a6,('unexpected PC',hex(pc),i)
    gpu_write=None
    if pc in gpu_reads:
     address=current.registers[gpu_reads[pc]]&0xffffff
     if address in [0xf03200,0xf03204]:runtime.inject(address,4)
    if pc in gpu_writes:
     source_reg,address_reg=gpu_writes[pc]
     if current.registers[address_reg]&0xffffff==0xf03204:gpu_write=current.registers[source_reg]
    core.m68k_execute(1)
    if core.GPUReadLong(0xf03204,0)==0x4320:runtime.device.write(0xf03204,0x4320)
    if gpu_write is not None:runtime.command_written(gpu_write)
    if pc in clear_poll_sites:
     q=runtime.queues.get((0xf02238,4))
     if q:core.m68k_set_reg(clear_poll_sites[pc],q.pop(0))
   else:raise AssertionError('shared bridge bound')
   core.vjtrace_disarm();end=core.vjtrace_ring_head();physical_polls=[]
   for n in range(begin,end):
    event=Event();assert core.vjtrace_ring_read(n,c.byref(event))
    if event.type==11 and event.who==6 and event.addr==0x10a684:physical_polls.append(dict(PC=hex(event.pc),address=event.addr))
   assert poll_reads==expected_poll_reads==len(physical_polls),(i,poll_reads,expected_poll_reads,len(physical_polls))
   assert all(int(row['PC'],16)in poll_sites for row in physical_polls)
   assert list(runtime.queues.get((0x10a684,4),[]))==expected_queue_remaining
   save(out/f'polls-{i}.json',physical_polls)
   compiled_mmio=mmio_events(begin);save(out/f'mmio-{i}.json',dict(original=original_mmio,compiled=compiled_mmio))
   actual_clear_reads=sum(e[0]=='r'and e[1]==0xf02238 for e in compiled_mmio)
   assert original_mmio==compiled_mmio and clear_reads==expected_clear_reads==actual_clear_reads,('clear MMIO/count',i,expected_clear_reads,clear_reads,actual_clear_reads)
   assert list(runtime.queues.get((0xf02238,4),[]))==expected_clear_remaining

   actual=runtime.device.ram();got=runtime.cpu()
   def normalize(raw):
    value=bytearray(raw);value[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
    for target in base.queue.SCRIPTS:value[target:target+2]=ram[target:target+2]
    return bytes(value)
   if normalize(expected)!=normalize(actual)or bytes(cpu)!=bytes(got)or runtime.calls!=original['calls']:
    save(out/'counterexample.json',dict(case=case,original_CPU=base.cd.scheduler.cpu_dict(cpu),native_CPU=base.cd.scheduler.cpu_dict(got),RAM_differences=[hex(a)for a,(x,y)in enumerate(zip(normalize(expected),normalize(actual)))if x!=y][:32],original_calls=original['calls'],native_calls=runtime.calls));raise AssertionError(out/'counterexample.json')
   for n in range(SLOTS):
    at=ARENA+n*STRIDE
    for lo,hi in FENCES:assert actual[at+lo:at+hi]==ram[at+lo:at+hi],('fence',i,n,lo)
   assert actual[ARENA:slot]==ram[ARENA:slot]and actual[slot+STRIDE:ARENA+SLOTS*STRIDE]==ram[slot+STRIDE:ARENA+SLOTS*STRIDE]
   allowed=set(range(OFFSET,OFFSET+118))|set(range(LOWER,TOP));assert all(j in allowed or actual[slot+j]==ram[slot+j]for j in range(STRIDE)),('other context',i)
   assert word(slot+OFFSET+114)==0 and word(slot+OFFSET+94)==0
   assert actual[CODE:CODE+len(payload)]==payload and captures==lookups==sum(x['target']in [0xe3e0,0xe220]for x in runtime.calls)and rotation_row is None and clear_row is None and display_row is None and gpu_row is None and gpu_wait_row is None and records_row is None and not record_helpers
   rows.append(dict(case=i,original_case_id=case['id'],record_fixture_id=record_case['id'],native_record_calls=record_calls,actual_record_helpers=actual_record_helpers,original_record_instructions_executed=0,long_completion_polls=case.get('long_completion_polls',0),long_clear_polls=case.get('long_clear_polls',0),task=hex(task),CCR=case['SR']&31,supervisor=bool(case['SR']&0x2000),full_CPU_nonarena_RAM_helper_entries_match=True,physical_C_stack_bytes=TOP-minimum,helper_returns=captures,SP_only_capture_lookups=lookups,native_rotation_calls=rotation_calls,native_clear_calls=clear_calls,native_display_calls=display_calls,native_gpu_family_calls=gpu_calls,native_internal_gpu_waits=gpu_wait_calls,actual_native_clear_reads=actual_clear_reads,original_clear_reads=expected_clear_reads,original_clear_instructions_executed=0,original_rotation_instructions_executed=0,native_instructions=step,original_completion_reads=expected_poll_reads,actual_native_completion_reads=len(physical_polls),queued_reads_match=True));state.update(status='checking',completed=len(rows));mark()
   if len(rows)%32==0:print('shared scene',len(rows),'/',len(vectors),flush=True)
  save(out/'cases.json',rows)
  paths=[Path(__file__),Path(support.__file__),Path(base.__file__),*SRC.glob('*'),ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-draw-structured-v1/scene-context.h',ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-draw-structured-v1/coordinator-reference.inc',ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-rotation-structured-v1/coordinator-reference.inc',ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-clear-structured-v1/coordinator-reference.inc',out/'cases.json',*out.glob('polls-*.json'),*out.glob('mmio-*.json'),build/'native-shared.bin',build/'symbols.txt',build/'disassembly.txt']
  paths += [ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-gpu-command-family-v1/coordinator-reference.inc',ROOT/'projects/black-ice-white-noise/restoration/experimental/geometry-records-structured-v1/coordinator-reference.inc',Path(records.__file__),Path(support.old.__file__)]
  state.update(status='terminal_scene17_shared_bridge_preflight_pass'if args.limit else'terminal_scene17_shared_bridge_original_CPU_fixtures_match',completed=len(rows),payload=str(build/'native-shared.bin'),payload_sha256=sha(build/'native-shared.bin'),payload_bytes=len(payload),symbols=syms,direct_poll_sites=[hex(a)for a in sorted(poll_sites)],actual_completion_read_counts_match=True,clear_poll_sites={hex(k):v for k,v in clear_poll_sites.items()},actual_clear_read_counts_match=True,ordered_MMIO_matches=True,read_values_available=False,code=CODE,arena=ARENA,maximum_C_stack_bytes=max(x['physical_C_stack_bytes']for x in rows),task_slots=len({x['task']for x in rows}),all32CCR_both_banks=len({(x['CCR'],x['supervisor'])for x in rows})==64,original_instruction_locations=len(coverage),native_rotation_calls=sum(x['native_rotation_calls']for x in rows),native_clear_calls=sum(x['native_clear_calls']for x in rows),native_display_calls=sum(x['native_display_calls']for x in rows),original_display_instructions_executed=0,original_rotation_instructions_executed=0,original_clear_instructions_executed=0,original_gpu_function_instructions_executed=0,native_gpu_family_calls=sum(x['native_gpu_family_calls']for x in rows),native_internal_gpu_waits=sum(x['native_internal_gpu_waits']for x in rows),native_record_calls=sum(x['native_record_calls']for x in rows),actual_record_helpers=sum(x['actual_record_helpers']for x in rows),original_record_instructions_executed=0,remaining_original_scene_services=['0xe3e0','0xe220'],source_sha256={str(p):sha(p)for p in paths if p.is_file()},scope=__doc__+' All seven partition fences across101slots checked eachcase. Only private arena normalized; every untouched slot and disjoint partition separately checked. No original helper stub. Actual bridge/capture assembly and complete original copy/matrix/wait helpers execute;no host interception of native bridge or target C. Actual native MMIO reads execute; controlled clear-read fixture values replace only the MOVE destination register after the actual read, matching the original E03E fixture seam. MMIO read addresses/counts/order and write values compare; read values are not recorded. Mode/completion queues retain their declared read-site injection. No new arena bytes;aliases require separate nested checks.');mark()
  if not args.limit:save(V/'scene17-geometry-records-strides-bridge-v1-current.json',state)
  print(state['status'],state['completed'],state['maximum_C_stack_bytes'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
 finally:
  if runtime:runtime.core.vjtrace_disarm();runtime.close()
if __name__=='__main__':main()
