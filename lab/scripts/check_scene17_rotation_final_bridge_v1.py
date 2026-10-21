"""Execute readable scene17 through the real shared 68000 entry/capture bridge.
Original clear executes; the new structured native rotation retains185B2 as an explicit service. Other services and busy reads are explicit
fixtures. Finite component proof, not disc/gameplay/IRQ or console timing proof.
"""
import argparse,ctypes as c,os,subprocess
from check_native_scene_reset_core_bus_v1 import Event
from datetime import datetime,timezone
from pathlib import Path
import scene17_host_runtime_v1 as support
from check_native_deck_coordinate_v1 import symbols
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
base=support.base
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v25-scene-rotation'
_BUILD=read(V/'native-scene17-rotation-disc-build-v1-current.json');CODE=_BUILD['shared_Deck_code_address'];ARENA=_BUILD['deck_arena_address'];SLOTS=101;STRIDE=1024;POOL=0xc0928
OFFSET=144;LOWER=608;TOP=816
FENCES=[(0,16),(136,144),(264,272),(400,416),(592,608),(816,832),(1008,1024)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 out=V/'scene17-rotation-final-bridge-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,game_image_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();runtime=None
 try:
  build=out/'build';p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  payload=(build/'native-shared.bin').read_bytes();resident=Path(_BUILD['component']).read_bytes();assert payload==resident[CODE-_BUILD['resident_address']:CODE-_BUILD['resident_address']+len(payload)];syms=symbols(build/'symbols.txt');assert CODE+len(payload)<=ARENA
  session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
  runtime=support.Runtime(V/'scene17-structured-host-v1/20261020T230553.352177Z/libscene-draw-cpu.dylib',mapping['instructions_decoded']);core=runtime.core;rows=[];coverage=set();helper_return=syms['biwn_v4_scene_helper_return'];capture_end=syms['biwn_v4_scene_capture_end']
  poll_opcode=bytes.fromhex('4ab90010a68466f8');poll_sites={CODE+i for i in range(0,len(payload)-7,2)if payload[i:i+8]==poll_opcode};assert 1<=len(poll_sites)<=2,poll_sites
  core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
  callback_reads={syms['r16']:2,syms['r32']:4}
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

  def dependency(guest):
   end={0xe03a:0xe096}[guest.pc];seed(guest)
   for _ in range(10000):
    pc=core.m68k_get_reg(None,16)
    if pc==end:return runtime.cpu()
    if pc in base.queue.SCRIPTS:
     current=runtime.cpu();runtime.scripted(current,pc);seed(current)
    else:assert pc in runtime.rows,hex(pc)
    core.m68k_execute(1)
    if pc==0xe03e:
     q=runtime.queues.get((0xf02238,4))
     if q:core.m68k_set_reg(0,q.pop(0))
   raise AssertionError('dependency bound')
  vectors=base.cases()[256:]
  for polls in [512,1024]:
   case=dict(base.cases()[257]);case['read_queues']=[q for q in case['read_queues']if q['address']!=0x10a684]+[dict(address=0x10a684,width=4,values=[1]*polls+[0])];case['long_completion_polls']=polls;vectors.append(case)
  if args.limit:vectors=vectors[:args.limit]
  for i,case0 in enumerate(vectors):
   task=POOL+(i%SLOTS)*STRIDE;slot=ARENA+(i%SLOTS)*STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3]
   case=dict(case0,body=False,SR=(case0['SR']&~0x201f)|(0x2000 if i%64>=32 else 0)|(i%32));case['registers']=list(case0['registers']);case['registers'][15]=sp;case['usp']=0x170000 if case['SR']&0x2000 else sp;case['ssp']=sp if case['SR']&0x2000 else 0x1d0000
   memory=bytearray(base.fixture(snapshot,case));memory[sp-256:sp+32]=memory[base.SP-256:base.SP+32];memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
   for n in range(SLOTS):
    for offset in [16,144,272]:memory[ARENA+n*STRIDE+offset+114:ARENA+n*STRIDE+offset+118]=bytes(4)
   memory[0xc0920:0xc0924]=task.to_bytes(4,'big');ram=bytes(memory)
   expected,cpu,original=runtime.native(ram,case,coverage);expected_poll_reads=sum(pc in [0x17e5c,0x17ed6]for pc in original['steps']);expected_queue_remaining=list(runtime.queues.get((0x10a684,4),[]))
   runtime.reset(ram,case,0)
   for target in base.queue.SCRIPTS:runtime.device.direct(target,2,0x4e75)
   core.vjtrace_disarm();core.vjtrace_watch_clear();assert core.vjtrace_watch_add(0x10a684,0x10a687,1)>=0;begin=core.vjtrace_ring_head();core.vjtrace_arm();poll_reads=0
   initial=base.queue.make_cpu(case);initial.pc=syms['biwn_v4_scene'];seed(initial);minimum=TOP;captures=0;lookups=0;last_helper_sp=None;rotation_row=None;rotation_calls=0
   for step in range(100000):
    current=runtime.cpu();pc=current.pc;physical_sp=current.registers[15]
    if pc==base.STOP:break
    if slot<=physical_sp<slot+STRIDE:
     if helper_return+12<=pc<capture_end:
      displacement={12:0,16:0,20:64}.get(pc-helper_return,4);assert physical_sp==slot+OFFSET+displacement,('capture SP',hex(pc),hex(physical_sp))
      if pc==helper_return+12:lookups+=1
     else:
      minimum=min(minimum,physical_sp-slot);assert physical_sp>=slot+LOWER,('C stack exceeds partition',i,physical_sp-slot)
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
    if pc in base.queue.SCRIPTS or pc in base.queue.ENTRIES:
     assert word(physical_sp)==helper_return;last_helper_sp=physical_sp
     if pc==0xe03a:
      row=dict(target=pc,actual_body=True,incoming=base.cd.scheduler.cpu_dict(current));runtime.calls.append(row);current=dependency(current);row['return']=base.cd.scheduler.cpu_dict(current);seed(current)
     else:runtime.scripted(current,pc);seed(current)
     core.m68k_execute(1);continue
    assert CODE<=pc<CODE+len(payload),('unexpected PC',hex(pc),i)
    core.m68k_execute(1)
   else:raise AssertionError('shared bridge bound')
   core.vjtrace_disarm();end=core.vjtrace_ring_head();physical_polls=[]
   for n in range(begin,end):
    event=Event();assert core.vjtrace_ring_read(n,c.byref(event))
    if event.type==11 and event.who==6 and event.addr==0x10a684:physical_polls.append(dict(PC=hex(event.pc),address=event.addr))
   assert poll_reads==expected_poll_reads==len(physical_polls),(i,poll_reads,expected_poll_reads,len(physical_polls))
   assert all(int(row['PC'],16)in poll_sites for row in physical_polls)
   assert list(runtime.queues.get((0x10a684,4),[]))==expected_queue_remaining
   save(out/f'polls-{i}.json',physical_polls)
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
   assert actual[CODE:CODE+len(payload)]==payload and captures==lookups==sum(x['target']==0xe03a or x['target']in base.queue.SCRIPTS for x in runtime.calls)and rotation_row is None
   rows.append(dict(case=i,original_case_id=case['id'],long_completion_polls=case.get('long_completion_polls',0),task=hex(task),CCR=case['SR']&31,supervisor=bool(case['SR']&0x2000),full_CPU_nonarena_RAM_helper_entries_match=True,physical_C_stack_bytes=TOP-minimum,helper_returns=captures,SP_only_capture_lookups=lookups,native_rotation_calls=rotation_calls,original_rotation_instructions_executed=0,native_instructions=step,original_completion_reads=expected_poll_reads,actual_native_completion_reads=len(physical_polls),queued_reads_match=True));state.update(status='checking',completed=len(rows));mark()
   if len(rows)%32==0:print('shared scene',len(rows),'/',len(vectors),flush=True)
  save(out/'cases.json',rows)
  paths=[Path(__file__),Path(support.__file__),Path(base.__file__),*SRC.glob('*'),ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-draw-structured-v1/scene-context.h',ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-draw-structured-v1/coordinator-reference.inc',ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-rotation-structured-v1/coordinator-reference.inc',out/'cases.json',*out.glob('polls-*.json'),build/'native-shared.bin',build/'symbols.txt',build/'disassembly.txt']
  state.update(deployed_module_byte_identity=True,build=str(V/'native-scene17-rotation-disc-build-v1-current.json'),status='terminal_scene17_shared_bridge_preflight_pass'if args.limit else'terminal_scene17_shared_bridge_original_CPU_fixtures_match',completed=len(rows),payload=str(build/'native-shared.bin'),payload_sha256=sha(build/'native-shared.bin'),payload_bytes=len(payload),symbols=syms,direct_poll_sites=[hex(a)for a in sorted(poll_sites)],actual_completion_read_counts_match=True,code=CODE,arena=ARENA,maximum_C_stack_bytes=max(x['physical_C_stack_bytes']for x in rows),task_slots=len({x['task']for x in rows}),all32CCR_both_banks=len({(x['CCR'],x['supervisor'])for x in rows})==64,original_instruction_locations=len(coverage),native_rotation_calls=sum(x['native_rotation_calls']for x in rows),original_rotation_instructions_executed=0,source_sha256={str(p):sha(p)for p in paths if p.is_file()},scope=__doc__+' All seven partition fences across101slots checked eachcase. Only private arena and declared helperRTSstubs normalized. Actual bridge/capture assembly and original helperRTS execute;no host interception of native bridge or target C. Read callbacks inject supplied mode/completion queues;actual memory accesses execute. No new arena bytes;aliases require separate nested checks.');mark()
  if not args.limit:save(V/'scene17-rotation-final-bridge-v1-current.json',state)
  print(state['status'],state['completed'],state['maximum_C_stack_bytes'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
 finally:
  if runtime:runtime.core.vjtrace_disarm();runtime.close()
if __name__=='__main__':main()
