"""Actual CPU wrappers plus inherited GPU dispatcher/context on interior data.
Host invokes E0F2 then E148; source scene caller/loading are separate dependencies.
"""
import ctypes as c,hashlib,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_gpu_interior_submit_cpu as wrappers
import check_biwn_actor_full_movement_runtime as actor
from biwn_disc_backend import Disc
ROOT=wrappers.ROOT;CPU=wrappers.CPU;save=wrappers.save;read=wrappers.read;sha=lambda b:hashlib.sha256(b).hexdigest();SP=wrappers.SP;STOP=wrappers.STOP
class Runtime(wrappers.Runtime):
 def __init__(self,library,rows):
  super().__init__(library,rows);self.device.close();self.device=actor.Device(ROOT/'tools/libbiwn-interior-render-device.dylib');self.native_oracle.device=self.device;lib=self.device.lib
  lib.lab_scene_render_GPU_RAM.argtypes=[c.c_void_p,c.c_uint];lib.lab_scene_render_GPU_RAM.restype=c.c_int;fixture=(ROOT/'render-assets/biwn-geometry-GPU-RAM-fixture.bin').read_bytes();assert lib.lab_scene_render_GPU_RAM(c.create_string_buffer(fixture),4096)==0
  lib.lab_scene_render_submit.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32];lib.lab_scene_render_submit.restype=c.c_int;lib.lab_scene_render_stat.argtypes=[c.c_uint];lib.lab_scene_render_stat.restype=c.c_uint64;lib.lab_scene_render_PC_hash.restype=c.c_uint64;lib.lab_interior_render_stat.argtypes=[c.c_uint];lib.lab_interior_render_stat.restype=c.c_uint64;self.core.GPUStateSave.argtypes=[c.c_void_p];self.core.GPUStateSave.restype=c.c_size_t
 def reset(self,ram,case,mode):
  if self.first:self.device.seed(ram,mode);self.device.lib.lab_scene_render_reset();self.events=[];self.first=False
  else:assert self.device.ram()==ram,'Host chain unexpectedly mutated input'
  self.case=case;self.calls=[];self.trace=[];self.errors=[];self.queues={}
 def submit(self,command):
  lib=self.device.lib;status=lib.lab_scene_render_submit(None,0xf03204,command);assert not status,dict(command=hex(command),status=status)
  raw=c.create_string_buffer(8192);size=self.core.GPUStateSave(raw);assert size>4396
  self.events.append(dict(command=hex(command),RAM_sha256=sha(self.device.ram()),GPU_architecture_and_RAM_sha256=sha(raw.raw[:4396]),direct_PC_count=lib.lab_scene_render_stat(9),direct_PC_hash=hex(lib.lab_scene_render_PC_hash())))
 def write(self,a,w,v):
  if a&0xffffff==0xf03204 and v in [0x6ae0,0x6da0]:self.trace.append(['w',a,w,v]);self.submit(v);return
  return super().write(a,w,v)
 def native(self,ram,case,coverage):
  self.reset(ram,case,0);wrappers.queue.lifecycle.seed_cpu(self,wrappers.queue.make_cpu(case));steps=[];stack=[];pending=None
  for _ in range(10000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==STOP:break
   assert pc in self.rows,hex(pc)
   if pending==pc:
    row=dict(target=pc,actual_body=True,incoming=wrappers.queue.cd.scheduler.cpu_dict(self.cpu()));self.calls.append(row);stack.append(row);pending=None
   if pc==0xe0a4 and stack:stack.pop()['return']=wrappers.queue.cd.scheduler.cpu_dict(self.cpu())
   if pc in [0xe0f2,0xe140,0xe148,0xe196]:pending=0xe098
   coverage.add(pc);steps.append(pc);self.core.m68k_execute(1)
   if pc in [0xe12a,0xe180]:self.submit(0x6ae0 if pc==0xe12a else 0x6da0)
  else:raise AssertionError('Actual CPU wrapper chain did not return')
  assert not stack
  return self.device.ram(),self.cpu(),dict(steps=steps,calls=self.calls,device=self.stats())
 def stats(self):
  row=super().stats();lib=self.device.lib;row['scene_render']=[lib.lab_scene_render_stat(i)for i in range(12)];row['interior_render']=[lib.lab_interior_render_stat(i)for i in range(3)];return row
 def chain(self,ram,case,translated,coverage):
  self.first=True;stages=[]
  for target in [0xe0f2,0xe148]:
   stage={**case,'entry':target,'body':False,'render':False,'outer_RTS':0xe146 if target==0xe0f2 else 0xe19c,'read_queues':[]};ram,cpu,info=self.translated(ram,stage)if translated else self.native(ram,stage,coverage)
   assert info.get('status',0)==0,info;stages.append(dict(target=hex(target),CPU=wrappers.queue.cd.scheduler.cpu_dict(cpu),calls=info['calls'],RAM_sha256=sha(ram)))
  return ram,stages,list(self.events),self.stats()
def main():
 out=ROOT/'verification/biwn-interior-cpu-gpu-chain'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-interior-submit-fullCPU-generation.json');base=(ROOT/'verification/biwn-render-actors-runtime/20261013T190116.161377Z/startup-C-0.bin').read_bytes();wait_rows,_=wrappers.queue.cd.gen.base.binary_tools.m68k_instructions(base[0xe098:0xe0a6],0xe098);prior=read(ROOT/'verification/biwn-gpu-interior-submit-cpu-checks.json');runtime=Runtime(Path(prior['directory'])/'libinterior-submit-cpu.dylib',mapping['instructions_decoded']+wait_rows);disc=Disc();vectors=[];rng=random.Random(0x6ae06da0)
 for interior in range(4):
  marker=disc.data.find((0x6000+interior).to_bytes(4,'big')*16);assert marker==0x591c90+interior*0x1260+674;payload=disc.data[marker+64:marker+64+0x1260];count=int.from_bytes(payload[:2],'big')
  for sector in [0,count//2,count-1]:
   record=payload[14+sector*24:14+(sector+1)*24];x=int.from_bytes(record[2:4],'big')*64;z=int.from_bytes(record[4:6],'big')*64
   for camera in [[0,0,0],[x,0,z],[x+64,32,z-64]]:
    memory=bytearray(base);scene=0x15b7c0;relocated=bytearray(payload)
    for p in [4,8]:relocated[p:p+4]=(scene+int.from_bytes(relocated[p:p+4],'big')).to_bytes(4,'big')
    memory[scene:scene+len(payload)]=relocated;memory[0x49c18:0x49c1c]=scene.to_bytes(4,'big');memory[0x49c1c:0x49c20]=sector.to_bytes(4,'big');memory[SP:SP+4]=STOP.to_bytes(4,'big')
    for a,v in zip([0x49b8c,0x49b8e,0x49b90],camera):memory[a:a+2]=(v&65535).to_bytes(2,'big')
    for j,v in enumerate([16384,0,0,0,16384,0,0,0,16384,0,0,0]):memory[0x47b88+j*2:0x47b8a+j*2]=v.to_bytes(2,'big')
    n=len(vectors);supervisor=n%2;case=dict(id=n,interior=interior,sector=sector,camera=camera,registers=[rng.getrandbits(32)for _ in range(15)]+[SP],SR=(0x2000 if supervisor else 0)|rng.randrange(32),usp=0x170000 if supervisor else SP,ssp=SP if supervisor else 0x1d0000);vectors.append((bytes(memory),case))
 rows=[];coverage=set()
 try:
  for ram,case in vectors:
   save(out/'status.json',dict(status='running',case=case['id']));left,original_stages,original_events,native_stats=runtime.chain(ram,case,False,coverage);right,C_stages,C_events,C_stats=runtime.chain(ram,case,True,coverage)
   if left!=right or original_stages!=C_stages or original_events!=C_events:
    save(out/'mismatch.json',dict(case=case,original_stages=original_stages,C_stages=C_stages,original_events=original_events,C_events=C_events,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:50]));raise AssertionError(str(out/'mismatch.json'))
   assert native_stats['original_GPUExec1_calls']>0 and not C_stats['original_GPUExec1_calls']and not C_stats['scene_render'][8]and C_stats['interior_render']==[1,1,1],C_stats
   rows.append(dict(case=case,stages=C_stages,GPU_submission_events=C_events,native_stats=native_stats,C_stats=C_stats,fullCPU_RAM_privateframes_GPU_state_directPC_count_hash_match=True))
  assert len(coverage)==25,len(coverage);save(out/'fixtures.json',rows)
  report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='actual_E0F2_E148_CPU_wrappers_C_GPU_dispatcher_chain_matches_original',directory=str(out),cases=len(rows),CPU_wrapper_calls=len(rows)*2,GPU_submissions=len(rows)*2,CPU_wrapper_and_wait_source_coverage=[25,25],original_GPU_steps_on_C_side=0,forbidden_original_GPU_attempts=0,source_CPU_scene_caller_executed=False,source_CPU_loader_executed=False,perframe_initial_GPU_reset=True,GPU_reset_between_6AE0_and_6DA0=False,original_GPU_steps=sum(r['native_stats']['original_GPUExec1_calls']for r in rows),C_dispatcher_calls=sum(r['C_stats']['scene_render'][5]for r in rows),source_sha256=mapping['source_sha256'],device_library_sha256=sha((ROOT/'tools/libbiwn-interior-render-device.dylib').read_bytes()),test_script_sha256=sha(Path(__file__).read_bytes()),new_published_components=0,whole_game_complete=False,limits=['Host directly invokes sourceE0F2thenE148with declared CPUentryregisters/stack each time; GPUcontext is preserved across wrappers. This is not source17E0E live scene iteration.', 'Preserved interior payloads plus two-pointer relocation, room/camera/identitymatrix fixtures; source loader/texturefixup/actorcreation and projection/draw are not executed. Initial6AE0GPUreset/seed/fixedRAM/resident injection retained.', 'FullCPU/registers/SR/USP/SSP/privateRAM/2MBRAM match aftereachwrapper. CompletedGPUlogicalarchitecture/4KBRAM and directPCcount/hash match aftereachcommand including source residentdispatcher. OriginalGPUguard stayszero on Cside; soleGPUoracle/sharedpinnedemulatordevices, nohardwaretiming/gameplay claim.'])
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-interior-cpu-gpu-chain-checks.json',report);print(json.dumps(report))
 except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
 finally:runtime.close()
if __name__=='__main__':main()
