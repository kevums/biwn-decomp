"""Controlled actor/resource pending wait -> idle signal -> caller resumption."""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
parser=argparse.ArgumentParser();parser.add_argument('--patched-task',action='store_true');opt=parser.parse_args();out=ROOT/'verification/BIWN-actor12-cold-resource'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);src=ROOT/'projects/black-ice-white-noise/restoration';task=src/'experimental/biwn_actor12_task_cpu.c'
if opt.patched_task:
 text=task.read_text();old='status==6&&s->cpu.pc==0xdf60u';assert text.count(old)==1;text=text.replace(old,'status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)');task=src/'experimental/biwn_actor12_resource_wait_cpu.c';task.write_text(text)
files=[task,src/'biwn_npc_cpu.c',src/'biwn_resource_cpu.c',src/'biwn_cd_cpu.c',src/'biwn_resource_sync.c',src/'biwn_scheduler.c',src/'biwn_task_loops.c',src/'biwn_media_setup_cpu.c'];lib=out/'libactor-wait.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in files],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
source=json.loads((ROOT/'verification/natural-actor13-task-current.json').read_text());ram=bytearray((Path(source['directory'])/'native-RAM.bin').read_bytes());initial=media.CPU();record=source['results'][0]['CPU'];initial.registers[:]=record['registers']
for field in ['pc','sr','usp','ssp']:setattr(initial,field,record[field])
assert initial.pc==0x173b0 and not(initial.sr&0x2000);main,idle=0xc3928,0xc5928
put=lambda a,w,v:ram.__setitem__(slice(a,a+w),(v&((1<<(8*w))-1)).to_bytes(w,'big'))
for context,other,pc,sp in [(main,idle,0x173b0,initial.registers[15]),(idle,main,0xf360,idle+0x400)]:
 for off,width,value in [(0,4,other),(4,4,other),(8,4,pc),(12,4,sp),(16,4,pc),(20,2,0),(22,4,0),(26,4,0),(30,4,0),(34,4,0)]:put(context+off,width,value)
put(0xc0920,4,main);put(0x80,4,0xde08);put(0x90,4,0xdef6)
for i in range(40):put(0x49d6c+i*206,2,0)
put(0x49d6c,2,12);put(0x49d6e,2,0);put(0x47b80,2,0);put(0x47b82,2,0)
session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);resource_rows=json.loads((session/'resource-fullCPU-generation.json').read_text())['instructions_decoded'];npc_rows=json.loads((session/'npc-fullCPU-generation.json').read_text())['instructions_decoded'];task_rows=json.loads((ROOT/'verification/actor12-task-generation.json').read_text())['instructions_decoded'];cd_rows=json.loads((session/'cd-wrapper-fullCPU-generation.json').read_text())['instructions_decoded'];runtime=media.Runtime(lib,resource_rows+npc_rows+task_rows+cd_rows);resource_pc={r['address']for r in resource_rows};cd_pc={r['address']for r in cd_rows};npc_pc={r['address']for r in npc_rows};task_pc={r['address']for r in task_rows};results=[];resource_targets=[0x1b044,0x1af04,0x152a2,0x15200,0x1545c,0x1b002,0xe3e0,0xe3ee];adversaries=[0x10252,0x1404c,0xeb04,0x13c9a];phases={}
try:
 for mode in ['native','C']:
  runtime.reset(bytes(ram),0);from biwn_disc_backend import Disc
  disc=Disc();TOC=bytes(ram[0x2c00:0x3000]);index=disc.manifest['track']['track']*8;assert TOC[index]==3;origin=TOC[index+1]*4500+TOC[index+2]*75+TOC[index+3];assert origin==13227
  def source_start(start,end,packed):
   absolute=((packed>>16)&255)*4500+((packed>>8)&255)*75+(packed&255);offset=(absolute-origin)*2352+674;count=end-start;assert start==0x1c0000 and 0<count<=0x40000 and 0<=offset<=len(disc.data)-count;data=disc.data[offset:offset+count];disc.pending=(start,end,data);disc.requests.append(dict(start=start,end=end,packed=packed,offset=offset,bytes=count,sha256=sha(data),origin_from_actual_TOC=origin,phase=674))
  disc.start=source_start
  cpu=media.CPU.from_buffer_copy(bytes(initial));calls=[];errors=[];trace=[]
  world=media.scheduler.cleanup.world
  def rd(w):
   def callback(_,a,v):v[0]=runtime.read(a,w);return 0
   return callback
  def wr(w):
   def callback(_,a,v):runtime.write(a,w,v);return 0
   return callback
  callbacks=[world.R8(rd(1)),world.R16(rd(2)),world.R32(rd(4)),world.W16(wr(2)),world.W32(wr(4)),media.W8(wr(1))];bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
  def body(name):
   f=getattr(runtime.lib,name);f.argtypes=runtime.fn.argtypes;f.restype=c.c_int;return f
  cd_fn=body('biwn_cd_cpu_body');actor_fn=body('biwn_actor12_task_cpu_body');npc_fn=body('biwn_npc_cpu_body');resource_fn=body('biwn_resource_cpu_body')
  def simple(name):
   f=getattr(runtime.lib,name);f.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];f.restype=c.c_int;return f
  wait_fn=simple('biwn_resource_wait');signal_fn=simple('biwn_resource_signal_call');idle_fn=runtime.lib.biwn_task_loop_step;idle_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_void_p,c.c_void_p,c.c_uint32];idle_fn.restype=c.c_int
  def provider(s,target):
   widths={0x10252:[4],0x1404c:[4],0xeb04:[4],0x13c9a:[4,4]};offset=4;args=[]
   for width in widths[target]:args.append(runtime.device.read(s.registers[15]+offset,width));offset+=width
   calls.append(dict(target=hex(target),arguments=args));s.registers[0]=10000 if target==0x10252 else 1;s.registers[1]=0x87654321;s.registers[8]=0x15f000;s.registers[9]=0x15e000;s.sr=(s.sr&0xffe0)|0x13
  def service(_,passed,state,target):
   if target in [0xd1e0,0xd206,0xd2f0,0xd306]:return cd_fn(passed,state,callbacks[5],service_cb,None,100000,1)
   if target==0x303c:disc.start(state.contents.registers[8],state.contents.registers[9],state.contents.registers[0]);return 0
   if target==0x3042:disc.stop();return 0
   if target in resource_targets:return resource_fn(passed,state,callbacks[5],service_cb,None,100000,1)
   if target==0x101e0:return npc_fn(passed,state,callbacks[5],service_cb,None,100000,1)
   if target in adversaries:provider(state.contents,target);return 0
   errors.append(hex(target));return 1
  service_cb=media.world_cpu.SERVICE(service)
  if mode=='native':runtime.seed_cpu(cpu)
  def native_until(target):
   for _ in range(100000):
    pc=runtime.cpu().pc
    if target(pc):return runtime.cpu()
    trace.append(pc)
    if pc in [0x303c,0x3042]:
     s=runtime.cpu()
     if pc==0x303c:disc.start(s.registers[8],s.registers[9],s.registers[0])
     else:disc.stop()
     old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);runtime.core.m68k_execute(1);runtime.device.direct(pc,2,old)
    elif pc in adversaries:
     s=runtime.cpu();provider(s,pc)
     for reg in [0,1,8,9]:runtime.core.m68k_set_reg(reg,s.registers[reg])
     runtime.core.m68k_set_reg(17,s.sr);old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);runtime.core.m68k_execute(1);runtime.device.direct(pc,2,old)
    else:runtime.core.m68k_execute(1)
   raise AssertionError(('native bound',hex(pc)))
  def mark(name):
   snapshot=dict(CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],current=hex(runtime.device.read(0xc0920,4)),main_wait=runtime.device.read(main+26,4),ready=runtime.device.read(0x15b53c,2));phases.setdefault(name,{})[mode]=snapshot;save(out/f'{mode}-{name}.json',snapshot)
  if mode=='native':cpu=native_until(lambda pc:pc==0xdf60)
  else:
   status=actor_fn(c.byref(bus),c.byref(cpu),callbacks[5],service_cb,None,100000,1);assert status==6 and cpu.pc==0xdf60,(status,hex(cpu.pc),errors)
  mark('cold_loader_yield');assert disc.pending is not None
  yielding=runtime.lib.biwn_scheduler_yield;yielding.argtypes=wait_fn.argtypes;yielding.restype=c.c_int
  if mode=='native':cpu=native_until(lambda pc:pc==0xf360 and runtime.device.read(0xc0920,4)==idle)
  else:assert yielding(c.byref(bus),c.byref(cpu),128)==0 and cpu.pc==0xf360
  mark('loader_selected_idle')
  # Data/completion provider is delivered only after actual source task handoff.
  disc.tick(lambda a,data:c.memmove(runtime.device.pointer+a,data,len(data)),lambda a,v:runtime.device.direct(a,4,v));mark('disc_completion_delivered')
  if mode=='native':cpu=native_until(lambda pc:pc==0x1b0da)
  else:assert idle_fn(c.byref(bus),c.byref(cpu),None,None,128)==0 and cpu.pc==0x1b0da
  mark('loader_continuation_resumed')
  if mode=='native':cpu=native_until(lambda pc:pc==0xdf60)
  else:
   for _ in range(32):
    if cpu.pc==0xdf60:break
    f=resource_fn if cpu.pc in resource_pc else cd_fn if cpu.pc in cd_pc else npc_fn if cpu.pc in npc_pc else actor_fn if cpu.pc in task_pc else None;assert f,hex(cpu.pc);status=f(c.byref(bus),c.byref(cpu),callbacks[5],service_cb,None,100000,1);assert status in [0,6]and not errors,(status,hex(cpu.pc),errors)
    if status==0:
     assert runtime.rows[cpu.pc]['assembly']=='rts';cpu.pc=runtime.device.read(cpu.registers[15],4);cpu.registers[15]+=4;cpu.usp=cpu.registers[15]
   else:raise AssertionError('C continuation bound')
  mark('actual_resource_initialized_actor_yielded');assert cpu.pc==0xdf60
  slots=[0x15b534+12*i for i in range(50)if runtime.device.read(0x15b534+12*i,2)==24 and runtime.device.read(0x15b53a+12*i,2)]
  assert len(slots)==1;cache=slots[0];handle=runtime.device.read(cache+2,4);payload=runtime.device.read(handle,4);assert runtime.device.read(cache+8,2)==1 and runtime.device.read(0x49d6c+0x58,4)==handle and runtime.device.read(0x49d6c+0x5e,4)!=0
  payload_record=dict(resource_id=24,cache=hex(cache),handle=hex(handle),payload=hex(payload),payload_bytes=26276,sha256=sha(runtime.device.ram()[payload:payload+26276]),model_count_at8=runtime.device.read(payload+8,4));save(out/f'{mode}-asset24.json',payload_record)
  results.append(dict(mode=mode,calls=calls,disc_requests=disc.requests,disc_completions=disc.completions,payload=payload_record,instructions=len(trace)if mode=='native'else None));(out/f'{mode}-final-RAM.bin').write_bytes(runtime.device.ram())
 for name,values in phases.items():assert values['native']==values['C'],('phase mismatch',name)
 for key in ['calls','disc_requests','disc_completions','payload']:assert results[0][key]==results[1][key],key
 assert results[0]['calls']==results[1]['calls'];assert(out/'native-final-RAM.bin').read_bytes()==(out/'C-final-RAM.bin').read_bytes()
 report=dict(status='actor12_actual_resource24_cold_read_copy_initialize_native_C_match',directory=str(out),phases=phases,results=results,patched_task=opt.patched_task,source_sha256={p.name:sha(p.read_bytes())for p in files},whole_game_complete=False,limits=['Controlled type12 activation and two-context ring; resource24 itself loaded through source acquire/allocator/loader/CD wrappers/copy/initializer. No borrowed cache or host-supplied asset pointer/payload substitution.','BIOS303C/3042 preserve-register adapters and completion provider after source handoff remain. TOC origin13227fromcaptured sourceRAM and captured674byte stream phase retained. No physical disk/timing/fullboot/game proof.','Distance/facing/animation/movement still ABI adversaries. No CPU/RAM reset between request, task switches, completion and initialized actor yield.']);save(out/'report.json',report);save(ROOT/'verification/actor12-cold-resource-current.json',report);print(report['status'],flush=True)
except BaseException as error:save(out/'failure.json',dict(error=repr(error),patched_task=opt.patched_task,phases=phases));raise
finally:runtime.oracle.close()
