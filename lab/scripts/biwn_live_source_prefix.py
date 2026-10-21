"""Run the checked captured4000 prefix on an existing runtime, without exporting state.

The original prefix script remains the separate oracle/fixture proof. This module
reuses that exact implementation and restores renderer/music helper bindings,
while retaining the live CPU/GPU/DSP and shared device state it produced.
"""
import ctypes as c,types,hashlib
from pathlib import Path
import observe_biwn_relocated_firmware as host
import check_biwn_full_video_cpu_gpu as video
import check_biwn_dsp_media_audio as dsp
from check_biwn_music_DSP_bootstrap import Bus as MusicBus,W16
from check_biwn_source_entry_boot import EntryBootMixin
import check_biwn_movie_boot_exit_AV as GPUboot
import check_biwn_movie_source_overlay_AV as GPUoverlay
import check_biwn_gpu_dispatcher as dispatcher
from check_biwn_main_GPU_boot import Bus as BootBus,W16 as GPUW16
from check_biwn_movie_GPU import state_from_raw,logical
from probe_biwn_gpu_projection import gpu_state
media=host.media

def run(runtime,library,mode,initial_CPU=None,preserve_owned_processors=False,platform_API=None,instruction_probe=False,instruction_clock=False):
 core=runtime.core;ticks=[0];instruction_records=[];observer_errors=[];clock_pending=0;clock_cycles=0;clock_us=0.0;main_events=0;clock_GPU_timers=[];
 original_counters_before={n:c.c_uint32.in_dll(core,n).value for n in ['gpu_exec_opcode_count','dsp_exec_opcode_count']}
 def pump_timer():
  state=runtime.gpu if mode=='C'else state_from_raw(gpu_state(core)[0])
  if not(state.flags&8)or state.pc!=0xf03020:return
  returnPC=core.GPUReadLong(state.registers[0][31]&~3,3)+2
  import struct
  trace_hash=hashlib.sha256();old_trace,old_blocks=runtime.gpu_trace,runtime.gpu_blocks
  if mode=='native':
   start=runtime.gpu_counter.value;blocks=0;delay_count=0
   for _ in range(100):
    pc=core.GPUGetPC()
    if pc==returnPC:break
    trace_hash.update(struct.pack('>I',pc));blocks+=1;opcode=core.GPUReadWord(pc,3);core.GPUExec(1)
    if opcode>>10 in [52,53]and core.GPUGetPC()!=pc+2:delay_count+=1
   else:raise AssertionError(('prefix pending GPU timer bound',hex(pc),hex(returnPC)))
   instructions=blocks+delay_count;image=gpu_state(core)[0][:4396]
  else:
   runtime.gpu_trace=trace_hash;runtime.gpu_blocks=0;start=runtime.gpu.instructions;counter=runtime.gpu_counter.value
   assert runtime.timer_run(c.byref(runtime.boot_bus),c.byref(runtime.gpu),100,returnPC)==0
   blocks=runtime.gpu_blocks;instructions=runtime.gpu.instructions-start;image=logical(runtime.gpu)
   assert runtime.gpu_counter.value==counter
   c.memmove(core.GPUGetRAM(),bytes(runtime.gpu.local_RAM),4096)
   raw=gpu_state(core)[0];assert core.GPUStateLoad(c.create_string_buffer(image+raw[4396:]))==4416
  runtime.gpu_trace,runtime.gpu_blocks=old_trace,old_blocks
  clock_GPU_timers.append(dict(return_PC=returnPC,blocks=blocks,instructions=instructions,PC_sha256=trace_hash.hexdigest(),logical_GPU_sha256=hashlib.sha256(image).hexdigest()))

 assert not instruction_clock or instruction_probe
 core.GetTimeToNextEvent.argtypes=[c.c_int];core.GetTimeToNextEvent.restype=c.c_double;core.HandleNextEvent.argtypes=[c.c_int];core.SubtractEventTimes.argtypes=[c.c_double,c.c_int]
 def advance(cycles):
  nonlocal clock_cycles,clock_us,main_events
  clock_cycles+=cycles;remaining=cycles*(0.03760684198*2)
  while remaining>0:
   due=core.GetTimeToNextEvent(0);assert due>=-0.001,due;due=max(0.0,due)
   if due>remaining:
    core.SubtractEventTimes(remaining,0);clock_us+=remaining;break
   if mode=='C':
    raw=gpu_state(core)[0];assert len(raw)==4416
    assert core.GPUStateLoad(c.create_string_buffer(logical(runtime.gpu)+raw[4396:]))==4416
   core.HandleNextEvent(0)
   if mode=='C':
    updated=state_from_raw(gpu_state(core)[0]);count=runtime.gpu.instructions
    c.memmove(c.byref(runtime.gpu),c.byref(updated),c.sizeof(updated));runtime.gpu.instructions=count
   pump_timer()
   remaining-=due;clock_us+=due;main_events+=1

 if instruction_probe:
  from biwn_m68k_cycle_cost import Cost
  cost=Cost(lambda a,w:int.from_bytes(c.string_at(runtime.device.pointer+a,w),'big'))
  def observe(cpu):
   nonlocal clock_pending
   try:
    if instruction_clock:advance(clock_pending);clock_pending=0
    opcode=int.from_bytes(c.string_at(runtime.device.pointer+cpu.pc,2),'big');cycles,family=cost.predict(opcode,cpu)
    instruction_records.append(dict(CPU=media.scheduler.cpu_dict(cpu),opcode=opcode,base_cycles=cycles,family=family))
    if instruction_clock:clock_pending=cycles
   except BaseException as error:observer_errors.append(repr(error))
 else:observe=lambda _:None
 core.BUTCHExec.argtypes=[c.c_uint32];initial=initial_CPU if initial_CPU is not None else runtime.cpu();assert initial.pc==0x4000;trace=[];errors=[];target_stop=0xdd40
 names=['raw_DSP','music_segment','run_dispatch','run_boot_exit','native_GPU','run_C_GPU','dispatch','dispatch_callbacks','dispatch_bus','main_boot','boot_callbacks','boot_bus','music_run','music_irq','music_callbacks','music_bus','reloc','gpu_bus']
 saved={name:getattr(runtime,name)for name in names if hasattr(runtime,name)}
 runtime.mode=mode;runtime.gpu_counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');runtime.gpu_calls=[];runtime.gpu_trace=__import__('hashlib').sha256();runtime.gpu_blocks=0;runtime.gpu=(runtime.gpu if preserve_owned_processors else state_from_raw(gpu_state(core)[0]))if mode=='C'else None;pending=[False];runtime.counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count');runtime.music_calls=[];runtime.music_trace=[];runtime.music_started=False
 def raw_DSP():
  buffer=c.create_string_buffer(12000);size=core.DSPStateSave(buffer);return buffer.raw[:size]
 runtime.raw_DSP=raw_DSP;runtime.C_DSP=(runtime.C_DSP if preserve_owned_processors else dsp.state_from_raw(raw_DSP()))if mode=='C'else None;runtime.music_segment=types.MethodType(EntryBootMixin.music_segment,runtime)
 core.DSPExec.argtypes=[c.c_int32];core.DSPGetPC.restype=c.c_uint32;core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32;core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.DSPWriteWord.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
 core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16;core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8
 runtime.run_dispatch=types.MethodType(GPUoverlay.Runtime.run_dispatch,runtime);runtime.run_boot_exit=types.MethodType(GPUboot.Runtime.run_boot_exit,runtime);runtime.native_GPU=types.MethodType(video.Runtime.native_GPU,runtime);runtime.run_C_GPU=types.MethodType(video.Runtime.run_C_GPU,runtime)
 if mode=='native':
  for _ in range(100000):
   pc=runtime.cpu().pc
   if pc==target_stop:break
   trace.append(pc)
   if instruction_probe:observe(runtime.cpu())
   if pc in {0x3544,0x3910,0x392e,0x37e0}:core.BUTCHExec(0);ticks[0]+=1
   if pc==0xd384 and core.GPUGetPC()!=0xf032c8:runtime.native_GPU(True)
   if pc==0xe038:runtime.run_boot_exit('main_boot');runtime.run_dispatch(True)
   if pc==0xe9a8:runtime.music_segment(0xf1b144)
   if pc==0xea08 and core.DSPGetPC()!=0xf1b148:runtime.music_segment(0xf1b148)
   core.m68k_execute(1)
  else:raise AssertionError(('native prefix limit',hex(pc)))
  final=runtime.cpu();status=0
 else:
  helper=c.CDLL(str(library));
  if instruction_probe:
   OBS=c.CFUNCTYPE(None,c.c_void_p)
   callback=OBS(lambda ptr:observe(c.cast(ptr,c.POINTER(media.CPU)).contents))
   setter=helper.biwn_set_instruction_observer;setter.argtypes=[OBS];setter.restype=None;setter(callback)
  fn=helper.biwn_entry_setup_cpu_call;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;helper.biwn_entry_setup_cpu_body.argtypes=fn.argtypes;helper.biwn_entry_setup_cpu_body.restype=c.c_int;helper.biwn_bios_controller_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_controller_cpu_body.restype=c.c_int;helper.biwn_bios_mode_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_mode_cpu_body.restype=c.c_int;helper.biwn_bios_toc_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_toc_cpu_body.restype=c.c_int;helper.biwn_video_cpu_body.argtypes=fn.argtypes;helper.biwn_video_cpu_body.restype=c.c_int;helper.biwn_GPU_boot_cpu_body.argtypes=fn.argtypes;helper.biwn_GPU_boot_cpu_body.restype=c.c_int;helper.biwn_bios_setup_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_setup_cpu_body.restype=c.c_int;captured=[]
  runtime.dispatch=helper.biwn_gpu_dispatcher_run;runtime.dispatch.argtypes=[c.POINTER(dispatcher.Bus),c.POINTER(dispatcher.State),c.c_uint32,c.c_uint32];runtime.dispatch.restype=c.c_int
  def dispatch_read(_,a,v):v[0]=int.from_bytes(bytes(runtime.gpu.local_RAM[a-0xf03000:a-0xf03000+4]),'big')if 0xf03000<=a<=0xf03ffc else core.GPUReadLong(a,3);return 0
  def dispatch_write(_,a,v):
   core.GPUWriteLong(a,v,3)
   if 0xf03000<=a<=0xf03ffc:runtime.gpu.local_RAM[a-0xf03000:a-0xf03000+4]=v.to_bytes(4,'big')
   return 0
  def dispatch_observe(_,pc,z,carry,n):runtime.dispatch_trace.update(__import__('struct').pack('>I',pc));runtime.dispatch_blocks+=1
  runtime.dispatch_callbacks=[dispatcher.R32(dispatch_read),dispatcher.W32(dispatch_write),dispatcher.TRACE(dispatch_observe)];runtime.dispatch_bus=dispatcher.Bus(*runtime.dispatch_callbacks,None)
  runtime.main_boot=helper.biwn_gpu_main_boot_run;runtime.main_boot.argtypes=[c.POINTER(BootBus),c.POINTER(video.State),c.c_uint32];runtime.main_boot.restype=c.c_int;core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
  def boot_observe(_,pc):runtime.gpu_trace.update(__import__('struct').pack('>I',pc));runtime.gpu_blocks+=1
  runtime.boot_callbacks=[video.R16(lambda _,a,v:(v.__setitem__(0,core.GPUReadWord(a,3)),0)[1]),video.R32(lambda _,a,v:(v.__setitem__(0,core.GPUReadLong(a,3)),0)[1]),GPUW16(lambda _,a,v:(core.GPUWriteWord(a,v,3),0)[1]),video.W32(lambda _,a,v:(core.GPUWriteLong(a,v,3),0)[1]),video.OBS(boot_observe)];runtime.boot_bus=BootBus(*runtime.boot_callbacks,None)
  runtime.music_run=helper.biwn_dsp_music_bootstrap_run;runtime.music_run.argtypes=[c.POINTER(MusicBus),c.POINTER(dsp.State),c.c_uint32,c.c_uint32];runtime.music_run.restype=c.c_int;runtime.music_irq=helper.biwn_dsp_music_bootstrap_cpu_interrupt;runtime.music_irq.argtypes=[c.POINTER(dsp.State)];runtime.music_irq.restype=c.c_int
  runtime.music_callbacks=[dsp.R8(lambda _,a,v:(v.__setitem__(0,core.JaguarReadByte(a,2)),0)[1]),dsp.R32(lambda _,a,v:(v.__setitem__(0,core.DSPReadLong(a,2)),0)[1]),dsp.W32(lambda _,a,v:(core.DSPWriteLong(a,v,2),0)[1]),W16(lambda _,a,v:(core.DSPWriteWord(a,v,2),0)[1]),dsp.OBS(lambda _,pc:runtime.music_trace.append(pc))];runtime.music_bus=MusicBus(*runtime.music_callbacks,None)
  runtime.reloc=helper.biwn_movie_relocation_GPU_run;runtime.reloc.argtypes=[c.POINTER(video.GPUBus),c.POINTER(video.State),c.c_uint32];runtime.reloc.restype=c.c_int
  def GPU_read(w):
   def cb(_,a,v):v[0]=core.JaguarReadByte(a,3)if w==1 else core.GPUReadWord(a,3)if w==2 else core.GPUReadLong(a,3);return 0
   return cb
  def GPU_write(_,a,v):core.GPUWriteLong(a,v,3);return 0
  def GPU_observe(_,pc):runtime.gpu_trace.update(__import__('struct').pack('>I',pc));runtime.gpu_blocks+=1
  GPU_callbacks=[video.R8(GPU_read(1)),video.R16(GPU_read(2)),video.R32(GPU_read(4)),video.W32(GPU_write),video.OBS(GPU_observe)];runtime.gpu_bus=video.GPUBus(*GPU_callbacks,None)
  def reader(w):
   def cb(_,a,v):
    try:
     if a==0xdfff00 and w==4:core.BUTCHExec(0);ticks[0]+=1
     if a==0xf1badc and w==4 and runtime.music_started:runtime.music_segment(0xf1b148);runtime.music_started=False
     if pending[0] and a==0xf039ec:runtime.run_C_GPU(True);pending[0]=False
     if a==0xf02100 and w==4:
      g=runtime.gpu;g.flags=(g.flags&~7)|g.z|(g.c<<1)|(g.n<<2);v[0]=g.flags&0xffffc1ff;return 0
     v[0]=int.from_bytes(bytes(runtime.gpu.local_RAM[a-0xf03000:a-0xf03000+w]),'big')if 0xf03000<=a<=0xf04000-w else runtime.read(a,w);return 0
    except BaseException as e:errors.append(repr(e));return 1
   return cb
  def writer(w):
   def cb(_,a,v):
    try:
     runtime.write(a,w,v)
     if 0xf1b000<=a<=0xf1d000-w:runtime.C_DSP.local_RAM[a-0xf1b000:a-0xf1b000+w]=v.to_bytes(w,'big')
     if 0xf03000<=a<=0xf04000-w:runtime.gpu.local_RAM[a-0xf03000:a-0xf03000+w]=v.to_bytes(w,'big')
     if w==4:
      if a==0xf1a100:runtime.C_DSP.flags=(v&~8)|((v&8)&runtime.C_DSP.flags);runtime.C_DSP.z=v&1;runtime.C_DSP.c=(v>>1)&1;runtime.C_DSP.n=(v>>2)&1
      if a==0xf1a10c:runtime.C_DSP.data_organization=v
      if a==0xf1a110:runtime.C_DSP.pc=v
      if a==0xf1a114:
       runtime.C_DSP.control=(runtime.C_DSP.control&0x1f7c0)|(v&~0x1f7c6)
       if v==1 and runtime.C_DSP.pc==0xf1b126:runtime.music_segment(0xf1b144)
       if v==5:assert runtime.music_irq(c.byref(runtime.C_DSP))==0;runtime.music_started=True;c.memmove(core.DSPGetRAM(),bytes(runtime.C_DSP.local_RAM),8192)
      if a==0xf02100:runtime.gpu.flags=(v&~8)|((v&8)&runtime.gpu.flags);runtime.gpu.z=v&1;runtime.gpu.c=(v>>1)&1;runtime.gpu.n=(v>>2)&1;runtime.gpu.bank=0 if runtime.gpu.flags&8 else bool(v&0x4000)
      if a==0xf0210c:runtime.gpu.data_organization=v
      if a==0xf02110:runtime.gpu.pc=v
      if a==0xf02114:
       runtime.gpu.control=(runtime.gpu.control&0xf7c0)|(v&~0xf7c6)
       if v&1 and runtime.gpu.pc==0xf03258:pending[0]=True
     return 0
    except BaseException as e:errors.append(repr(e));return 1
   return cb
  world=media.scheduler.cleanup.world
  callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),media.W8(writer(1))];bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
  def stop(_,passed,cpu,target):
   if platform_API is not None and target in [0x3000,0x3006,0x3048,0x305a]:
    if instruction_probe:observe(cpu.contents)
    return platform_API(cpu.contents)
   if target==0xdff4 and target_stop!=0xdff4:return helper.biwn_entry_setup_cpu_body(passed,cpu,callbacks[5],service,None,1000,0)
   if target==0x3048 and True:return helper.biwn_bios_controller_cpu_body(passed,cpu,callbacks[5],service,None,1000,0)
   if target in [0x3006,0x3544]:return helper.biwn_bios_mode_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
   if target in [0x305a,0x390e]:return helper.biwn_bios_toc_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
   if target==0xe6a0 and target_stop!=0xe6a0:return helper.biwn_entry_setup_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
   if target==0xd340:return helper.biwn_video_cpu_body(passed,cpu,callbacks[5],service,None,1000000,0)
   if target==0xe00a:
    result=helper.biwn_GPU_boot_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
    if result:return result
    runtime.run_boot_exit('main_boot');runtime.run_dispatch(True);return 0
   if target==0x3000 and True:return helper.biwn_bios_setup_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
   if target in [0x1557a,0x17340,0xe942,0xe96c,0xea08] and True:return helper.biwn_entry_setup_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
   if target==0xe7aa:return helper.biwn_video_cpu_body(passed,cpu,callbacks[5],service,None,1000000,0)
   if target!=target_stop:errors.append('unexpected service '+hex(target))
   captured.append(media.CPU.from_buffer_copy(bytes(cpu.contents)));return 1
  service=media.world_cpu.SERVICE(stop);original_CPU_before=bytes(runtime.cpu())
  def forbidden(*args):raise AssertionError('Original processor execution forbidden on C path')
  core.m68k_execute=forbidden;core.GPUExec=forbidden;core.DSPExec=forbidden
  status=fn(c.byref(bus),c.byref(initial),callbacks[5],service,None,1000,0);assert status==8 and not captured and not errors,(status,errors);final=initial
  # READY8 commits C-owned CPU state atDD40; original CPU shadow stays4000.
  assert original_CPU_before==bytes(runtime.cpu()),'original CPU unexpectedly changed on C path'
  if instruction_probe:setter(OBS())

 if instruction_clock:advance(clock_pending);clock_pending=0
 if instruction_probe:
  import json
  (runtime.out/(mode+'-prefix-instruction-boundaries.json')).write_text(json.dumps(dict(instructions=instruction_records,errors=observer_errors),indent=2)+'\n')
  assert not observer_errors,observer_errors
 runtime.entry_CPU=final;runtime.live_prefix_library=c.CDLL(str(library))
 row=dict(CPU=media.scheduler.cpu_dict(final),RAM=hashlib.sha256(runtime.device.ram()).hexdigest(),native_CPU_instructions=len(trace)if mode=='native'else None,BUTCH_poll_ticks=ticks[0],GPU_calls=list(runtime.gpu_calls),music_calls=list(runtime.music_calls),logical_GPU_sha256=hashlib.sha256(logical(runtime.gpu)if mode=='C'else gpu_state(core)[0][:4396]).hexdigest(),logical_DSP_sha256=hashlib.sha256(dsp.logical(runtime.C_DSP)if mode=='C'else runtime.raw_DSP()[:8496]).hexdigest())
 if instruction_clock:row['instruction_clock']=dict(CPU_cycles=clock_cycles,elapsed_us=clock_us,main_events=main_events,CPU_instruction_boundaries=len(instruction_records),CPU_clock_rate_from_pinned_NTSC=True,source_GPU_and_DSP_services_still_synchronous=True,JERRY_event_queue_held=True,GPU_timer_events=clock_GPU_timers,global_cycle_scheduling_verified=False)
 if instruction_probe:
  after={n:c.c_uint32.in_dll(core,n).value for n in original_counters_before}
  if mode=='C':assert after==original_counters_before,('original GPU/DSP execution on C prefix',original_counters_before,after)
  row['original_GPU_DSP_opcodes_on_C_path_forbidden']=True
 for name,value in saved.items():setattr(runtime,name,value)
 return row
