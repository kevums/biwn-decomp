"""Compare previous and new native scene with identical actual disc providers.

Reference is immutable v30 scene C with captured original170A0; candidate is
v33 scene C with readable170A0. Both use the same inherited E3E0/E220/E098
machine-code providers from the candidate stage/resident. Mailbox busy/ack/
completion inputs are explicit fixtures; originalGPU4320 runs synchronously.
This is finite preservation of inherited restoration behavior,not original
whole-game equivalence,asynchronous scheduling,arbitraryIRQ or console proof.
"""
import argparse,ctypes as c,re,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
import geometry_records_scene_runtime_v1 as support
import check_geometry_records_structured_host_v1 as records
from check_native_deck_coordinate_v1 import symbols
from check_native_scene_reset_core_bus_v1 import Event
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
base=support.base

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 bp=V/'native-geometry-records-disc-build-v1-current.json';b=read(bp);CODE=b['shared_Deck_code_address'];ARENA=b['deck_arena_address'];resident_base=b['resident_address'];resident=Path(b['component']).read_bytes();stage=Path(b['derived_stage']).read_bytes()
 out=V/'geometry-records-whole-scene-disc-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building_reference',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,disc_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();runtime=None
 try:
  for p,h in b['source_sha256'].items():assert sha(p)==h,p
  old=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v30-scene-gpu-commands-v1';build=out/'reference-build';q=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=old,capture_output=True,text=True);(out/'reference-compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
  candidate=Path(b['directory'])/'five-build';profiles=[dict(name='v30_scene_captured_original_records',payload=(build/'native-shared.bin').read_bytes(),symbols=symbols(build/'symbols.txt')),dict(name='v33_scene_readable_records',payload=(candidate/'native-shared.bin').read_bytes(),symbols=symbols(candidate/'symbols.txt'))]
  assert len(profiles[0]['payload'])==48738 and len(profiles[1]['payload'])==54214
  assert profiles[1]['payload']==resident[CODE-resident_base:CODE-resident_base+54214]
  session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json')['instructions_decoded'];mapping+=read(session/'display-list-fullCPU-generation.json')['instructions_decoded']+read(session/'geometry-records-fullCPU-generation.json')['instructions_decoded']+[x for x in read(session/'resource-fullCPU-generation.json')['instructions_decoded']if 0xe3e0<=x['address']<0xe4aa]
  runtime=support.Runtime(V/'scene17-structured-host-v1/20261020T230553.352177Z/libscene-draw-cpu.dylib',mapping);core=runtime.core
  core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
  decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
  snapshot=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());snapshot[0x4000:0x4000+len(stage)]=stage;snapshot[resident_base:resident_base+len(resident)]=resident
  vectors=base.cases()[256:];record_cases=records.cases()
  for polls in [512,1024]:
   case=dict(base.cases()[257]);case['read_queues']=[x for x in case['read_queues']if x['address']!=0x10a684]+[dict(address=0x10a684,width=4,values=[1]*polls+[0])];case['long_completion_polls']=polls;vectors.append(case)
  for polls in [512,1024]:
   case=dict(base.cases()[257]);case['read_queues']=[x for x in case['read_queues']if x['address']!=0xf02238]+[dict(address=0xf02238,width=4,values=[0]*polls+[1])];case['long_clear_polls']=polls;vectors.append(case)
  if args.limit:vectors=[vectors[i]for i in [0,1,2,32,33,34,64,65,66,96,97,98,128,129,130,131,159,160,161,162,163,164,192,255,256,511,768,769,770,771][:args.limit]]
  rows=[];original_snapshot=bytes(snapshot);operand_cache={}
  def absolute_read(cpu,memory):
   pc=cpu.pc;key=(pc,bytes(memory[pc:pc+10]))
   if key not in operand_cache:
    instructions=list(decoder.disasm(key[1],pc,count=1));assert len(instructions)==1,('Decode',hex(pc));ins=instructions[0];operand_cache[key]=(ins.mnemonic,ins.op_str)
   mnemonic,operands=operand_cache[key];value=None
   if mnemonic in ['move.l','cmp.l','tst.l','cmpi.l']:
    parts=operands.split(', ');read_operand=parts[1]if mnemonic=='cmpi.l'else parts[0]
    a=re.fullmatch(r'\$([0-9a-f]+)\.l',read_operand)
    if a:value=int(a.group(1),16)
    a=re.fullmatch(r'\(a([0-7])\)',read_operand)
    if a:value=cpu.registers[8+int(a.group(1))]&0xffffff
   return value
  for i,case0 in enumerate(vectors):
   # Use the source case ID to retain density coverage in limited preflights.
   original_index=(case0['id']-256)if case0['id']>=256 else i;record_case=record_cases[original_index%len(record_cases)];task=0xc0928+(i%101)*1024;slot=ARENA+(i%101)*1024;sp=task+[0x3c0,0x3be,0x200][i%3]
   case=dict(case0,body=False,SR=(case0['SR']&~0x201f)|(0x2000 if i%64>=32 else 0)|(i%32));case['registers']=list(case0['registers']);case['registers'][15]=sp;case['usp']=0x170000 if case['SR']&0x2000 else sp;case['ssp']=sp if case['SR']&0x2000 else 0x1d0000
   memory=bytearray(base.fixture(records.fixture(original_snapshot,record_case),case));memory[sp-512:sp+32]=memory[base.SP-512:base.SP+32];memory[ARENA:ARENA+101*1024]=bytes([0xa5])*(101*1024)
   for n in range(101):
    for offset in [16,144,272]:memory[ARENA+n*1024+offset+114:ARENA+n*1024+offset+118]=bytes(4)
   memory[0xc0920:0xc0924]=task.to_bytes(4,'big');common=bytes(memory)
   def run(profile):
    syms=profile['symbols'];payload=profile['payload'];ram=bytearray(common);ram[CODE:CODE+54214]=payload+bytes(54214-len(payload));ram=bytes(ram);runtime.reset(ram,case,0);initial=base.queue.make_cpu(case);initial.pc=syms['biwn_v4_scene'];base.lifecycle.seed_cpu(runtime,initial)
    def symbol(name):
     found=[v for k,v in syms.items()if k==name or k.startswith(name+'.lto_priv.')];assert len(found)==1,(name,found);return found[0]
    callbacks={symbol('r16'):2,symbol('r32'):4};helper_return=syms['biwn_v4_scene_helper_return'];floor=syms['midpoint']
    poll_sites={CODE+j for j in range(0,len(payload)-7,2)if payload[j:j+8]==bytes.fromhex('4ab90010a68466f8')};assert poll_sites
    clear_sites={}
    for j in range(0,len(payload)-9,2):
     for reg in range(8):
      op=(0x2039+(reg<<9)).to_bytes(2,'big')+bytes.fromhex('00f02238')+(0xe248+reg).to_bytes(2,'big')+bytes.fromhex('64f6')
      if payload[j:j+10]==op:clear_sites[CODE+j]=reg
    assert len(clear_sites)==1
    core.vjtrace_disarm();core.vjtrace_watch_clear()
    for lo,hi in [(0xf02200,0xf0229f),(0xf03200,0xf0321f),(0x10a684,0x10a687)]:assert core.vjtrace_watch_add(lo,hi,3)>=0
    begin=core.vjtrace_ring_head();core.vjtrace_arm();low=816;record_entries=record_returns=original_steps=copy_entries=matrix_entries=matrix_submits=completion_reads=0
    for steps in range(3000000):
     cpu=runtime.cpu();pc=cpu.pc;physical_sp=cpu.registers[15]
     if pc==base.STOP:break
     assert c.c_int.in_dll(core,'vjtrace_armed').value==1,('Observer disarmed',hex(pc))
     assert resident_base<=pc<ARENA or 0x170a0<=pc<0x17326 or pc in [0xe3e0,0xe220,0xe098],('Unexpected PC',hex(pc))
     if floor<=pc<CODE+len(payload):low=min(low,physical_sp-slot);assert slot+608<=physical_sp<=slot+816,('C stack',profile['name'],hex(pc),physical_sp-slot)
     if pc==0x170a0:record_entries+=1
     if pc==0x17324:record_returns+=1
     if 0x170a0<=pc<0x17326:original_steps+=1
     if pc==syms.get('biwn_v33_records_begin'):record_entries+=1
     if pc==syms.get('biwn_v33_records_end'):record_returns+=1
     copy_entries+=pc==0xe3e0;matrix_entries+=pc==0xe220
     if pc in callbacks:runtime.inject(runtime.device.read(physical_sp+8,4),callbacks[pc])
     if pc in poll_sites:runtime.inject(0x10a684,4);completion_reads+=1
     address=absolute_read(cpu,ram)
     if address in [0xf03200,0xf03204]:runtime.inject(address,4)
     before=core.vjtrace_ring_head();core.m68k_execute(1);after=core.vjtrace_ring_head()
     for index in range(before,after):
      event=Event();assert core.vjtrace_ring_read(index,c.byref(event))
      if event.type==12 and event.who==6 and event.addr==0xf03204:
       if event.value==0x4320:
        runtime.device.write(0xf03204,0x4320);core.vjtrace_arm();runtime.command_written(0xffffffff);matrix_submits+=1
       else:runtime.command_written(event.value)
     if pc in clear_sites:
      queue=runtime.queues.get((0xf02238,4))
      if queue:core.m68k_set_reg(clear_sites[pc],queue.pop(0))
    else:raise AssertionError(('Whole scene instruction bound',hex(pc),profile['name']))
    core.vjtrace_disarm();end=core.vjtrace_ring_head();mmio=[];observed_polls=0
    for index in range(begin,end):
     event=Event();assert core.vjtrace_ring_read(index,c.byref(event))
     if event.type not in [11,12]or event.who!=6:continue
     if event.type==11 and event.addr==0x10a684:observed_polls+=1
     if 0xf02200<=event.addr<=0xf0229f or 0xf03200<=event.addr<=0xf0321f:mmio.append(['r'if event.type==11 else'w',event.addr,None if event.type==11 else event.value])
    assert observed_polls==completion_reads
    result=runtime.device.ram();assert result[CODE:CODE+54214]==ram[CODE:CODE+54214],'Shared module mutated'
    assert runtime.device.read(slot+144+114,4)==runtime.device.read(slot+144+94,4)==0
    return result,runtime.cpu(),mmio,dict(native_instructions=steps,C_stack_bytes=816-low,record_entries=record_entries,record_returns=record_returns,original_record_instructions=original_steps,copy_entries=copy_entries,matrix_entries=matrix_entries,matrix_submits=matrix_submits,completion_reads=completion_reads,remaining_queues={hex(a)+':'+str(w):values for(a,w),values in runtime.queues.items()})
   left,expected,old_bus,old_detail=run(profiles[0]);right,actual,new_bus,new_detail=run(profiles[1])
   def normalize(raw):
    value=bytearray(raw)
    # Module bytes intentionally differ; both were checked immutable per lane.
    for lo,hi in [(CODE,CODE+54214),(slot+144,slot+144+118),(slot+608,slot+816)]:value[lo:hi]=common[lo:hi]
    return bytes(value)
   same_keys=['record_entries','record_returns','copy_entries','matrix_entries','matrix_submits','completion_reads','remaining_queues']
   if bytes(expected)!=bytes(actual)or normalize(left)!=normalize(right)or old_bus!=new_bus or any(old_detail[k]!=new_detail[k]for k in same_keys):
    save(out/'counterexample.json',dict(case=case,record_case=record_case,expected_CPU=base.cd.scheduler.cpu_dict(expected),actual_CPU=base.cd.scheduler.cpu_dict(actual),RAM_differences=[hex(j)for j,(a,z)in enumerate(zip(normalize(left),normalize(right)))if a!=z][:64],reference=old_detail,candidate=new_detail,reference_bus=old_bus,candidate_bus=new_bus));raise AssertionError(out/'counterexample.json')
   assert new_detail['original_record_instructions']==0 and new_detail['record_entries']==new_detail['record_returns']
   rows.append(dict(case=case['id'],record_fixture_id=record_case['id'],CPU_nonprivate_RAM_and_mailbox_bus_match=True,reference_original_record_instructions=old_detail['original_record_instructions'],**new_detail));state.update(status='checking',completed=len(rows));mark()
   if len(rows)%16==0:print('whole scene actual providers',len(rows),'/',len(vectors),flush=True)
  save(out/'cases.json',rows);state.update(status='terminal_whole_scene_disc_provider_preflight_pass'if args.limit else'terminal_whole_scene_readable_records_actual_disc_providers_match',reference_profile=profiles[0]['name'],candidate_profile=profiles[1]['name'],maximum_C_stack_bytes=max(x['C_stack_bytes']for x in rows),native_record_calls=sum(x['record_entries']for x in rows),actual_copy_calls=sum(x['copy_entries']for x in rows),actual_matrix_calls=sum(x['matrix_entries']for x in rows),actual_matrix_submissions=sum(x['matrix_submits']for x in rows),original_record_instructions_on_candidate=0,read_values_available=False,new_arena_bytes=0,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(support.__file__),Path(support.old.__file__),Path(records.__file__),bp,Path(b['component']),Path(b['derived_stage']),build/'native-shared.bin',build/'symbols.txt',candidate/'native-shared.bin',candidate/'symbols.txt',out/'cases.json',*old.glob('*')]if p.is_file()},scope=__doc__+' Full physicalCPU/banks and2MBRAM compare except explicitly different immutable shared module and supplied current118byte context/208byteCstack. All other slots,fences,guest stacks and inherited providers compare. Ordered actual CPU MMIO addresses/writes and physical completion-read counts compare;readvalues/widths unavailable. Observer asserted armed before every CPU instruction and rearmed after synchronous originalGPU provider. No target state repair.');mark()
  if not args.limit:save(V/'geometry-records-whole-scene-disc-v1-current.json',state)
  print(state['status'],len(rows),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
 finally:
  if runtime:runtime.core.vjtrace_disarm();runtime.close()
if __name__=='__main__':main()
