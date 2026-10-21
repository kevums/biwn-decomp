"""Original E26C/E098+resident dispatcher+GPU4720 versus all-source C.

Source resident context and read-triggered progression are explicit fixtures.
No initial/publish/poll completion flags are synthesized by the host.
"""
import argparse,ctypes as c,hashlib,json,os,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_movie_GPU as gpu
import check_biwn_retained_merchant_movement as joined
import check_biwn_gpu_dispatcher as dispatch
ROOT=gpu.ROOT;media=gpu.media;SP=0x1ff000;STOP=0x190000
sha=lambda data:hashlib.sha256(data).hexdigest()
class Device:
 def __init__(self,library):
  session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text());proof=json.loads((ROOT/'verification/biwn-media-setup-cpu-checks.json').read_text());self.runtime=media.Runtime(Path(proof['directory'])/'libmedia-setup.dylib',setup['instructions_decoded']);self.core=self.runtime.core;self.lib=c.CDLL(str(library))
  self.core.GPUExec.argtypes=[c.c_int32];self.core.GPUGetPC.restype=c.c_uint32;self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32;self.core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadWord.restype=c.c_uint16;self.core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];self.core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];self.core.GPUStateLoad.argtypes=[c.c_void_p];self.core.GPUStateLoad.restype=c.c_size_t
  self.counter=c.c_uint32.in_dll(self.core,'gpu_exec_opcode_count');self.dispatch=self.lib.biwn_gpu_dispatcher_run;self.dispatch.argtypes=[c.POINTER(dispatch.Bus),c.POINTER(dispatch.State),c.c_uint32,c.c_uint32];self.dispatch.restype=c.c_int
  self.kernel=self.lib.biwn_gpu_command4720_run;self.kernel.argtypes=[c.POINTER(joined.MovementBus),c.POINTER(gpu.State),c.c_uint32];self.kernel.restype=c.c_int
  def rd32(_,a,out):
   out[0]=int.from_bytes(bytes(self.s.local_RAM[a-0xf03000:a-0xf03000+4]),'big')if 0xf03000<=a<=0xf03ffc else self.core.GPUReadLong(a,3);return 0
  def wr32(_,a,value):
   self.core.GPUWriteLong(a,value,3)
   if 0xf03000<=a<=0xf03ffc:self.s.local_RAM[a-0xf03000:a-0xf03000+4]=value.to_bytes(4,'big')
   return 0
  def rd16(_,a,out):out[0]=self.core.GPUReadWord(a,3);return 0
  def wr16(_,a,value):self.core.GPUWriteWord(a,value,3);return 0
  self.dispatch_cb=[dispatch.R32(rd32),dispatch.W32(wr32),dispatch.TRACE(lambda _,pc,z,carry,n:self.pcs.append(pc))];self.dispatch_bus=dispatch.Bus(*self.dispatch_cb,None)
  self.kernel_cb=[gpu.R16(rd16),gpu.R32(rd32),joined.W16(wr16),gpu.W32(wr32),gpu.OBS(lambda _,pc:self.pcs.append(pc))];self.kernel_bus=joined.MovementBus(*self.kernel_cb,None)
 def prepare(self,ram,initial,case,mode):
  self.runtime.reset(ram,case['seed']);raw,_=joined.video.gpu_state(self.core);buffer=c.create_string_buffer(gpu.logical(initial)+raw[4396:]);assert self.core.GPUStateLoad(buffer)==len(raw);self.s=gpu.State.from_buffer_copy(bytes(initial));self.mode=mode;self.case=case;self.trace=[];self.stages=[];self.pcs=[];self.ready=False;self.published=False;self.loaded=False;self.finished=False;self.polls=[0,0,0];self.start_count=self.counter.value
 def stage(self,name):
  self.pcs=[];delays=0
  if self.mode=='original':
   image=c.string_at(self.core.GPUGetRAM(),4096)
   for _ in range(10000):
    pc=self.core.GPUGetPC()
    if name=='kernel':stop=pc==0xf031be
    else:stop=not 0xf031be<=pc<0xf03200 or(name!='load'and pc==0xf031ce and self.core.GPUReadLong(0xf03204,6)==0xffffffff and self.core.GPUReadLong(0xf03200,6)==0)
    if stop:break
    self.pcs.append(pc);word=int.from_bytes(image[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
    if word>>10 in [52,53]and self.core.GPUGetPC()!=pc+2:delays+=1
   else:raise AssertionError('Native GPU stage bound '+name)
   raw=joined.video.gpu_state(self.core)[0][:4396];count=len(self.pcs)+delays
  else:
   old=self.counter.value
   if name=='kernel':
    begin=self.s.instructions;assert self.kernel(c.byref(self.kernel_bus),c.byref(self.s),10000)==0;count=self.s.instructions-begin
   else:
    state=dispatch.State();state.registers[:]=self.s.registers
    for key in ['pc','z','c','n']:setattr(state,key,getattr(self.s,key))
    assert self.dispatch(c.byref(self.dispatch_bus),c.byref(state),10000,int(name!='load'))==0
    self.s.registers[:]=state.registers
    for key in ['pc','z','c','n']:setattr(self.s,key,getattr(state,key))
    self.s.instructions+=state.instructions;count=state.instructions
   assert self.counter.value==old;raw=gpu.logical(self.s)
  self.stages.append(dict(stage=name,PCs=list(self.pcs),instructions=count,logical_GPU_sha256=sha(raw),main_RAM_sha256=sha(self.runtime.device.ram())));return raw
 def read(self,a,width):
  if a==0xf03200 and not self.ready:
   if self.polls[0]>=self.case['delays'][0]:self.stage('initial_idle');self.ready=True
   self.polls[0]+=1
  if a==0xf03204 and self.published and not self.loaded:
   if self.polls[1]>=self.case['delays'][1]:self.stage('load');self.loaded=True;assert(self.core.GPUGetPC()if self.mode=='original'else self.s.pc)==0xf03240
   self.polls[1]+=1
  if a==0xf03200 and self.loaded and not self.finished:
   if self.polls[2]>=self.case['delays'][2]:self.stage('kernel');self.stage('return_idle');self.finished=True
   self.polls[2]+=1
  value=self.runtime.readers[width](a)&((1<<(8*width))-1);self.trace.append(['r',a,width,value]);return value
 def write(self,a,width,value):
  self.trace.append(['w',a,width,value]);self.runtime.writers[width](a,value)
  if 0xf03000<=a<=0xf03ffc:self.s.local_RAM[a-0xf03000:a-0xf03000+width]=value.to_bytes(width,'big')
  if a==0xf03204 and value==0x4720:self.published=True
 def output(self):
  raw=joined.video.gpu_state(self.core)[0][:4396]if self.mode=='original'else gpu.logical(self.s)
  if self.mode=='C':assert self.counter.value==self.start_count
  assert self.finished and len(self.stages)==4
  return dict(GPU=sha(raw),RAM=sha(self.runtime.device.ram()),stages=self.stages,CPU_bus=self.trace,polls=self.polls)
 def close(self):self.runtime.oracle.close()

def original(device,ram,initial,case,coverage):
 device.prepare(ram,initial,case,'original');cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,ram)
 for register,value in zip(media.REGS,case['registers']):cpu.reg_write(register,value)
 cpu.reg_write(UC_M68K_REG_SR,case['SR']);cpu.reg_write(UC_M68K_REG_A7,SP)
 def code(e,a,w,_):assert 0xe26c<=a<=0xe2b6 or 0xe098<=a<=0xe0a4,hex(a);coverage.add(a)
 def read(e,t,a,width,value,_):e.mem_write(a,device.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):device.write(a,width,value&((1<<(width*8))-1))
 h=cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0xe26c,STOP,count=10000,timeout=3000000);assert cpu.reg_read(UC_M68K_REG_PC)==STOP
 registers=[cpu.reg_read(r)for r in media.REGS];state=dict(registers=registers,PC=STOP,usp=case['usp']if case['SR']&0x2000 else SP+4,ssp=SP+4 if case['SR']&0x2000 else case['ssp']);result=device.output();cpu.hook_del(h);cpu.mem_write(STOP,b'\x40\xc7');cpu.emu_start(STOP,STOP+2,count=1);state['SR']=cpu.reg_read(UC_M68K_REG_D7)&65535;return state,result

def translated(fn,device,ram,initial,case):
 device.prepare(ram,initial,case,'C');errors=[]
 def read(_,a,out):
  try:out[0]=device.read(a,4);return 0
  except Exception as error:errors.append(repr(error));return 1
 def write(_,a,value):
  try:device.write(a,4,value);return 0
  except Exception as error:errors.append(repr(error));return 1
 callbacks=[media.Bus._fields_[2][1](read),media.Bus._fields_[4][1](write)];w=media.scheduler.cleanup.world;bus=media.Bus(w.R8(),w.R16(),callbacks[0],w.W16(),callbacks[1],w.CALL(),None,0);cpu=media.CPU();cpu.registers[:]=case['registers'];cpu.pc=0xe26c;cpu.sr=case['SR'];cpu.usp=case['usp'];cpu.ssp=case['ssp'];status=fn(c.byref(bus),c.byref(cpu),1000);assert status==0 and not errors,(status,errors)
 return dict(registers=list(cpu.registers),PC=cpu.pc,SR=cpu.sr,usp=cpu.usp,ssp=cpu.ssp),device.output()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/GPU4720-CPU-dispatch'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);src=ROOT/'projects/black-ice-white-noise/restoration';dispatch_proof=json.loads((ROOT/'verification/biwn-gpu-dispatcher-candidate-checks.json').read_text());dispatch_source=Path(dispatch_proof['candidate_directory'])/'biwn_gpu_dispatcher.c';library=out/'libGPU4720-CPU-dispatch.dylib';sources=[src/'biwn_gpu4720_submit_cpu.c',src/'biwn_gpu_command4720.c',dispatch_source]
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(p)for p in sources],'-o',str(library)];built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
 lib=c.CDLL(str(library));fn=lib.biwn_gpu4720_submit_cpu_call;fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];fn.restype=c.c_int;device=Device(library);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0xe26c4720);rows=[];coverage=set()
 try:
  for i in range(opt.limit or 128):
   params=[0x80080,*[rng.getrandbits(32)for _ in range(3)],[0,1,0x7fff,0x8000,0xffff,0x12340000,0xffffffff][i%7]];case=dict(params=params,registers=[rng.getrandbits(32)for _ in range(15)]+[SP],SR=(0x2000 if i%2 else 0)|rng.randrange(32)|((i%8)<<8),usp=0x180000 if i%2 else SP,ssp=SP if i%2 else 0x1d0000,seed=i%3,cache_hit=bool((i//2)%2),delays=[i%4,(i//4)%4,(i//16)%4])
   ram=bytearray(snapshot);ram[0x80080:0x800c0]=rng.randbytes(64);ram[SP:SP+24]=STOP.to_bytes(4,'big')+b''.join(p.to_bytes(4,'big')for p in params);device.runtime.reset(bytes(ram),case['seed']);raw,_=joined.video.gpu_state(device.core);initial=gpu.state_from_raw(raw);initial.local_RAM[:512]=ram[0x40a8:0x42a8]
   if case['cache_hit']:initial.local_RAM[0x240:0x240+968]=ram[0x4728:0x4af0]
   for off,value in [(0x200,0x12345678),(0x204,0xffffffff),(0x208,0x4720 if case['cache_hit']else 0x52e0)]:initial.local_RAM[off:off+4]=value.to_bytes(4,'big')
   for bank in range(2):
    for register in range(32):initial.registers[bank][register]=rng.getrandbits(32)
   initial.pc=0xf031be;initial.active_bank=0;initial.control=0x2801;initial.flags=0xd0;initial.z=i&1;initial.c=(i>>1)&1;initial.n=(i>>2)&1
   a,left=original(device,bytes(ram),initial,case,coverage);b,right=translated(fn,device,bytes(ram),initial,case)
   if a!=b or left!=right:
    (out/'mismatch.json').write_text(json.dumps(dict(case=case,original_CPU=a,C_CPU=b,original=left,C=right),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
   rows.append(dict(case=i,params=params,CPU=a,polls=left['polls'],stages=left['stages'],CPU_bus_sha256=sha(json.dumps(left['CPU_bus']).encode()),GPU_sha256=left['GPU'],RAM_sha256=left['RAM'],original_GPU_executed_on_C_path=0));(out/'progress.json').write_text(json.dumps(dict(completed=i+1,total=opt.limit or 128))+'\n')
 finally:device.close()
 (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='preflight_pass'if opt.limit else'CPU_E26C_dispatcher_GPU4720_original_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),CPU_instruction_addresses=sorted(coverage),source_sha256={str(p):sha(p.read_bytes())for p in sources},both_CPU_stack_banks_checked=True,cache_copy_and_hit_checked=True,delayed_polling_checked=True,original_GPU_on_C_path=0,new_training=False,scope='Original E26C/E098 instructions inUnicorn+native resident dispatcher/GPU4720 versus C CPU/dispatcher/kernel. FullCPU/SR/activebank/privateRAM,finallogicalGPU/mainRAM,orderedCPUbus and stagePC/count/state hashes compare. Declared source-loaded resident context and status-read-triggered GPU progression; not asynchronous cycle scheduling,fullGPUboot,physicalhardware,naturalgameplay or seven-scene integration.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if not opt.limit:(ROOT/'verification/GPU4720-CPU-dispatch-current.json').write_text(json.dumps(report,indent=2)+'\n')
 print(report['status'],len(rows),'CPUaddresses',len(coverage),flush=True)
if __name__=='__main__':main()
