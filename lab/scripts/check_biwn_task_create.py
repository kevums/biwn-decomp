"""Native full CPU creation/wrapper plus Unicorn full bus oracle."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as scheduler
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;CPU=scheduler.CPU;STOP=0x192000
RANGES={0xde5c:0xdeb6,0xdf6c:0xdf7a}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def make_cpu(case):
 cpu=CPU();cpu.registers[:]=case['registers'];cpu.pc=case['entry'];cpu.usp=case['usp'];cpu.ssp=case['ssp'];cpu.sr=case['sr'];return cpu
class Native(scheduler.Native):
 def run(self,script,case,coverage):
  self.device.seed(bytes(script.memory),0);self.lib.m68k_pulse_reset();self.lib.m68k_set_irq(0)
  self.lib.m68k_set_reg(17,0x2000);self.lib.m68k_set_reg(15,case['ssp']);self.lib.m68k_set_reg(17,0);self.lib.m68k_set_reg(15,case['usp']);self.lib.m68k_set_reg(17,case['sr'])
  for i,value in enumerate(case['registers']):self.lib.m68k_set_reg(i,value)
  self.lib.m68k_set_reg(16,case['entry']);steps=[];illegal=False
  for _ in range(128):
   pc=self.lib.m68k_get_reg(None,16)
   if pc==STOP:break
   assert any(a<=pc<b for a,b in RANGES.items()),hex(pc)
   a0=self.lib.m68k_get_reg(None,8);a1=self.lib.m68k_get_reg(None,9);sp=self.lib.m68k_get_reg(None,15)
   address={0xdf6c:sp+4,0xdf70:sp+8,0xde5c:0xc0920,0xde62:0xc0924,0xde6e:a1,0xde76:a0,0xde84:a1}.get(pc)
   if address is not None and any(q['address']==address and q['width']==4 for q in case.get('read_queues',[])):self.device.direct(address,4,script.read(address,4))
   if pc==0xdeb4:illegal=True
   coverage.add(pc);steps.append(pc);self.lib.m68k_execute(1)
  else:raise AssertionError('Native creation did not return/trap')
  cpu=CPU();cpu.registers[:]=[self.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=self.lib.m68k_get_reg(None,16);cpu.sr=self.lib.m68k_get_reg(None,17);cpu.usp=self.prefix[16]if cpu.sr&0x2000 else cpu.registers[15];cpu.ssp=cpu.registers[15]if cpu.sr&0x2000 else self.prefix[17]
  return self.device.ram(),cpu,steps,illegal
def bus_original(script,case):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory))
 for reg,value in zip(world.REGS,case['registers']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,case['sr']);cpu.reg_write(UC_M68K_REG_A7,case['registers'][15])
 def code(e,a,w,_):
  assert any(lo<=a<hi for lo,hi in RANGES.items()),hex(a)
  if a==0xdeb4:e.emu_stop()
 def read(e,t,a,w,v,_):e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):script.write(a,w,v&((1<<(w*8))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=128,timeout=500000)
 assert cpu.reg_read(UC_M68K_REG_PC)==(0xdeb4 if case['no_free']else STOP)
 assert bytes(cpu.mem_read(0,0x200000))==script.memory
 return script.trace
def bind(lib):
 fn=lib.biwn_task_create;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU)];fn.restype=c.c_int;return fn
def translated(fn,script,case,missing=None,null_cpu=False,null_bus=False):
 def reader(_,a,v):
  try:v[0]=script.read(a,4);return 0
  except Exception as error:script.errors.append(str(error));return 1
 def writer(w):
  def cb(_,a,v):
   try:script.write(a,w,v);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 callbacks=[world.R32(reader),world.W16(writer(2)),world.W32(writer(4))]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(world.R8(),world.R16(),callbacks[0],callbacks[1],callbacks[2],world.CALL(),None,0);cpu=make_cpu(case);status=fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(cpu));return status,cpu
def translated_logical(fn,script,case,missing=None,scratch=None,null_out=False):
 def read(_,a,v):
  try:v[0]=script.read(a,4);return 0
  except Exception as error:script.errors.append(str(error));return 1
 def write(width):
  def cb(_,a,v):
   try:script.write(a,width,v);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 callbacks=[world.R32(read),world.W16(write(2)),world.W32(write(4))]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(world.R8(),world.R16(),callbacks[0],callbacks[1],callbacks[2],world.CALL(),None,0)
 stack=case['registers'][15]
 values=case['registers'][:2]if case['entry']==0xde5c else[int.from_bytes(script.memory[stack+i:stack+i+4],'big')for i in[4,8]]
 output=c.c_uint32(0xa55aa55a)
 status=fn(c.byref(bus),*values,stack if scratch is None else scratch,None if null_out else c.byref(output))
 return status,output.value
def cases():
 rng=random.Random(0xde5c);rows=[]
 for i in range(1024):
  entry=0xde5c if i%2==0 else 0xdf6c;mode=0x2000 if i%4>=2 else 0;usp=0x180900;ssp=0x1d0000;stack=ssp if mode else usp
  registers=[rng.getrandbits(32)for _ in range(16)];registers[15]=stack;n=1+i%5;current=0x100000;free=0x110000
  sr=mode|(rng.randrange(0x800)&0x71f);case={'entry':entry,'registers':registers,'usp':usp,'ssp':ssp,'sr':sr,'no_free':False,'initial':[[0xc0920,4,current],[0xc0924,4,free],[0x10,4,STOP],[stack,4,STOP],[stack+4,4,rng.getrandbits(32)],[stack+8,4,rng.getrandbits(32)]],'default_helper_return':0,'read_queues':[]}
  for j in range(n):
   obj=current+j*0x1000;case['initial'] += [[obj,4,current+((j+1)%n)*0x1000],[obj+4,4,current+((j-1)%n)*0x1000]]
  for j in range(3):case['initial'].append([free+j*0x1000,4,free+(j+1)*0x1000 if j<2 else 0])
  if i%11==0:case['read_queues'].append({'address':free,'width':4,'values':[free+0x1000,current]})
  if i%13==0:case['read_queues'].append({'address':current,'width':4,'values':[current]})
  rows.append(case)
 for i in range(4):
  case=dict(rows[i]);case['initial']=list(case['initial'])+[[0xc0924,4,0]];case['no_free']=True;case['read_queues']=[];rows.append(case)
 return rows
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-task-create'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libtask-create.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_task_create.c'),'-o',str(lib)];subprocess.run(cmd,check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});fn=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opts.limit:vectors=vectors[:opts.limit]+vectors[-4:]
 logical=c.CDLL(str(lib)).biwn_task_create_logical;logical.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];logical.restype=c.c_int
 native=Native();coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});a=boundary.Script(snapshot,case);b=boundary.Script(snapshot,case);u=boundary.Script(snapshot,case);ram,cpu,steps,illegal=native.run(a,case,coverage);trace=bus_original(u,case);status,actual=translated(fn,b,case)
   if case['no_free']:
    assert status==3 and bytes(actual)==bytes(make_cpu(case))and illegal and cpu.sr&0x2000 and cpu.pc==STOP
    assert b.trace==trace and b.memory==u.memory
    frame=ram[cpu.ssp:cpu.ssp+6];assert int.from_bytes(frame[2:],'big')==0xdeb4
   else:
    if status or ram!=b.memory or bytes(cpu)!=bytes(actual)or b.trace!=trace:
     save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_CPU':scheduler.cpu_dict(cpu),'C_CPU':scheduler.cpu_dict(actual),'original_steps':[hex(x)for x in steps],'Unicorn_trace':trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
    assert not illegal;frame=None
   portable=boundary.Script(snapshot,case);logical_status,logical_d0=translated_logical(logical,portable,case);stack=case['registers'][15]
   public=lambda trace:[event for event in trace if not(event[0]in['r','w']and stack<=event[1]<stack+12)]
   assert logical_status==(3 if case['no_free']else 0)and logical_d0==(0xa55aa55a if case['no_free']else cpu.registers[0])
   assert portable.memory[:stack]==b.memory[:stack]and portable.memory[stack+12:]==b.memory[stack+12:]and public(portable.trace)==public(trace)and not portable.errors
   rows.append({'case':i,'parameters':case,'original_CPU':scheduler.cpu_dict(cpu),'C_CPU':scheduler.cpu_dict(actual),'trace':b.trace,'source_instructions':len(steps),'native_ILLEGAL_executed':illegal,'exception_frame':frame.hex()if frame else None,'logical_entry':dict(status=logical_status,D0=logical_d0,public_bus_events=len(public(trace)),public_RAM_and_bus_match=True,private_RTS_and_argument_slots_excluded=True),'comparison_scope':'Prefix bus and CNO_FREE vs actual nativeILLEGAL; exception CPU/frame not reproduced inC'if illegal else'All2MBRAM/fullCPU/SR/USP/SSP andcompletebus match'})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:native.close()
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded=[]
 for lo,hi in RANGES.items():
  part,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);decoded+=part
 addresses={x['address']if isinstance(x['address'],int)else int(x['address'],16)for x in decoded}
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(addresses&coverage),len(addresses)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(addresses&coverage),len(addresses)]}));return
 assert addresses<=coverage
 guards=[];case=vectors[1]
 for missing in range(3):
  script=boundary.Script(snapshot,case);status,cpu=translated(fn,script,case,missing=missing);assert status==1 and bytes(cpu)==bytes(make_cpu(case))and not script.trace;guards.append({'missing_callback':missing,'CPU_unchanged':True})
 for kwargs in[{'null_cpu':True},{'null_bus':True}]:
  script=boundary.Script(snapshot,case);status,cpu=translated(fn,script,case,**kwargs);assert status==1 and bytes(cpu)==bytes(make_cpu(case));guards.append({'arguments':kwargs,'rejected':True})
 bad={**case,'entry':0x17c40};assert translated(fn,boundary.Script(snapshot,bad),bad)[0]==1;guards.append({'unsupported_PC':True})
 for kind in['read','write16','write32']:
  script=boundary.Script(snapshot,case)
  if kind=='read':script.fail_read=(0xc0920,4)
  else:script.fail_write=(0x110014,2)if kind=='write16'else(0xc0924,4)
  status,cpu=translated(fn,script,case);assert status==2 and bytes(cpu)==bytes(make_cpu(case));guards.append({'failure':kind,'CPU_unchanged':True,'partial_bus_effects_retained':True})
 logical_guards=[]
 for options in[dict(missing=0),dict(missing=1),dict(missing=2),dict(scratch=0),dict(null_out=True)]:
  script=boundary.Script(snapshot,case);status,value=translated_logical(logical,script,case,**options)
  assert status==1 and value==0xa55aa55a and not script.trace
  logical_guards.append(options)
 for failure in[('fail_write',(case['registers'][15],4)),('fail_read',(0xc0920,4)),('fail_write',(0xc0924,4))]:
  script=boundary.Script(snapshot,case);setattr(script,*failure);status,value=translated_logical(logical,script,case)
  assert status==2 and value==0xa55aa55a
  logical_guards.append(dict(injected_failure=failure,status=status,output_untouched=True))
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'task_creation_wrapper_native_CPU_and_bus_match_C','directory':str(out),'native_CPU_cases':len(rows),'successful_return_cases':1024,'native_ILLEGAL_cases':4,'Unicorn_bus_cases':len(rows),'CPU_instruction_coverage':[len(addresses),len(addresses)],'host_guards':len(guards),'portable_components':2,'original_bytes':sum(hi-lo for lo,hi in RANGES.items()),'intervals':{hex(lo):hex(hi)for lo,hi in RANGES.items()},'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_task_create.c','biwn_task_create.h']},'matched':['1024normalreturns:whole2MBRAM/fullD0-D7/A0-A7/PC/SR/normalizedUSP/SSP matchnativeCPU, andcompletecallbackbustrace includingwrapperstackargs/RTS matchesUnicorn.','Free-list removal, insertion aftercurrent, successorprev/sourcepointerrereads, entry/savedPC/argument/SPinitialization and readiness resets; single/multiple ring contexts, user/supervisor modes andnonzero lowword-zero pointer.','Four empty-free-list cases executeactualnativeILLEGAL andvectorframe; Creturns explicitNO_FREE with unchangedCPU/no invented successful return andmatchingpre-exceptionbusprefix.'],'limits':['OriginalILLEGALexceptionCPU/frame is observed, not emulated byCNO_FREE host result. Added argument/bus errors retain previous effects and do not publish partialCPU.','Finite supplied task/free-list records and controlled rereads; no real pool setup/generalallocation, interrupts/concurrency, complete startup/taskset/mainloop/game orphysicalhardware proof.']};report['logical_entry_cases']=len(rows);report['logical_entry_guards']=logical_guards;report['logical_entry_scope']='Logicalcallback/parameter API reuses DE5C with privatezeroCPU seeds/RTSslot. FullpublicRAM andorderedpublicbus plusfullD0 oruntouchedoutput match original in1028cases. Only12privateRTS/argumentbytes excluded; nootherCPUABIclaim.';save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-task-create-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
