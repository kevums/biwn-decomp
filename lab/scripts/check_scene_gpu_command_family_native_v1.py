"""Six structured GPU mailbox bodies executing compiled68000 code.
Declared mailbox inputs;full final logicalCPU,nonprivateRAM and actual bus order.
"""
import argparse,ctypes as c,os,re,subprocess
from pathlib import Path
from datetime import datetime,timezone
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
import check_scene_gpu_command_family_host_v1 as host
from check_native_scene_reset_core_bus_v1 import Event
from check_native_deck_coordinate_v1 import symbols
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v30-scene-gpu-commands-v1'
CODE=0x180000;ARENA=0x1b0000;SLOTS=101;STRIDE=1024;OFFSET=144;LOWER=608;TOP=816
def pack(cpu):return b''.join(int(v).to_bytes(4,'big')for v in list(cpu.registers)+[cpu.pc,cpu.usp,cpu.ssp])+int(cpu.sr).to_bytes(2,'big')
def unpack(raw):
 cpu=host.CPU();cpu.registers[:]=[int.from_bytes(raw[i:i+4],'big')for i in range(0,64,4)];cpu.pc=int.from_bytes(raw[64:68],'big');cpu.usp=int.from_bytes(raw[68:72],'big');cpu.ssp=int.from_bytes(raw[72:76],'big');cpu.sr=int.from_bytes(raw[76:78],'big');return cpu

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args();out=V/'scene-gpu-command-family-native-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,game_image_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();runtime=None
 try:
  gp=V/'scene-gpu-command-family-host-v1-current.json';g=read(gp);assert g['completed']==768
  for p,h in g['source_sha256'].items():assert sha(p)==h,p
  build=out/'build';q=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
  payload=(build/'native-shared.bin').read_bytes();syms=symbols(build/'symbols.txt');entry=next(v for k,v in syms.items()if k=='scene_gpu_family_body'or k.startswith('scene_gpu_family_body.lto_priv.'));assert CODE+len(payload)<ARENA
  reads={}
  for ins in Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(payload,CODE):
   match=re.fullmatch(r'\(a([0-7])\), d[0-7]',ins.op_str)
   if ins.mnemonic=='move.l'and match:reads[ins.address]=8+int(match.group(1))
  assert reads,'No forced native MOVE read sites decoded'
  snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();instructions,_=host.queue.cd.gen.base.binary_tools.m68k_instructions(snapshot[0xe098:0xe220],0xe098)
  runtime=host.Runtime(g['library'],instructions);core=runtime.core
  core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
  def arm():
   core.vjtrace_disarm();core.vjtrace_watch_clear()
   for lo,hi in [(0,CODE-1),(CODE+len(payload),ARENA-1),(ARENA+SLOTS*STRIDE,0x1fffff),(0xf03200,0xf0321f)]:
    if lo<=hi:assert core.vjtrace_watch_add(lo,hi,3)>=0
   begin=core.vjtrace_ring_head();core.vjtrace_arm();return begin
  def events(begin,original=False):
   core.vjtrace_disarm();rows=[]
   for n in range(begin,core.vjtrace_ring_head()):
    e=Event();assert core.vjtrace_ring_read(n,c.byref(e))
    if e.type not in [11,12]or e.who!=6:continue
    if original and not 0xe098<=e.pc<0xe220:continue
    if 0xe098<=e.addr<0xe220 or host.STOP<=e.addr<host.STOP+4:continue
    rows.append(['r'if e.type==11 else'w',e.addr,None if e.type==11 else e.value])
   return rows
  vectors=[dict(x,body=True)for x in host.cases()];vectors=vectors[:args.limit]if args.limit else vectors;rows=[];maximum=0;coverage=set();fixture_reads=0
  for i,case in enumerate(vectors):
   slot=ARENA+(i%SLOTS)*STRIDE;ctx=slot+OFFSET;csp=slot+TOP-8;memory=bytearray(host.fixture(snapshot,case));memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
   initial=host.queue.make_cpu(case);memory[ctx:ctx+98]=next(v for k,v in syms.items()if k=='memory'or k.startswith('memory.lto_priv.')).to_bytes(4,'big')+pack(initial)+bytes(16);memory[csp:csp+8]=host.STOP.to_bytes(4,'big')+ctx.to_bytes(4,'big');ram=bytes(memory)
   begin=arm();left,expected,original=runtime.native(ram,case,coverage);original_bus=events(begin,True)
   runtime.reset(ram,case,0);physical=host.queue.make_cpu(case);physical.pc=entry;physical.registers[15]=csp;physical.sr=case['SR']&0x2000
   if physical.sr:physical.ssp=csp
   else:physical.usp=csp
   host.queue.lifecycle.seed_cpu(runtime,physical);begin=arm();low=TOP;injected=0
   for steps in range(200000):
    current=runtime.cpu();pc=current.pc
    if pc==host.STOP:break
    assert CODE<=pc<CODE+len(payload),('Native body escaped module',hex(pc))
    low=min(low,current.registers[15]-slot);assert current.registers[15]>=slot+LOWER,('Native C stack exceeds partition',i,current.registers[15]-slot)
    if pc in reads:
     address=current.registers[reads[pc]]&0xffffff
     if runtime.queues.get((address,4)):runtime.inject(address,4);injected+=1
    core.m68k_execute(1)
   else:raise AssertionError('Native GPU-family fixture instruction bound')
   native_bus=events(begin);right=runtime.device.ram();actual=unpack(right[ctx+4:ctx+82]);error=int.from_bytes(right[ctx+94:ctx+98],'big');maximum=max(maximum,TOP-low);fixture_reads+=injected
   def normal(raw):
    value=bytearray(raw)
    for lo,hi in [(ctx,ctx+98),(slot+LOWER,slot+TOP)]:value[lo:hi]=ram[lo:hi]
    return bytes(value)
   valid=not error and bytes(expected)==bytes(actual)and normal(left)==normal(right)and original_bus==native_bus
   if not valid:
    save(out/'counterexample.json',dict(case=case,native_error=error,expected_CPU=host.queue.cd.scheduler.cpu_dict(expected),actual_CPU=host.queue.cd.scheduler.cpu_dict(actual),original_bus=original_bus,native_bus=native_bus,RAM_differences=[hex(n)for n,(a,b)in enumerate(zip(normal(left),normal(right)))if a!=b][:24],injected_fixture_reads=injected,C_stack_bytes=TOP-low));raise AssertionError(out/'counterexample.json')
   assert current.registers[15]==csp+4
   if i<12:save(out/f'bus-{i}.json',dict(original=original_bus,native=native_bus))
   rows.append(dict(case=case['id'],entry=hex(case['entry']),CCR=case['SR']&31,supervisor=bool(case['SR']&0x2000),native_instructions=steps,original_instructions=len(original['steps']),C_stack_bytes=TOP-low,declared_mailbox_read_fixture_injections=injected,actual_data_bus_events=len(native_bus),full_CPU_nonprivate_RAM_and_actual_bus_order_match=True));state.update(status='checking',completed=len(rows));mark()
   if len(rows)%64==0:print('GPU family native',len(rows),'/',len(vectors),flush=True)
  save(out/'cases.json',rows);save(out/'vectors.json',vectors)
  paths=[Path(__file__),Path(host.__file__),gp,*SRC.rglob('*'),*host.SRC.iterdir(),build/'native-shared.bin',out/'cases.json',out/'vectors.json',*out.glob('bus-*.json')]
  state.update(status='terminal_gpu_family_native_body_preflight'if args.limit else'terminal_six_gpu_family_native_CPU_RAM_and_bus_order_pass',payload=str(build/'native-shared.bin'),payload_sha256=sha(build/'native-shared.bin'),payload_bytes=len(payload),symbols=syms,body_only=True,maximum_C_stack_bytes=maximum,C_stack_reserved=208,native_read_sites=len(reads),declared_mailbox_fixture_injections=fixture_reads,original_function_instructions_on_native_path=0,source_instruction_locations=len(coverage),source_sha256={str(p):sha(p)for p in paths if p.is_file()},scope=__doc__+' Body-only entry,not shared entry/capture integration. Original functions do not execute on native lane. Complete2MBRAM except supplied98bytecontext and208byteCstack;allother slots/fencesremainchecked. Target data-bus readaddress/order/count andwritevalues compare;recorderwidths/readvaluesunavailable. HostdualCPUgate supplieswidth/value andinternalwaitstatecoverage. Mailbox values supplied before actual original/native reads as declared fixtures;no hostCPU mutation afterinitialseeding. Targetwork hasno artificialdeadline. NoGPUexecution,IRQ,disc/gameplay/console proof.')
  mark()
  if not args.limit:save(V/'scene-gpu-command-family-native-v1-current.json',state)
  print(state['status'],len(rows),maximum,len(payload),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
 finally:
  if runtime:runtime.core.vjtrace_disarm();runtime.close()
if __name__=='__main__':main()
