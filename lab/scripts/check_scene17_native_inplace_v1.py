"""Execute structured17E0E machine code with declared bus/service providers.
Real original E03A/17F14 dependencies execute in the same pinned CPU;remaining
services retain ABI fixtures. No game/disc/IRQ/timing qualification.
"""
import argparse,ctypes as c,struct
from datetime import datetime,timezone
from pathlib import Path
import scene17_host_runtime_v1 as support
from check_native_scene_reset_core_bus_v1 import Event
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
base=support.base;CODE=0x180000;DATA=0x1e0000;CSP=0x1d0000;LOW=CSP-4096
def pack(cpu):return struct.pack('>19IH',*cpu.registers,cpu.pc,cpu.usp,cpu.ssp,cpu.sr)
def unpack(raw):
 values=struct.unpack('>19IH',raw);s=base.CPU();s.registers[:]=values[:16];s.pc,s.usp,s.ssp,s.sr=values[16:];return s
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=64);args=ap.parse_args();assert 1<=args.limit<=64
 bp=V/'scene17-native-inplace-build-v1-current.json';b=read(bp);payload=Path(b['payload']).read_bytes();syms=b['symbols'];out=V/'scene17-native-inplace-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);state=dict(status='checking',directory=str(out),completed=0,new_predictions=0,new_training=False,game_image_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();runtime=support.Runtime(V/'scene17-structured-host-v1/20261020T230553.352177Z/libscene-draw-cpu.dylib',mapping['instructions_decoded']);core=runtime.core;rows=[]
 def seed(s):base.lifecycle.seed_cpu(runtime,s)
 def read_cpu(at):return unpack(runtime.device.ram()[at:at+78])
 def write_cpu(at,s):
  raw=pack(s)
  for offset in range(0,76,4):runtime.device.direct(at+offset,4,int.from_bytes(raw[offset:offset+4],'big'))
  runtime.device.direct(at+76,2,int.from_bytes(raw[76:78],'big'))
 def word(a):return runtime.device.read(a,4)
 core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
 def dependency(initial,case):
  end={0xe03a:0xe096,0x17f14:0x17f66}[initial.pc];seed(initial)
  for _ in range(10000):
   pc=core.m68k_get_reg(None,16)
   if pc==end:return runtime.cpu()
   if pc in base.queue.SCRIPTS:
    s=runtime.cpu();runtime.scripted(s,pc)
    for reg in [0,1,8,9]:core.m68k_set_reg(reg,s.registers[reg])
    core.m68k_set_reg(17,s.sr)
   else:assert pc in runtime.rows,hex(pc)
   core.m68k_execute(1)
   if pc==0xe03e:
    values=runtime.queues.get((0xf02238,4))
    if values:core.m68k_set_reg(0,values.pop(0))
  raise AssertionError('native dependency bound')
 try:
  for i,case0 in enumerate(base.cases()[256:256+args.limit]):
   case=dict(case0,SR=(case0['SR']&~0x201f)|(0x2000 if i>=32 else 0)|(i%32));case['usp']=0x170000 if case['SR']&0x2000 else base.SP;case['ssp']=base.SP if case['SR']&0x2000 else 0x1d0000
   memory=bytearray(base.fixture(snapshot,case));memory[CODE:CODE+len(payload)]=payload;memory[LOW-16:CSP+32]=bytes([0xa5])*(CSP+48-LOW);logical=base.queue.make_cpu(case);memory[DATA:DATA+98]=bytes(4)+pack(logical)+bytes(16);memory[CSP:CSP+12]=struct.pack('>3I',base.STOP,DATA,int(case['body']));ram=bytes(memory);expected,cpu,original=runtime.native(ram,case,set())
   runtime.reset(ram,case,0)
   for target in base.queue.SCRIPTS:runtime.device.direct(target,2,0x4e75)
   physical=base.CPU();physical.registers[:]=[(0x1234567*(n+1))&0xffffffff for n in range(15)]+[CSP];physical.pc=syms['run'];physical.sr=0;physical.usp=CSP;physical.ssp=0x1c8000;seed(physical)
   counts=dict(read8=0,read16=0,read32=0,write16=0,write32=0,service=0);provider_depth={name:0 for name in counts};minimum=CSP;providers={syms['native_'+name]:name for name in counts};core.vjtrace_disarm();core.vjtrace_watch_clear()
   for a,z in [(base.SP-128,base.SP+3),(0x49b88,0x49b8b)]:assert core.vjtrace_watch_add(a,z,3)>=0
   begin=core.vjtrace_ring_head();core.vjtrace_arm()
   for step in range(100000):
    current=runtime.cpu();pc=current.pc;sp=current.registers[15]
    if pc==base.STOP:break
    assert CODE<=pc<CODE+len(payload),('unexpected native PC',hex(pc));assert LOW<=sp<=CSP;minimum=min(minimum,sp)
    if pc in providers:
     name=providers[pc];counts[name]+=1;provider_depth[name]=max(provider_depth[name],CSP-sp);ret=word(sp);assert CODE<=ret<CODE+len(payload);a=word(sp+8)
     if name.startswith('read'):
      width=int(name[4:])//8;at=word(sp+12);assert LOW<=at and at+width<=CSP;runtime.device.direct(at,width,runtime.read(a,width))
     elif name.startswith('write'):
      width=int(name[5:])//8;value=word(sp+12)&((1<<(8*width))-1);runtime.write(a,width,value)
     else:
      at=word(sp+12);target=word(sp+16);assert (LOW<=at and at+78<=CSP)or at==DATA+4;guest=read_cpu(at);assert guest.pc==target
      if target in base.queue.ENTRIES:
       row=dict(target=target,actual_body=True,incoming=base.cd.scheduler.cpu_dict(guest));runtime.calls.append(row);guest=dependency(guest,case);row['return']=base.cd.scheduler.cpu_dict(guest)
      else:assert target in base.queue.SCRIPTS;runtime.scripted(guest,target)
      write_cpu(at,guest)
     current.pc=ret;current.registers[0]=0;current.registers[15]+=4;current.usp=current.registers[15];seed(current);continue
    core.m68k_execute(1)
   else:raise AssertionError('compiled body bound')
   core.vjtrace_disarm();end=core.vjtrace_ring_head();actual=runtime.device.ram();got=unpack(actual[DATA+4:DATA+82]);done=runtime.cpu();assert done.registers[0]==0 and done.registers[15]==CSP+4
   assert word(DATA)==syms['memory']and word(DATA+82)==syms['native_service']and word(DATA+86)==0 and word(DATA+90)<=128 and word(DATA+94)==0
   for reg in [*range(2,8),*range(10,15)]:assert done.registers[reg]==physical.registers[reg],('C ABI',i,reg)
   def normalize(raw):
    value=bytearray(raw);value[LOW:CSP+12]=ram[LOW:CSP+12];value[DATA:DATA+98]=ram[DATA:DATA+98]
    for target in base.queue.SCRIPTS:value[target:target+2]=ram[target:target+2]
    return bytes(value)
   if bytes(got)!=bytes(cpu)or normalize(expected)!=normalize(actual)or runtime.calls!=original['calls']:
    save(out/'counterexample.json',dict(case=case,expected_CPU=base.cd.scheduler.cpu_dict(cpu),actual_CPU=base.cd.scheduler.cpu_dict(got),RAM_differences=[hex(a)for a,(x,y)in enumerate(zip(normalize(expected),normalize(actual)))if x!=y][:30],original_calls=original['calls'],native_calls=runtime.calls));raise AssertionError(out/'counterexample.json')
   assert actual[CODE:CODE+len(payload)]==payload and actual[LOW-16:LOW]==ram[LOW-16:LOW]and actual[CSP+12:CSP+32]==ram[CSP+12:CSP+32]
   clear_events=[]
   for n in range(begin,end):
    e=Event();assert core.vjtrace_ring_read(n,c.byref(e))
    if e.type in [11,12]and e.who==6 and CODE<=e.pc<CODE+len(payload):
     opcode=int.from_bytes(payload[e.pc-CODE:e.pc-CODE+2],'big')
     if opcode&0xff00==0x4200:clear_events.append(dict(kind='r'if e.type==11 else'w',address=e.addr,value=e.value,PC=hex(e.pc)))
   expected_clrs=sum(pc in [0x17e1e,0x17e2c,0x17f02]for pc in original['steps']);assert [e['kind']for e in clear_events]==['r','w']*expected_clrs,(i,expected_clrs,clear_events)
   assert all(e['value']==0 for e in clear_events if e['kind']=='w');save(out/f'CLR-{i}.json',clear_events);rows.append(dict(case=i,original_case_id=case['id'],supervisor=bool(case['SR']&0x2000),CCR=case['SR']&31,full_CPU_nonfixture_RAM_helper_entries_match=True,C_ABI_preserved=True,native_instructions=step,physical_C_stack_bytes=CSP-minimum,provider_C_stack_bytes=provider_depth,actual_native_CLR_pairs=expected_clrs,providers=counts));state['completed']=len(rows);mark()
   if len(rows)%16==0:print('native scene',len(rows),flush=True)
 finally:core.vjtrace_disarm();runtime.close()
 save(out/'cases.json',rows);src=ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-draw-structured-v1';paths=[Path(__file__),Path(support.__file__),Path(base.__file__),bp,Path(b['payload']),*list(src.glob('*')),out/'cases.json',*out.glob('CLR-*.json')];state.update(status='terminal_readable_scene17_native_component_cases_match',target_C_machine_code_executed=True,completed=len(rows),all32CCR_both_banks=args.limit==64,maximum_C_stack_bytes=max(x['physical_C_stack_bytes']for x in rows),actual_native_CLR_pairs=sum(x['actual_native_CLR_pairs']for x in rows),payload_bytes=len(payload),payload_sha256=sha(b['payload']),source_sha256={str(p):sha(p)for p in paths if p.is_file()},scope=__doc__+'Host fixture intercepts external bus/service entries;Cbody/flag/stack code executes on68000. Original clear/rotation bodies execute,other helpers declared. Only privateCstack/CPUbuffer and declared helperRTSstubs normalized. CLRphysicalread/writepairs independently observed;readvalues unavailable. No image/IRQ/timing/console proof.');mark();save(V/'scene17-native-inplace-v1-current.json',state);print(state['status'],len(rows),state['maximum_C_stack_bytes'])
if __name__=='__main__':main()
