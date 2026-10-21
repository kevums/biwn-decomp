"""Adopt source-derived DD40 native/C contexts into existing resource startup.

No inventory baseline reset, extracted stage/stub, or CPU reseed. Existing
startup clock/buttons/BIOS file ABI/disc completion/GPU services retained.
"""
import ctypes as c,hashlib,json,types
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_entry_scheduled_startup as entry
import check_biwn_movie_GPU as GPU
import check_biwn_dsp_media_audio as DSP
ROOT=entry.ROOT;save=entry.save;sha=entry.sha;base=entry.base;media=entry.media
world=json.loads((ROOT/'verification/natural-world-entry-current.json').read_text());source=Path(world['captured']['directory']);record=json.loads((source/'checkpoint.json').read_text())
out=ROOT/'verification/BIWN-natural-world-handoff'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);lib=ROOT/'verification/BIWN-game-firstboot-movie-transport-music-cold-entry-timer-startup-loading-movie-world/20261015T001755.513281Z/libscheduled-startup.dylib';assert lib.exists();mappings=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup']];rows=[]
for p in session.glob('*-fullCPU-generation.json'):rows+=json.loads(p.read_text()).get('instructions_decoded',[])
ram=(source/'RAM.bin').read_bytes();rows+=json.loads((session/'input-dispatch-fullCPU-workmap.json').read_text())['instructions']
for a,b in base.joined.actor.navigation.RANGES+base.joined.actor.rng_cpu.RANGES+[(0x4088,0x408a),(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xdf7a,0xdf7c),(0xdeb6,0xdee2),(0xe4c0,0xe53c),(0xeac4,0xec04),(0x13440,0x134dc),(0x13c9a,0x13f12),(0xe220,0xe26c),(0x13b5a,0x13c9a),(0x1028e,0x10430),(0x10652,0x106c4),(0x191f4,0x192a2),(0x192bc,0x19f2c),(0xf360,0xf368),(0xf880,0xf888),(0xf0fa,0xf35e),(0x20820,0x20a9c)]:rows+=base.fixtures.gen.loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
entry.Runtime.entry_rows=json.loads((session/'entry-setup-fullCPU-generation.json').read_text())['instructions_decoded'];disc=base.joined.Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';results=[];original_Native=media.scheduler.Native;original_device_init=media.scheduler.movement.Device.__init__
try:
 selected=None
 for mode in ['C','native']:
  export={**record,'core_path':record['execution_core_path'],'core_sha256':record['execution_core_sha256']}
  def selected_Native(*args,**kwargs):kwargs['diagnostic_core']=Path(export['core_path']);return original_Native(*args,**kwargs)
  def selected_device_init(self,*args,**kwargs):kwargs['core']=Path(export['core_path']);return original_device_init(self,*args,**kwargs)
  media.scheduler.Native=selected_Native;media.scheduler.movement.Device.__init__=selected_device_init
  try:runtime=entry.Runtime(lib,rows,*[m['instructions_decoded']for m in mappings],disc=disc,out=out,frame_directory=frames)
  finally:media.scheduler.Native=original_Native;media.scheduler.movement.Device.__init__=original_device_init
  try:
   runtime.health_addresses={r['address']for r in json.loads((session/'health-timeout-fullCPU-generation.json').read_text())['instructions_decoded']};runtime.entry_coverage=set();runtime.timer_enabled=False
   core=runtime.core;runtime.mode=mode
   core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool;assert core.CDIntfOpenImage(record['disc_image'].encode());core.CDROMInit();core.CDROMReset();core.BIWNDiagnosticRepeatSeek.argtypes=[c.c_uint32];core.BIWNDiagnosticRepeatSeek(int(record['force_repeated_seek_diagnostic']));core.BIWNDiagnosticTOCOrigin.argtypes=[c.c_uint32];core.BIWNDiagnosticTOCOrigin(int(record['TOC_origin_diagnostic'])+2*int(record['TOC_read_origin_diagnostic']));c.c_bool.in_dll(core,'bootConfig').value=record['native_CD_scheduler_enabled']
   runtime.rom=c.c_void_p.in_dll(core,'jaguarMainROM').value;ROM=(source/'ROM-provider.bin').read_bytes();c.memmove(runtime.rom,ROM,len(ROM));blob=(source/'libretro-state.bin').read_bytes();core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool;assert core.retro_unserialize(c.create_string_buffer(blob),len(blob));runtime.device.pointer=runtime.device.lib.lab_device_ram();assert runtime.device.pointer==c.c_void_p.in_dll(core,'jaguarMainRAM').value and runtime.device.ram()==ram
   runtime.trace=hashlib.sha256();runtime.trace_count=0;runtime.bus_events=[];runtime.errors=[];runtime.gpu_calls=[];runtime.C_original_CPU_attempts=0;runtime.full_running=True;runtime.prefix_running=False;runtime.loading_active=False;runtime.movie_started=False;runtime.near_supplied=True;runtime.dialogue_returned=False;runtime.renderer_active=False;runtime.pending_render=None;runtime.pending_movement=False;runtime.pending_init=False;runtime.pending_overlay=False;runtime.C_stopped=False;runtime.polls=[];runtime.queries=[];runtime.deliveries=[];runtime.global_clock_step=0
   from probe_biwn_gpu_projection import gpu_state
   from check_biwn_full_video_cpu_gpu import logical
   buffer=c.create_string_buffer(12000);size=core.DSPStateSave(buffer);runtime.C_DSP=DSP.state_from_raw(buffer.raw[:size])if mode=='C'else None;runtime.gpu=GPU.state_from_raw(gpu_state(core)[0])if mode=='C'else None;runtime.renderer_mode(int(mode=='C'))
   CPU=media.CPU();CPU.registers[:]=record['CPU']['registers']
   for field in ['pc','sr','usp','ssp']:setattr(CPU,field,record['CPU'][field])
   assert CPU.pc==0x1a544 and runtime.current()==0xc2128
   def begin_poll(self):
    self.pad.set_buttons([]);self.polls.append(dict(poll=len(self.polls),buttons=[],clock=self.device.read(0x778cc,4),player_before=self.player_state(),no_host_clock_increment=True))
   runtime.begin_poll=types.MethodType(begin_poll,runtime);parent_service=runtime.service
   def natural_service(_,bus,cpu,target):
    try:
     if target==0xe4c0:
      runtime.begin_poll();status=runtime.poll_body(bus,cpu)
      if status==0:runtime.end_poll()
      return status
     if target in runtime.render_groups:return runtime.render_CPU[runtime.render_groups[target]](bus,cpu,runtime.callbacks[5],runtime.service,None,1000000,1)
     if target in runtime.new_groups:
      if target==0xe4c0:runtime.begin_poll()
      status=runtime.new_groups[target](bus,cpu,runtime.callbacks[5],runtime.service,None,1000000,1)
      if target==0xe4c0 and status==0:runtime.end_poll()
      return status
     if target==0xf0fa:return runtime.world_camera(bus,cpu,runtime.callbacks[5],runtime.service,None)
     if target==0x20820:return runtime.world_target(bus,cpu,runtime.service,None)
     return parent_service(_,bus,cpu,target)
    except BaseException as error:runtime.errors.append(repr(error));return 1
   runtime.service=media.world_cpu.SERVICE(natural_service);save(out/'status.json',dict(status='running',mode=mode));trace=[]
   try:
    if mode=='native':
     for _ in range(1000000):
      pc=runtime.cpu().pc
      if selected is not None and pc==selected['CPU']['pc'] and runtime.current()==selected['context']:break
      trace.append(pc)
      if pc==0xe4c0:runtime.begin_poll()
      core.m68k_execute(1)
      if pc==0xe504:runtime.end_poll()
      command=core.GPUReadLong(0xf03204,6)
      if command==0x4320:runtime.run_movement_request()
      elif command==0x4b00:runtime.run_render_request(command)
     else:raise AssertionError(('native natural world bound',hex(pc)))
     final=runtime.cpu();status=6
    else:
     runtime.C_CPU=CPU;status=runtime.render_CPU['world_flow'](c.byref(runtime.bus),c.byref(CPU),runtime.callbacks[5],runtime.service,None,1000000,1);assert status==6 and not runtime.errors,(status,hex(CPU.pc),runtime.errors);final=CPU;assert runtime.C_original_CPU_attempts==0
    if mode=='C':
     assert final.pc==0xdf60;assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0;selected=dict(CPU=media.scheduler.cpu_dict(final),context=runtime.current());save(out/'selected-C-continuation.json',selected)
    assert selected and final.pc==selected['CPU']['pc'] and runtime.current()==selected['context'];RAM=runtime.device.ram();(out/(mode+'-RAM.bin')).write_bytes(RAM);row=dict(CPU=media.scheduler.cpu_dict(final),RAM=sha(RAM),hardware=runtime.hardware(),GPU_calls=runtime.gpu_calls,polls=runtime.polls,source_clock=int.from_bytes(RAM[0x778cc:0x778d0],'big'),context=hex(runtime.current()),next_PC_in_existing_source_instruction_maps=final.pc in runtime.rows,status=status,processor_instructions=len(trace)if mode=='native'else None);save(out/(mode+'.json'),row);results.append(row)
   except BaseException as error:
    (out/(mode+'-failure-RAM.bin')).write_bytes(runtime.device.ram());save(out/(mode+'-failure.json'),dict(error=repr(error),CPU=media.scheduler.cpu_dict(runtime.cpu())if mode=='native'else media.scheduler.cpu_dict(CPU),errors=runtime.errors,GPU_calls=runtime.gpu_calls,polls=runtime.polls,trace_last=list(map(hex,trace[-30:]))));raise
  finally:runtime.oracle.close()
 for key in ['CPU','RAM','hardware','GPU_calls','polls','source_clock','context']:assert results[0][key]==results[1][key],('natural world task mismatch',key)
 report=dict(status='natural_source_world_task_and_next_task_handoff_C_native_match',directory=str(out),source_checkpoint=str(source/'checkpoint.json'),results=results,no_CPU_reseed=True,no_supplied_world_pose=True,no_task_quiescence=True,no_host_world_clock_increment=True,whole_game_complete=False,limits=['Captured natural world-entry state with earlier firmware/CD/SSI/GPU-stack inputs. CPU-task prefix plus originalTRAP3/scheduler/RTE to next selected continuation; global scheduler/video/DSP held and synchronous movement GPU service if reached remains.','No nativeC full-frame playability/physical/ordinaryboot or later task/scene proof.']);save(out/'report.json',report);save(ROOT/'verification/natural-world-handoff-current.json',report);save(out/'status.json',dict(status='terminal_pass'));print(report['status'],flush=True)
except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
finally:media.scheduler.Native=original_Native;media.scheduler.movement.Device.__init__=original_device_init
