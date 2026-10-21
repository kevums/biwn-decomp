"""Constructor with all recovered C helpers and actual preserved-disc loading."""
import ctypes as c,json,hashlib,random,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_resources_native as native
import check_local_slot_clear as slot
import check_scene_device_initialize as device_check
resources=native.resources;memory=native.memory;world=native.world;ROOT=native.ROOT;SP=native.SP;STOP=native.STOP;SCRATCH=SP-32
for entry,end in [(0x10990,0x10a6a),(0x10968,0x10990),(0x11762,0x11808),(0x10a6a,0x10ba4),(0x1ae88,0x1aeda),(0x1ac68,0x1ae56),(0x18160,0x181da)]:resources.RANGES[entry]=end
STUBS=native.STUBS;WIDTHS={**native.WIDTHS,0x1aa40:[2],0x18160:[],0x10a6a:[2],0x10968:[2,2],0x11762:[2,4,4,4],0x1ae88:[2],0x1ac68:[2]};Position=native.Position
Disc=native.Disc;get=native.get;masked=native.masked;save=native.save
class OriginalRetry(RuntimeError):pass
class Runtime(native.prior.Runtime):
 def __init__(self,lib):
  super().__init__(lib);self.acquisition=self.lib.biwn_frame_resource_acquire;self.acquisition.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];self.acquisition.restype=c.c_int;self.initialize=self.lib.biwn_scene_initial_setup;self.initialize.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];self.initialize.restype=c.c_int;self.selector=self.lib.biwn_scene_select;self.selector.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];self.selector.restype=c.c_int;self.release=self.lib.biwn_frame_reference_release;self.release.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];self.release.restype=c.c_int;self.device_initialize=self.lib.biwn_scene_device_initialize;self.device_initialize.argtypes=[c.POINTER(world.Bus),c.POINTER(c.c_uint32)];self.device_initialize.restype=c.c_int;self.insert=self.lib.biwn_scene_record_insert;self.insert.argtypes=[c.POINTER(world.Bus),c.c_uint16,*[c.c_uint32]*4,c.POINTER(c.c_uint32)];self.insert.restype=c.c_int;self.clear=self.lib.biwn_slot_clear;self.clear.argtypes=[c.POINTER(slot.Bus),c.c_uint16,c.c_uint16,c.POINTER(c.c_uint32)];self.clear.restype=c.c_int;self.cd_begin=self.lib.biwn_cd_read_wrapper;self.cd_begin.argtypes=[c.POINTER(world.Bus),*[c.c_uint32]*3,c.POINTER(c.c_uint32)];self.cd_begin.restype=c.c_int;self.cd_stop=self.lib.biwn_cd_stop_wrapper;self.cd_stop.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];self.cd_stop.restype=c.c_int;self.raw=device_check.CoreMemory(self);self.resources=resources.bind(self.lib);self.disc=Disc();self.free=self.lib.biwn_cleanup_free_handle;self.free.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];self.free.restype=c.c_int
  self.cd=self.lib.biwn_cd_offset_msf;self.cd.argtypes=[c.c_uint32,c.c_uint32,c.c_void_p,c.c_size_t,c.POINTER(Position)];self.cd.restype=c.c_int
 def bulk(self,address,data):c.memmove(self.device.pointer+address,data,len(data))
 def native(self,ram,case,coverage):
  self.seed(ram);self.disc.reset()
  for target in STUBS:self.device.direct(target,2,0x4e75)
  self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000)
  for i,value in enumerate(case['incoming']):self.core.m68k_set_reg(i,value)
  self.core.m68k_set_reg(15,SP);self.core.m68k_set_reg(16,case['entry']);self.device.direct(SP,4,STOP);self.device.direct(SP+4,2,case['id']);calls=[];steps=[]
  for _ in range(250000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==STOP:break
   assert any(lo<=pc<hi for lo,hi in resources.RANGES.items())or any(lo<=pc<hi for lo,hi in memory.RANGES.items())or 0x1545c<=pc<0x1557a or 0xd1e0<=pc<0xd2a0 or 0xd2f0<=pc<0xd30a or pc in STUBS,hex(pc)
   coverage.add(pc);steps.append(pc)
   if pc in WIDTHS and pc!=case['entry']:
    stack=self.core.m68k_get_reg(None,15);args=[];offset=4
    for width in WIDTHS[pc]:args.append(int.from_bytes(c.string_at(self.device.pointer+stack+offset,width),'big'));offset+=width
    calls.append(['call',pc,args])
   if pc==0x303c:
    seeds=[self.core.m68k_get_reg(None,i)for i in [8,9,0]];calls.append(['call',0x303c,seeds]);self.disc.start(*seeds)
   elif pc==0x3042:calls.append(['call',0x3042,[]]);self.disc.stop()
   elif pc==0xdf60:self.disc.tick(self.bulk,lambda a,v:self.device.direct(a,4,v))
   elif pc in[0xdf8c,0xdf9c]:raise AssertionError('Unexpected ready-wait/wake; standalone checks cover these scripted boundaries')
   self.core.m68k_execute(1)
  else:
   self.failure=dict(pc=hex(self.core.m68k_get_reg(None,16)),steps=len(steps),disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),calls=calls[-20:]);raise OriginalRetry('Original loader did not return within250000 instructions')
  assert self.core.m68k_get_reg(None,15)==SP+4
  for i,value in enumerate(case['incoming']):
   if i not in[0,1,8,9]:assert self.core.m68k_get_reg(None,i)==value
  for target in STUBS:self.device.direct(target,2,get(ram,target,2))
  return self.device.ram(),self.core.m68k_get_reg(None,0),{'calls':calls,'instructions':len(steps),'disc_requests':list(self.disc.requests),'disc_completions':list(self.disc.completions),'disc_stops':self.disc.stops,'hardware':self.hardware(),'device':self.device.stats()}
 def translated(self,ram,case):
  self.seed(ram);self.disc.reset();alloc,compact,copy=self.functions;calls=[];errors=[]
  def call(_,target,args,n,out):
   try:
    values=list(args[:n])if n else[];calls.append(['call',target,values])
    if target==0x18160:return self.device_initialize(c.byref(bus),out)
    if target==0x1aa40:return self.resources[target](c.byref(bus),values[0],0,out)
    if target==0x10a6a:return self.selector(c.byref(bus),values[0],out[0],out)
    if target==0x1ae88:return self.release(c.byref(bus),values[0],out[0],out)
    if target==0x1ac68:return self.acquisition(c.byref(bus),values[0],SCRATCH,out)
    if target==0x10968:
     sb=slot.Bus(self.device.write8,None);return self.clear(c.byref(sb),*values,out)
    if target==0x11762:return self.insert(c.byref(bus),*values,out[0],out)
    if target==0x152a2:return alloc(c.byref(bus),values[0],4096,out)
    if target==0x15200:return compact(c.byref(bus),4096,out)
    if target==0xe3e0:return copy(c.byref(bus),self.device.write8,target,*values,out[0],4096,out)
    if target==0x1545c:return self.free(c.byref(bus),values[0],out[0],4096,out)
    if target==0x1b044:return self.resources[target](c.byref(bus),*values,32768,out)
    if target==0xd206:
     toc=c.create_string_buffer(c.string_at(self.device.pointer+0x2c00,256));position=Position();status=self.cd(*values,toc,256,c.byref(position))
     if not status:out[0]=position.packed
     return status
    if target==0xd2f0:return self.cd_begin(c.byref(bus),*values,out)
    if target==0x303c:self.disc.start(*values);return 0
    if target==0xd306:return self.cd_stop(c.byref(bus),out[0],out)
    if target==0x3042:self.disc.stop();return 0
    if target==0xdf60:self.disc.tick(self.bulk,lambda a,v:self.device.direct(a,4,v));return 0
    raise AssertionError(hex(target))
   except Exception as error:errors.append(repr(error));return 1
  def read(width):
   def f(_,address,out):
    try:out[0]=self.raw.read(address,width);return 0
    except Exception as error:errors.append(repr(error));return 1
   return f
  def write(width):
   def f(_,address,value):
    try:self.raw.write(address,width,value);return 0
    except Exception as error:errors.append(repr(error));return 1
   return f
  callbacks=[self.device.r8,world.R16(read(2)),world.R32(read(4)),world.W16(write(2)),world.W32(write(4)),world.CALL(call)]
  bus=world.Bus(*callbacks,None,32768);out=c.c_uint32(0xa55aa55a)
  if case['entry']==0x10990:status=self.initialize(c.byref(bus),case['incoming'][0],c.byref(out))
  elif case['entry']==0x1ac68:status=self.acquisition(c.byref(bus),case['id'],SCRATCH,c.byref(out))
  elif case['entry']==0x1aa40:status=self.resources[case['entry']](c.byref(bus),case['id'],SCRATCH,c.byref(out))
  else:status=self.resources[case['entry']](c.byref(bus),case['id'],32768,c.byref(out))
  if not case.get('allow_host_error'):assert status==0 and not errors,(status,errors)
  return self.device.ram(),out.value,{'status':status,'errors':errors,'calls':calls,'disc_requests':list(self.disc.requests),'disc_completions':list(self.disc.completions),'disc_stops':self.disc.stops,'hardware':self.hardware(),'device':self.device.stats()}
def main():
 out=ROOT/'verification/scene-initial-real-disc'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 restore=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_scene_initial_setup.c','biwn_slot_clear.c','biwn_scene_record_insert.c','biwn_scene_select.c','biwn_frame_reference_release.c','biwn_frame_resource_acquire.c','biwn_scene_device_initialize.c','biwn_resources.c','biwn_memory.c','biwn_transition_cleanup.c','biwn_cd_math.c','biwn_cd_wrappers.c'];library=out/'libscene-initial-disc.dylib'
 frozen=json.loads((ROOT/'verification/local-scene-initial-setup-devices-checks-current.json').read_text())['source_sha256']
 for name in names[:8]:assert hashlib.sha256((restore/name).read_bytes()).hexdigest()in frozen.values()
 subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(restore/name)for name in names],'-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 assert hashlib.sha256((restore/'biwn_cd_wrappers.c').read_bytes()).hexdigest()==json.loads((ROOT/'verification/CD-wrappers-current.json').read_text())['source_sha256']
 runtime=Runtime(library);atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();_,snapshot=native.prior.prior.render.assets();rng=random.Random(0x109901b044);rows=[];coverage=set()
 try:
  for index in [0,1,15]:
   ram=bytearray(native.seed(snapshot));scene=0x3d822+146
   for address,width in [(0x464a6,2),(0x464ce,2),(0x464b4,4),(0x464c4,4)]:ram[address:address+width]=atlas[address:address+width]
   ram[scene:scene+4]=bytes(4);ram[0x400e4:0x400e6]=index.to_bytes(2,'big')
   case=dict(entry=0x10990,id=0,incoming=[rng.getrandbits(32)for _ in world.REGS])
   save(out/'status.json',dict(status='running',index=index))
   left,expected,original=runtime.native(bytes(ram),case,coverage);right,value,rebuilt=runtime.translated(bytes(ram),case)
   if masked(left)!=masked(right)or expected!=value or any(original[k]!=rebuilt[k]for k in ['calls','disc_requests','disc_completions','disc_stops','hardware']):
    save(out/'mismatch.json',dict(index=index,case=case,original_D0=expected,C_D0=value,original=original,rebuilt=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(masked(left),masked(right)))if a!=b][:32]));raise AssertionError(out/'mismatch.json')
   assert len(rebuilt['disc_requests'])==1 and not rebuilt['device']['original_GPUExec1_calls']
   payload=right[0x1134a0:0x1334a0];request=rebuilt['disc_requests'][0];stream=runtime.disc.data[request['normalized_track_offset']:request['normalized_track_offset']+request['bytes']];pos=stream.find((0xc000).to_bytes(4,'big')*16);assert pos>=0 and payload==stream[pos+64:pos+64+len(payload)]
   rows.append(dict(index=index,full_D0=value,payload_bytes=len(payload),payload_sha256=hashlib.sha256(payload).hexdigest(),original=original,rebuilt=rebuilt))
 except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error),diagnostic=getattr(runtime,'failure',None)));raise
 finally:runtime.close()
 report=dict(status='scene_constructor_all_source_helpers_real_disc_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),disc_requests=sum(len(r['rebuilt']['disc_requests'])for r in rows),observed_instruction_addresses=sorted(coverage),source_sha256={name:hashlib.sha256((restore/name).read_bytes()).hexdigest()for name in names},scripted_game_helpers=[],BIOS_device_adapters=['0x303c','0x3042'],completion_tick_adapter='0xdf60',natural_gameplay_integration_verified=False,new_training=False,native_Chat_verified=False,scope='Three controlled constructor cases with recovered device,texture initialization,slot clear,selector,reference release,frame acquisition,record insertion,resource loader,copy,CD math andactualC read/stop wrappers. BIOS303C registerseed calls and3042 noarg calls are explicit andmatched in the logical helper trace. Real internal disc bytes,wholeexternalRAM,fullD0,helperargs/order,transfer events andsevenblitter registers compare with pinned originalCPU. Descriptor scene1 forced tag0/asset0 and record indices0,1,15; fixedmode tables/TOC/heap and674bytephase plusBIOS303C/3042/DF60completion remain. Copied131072bytes reproduce original andinclude following marker data because physicalmode3extent is106496bytes; no repaired asset packing,othermode3groups,global scheduler,natural gameplay,physicaltiming orwhole-game proof.')
 save(out/'cases.json',rows);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/scene-initial-real-disc-current.json',report);print(json.dumps({k:report[k]for k in ['status','cases','disc_requests']}),flush=True)
if __name__=='__main__':main()
