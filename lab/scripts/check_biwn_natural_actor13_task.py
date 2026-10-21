"""Adopt source-derived DD40 native/C contexts into existing resource startup.

No inventory baseline reset, extracted stage/stub, or CPU reseed. Existing
startup clock/buttons/BIOS file ABI/disc completion/GPU services retained.
"""
import ctypes as c,hashlib,json,types,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_entry_scheduled_startup as entry
import check_biwn_movie_GPU as GPU
import check_biwn_dsp_media_audio as DSP
ROOT=entry.ROOT;save=entry.save;sha=entry.sha;base=entry.base;media=entry.media
world=json.loads((ROOT/'verification/natural-world-entry-current.json').read_text());source=Path(world['captured']['directory']);record=json.loads((source/'checkpoint.json').read_text())
out=ROOT/'verification/BIWN-natural-actor13-task'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);lib=ROOT/'verification/BIWN-game-firstboot-movie-transport-music-cold-entry-timer-startup-loading-movie-world/20261015T001755.513281Z/libscheduled-startup.dylib';assert lib.exists();mappings=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup']];rows=[]
for p in session.glob('*-fullCPU-generation.json'):rows+=json.loads(p.read_text()).get('instructions_decoded',[])
ram=(source/'RAM.bin').read_bytes();rows+=json.loads((session/'input-dispatch-fullCPU-workmap.json').read_text())['instructions']
for a,b in base.joined.actor.navigation.RANGES+base.joined.actor.rng_cpu.RANGES+[(0x4088,0x408a),(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xdf7a,0xdf7c),(0xdeb6,0xdee2),(0xe4c0,0xe53c),(0xeac4,0xec04),(0x13440,0x134dc),(0x13c9a,0x13f12),(0xe220,0xe26c),(0x13b5a,0x13c9a),(0x1028e,0x10430),(0x10652,0x106c4),(0x191f4,0x192a2),(0x192bc,0x19f2c),(0xf360,0xf368),(0xf880,0xf888),(0xf0fa,0xf35e),(0x20820,0x20a9c)]:rows+=base.fixtures.gen.loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
entry.Runtime.entry_rows=json.loads((session/'entry-setup-fullCPU-generation.json').read_text())['instructions_decoded'];disc=base.joined.Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';extra_lib=out/'libgeometry-submit.dylib';extra_src=ROOT/'projects/black-ice-white-noise/restoration/biwn_gpu_geometry_submit_cpu.c';compile_run=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(extra_src.parent),str(extra_src),'-o',str(extra_lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'extra-compiler.txt').write_text(compile_run.stdout+compile_run.stderr);assert compile_run.returncode==0;results=[];original_Native=media.scheduler.Native;original_device_init=media.scheduler.movement.Device.__init__
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
   runtime.health_addresses={r['address']for r in json.loads((session/'health-timeout-fullCPU-generation.json').read_text())['instructions_decoded']};runtime.entry_coverage=set();runtime.timer_enabled=True
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
   runtime.begin_poll=types.MethodType(begin_poll,runtime);extra=c.CDLL(str(extra_lib));geometry_submit=extra.biwn_gpu_geometry_submit_cpu_body;geometry_submit.argtypes=runtime.fn.argtypes;geometry_submit.restype=c.c_int;parent_service=runtime.service
   def natural_service(_,bus,cpu,target):
    try:
     if target==0xe0a6:return geometry_submit(bus,cpu,runtime.callbacks[5],runtime.service,None,1000000,1)
     if target==0xde08:return runtime.system_dispatch(bus,cpu,128)
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
   runtime.service=media.world_cpu.SERVICE(natural_service);save(out/'status.json',dict(status='running',mode=mode));trace=[];timer_delivered=[False]
   try:
    if mode=='native':
     for _ in range(1000000):
      pc=runtime.cpu().pc
      if pc==0xddec and runtime.current()==0xc0928 and not timer_delivered[0]:runtime.clock_tick();timer_delivered[0]=True
      if selected is not None and pc==selected['CPU']['pc'] and runtime.current()==selected['context']:break
      trace.append(pc)
      if pc==0xe4c0:runtime.begin_poll()
      core.m68k_execute(1)
      if pc==0xe504:runtime.end_poll()
      command=core.GPUReadLong(0xf03204,6)
      if command==0x4320:runtime.run_movement_request()
      elif command in [0x4b00,0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:runtime.run_render_request(command)
     else:raise AssertionError(('native natural world bound',hex(pc)))
     final=runtime.cpu();status=6
    else:
     runtime.C_CPU=CPU;status=runtime.render_CPU['world_flow'](c.byref(runtime.bus),c.byref(CPU),runtime.callbacks[5],runtime.service,None,1000000,1);assert status==6 and not runtime.errors,(status,hex(CPU.pc),runtime.errors);final=CPU;assert runtime.C_original_CPU_attempts==0
    if mode=='C':
     assert final.pc==0xdf60;assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0;assert final.pc==0x21d1a and runtime.current()==0xc1d28
     tile_proof=json.loads((ROOT/'verification/tile-task-candidate-current.json').read_text());assert tile_proof['cases']==384 and tile_proof['accepted_for_standalone_scope'];tile_lib=c.CDLL(str(Path(tile_proof['directory'])/'libtile-task.dylib'));tile_fn=tile_lib.biwn_tile_task_cpu_run;tile_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];tile_fn.restype=c.c_int;assert tile_fn(c.byref(runtime.bus),c.byref(final),100)==6 and final.pc==0xdf60;assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     assert final.pc==0xf4d8 and runtime.current()==0xc1928
     for _ in range(128):
      runtime.C_CPU=final
      if final.pc==0xdf60:break
      assert final.pc in [0xf4d8,0xf56e,0xf70c],('actor continuation',hex(final.pc))
      status=runtime.actor_body(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],c.cast(runtime.service,base.joined.actor.actor.SERVICE),None,1000000);assert status in [0,4,6,8] and not runtime.errors,(status,hex(final.pc),runtime.errors)
     else:raise AssertionError(('actor task bound',hex(final.pc)))
     assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     assert final.pc==0xf4d8 and runtime.current()==0xc1528
     for _ in range(128):
      runtime.C_CPU=final
      if final.pc==0xdf60:break
      assert final.pc in [0xf4d8,0xf56e,0xf70c],('second actor continuation',hex(final.pc))
      status=runtime.actor_body(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],c.cast(runtime.service,base.joined.actor.actor.SERVICE),None,1000000);assert status in [0,4,6,8] and not runtime.errors,(status,hex(final.pc),runtime.errors)
     else:raise AssertionError(('second actor bound',hex(final.pc)))
     assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     assert final.pc==0xddec and runtime.current()==0xc0928
     runtime.clock_tick();timer_delivered[0]=True
     for _ in range(128):
      if runtime.current()!=0xc0928:break
      assert final.pc in runtime.system_addresses,('system continuation',hex(final.pc));status=runtime.system_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,1,0);assert status in [0,4,6,8] and not runtime.errors,(status,hex(final.pc),runtime.errors)
     else:raise AssertionError(('system bound',hex(final.pc)))
     if final.pc==0xdf66:assert runtime.resume_fn(c.byref(runtime.bus),c.byref(final))==0
     assert final.pc==0x17dce and runtime.current()==0xc0d28
     for _ in range(128):
      runtime.C_CPU=final
      if final.pc==0xdf60:break
      assert final.pc in runtime.render_groups,('renderer continuation',hex(final.pc));status=runtime.render_CPU[runtime.render_groups[final.pc]](c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,1000000,1);assert status in [0,4,6,8] and not runtime.errors,(status,hex(final.pc),runtime.errors)
      if status==0:runtime.virtual_RTS(final)
     else:raise AssertionError(('renderer task bound',hex(final.pc)))
     assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     idle_steps=[]
     for _ in range(128):
      before_context=runtime.current();before_pc=final.pc
      if final.pc not in [0xf360,0xf366,0xf880,0xf886]:break
      status=runtime.idle_body(c.byref(runtime.bus),c.byref(final),base.joined.actor.prior.BODY(),None,128);assert status==0 and not runtime.errors,(status,hex(final.pc),runtime.errors)
      idle_steps.append(dict(before_context=hex(before_context),before_PC=hex(before_pc),after_context=hex(runtime.current()),after_PC=hex(final.pc)))
     else:raise AssertionError(('idle continuation bound',hex(final.pc)))
     save(out/'C-idle-continuations.json',idle_steps)
     assert final.pc==0x1b4e8 and runtime.current()==0xc5128
     proximity_proof=json.loads((ROOT/'verification/proximity-message-task-current.json').read_text());assert proximity_proof['cases']==240 and proximity_proof['instructions_covered']==[28,28];proximity_lib=c.CDLL(str(Path(proximity_proof['directory'])/'libproximity.dylib'));proximity_fn=proximity_lib.biwn_proximity_message_task_cpu_body;proximity_fn.argtypes=runtime.fn.argtypes;proximity_fn.restype=c.c_int;status=proximity_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,100000,1);assert status==6 and final.pc==0xdf60 and not runtime.errors,(status,hex(final.pc),runtime.errors);assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     assert final.pc==0xec46 and runtime.current()==0xc4d28
     actor20_proof=json.loads((ROOT/'verification/actor20-task-current.json').read_text());assert actor20_proof['cases']==640 and actor20_proof['instructions_covered']==[84,84];actor20_lib=c.CDLL(str(Path(actor20_proof['directory'])/'libproximity.dylib'));actor20_fn=actor20_lib.biwn_actor20_task_cpu_body;actor20_fn.argtypes=runtime.fn.argtypes;actor20_fn.restype=c.c_int;status=actor20_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,100000,1);assert status==6 and final.pc==0xdf60 and not runtime.errors,(status,hex(final.pc),runtime.errors);assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     assert final.pc==0xefc6 and runtime.current()==0xc4928
     actor19_proof=json.loads((ROOT/'verification/actor19-task-current.json').read_text());assert actor19_proof['cases']==640 and actor19_proof['instructions_covered']==[79,79];actor19_lib=c.CDLL(str(Path(actor19_proof['directory'])/'libproximity.dylib'));actor19_fn=actor19_lib.biwn_actor19_task_cpu_body;actor19_fn.argtypes=runtime.fn.argtypes;actor19_fn.restype=c.c_int;status=actor19_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,100000,1);assert status==6 and final.pc==0xdf60 and not runtime.errors,(status,hex(final.pc),runtime.errors);assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     assert final.pc==0x1a946 and runtime.current()==0xc4528
     actor15_proof=json.loads((ROOT/'verification/actor15-task-current.json').read_text());assert actor15_proof['cases']==640 and actor15_proof['instructions_covered']==[79,79];actor15_lib=c.CDLL(str(Path(actor15_proof['directory'])/'libproximity.dylib'));actor15_fn=actor15_lib.biwn_actor15_task_cpu_body;actor15_fn.argtypes=runtime.fn.argtypes;actor15_fn.restype=c.c_int;status=actor15_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,100000,1);assert status==6 and final.pc==0xdf60 and not runtime.errors,(status,hex(final.pc),runtime.errors);assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     assert final.pc==0x1a58e and runtime.current()==0xc4128
     actor14_proof=json.loads((ROOT/'verification/actor14-task-current.json').read_text());assert actor14_proof['cases']==764 and actor14_proof['instructions_covered']==[108,108];actor14_lib=c.CDLL(str(Path(actor14_proof['directory'])/'libproximity.dylib'));actor14_fn=actor14_lib.biwn_actor14_task_cpu_body;actor14_fn.argtypes=runtime.fn.argtypes;actor14_fn.restype=c.c_int;status=actor14_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,100000,1);assert status==6 and final.pc==0xdf60 and not runtime.errors,(status,hex(final.pc),runtime.errors);assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     assert final.pc==0x17676 and runtime.current()==0xc3d28
     actor13_proof=json.loads((ROOT/'verification/actor13-task-current.json').read_text());assert actor13_proof['cases']==2908 and actor13_proof['instructions_covered']==[169,169];actor13_lib=c.CDLL(str(Path(actor13_proof['directory'])/'libproximity.dylib'));actor13_fn=actor13_lib.biwn_actor13_task_cpu_body;actor13_fn.argtypes=runtime.fn.argtypes;actor13_fn.restype=c.c_int;status=actor13_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,100000,1);assert status==6 and final.pc==0xdf60 and not runtime.errors,(status,hex(final.pc),runtime.errors);assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0
     selected=dict(CPU=media.scheduler.cpu_dict(final),context=runtime.current());save(out/'selected-C-continuation.json',selected)
    assert selected and final.pc==selected['CPU']['pc'] and runtime.current()==selected['context'];RAM=runtime.device.ram();(out/(mode+'-RAM.bin')).write_bytes(RAM);row=dict(CPU=media.scheduler.cpu_dict(final),RAM=sha(RAM),hardware=runtime.hardware(),GPU_calls=runtime.gpu_calls,polls=runtime.polls,source_clock=int.from_bytes(RAM[0x778cc:0x778d0],'big'),externally_supplied_source_GPU_IRQ2_events=int(timer_delivered[0]),context=hex(runtime.current()),next_PC_in_existing_source_instruction_maps=final.pc in runtime.rows,status=status,processor_instructions=len(trace)if mode=='native'else None);save(out/(mode+'.json'),row);results.append(row)
   except BaseException as error:
    (out/(mode+'-failure-RAM.bin')).write_bytes(runtime.device.ram());save(out/(mode+'-failure.json'),dict(error=repr(error),CPU=media.scheduler.cpu_dict(runtime.cpu())if mode=='native'else media.scheduler.cpu_dict(CPU),errors=runtime.errors,GPU_calls=runtime.gpu_calls,polls=runtime.polls,trace_last=list(map(hex,trace[-30:]))));raise
  finally:runtime.oracle.close()
 for key in ['CPU','RAM','hardware','GPU_calls','polls','source_clock','context','externally_supplied_source_GPU_IRQ2_events']:assert results[0][key]==results[1][key],('natural world task mismatch',key)
 report=dict(status='natural_renderer_idle_proximity_actor20_actor19_actor15_actor14_actor13_prefix_C_native_match',directory=str(out),source_checkpoint=str(source/'checkpoint.json'),tile_candidate_check=str(Path(tile_proof['directory'])/'report.json'),tile_candidate_sha256=tile_proof['protocol']['candidate_sha256'],results=results,no_CPU_reseed=True,no_supplied_world_pose=True,no_task_quiescence=True,no_host_world_clock_increment=True,whole_game_complete=False,limits=['Captured natural world-entry state with earlier firmware/CD/SSI/GPU-stack inputs. Worldtask plus guardedtile12task and two originalTRAP3/scheduler/RTE handoffs to selected actor continuation; global scheduler/video/DSP held and synchronous movement GPU service if reached remains.','No nativeC full-frame playability/physical/ordinaryboot or later task/scene proof.']);save(out/'report.json',report);save(ROOT/'verification/natural-actor13-task-current.json',report);save(out/'status.json',dict(status='terminal_pass'));print(report['status'],flush=True)
except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
finally:media.scheduler.Native=original_Native;media.scheduler.movement.Device.__init__=original_device_init
