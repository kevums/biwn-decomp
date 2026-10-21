"""Original input poll versus C with exact raw MMIO/RAM traces and edges."""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_world_update as world
ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
class Script:
 def __init__(self,snapshot,case):
  self.memory=bytearray(snapshot);self.case=case;self.trace=[];self.row=0;self.select=0;self.fail_read=None;self.fail_write=None
  self.memory[0x49ba4:0x49ba8]=case['previous'].to_bytes(4,'big');self.memory[0x49bac:0x49bb0]=bytes.fromhex('a55aa55a')
 def read(self,a,w):
  if self.fail_read==(a,w,self.row)or self.fail_read==(a,w):raise RuntimeError('injected read failure')
  if a==0xf14000:
   assert w==4 and self.row<4;v=self.case['rows'][self.row];self.row+=1
  else:assert w==4 and a==0x49ba4;v=int.from_bytes(self.memory[a:a+w],'big')
  self.trace.append(['r',a,w,v]);return v
 def write(self,a,w,v):
  if self.fail_write==(a,w,self.select)or self.fail_write==(a,w):raise RuntimeError('injected write failure')
  if a==0xf14000:assert w==2 and v==[0x810e,0x810d,0x810b,0x8107][self.select];self.select+=1
  else:assert w==4 and a in[0x49ba4,0x49bac];self.memory[a:a+w]=v.to_bytes(w,'big')
  self.trace.append(['w',a,w,v])
def original(script,incoming,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf14000,0x1000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
 for reg,v in zip(world.REGS,incoming):cpu.reg_write(reg,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 def code(e,a,w,_):assert 0xe4c0<=a<0xe53c;coverage.add(a)
 def read(e,access,a,w,v,_):
  if SP-16<=a<SP+8:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-16<=a<SP+8:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0xe4c0,STOP,count=200,timeout=500000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 assert all(cpu.reg_read(reg)==v for reg,v in zip(world.REGS,incoming))
 ram=bytes(cpu.mem_read(0,0x200000));assert ram[:SP-16]==script.memory[:SP-16]and ram[SP+8:]==script.memory[SP+8:]
def translated(fn,script,missing=None):
 def read(_,a,v):
  try:v[0]=script.read(a,4);return 0
  except Exception:return 1
 def writer(width):
  def write(_,a,v):
   try:script.write(a,width,v);return 0
   except Exception:return 1
  return write
 types=[world.R32,world.W16,world.W32];callbacks=[types[0](read),types[1](writer(2)),types[2](writer(4))]
 if missing is not None:callbacks[missing]=types[missing]()
 bus=world.Bus(world.R8(),world.R16(),callbacks[0],callbacks[1],callbacks[2],world.CALL(),None,0);return fn(c.byref(bus))
def cases():
 rng=random.Random(0xe4c0);rows=[{'rows':[v]*4,'previous':p,'kind':'all_rows'}for v,p in[(0xffffffff,0),(0xffffffff,0xffffffff),(0,0),(0,0xffffffff)]]
 for row in range(4):
  for bit in range(32):
   for previous in[0,0xffffffff]:
    raw=[0xffffffff]*4;raw[row]^=1<<bit;rows.append({'rows':raw,'previous':previous,'kind':'single_raw_bit','row':row,'bit':bit})
 while len(rows)<1024:rows.append({'rows':[rng.getrandbits(32)for _ in range(4)],'previous':rng.getrandbits(32),'kind':'mixed_raw_rows'})
 return rows
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opts=parser.parse_args();out=ROOT/'verification/biwn-input-poll'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libinput.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_input_poll.c'),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 lib=c.CDLL(str(library));fn=lib.biwn_input_poll;fn.argtypes=[c.POINTER(world.Bus)];fn.restype=c.c_int;snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases();coverage=set();rng=random.Random(0x810e);rows=[]
 if opts.limit:vectors=vectors[:opts.limit]
 for i,case in enumerate(vectors):
  a=Script(snapshot,case);b=Script(snapshot,case);original(a,[rng.getrandbits(32)for _ in world.REGS],coverage);status=translated(fn,b)
  if status or a.trace!=b.trace or a.memory!=b.memory:save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_trace':a.trace,'C_trace':b.trace});raise AssertionError(str(out/'mismatch.json'))
  rows.append({'case':i,'parameters':case,'held':int.from_bytes(a.memory[0x49ba4:0x49ba8],'big'),'press_edges':int.from_bytes(a.memory[0x49bac:0x49bb0],'big'),'trace':a.trace,'RAM_trace_and_original_register_preservation_match':True})
 save(out/'fixtures.json',rows)
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out)}));return
 guards=[];assert fn(None)==1;guards.append({'null_bus':True,'status':1})
 for missing in range(3):
  script=Script(snapshot,vectors[0]);assert translated(fn,script,missing)==1 and not script.trace;guards.append({'missing_callback':missing,'status':1})
 for row in range(4):
  for kind in['fail_read','fail_write']:
   script=Script(snapshot,vectors[0]);setattr(script,kind,(0xf14000,4 if kind=='fail_read'else 2,row));assert translated(fn,script)==2;guards.append({'MMIO_failure':kind,'row':row,'status':2,'prior_effects':script.trace})
 for kind,address in[('fail_read',0x49ba4),('fail_write',0x49ba4),('fail_write',0x49bac)]:
  script=Script(snapshot,vectors[2]);setattr(script,kind,(address,4));assert translated(fn,script)==2;guards.append({'RAM_failure':kind,'address':hex(address),'status':2,'prior_effects':script.trace})
  if address==0x49bac:assert int.from_bytes(script.memory[0x49ba4:0x49ba8],'big')==0x33ff33ff
 save(out/'guards.json',guards);decoded,_=world.select.binary_tools.m68k_instructions(snapshot[0xe4c0:0xe53c],0xe4c0);missing=[x for x in decoded if x['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing});assert not missing
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'original_CPU_input_poll_matches_C','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(decoded),len(decoded)],'host_guards':len(guards),'portable_components':1,'interval':'[0xe4c0,0xe53c)','original_bytes':124,'row_select_words':['0x810e','0x810d','0x810b','0x8107'],'max_raw_row_output_mask':'0x33ff33ff','source_sha256':{name:world.select.binary_tools.sha(source/name)for name in['biwn_input_poll.c','biwn_input_poll.h']},'compiler':command,
 'matched':['Complete original CPU function, allD0-D7/A0-A6 unchanged, private stack balanced; host status separate from originalD0.','Allfour ordered word-select/long-read MMIO pairs, oldheld read and both ordered held/press-edge long stores; exact externalRAM and bus widths/values/order.','Raw active-low mask/rotations and press edges (previous XOR current) AND current; allsingle raw bits, ignored bits, arbitrary previous masks and mixed raw rows.'],
 'limits':['Scripted opaque raw MMIO values, not physicalpad/port mapping or hardware timing. FullCCR excluded.','Not linked into current task runtime at this standalone checkpoint. Added callback errors retain prior writes/stores; no realCPUbus-error proof.']}
 save(out/'status.json',{'status':'terminal_pass'});save(out/'report.json',report);save(ROOT/'verification/biwn-input-poll-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
