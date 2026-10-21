"""Original native CPU TRAP/RTE/task switches plus Unicorn pre-RTE bus oracle."""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_transition_cleanup as cleanup
import check_biwn_world_movement_pipeline as movement
ROOT=cleanup.ROOT;RANGES={0xde08:0xde5c,0xdf60:0xdf6c};STOP=0x192000
class CPU(c.Structure):_fields_=[('registers',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def copy_cpu(cpu):return CPU.from_buffer_copy(bytes(cpu))
def cpu_dict(cpu):return {'registers':list(cpu.registers),'pc':cpu.pc,'usp':cpu.usp,'ssp':cpu.ssp,'sr':cpu.sr}
def make_cpu(case):
 cpu=CPU();cpu.registers[:]=case['registers'];cpu.pc=case['entry'];cpu.usp=case['usp'];cpu.ssp=case['ssp'];cpu.sr=case['sr'];return cpu

class Native:
 def __init__(self,diagnostic_core=None):
  expected=json.loads((ROOT/'verification/biwn-movement-matrix-checks.json').read_text())['core_sha256']
  assert cleanup.world.select.binary_tools.sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib')==expected
  core=Path(diagnostic_core)if diagnostic_core else ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'
  self.device=movement.Device(core=core);self.lib=c.CDLL(str(core))
  self.lib.m68k_set_reg.argtypes=[c.c_int,c.c_uint32];self.lib.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];self.lib.m68k_get_reg.restype=c.c_uint32
  self.lib.m68k_execute.argtypes=[c.c_int];self.lib.m68k_execute.restype=c.c_int;self.lib.m68k_set_irq.argtypes=[c.c_uint32]
  # Read-only prefix, verified against pinned cpudefs.h: D/A[16],USP,ISP.
  self.prefix=(c.c_uint32*18).in_dll(self.lib,'regs')
 def original(self,script,case,coverage):
  self.device.seed(bytes(script.memory),0);self.lib.m68k_pulse_reset();self.lib.m68k_set_irq(0)
  self.lib.m68k_set_reg(17,0x2000);self.lib.m68k_set_reg(15,case['ssp']);self.lib.m68k_set_reg(17,0);self.lib.m68k_set_reg(15,case['usp']);self.lib.m68k_set_reg(17,case['sr'])
  for i,value in enumerate(case['registers']):self.lib.m68k_set_reg(i,value)
  self.lib.m68k_set_reg(16,case['entry']);steps=[]
  for _ in range(10000):
   pc=self.lib.m68k_get_reg(None,16)
   if STOP<=pc<STOP+0x20:break
   assert any(a<=pc<b for a,b in RANGES.items()),hex(pc)
   # Inject only declared external read changes before the original source
   # instruction. Branches, TRAP/RTE, stack banks and all stores run natively.
   obj=self.lib.m68k_get_reg(None,8)
   address={0xde08:0xc0920,0xde1c:obj,0xde20:obj+26,0xde26:obj+34,0xde2c:obj+22,0xde32:obj+22,0xde36:0x778cc,0xde4c:obj+16,0xde50:obj+20,0xde54:obj+12}.get(pc)
   if address is not None:
    for q in case.get('read_queues',[]):
     if q['address']==address:
      value=script.read(address,q['width']);self.device.direct(address,q['width'],value)
   coverage.add(pc);steps.append(pc);self.lib.m68k_execute(1)
  else:raise AssertionError('Original scheduler did not reach a selected continuation')
  cpu=CPU();cpu.registers[:]=[self.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=self.lib.m68k_get_reg(None,16);cpu.sr=self.lib.m68k_get_reg(None,17)
  cpu.usp=self.prefix[16]if cpu.sr&0x2000 else cpu.registers[15];cpu.ssp=cpu.registers[15]if cpu.sr&0x2000 else self.prefix[17]
  return self.device.ram(),cpu,steps
 def close(self):self.device.close()

def prefix_original(script,case):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory))
 for i,reg in enumerate(cleanup.REGS):cpu.reg_write(reg,case['registers'][i])
 cpu.reg_write(UC_M68K_REG_SR,case['sr']);cpu.reg_write(UC_M68K_REG_A7,case['registers'][15]);cpu.reg_write(UC_M68K_REG_CR_USP,case['usp'])
 def read(engine,access,a,w,v,_):engine.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(engine,access,a,w,v,_):script.write(a,w,v&((1<<(w*8))-1))
 cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0xde08,0xde5a,count=10000,timeout=500000)
 assert cpu.reg_read(UC_M68K_REG_PC)==0xde5a
 assert bytes(cpu.mem_read(0,0x200000))==script.memory
 return cpu

def bind(lib):
 functions={0xde08:lib.biwn_scheduler_dispatch,0xdf60:lib.biwn_scheduler_yield}
 for fn in functions.values():fn.argtypes=[c.POINTER(cleanup.world.Bus),c.POINTER(CPU),c.c_uint32];fn.restype=c.c_int
 return functions
def translated(functions,script,case,limit=64,missing=None,null_cpu=False):
 def reader(width):
  def callback(_,a,v):
   try:v[0]=script.read(a,width);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return callback
 def writer(width):
  def callback(_,a,v):
   try:script.write(a,width,v);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return callback
 types=[cleanup.world.R16,cleanup.world.R32,cleanup.world.W16,cleanup.world.W32];callbacks=[types[0](reader(2)),types[1](reader(4)),types[2](writer(2)),types[3](writer(4))]
 if missing is not None:callbacks[missing]=types[missing]()
 bus=cleanup.world.Bus(cleanup.world.R8(),*callbacks,cleanup.world.CALL(),None,0);cpu=make_cpu(case)
 status=functions[case['entry']](c.byref(bus),None if null_cpu else c.byref(cpu),limit);return status,cpu

def cases():
 rng=random.Random(0xde08);rows=[]
 for variant in range(256):
  for entry in RANGES:
   count=1+(variant//10)%5;current=0x100000;ssp=0x1e0000 if entry==0xdf60 else 0x1dfffa;usp=0x180900;sr=rng.randrange(0x800)&0x71f
   if entry==0xde08:sr|=0x2000
   registers=[rng.getrandbits(32)for _ in range(16)];registers[15]=ssp if entry==0xde08 else usp
   case={'entry':entry,'kind':'scheduler_'+str(variant%10),'params':[],'registers':registers,'usp':usp,'ssp':ssp,'sr':sr,'incoming':registers[:15],'initial':[[0x80,4,0xde08],[0xc0920,4,current],[0x778cc,4,10]],'default_helper_return':0}
   for i in range(count):
    obj=current+i*0x1000;stack=0x180800+i*0x1000;warm=entry==0xdf60 and variant%10!=9
    target_sr=(variant*7+i*13)&0x71f
    if entry==0xde08 and variant%7==0 and i:target_sr|=0x2000
    case['initial'] += [[obj,4,current+(i+1)%count*0x1000],[obj+12,4,stack],[obj+16,4,0xdf66 if warm else STOP+i*2],[obj+20,2,target_sr],[obj+22,4,0],[obj+26,4,0],[obj+34,4,0]]
    for j,reg in enumerate([2,3,4,5,6,7,10,11,12,13,14]):case['initial'].append([stack+j*4,4,rng.getrandbits(32)])
    case['initial'].append([stack+44,4,STOP+i*2])
   if entry==0xde08:case['initial'] += [[ssp,2,variant&0x71f],[ssp+2,4,STOP]]
   else:case['initial'].append([usp,4,STOP])
   if count>1:
    obj=current+0x1000;mode=variant%10
    if mode==1:case['initial'].append([obj+26,4,0xffffffff])
    elif mode==2:case['initial'].append([obj+34,4,1])
    elif mode==3:case['initial'].append([obj+22,4,10])
    elif mode==4:case['initial'].append([obj+22,4,11])
    elif mode==5:
     pair=[(0x80000000,0x7fffffff),(0xffffffff,0),(1,0xffffffff)][(variant//10)%3]
     case['initial'] += [[obj+22,4,pair[0]],[0x778cc,4,pair[1]]]
    elif mode==6:case['read_queues']=[{'address':obj+22,'width':4,'values':[1,20]}]
    elif mode==7:
     for i in range(count):
      if i!=1:case['initial'].append([current+i*0x1000+26,4,1])
     case['initial'].append([obj+22,4,10]);case['read_queues']=[{'address':0x778cc,'width':4,'values':[9,10]}]
    elif mode==8:
     for i in range(1,count):case['initial'].append([current+i*0x1000+26,4,1])
   rows.append(case)
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opts=parser.parse_args();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes()
 for a,b in RANGES.items():assert snapshot[a:b]==image[a-0x4000:b-0x4000]
 out=ROOT/'verification/biwn-scheduler'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libscheduler.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_scheduler.c'),'-o',str(library)]
 run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 functions=bind(c.CDLL(str(library)));vectors=cases();rows=[];coverage=set();native=Native()
 if opts.limit:vectors=vectors[:opts.limit]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=cleanup.Script(snapshot,case);b=cleanup.Script(snapshot,case);ram,cpu,steps=native.original(a,case,coverage);status,actual=translated(functions,b,case)
   if status or cpu_dict(actual)!=cpu_dict(cpu)or ram!=b.memory:
    save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_CPU':cpu_dict(cpu),'C_CPU':cpu_dict(actual),'original_steps':[hex(a)for a in steps],'C_trace':b.trace,'RAM_differences':[[j,ram[j],b.memory[j]]for j in range(len(ram))if ram[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
   if case['entry']==0xde08:
    prefix=cleanup.Script(snapshot,case);uc=prefix_original(prefix,case)
    assert b.trace[:-2]==prefix.trace and b.trace[-2:]==[['r',uc.reg_read(UC_M68K_REG_A7),2,int.from_bytes(prefix.memory[uc.reg_read(UC_M68K_REG_A7):uc.reg_read(UC_M68K_REG_A7)+2],'big')],['r',uc.reg_read(UC_M68K_REG_A7)+2,4,int.from_bytes(prefix.memory[uc.reg_read(UC_M68K_REG_A7)+2:uc.reg_read(UC_M68K_REG_A7)+6],'big')]]
    assert prefix.memory==b.memory
   rows.append({'case':i,'parameters':case,'original_CPU_instructions':len(steps),'original_steps':[hex(a)for a in steps],'CPU_state':cpu_dict(cpu),'selected_context':int.from_bytes(ram[0xc0920:0xc0924],'big'),'fresh_task_entry':case['entry']==0xdf60 and 0xdf66 not in steps,'trace':b.trace,'whole_RAM_and_full_CPU_state_match':True,'Unicorn_pre_RTE_bus_match':case['entry']==0xde08})
 finally:native.close()
 save(out/'fixtures.json',rows)
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out)}));return
 guards=[]
 for entry in RANGES:
  case=next(x for x in vectors if x['entry']==entry)
  for missing in range(4):
   script=cleanup.Script(snapshot,case);status,cpu=translated(functions,script,case,missing=missing);assert status==1 and cpu_dict(cpu)==cpu_dict(make_cpu(case))and not script.trace;guards.append({'entry':hex(entry),'missing_callback':missing})
  for arg in ['null_cpu','zero_limit']:
   script=cleanup.Script(snapshot,case);status,cpu=translated(functions,script,case,null_cpu=arg=='null_cpu',limit=0 if arg=='zero_limit'else 64);assert status==1 and cpu_dict(cpu)==cpu_dict(make_cpu(case))and not script.trace;guards.append({'entry':hex(entry),'argument':arg})
  wrong=dict(case);wrong['sr']=case['sr']^0x2000;script=cleanup.Script(snapshot,wrong);status,cpu=translated(functions,script,wrong);assert status==1 and not script.trace;guards.append({'entry':hex(entry),'wrong_mode':True})
 case=next(x for x in vectors if x['entry']==0xde08 and x['kind']=='scheduler_8');case=dict(case);case['initial']=list(case['initial'])+[[0x10001a,4,1]];script=cleanup.Script(snapshot,case);status,cpu=translated(functions,script,case,limit=2);assert status==2 and cpu_dict(cpu)==cpu_dict(make_cpu(case));guards.append({'scan_limit':2,'partial_trace':script.trace})
 case=next(x for x in vectors if x['entry']==0xdf60);case=dict(case);case['initial']=list(case['initial'])+[[0x80,4,0]];script=cleanup.Script(snapshot,case);status,cpu=translated(functions,script,case);assert status==4 and cpu_dict(cpu)==cpu_dict(make_cpu(case));guards.append({'bad_vector':True,'partial_trace':script.trace})
 for kind in ['fail_read','fail_write']:
  case=next(x for x in vectors if x['entry']==0xde08);script=cleanup.Script(snapshot,case);setattr(script,kind,(0xc0920,4)if kind=='fail_read'else(0x10000c,4));status,cpu=translated(functions,script,case);assert status==3 and cpu_dict(cpu)==cpu_dict(make_cpu(case));guards.append({'callback_failure':kind,'partial_trace':script.trace})
 save(out/'guards.json',guards);decoded=[]
 for a,b in RANGES.items():part,_=cleanup.world.select.binary_tools.m68k_instructions(image[a-0x4000:b-0x4000],a);decoded+=part
 missing=[row for row in decoded if row['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing});assert not missing
 switches=sum(row['selected_context']!=0x100000 for row in rows);fresh=sum(row['fresh_task_entry']for row in rows)
 high_bit=sum(any(t[:3]==['r',0x101016,4]and t[3]&0x80000000 for t in row['trace'])for row in rows)
 assert switches and fresh and high_bit
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'original_native_CPU_scheduler_and_yield_match_C','directory':str(out),'native_CPU_cases':len(rows),'handler_cases':sum(x['entry']==0xde08 for x in vectors),'yield_cases':sum(x['entry']==0xdf60 for x in vectors),'Unicorn_pre_RTE_bus_cases':sum(x['entry']==0xde08 for x in vectors),'different_context_cases':switches,'fresh_task_entry_cases':fresh,'high_bit_deadline_read_cases':high_bit,'host_guards':len(guards),'CPU_instruction_coverage':[len(decoded),len(decoded)],'portable_components':2,'original_bytes':sum(b-a for a,b in RANGES.items()),'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'original_TRAP_and_RTE_executed':True,'helper_stubs':0,'source_sha256':{name:cleanup.world.select.binary_tools.sha(source/name)for name in ['biwn_scheduler.c','biwn_scheduler.h']},'core_sha256':cleanup.world.select.binary_tools.sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'),'compiler':command,
 'matched':['All2MBRAM and complete D0-D7/A0-A7,PC,SR,normalizedUSP/SSP versus pinned native CPU executing originalTRAP/RTE/MOVEM/RTS.','Handler bus widths/values/order also match originalUnicorn up toRTE; final two RTE reads modeled from documented six-byte frame and nativeCPU implementation.','One-to-five linked contexts, blocked flags, unsigned deadline comparison, timer/clock rereads, wrap tocurrent, warm saved yield continuations, fresh task entry and supervisor handler returns.'],
 'limits':['No full game or linked world integration yet; C returns explicit selected CPU continuation. Other task code/host continuation dispatcher remains to be connected.','Pinned software CPU, finite privateRAM layouts, SRbits0x271f and no external interrupts/tracing/cycle timing/arbitrary aliases. Not physicalhardware or a full architecture emulator.','Native readwatch values/widths unavailable; native end-state/fullRAM proof plus separateUnicorn preRTE bus proof. Unicorn does not executeRTE. Added host limits/errors leave CPU state unchanged and retain prior memory effects.'],
 'primary_architecture_reference':{'URL':'https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf','TRAP':'printed4-188,MC68000 no format/vector word','RTE':'printed6-84,SR/PC restore'},'game_frames_executed':0}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass','cases':len(rows)});save(ROOT/'verification/biwn-scheduler-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
