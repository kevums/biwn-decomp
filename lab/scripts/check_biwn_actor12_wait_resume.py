"""Controlled actor/resource pending wait -> idle signal -> caller resumption."""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
parser=argparse.ArgumentParser();parser.add_argument('--patched-task',action='store_true');opt=parser.parse_args();out=ROOT/'verification/BIWN-actor12-wait-resume'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);src=ROOT/'projects/black-ice-white-noise/restoration';task=src/'experimental/biwn_actor12_task_cpu.c'
if opt.patched_task:
 text=task.read_text();old='status==6&&s->cpu.pc==0xdf60u';assert text.count(old)==1;text=text.replace(old,'status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)');task=src/'experimental/biwn_actor12_resource_wait_cpu.c';task.write_text(text)
files=[task,src/'biwn_npc_cpu.c',src/'biwn_resource_cpu.c',src/'biwn_resource_sync.c',src/'biwn_scheduler.c',src/'biwn_task_loops.c',src/'biwn_media_setup_cpu.c'];lib=out/'libactor-wait.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in files],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
source=json.loads((ROOT/'verification/natural-actor13-task-current.json').read_text());ram=bytearray((Path(source['directory'])/'native-RAM.bin').read_bytes());initial=media.CPU();record=source['results'][0]['CPU'];initial.registers[:]=record['registers']
for field in ['pc','sr','usp','ssp']:setattr(initial,field,record[field])
assert initial.pc==0x173b0 and not(initial.sr&0x2000);main,idle=0xc3928,0xc5928
put=lambda a,w,v:ram.__setitem__(slice(a,a+w),(v&((1<<(8*w))-1)).to_bytes(w,'big'))
for context,other,pc,sp in [(main,idle,0x173b0,initial.registers[15]),(idle,main,0xf360,idle+0x400)]:
 for off,width,value in [(0,4,other),(4,4,other),(8,4,pc),(12,4,sp),(16,4,pc),(20,2,0),(22,4,0),(26,4,0),(30,4,0),(34,4,0)]:put(context+off,width,value)
put(0xc0920,4,main);put(0x80,4,0xde08);put(0x90,4,0xdef6)
for i in range(40):put(0x49d6c+i*206,2,0)
put(0x49d6c,2,12);put(0x49d6e,2,0);put(0x15b534,2,24);put(0x15b53a,2,1);put(0x15b53c,2,0)
session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);resource_rows=json.loads((session/'resource-fullCPU-generation.json').read_text())['instructions_decoded'];npc_rows=json.loads((session/'npc-fullCPU-generation.json').read_text())['instructions_decoded'];task_rows=json.loads((ROOT/'verification/actor12-task-generation.json').read_text())['instructions_decoded'];runtime=media.Runtime(lib,resource_rows+npc_rows+task_rows);resource_pc={r['address']for r in resource_rows};npc_pc={r['address']for r in npc_rows};task_pc={r['address']for r in task_rows};results=[];resource_targets=[0x1af04,0x152a2,0x15200,0x1545c,0x1b002,0xe3e0,0xe3ee];adversaries=[0x10252,0x1404c,0xeb04,0x13c9a];phases={}
try:
 for mode in ['native','C']:
  runtime.reset(bytes(ram),0);cpu=media.CPU.from_buffer_copy(bytes(initial));calls=[];errors=[];trace=[]
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
  actor_fn=body('biwn_actor12_task_cpu_body');npc_fn=body('biwn_npc_cpu_body');resource_fn=body('biwn_resource_cpu_body')
  def simple(name):
   f=getattr(runtime.lib,name);f.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];f.restype=c.c_int;return f
  wait_fn=simple('biwn_resource_wait');signal_fn=simple('biwn_resource_signal_call');idle_fn=runtime.lib.biwn_task_loop_step;idle_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_void_p,c.c_void_p,c.c_uint32];idle_fn.restype=c.c_int
  def provider(s,target):
   widths={0x10252:[4],0x1404c:[4],0xeb04:[4],0x13c9a:[4,4]};offset=4;args=[]
   for width in widths[target]:args.append(runtime.device.read(s.registers[15]+offset,width));offset+=width
   calls.append(dict(target=hex(target),arguments=args));s.registers[0]=10000 if target==0x10252 else 1;s.registers[1]=0x87654321;s.registers[8]=0x15f000;s.registers[9]=0x15e000;s.sr=(s.sr&0xffe0)|0x13
  def service(_,passed,state,target):
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
    if pc in adversaries:
     s=runtime.cpu();provider(s,pc)
     for reg in [0,1,8,9]:runtime.core.m68k_set_reg(reg,s.registers[reg])
     runtime.core.m68k_set_reg(17,s.sr);old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);runtime.core.m68k_execute(1);runtime.device.direct(pc,2,old)
    else:runtime.core.m68k_execute(1)
   raise AssertionError(('native bound',hex(pc)))
  def mark(name):
   snapshot=dict(CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],current=hex(runtime.device.read(0xc0920,4)),main_wait=runtime.device.read(main+26,4),ready=runtime.device.read(0x15b53c,2));phases.setdefault(name,{})[mode]=snapshot;save(out/f'{mode}-{name}.json',snapshot)
  if mode=='native':cpu=native_until(lambda pc:pc==0xdf8c)
  else:
   status=actor_fn(c.byref(bus),c.byref(cpu),callbacks[5],service_cb,None,100000,1);assert status==6 and cpu.pc==0xdf8c,(status,hex(cpu.pc),errors)
  mark('pending_wait')
  if mode=='native':cpu=native_until(lambda pc:pc==0xf360 and runtime.device.read(0xc0920,4)==idle)
  else:assert wait_fn(c.byref(bus),c.byref(cpu),128)==0 and cpu.pc==0xf360
  mark('wait_selected_idle');assert runtime.device.read(main+26,4)==1
  # Declared completion event: set ready and call original DF9C on the idle CPU.
  runtime.device.direct(0x15b53c,2,1);cpu.registers[15]-=4;runtime.device.direct(cpu.registers[15],4,1);cpu.registers[15]-=4;runtime.device.direct(cpu.registers[15],4,0xf360);cpu.usp=cpu.registers[15];cpu.pc=0xdf9c
  if mode=='native':runtime.core.m68k_set_reg(15,cpu.registers[15]);runtime.core.m68k_set_reg(16,cpu.pc);cpu=native_until(lambda pc:pc==0xf360)
  else:assert signal_fn(c.byref(bus),c.byref(cpu),128)==0
  cpu.registers[15]+=4;cpu.usp=cpu.registers[15]
  if mode=='native':runtime.core.m68k_set_reg(15,cpu.registers[15])
  mark('source_signal_completed');assert runtime.device.read(main+26,4)==0
  if mode=='native':cpu=native_until(lambda pc:pc==0x1af56)
  else:assert idle_fn(c.byref(bus),c.byref(cpu),None,None,128)==0 and cpu.pc==0x1af56
  mark('resource_continuation_resumed')
  if mode=='native':cpu=native_until(lambda pc:pc==0xdf60)
  else:
   for _ in range(32):
    if cpu.pc==0xdf60:break
    f=resource_fn if cpu.pc in resource_pc else npc_fn if cpu.pc in npc_pc else actor_fn if cpu.pc in task_pc else None;assert f,hex(cpu.pc);status=f(c.byref(bus),c.byref(cpu),callbacks[5],service_cb,None,100000,1);assert status in [0,6]and not errors,(status,hex(cpu.pc),errors)
    if status==0:
     assert runtime.rows[cpu.pc]['assembly']=='rts';cpu.pc=runtime.device.read(cpu.registers[15],4);cpu.registers[15]+=4;cpu.usp=cpu.registers[15]
   else:raise AssertionError('C continuation bound')
  mark('actor_initialized_and_yielded');assert cpu.pc==0xdf60 and runtime.device.read(0x49d6c+0x58,4)==runtime.device.read(0x15b536,4)and runtime.device.read(0x49d6c+0x5e,4)!=0
  results.append(dict(mode=mode,calls=calls,instructions=len(trace)if mode=='native'else None));(out/f'{mode}-final-RAM.bin').write_bytes(runtime.device.ram())
 for name,values in phases.items():assert values['native']==values['C'],('phase mismatch',name)
 assert results[0]['calls']==results[1]['calls'];assert(out/'native-final-RAM.bin').read_bytes()==(out/'C-final-RAM.bin').read_bytes()
 report=dict(status='actor12_real_initializer_resource_wait_signal_resume_native_C_match',directory=str(out),phases=phases,results=results,patched_task=opt.patched_task,source_sha256={p.name:sha(p.read_bytes())for p in files},whole_game_complete=False,limits=['Controlled type12 activation and borrowed resident model0 cache aliased to resource24; actual resource24 asset/CD loading unproved.','Controlled two-context ring and one ready/signal ABI event on idle CPU; no hardware completion/timing proof. No CPU/RAM reset between pending wait, signal, resumption and initialization.','Real actor caller/NPC initializer/acquire/allocator/wait/TRAP4/RTE/signal/idle-yield/resumption execute; distance/facing/animation/movement remain ABI adversaries.']);save(out/'report.json',report);save(ROOT/'verification/actor12-wait-resume-current.json',report);print(report['status'],flush=True)
except BaseException as error:save(out/'failure.json',dict(error=repr(error),patched_task=opt.patched_task,phases=phases));raise
finally:runtime.oracle.close()
