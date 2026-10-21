"""Adopt source-derived DD40 native/C contexts into existing resource startup.

No inventory baseline reset, extracted stage/stub, or CPU reseed. Existing
startup clock/buttons/BIOS file ABI/disc completion/GPU services retained.
"""
import ctypes as c,hashlib,json,types,re,os,subprocess,argparse,uuid
from array import array
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_entry_scheduled_startup as entry
import check_biwn_movie_GPU as GPU
import check_biwn_dsp_media_audio as DSP
import check_biwn_music_DSP_engine as music
from biwn_music_engine_runtime import MusicEngineMixin
import biwn_live_source_prefix
import biwn_live_header_handoff
from probe_biwn_gpu_projection import gpu_state
def framebuffer_metadata(runtime,pixels):
 return dict(allocation_pixels=1024*512,sha256=hashlib.sha256(pixels).hexdigest(),
             screen_pitch_pixels=c.c_uint32.in_dll(runtime.core,'screenPitch').value,
             tom_width=c.c_uint32.in_dll(runtime.core,'tomWidth').value,
             tom_height=c.c_uint32.in_dll(runtime.core,'tomHeight').value,
             frontend_width=c.c_int.in_dll(runtime.core,'videoWidth').value,
             frontend_height=c.c_int.in_dll(runtime.core,'videoHeight').value,
             pixel_format='XRGB8888; little-endian BGRX',
             scope='Shared core host allocation and live layout; no frontend/physical presentation proof')

class MusicRuntime(MusicEngineMixin,entry.Runtime):
 source_system_clock_tick=entry.Runtime.clock_tick
class JerryEventRuntime(MusicRuntime):
 def hardware(self):
  result=super().hardware();buf=c.create_string_buffer(100000);self.core.EventStateSave.argtypes=[c.c_void_p];self.core.EventStateSave.restype=c.c_size_t;size=self.core.EventStateSave(buf)
  assert 0<size<=len(buf);result['event_queue']=dict(size=size,sha256=sha(buf.raw[:size]));return result
 def setup_event_owner(self):
  self.jerry_events=[];self.jerry_elapsed=0.0;self.jerry_owner_error=[];self.jerry_current_IRQs=[]
  self.core.GetTimeToNextEvent.argtypes=[c.c_int];self.core.GetTimeToNextEvent.restype=c.c_double
  self.core.HandleNextEvent.argtypes=[c.c_int];self.core.SubtractEventTimes.argtypes=[c.c_double,c.c_int]
  self.IRQ_OWNER=c.CFUNCTYPE(c.c_int,c.c_int,c.c_int)
  def owner(irq,state):
   self.jerry_current_IRQs.append([irq,state])
   if self.mode=='native':return 0
   try:
    assert state==1 and self.engine_irq(c.byref(self.C_DSP),irq)==0,('C IRQ ownership',irq,state)
   except BaseException as error:self.jerry_owner_error.append(repr(error))
   return 1
  self.irq_owner=self.IRQ_OWNER(owner);self.core.BIWNSetDSPIRQOwner.argtypes=[self.IRQ_OWNER];self.core.BIWNSetDSPIRQOwner(self.irq_owner)
  def queue_bytes():
   buf=c.create_string_buffer(100000);self.core.EventStateSave.argtypes=[c.c_void_p];self.core.EventStateSave.restype=c.c_size_t;size=self.core.EventStateSave(buf);return buf.raw[:size]
  self.event_queue_initial=queue_bytes()
  if options.normalize_jerry_queue:
   self.core.RemoveCallback.argtypes=[c.c_void_p]
   for name in ['JERRYI2SCallback','JERRYPIT1Callback','JERRYPIT2Callback']:
    for _ in range(32):self.core.RemoveCallback(c.cast(getattr(self.core,name),c.c_void_p))
   self.core.JERRYResetPIT1();self.core.JERRYResetPIT2();self.core.JERRYRescheduleI2S()
  self.event_queue_after_setup=queue_bytes();(self.out/(self.mode+'-initial-event-queue.bin')).write_bytes(self.event_queue_initial);(self.out/(self.mode+'-setup-event-queue.bin')).write_bytes(self.event_queue_after_setup)

 def clock_tick(self):
  self.source_system_clock_tick();remaining=options.jerry_slice_us
  for _ in range(10000):
   due=self.core.GetTimeToNextEvent(1)
   assert due>=-0.001,('negative JERRY event time',due)
   due=max(0.0,due)
   if due>remaining:
    self.core.SubtractEventTimes(remaining,1);self.jerry_elapsed+=remaining;break
   self.jerry_current_IRQs=[];self.core.HandleNextEvent(1);remaining-=due;self.jerry_elapsed+=due
   assert not self.jerry_owner_error,self.jerry_owner_error
   self.engine_pump('JERRY_event_'+str(len(self.jerry_events)))
   self.jerry_events.append(dict(time_us=self.jerry_elapsed,IRQs=list(self.jerry_current_IRQs),PCM=music.dsp.strobed_pair(self.dac()),DSP_sha256=sha(self.logical_DSP()),DAC_sha256=sha(self.dac())))
  else:raise AssertionError('JERRY event bound')

ROOT=entry.ROOT;save=entry.save;sha=entry.sha;base=entry.base;media=entry.media
parser=argparse.ArgumentParser();parser.add_argument('--rounds',type=int,default=3);parser.add_argument('--world-step-budget',type=int,help='Explicit bounded instruction/dispatch limit for action discovery');parser.add_argument('--controller-script',type=Path,help='JSON poll windows selecting documented emulated-pad button names; no guest memory/clock patches');parser.add_argument('--sustained-input',action='store_true',help='After120polls hold first direction from input plan; no pose writes');parser.add_argument('--input-plan',choices=['none','up-left','down-right'],default='none');parser.add_argument('--no-publish',action='store_true',help='Keep this exploratory run separate from the accepted current proof');parser.add_argument('--music-words',action='store_true',help='Advance the source DSP mixer with declared word/timer events; video and global cycle scheduling remain held');parser.add_argument('--cpu-library',type=Path,help='Explicit CPU runtime candidate; default uses the checked runtime when available');parser.add_argument('--jerry-events',action='store_true',help='Use actual pinned JERRY event queue callbacks; CPU/world time slice remains a supplied schedule');parser.add_argument('--jerry-slice-us',type=float,default=16666.666666666668);parser.add_argument('--event-core',type=Path);parser.add_argument('--normalize-jerry-queue',action='store_true',help='Explicitly rebuild SSI/PIT callbacks from existing device registers after removing duplicate callbacks from the held-event export');parser.add_argument('--entry-proof',type=Path);parser.add_argument('--entry-export-proof',type=Path);parser.add_argument('--live-4000',action='store_true',help='Run the source4000prefix on the same runtime before startup; never load the DD40 export');parser.add_argument('--live-header',action='store_true',help='Start at earlier captured361E BIOS completion and run its checked tail before game entry');parser.add_argument('--fresh-hle',action='store_true',help='Fresh disc HLE load through reconstructed entry/prefix; no initial machine-state file');parser.add_argument('--execution-mode',choices=['native','C'],help='Isolated process side of fresh HLE comparison; reports remain unpaired');parser.add_argument('--hle-assets',action='store_true',help='Experimental sole HLE sector-stream owner and source VBI progress afterDD40');parser.add_argument('--hle-asset-clock',action='store_true',help='Experimental incremental asset stream/source VBI at supplied system clock pulses');parser.add_argument('--cpu-cycle-probe',action='store_true',help='Original CPU cycle cost comparison; does not adopt timing');parser.add_argument('--loader-cycle-clock',action='store_true',help='Experimental CPU-cost-driven main event timing through loader180000->4000 only');parser.add_argument('--prefix-instruction-probe',action='store_true',help='Read-only C/native prefix instruction-state/cost tracing using observer candidate library');parser.add_argument('--prefix-instruction-clock',action='store_true',help='Experimental CPU-cost-driven main events4000->DD40, using case-boundary observer');parser.add_argument('--startup-clock-probe',action='store_true',help='Record supplied clock pulse boundaries without changing timing');parser.add_argument('--startup-instruction-probe',action='store_true',help='Read-only generated-C/native startup instruction coverage');parser.add_argument('--startup-state-probe',action='store_true',help='Full CPU state hashes at every startup instruction boundary');parser.add_argument('--startup-cost-probe',action='store_true',help='Record cost-only predictions at every startup instruction; no timing adoption');parser.add_argument('--startup-elapsed-clock',action='store_true',help='Candidate CPU-budgeted startup services at system-task safe points; event boundary coupling remains deferred');parser.add_argument('--startup-single-step',action='store_true',help='Experimental direct C startup one-instruction dispatcher');parser.add_argument('--startup-boundary-events',action='store_true',help='Experimental main/JERRY events advanced at startup CPU boundaries');parser.add_argument('--OP-GPU-trace',action='store_true',help='Reference-only read-only OP GPU slices');parser.add_argument('--OP-GPU-owner',action='store_true',help='Experimental compiled OP GPU slices with full retained reference comparison');parser.add_argument('--world-instruction-probe',action='store_true',help='Read-only original world CPU PCs/states/costs');parser.add_argument('--framebuffer-probe',action='store_true',help='Capture shared1x framebuffer allocation without modifying it');parser.add_argument('--world-single-step',action='store_true',help='Experimental one-instruction C world dispatcher');parser.add_argument('--world-stable-clock',action='store_true',help='World clock assigns exact CPU target and phase-relative JERRY time, making repeated samples idempotent');parser.add_argument('--frontend-video-layout',action='store_true',help='Refresh headless host pitch/dimensions from live TOM geometry;1xonly');parser.add_argument('--world-boundary-events',action='store_true',help='Experimental world main/JERRY CPU event time');options=parser.parse_args();assert options.world_step_budget is None or 200000<=options.world_step_budget<=50000000;assert not options.world_stable_clock or options.world_boundary_events;assert not options.frontend_video_layout or options.world_boundary_events;assert not options.world_boundary_events or(options.world_instruction_probe and options.startup_boundary_events);assert not options.world_single_step or(options.execution_mode=='C'and options.world_instruction_probe);assert not options.world_instruction_probe or(options.execution_mode in ['native','C']and options.startup_instruction_probe);assert not options.OP_GPU_owner or(options.startup_boundary_events and options.execution_mode=='C');assert not options.OP_GPU_trace or (options.startup_boundary_events and options.execution_mode=='native');assert not options.startup_boundary_events or options.startup_single_step;assert not options.startup_single_step or options.startup_elapsed_clock;assert not options.startup_elapsed_clock or options.startup_cost_probe;assert not options.startup_cost_probe or options.startup_state_probe;assert not options.startup_state_probe or options.startup_instruction_probe;assert not options.startup_instruction_probe or (options.fresh_hle and options.cpu_library and options.no_publish);assert not options.prefix_instruction_clock or options.prefix_instruction_probe;assert not options.prefix_instruction_probe or (options.fresh_hle and options.cpu_library and options.no_publish);assert not options.loader_cycle_clock or (options.fresh_hle and options.no_publish);assert not options.cpu_cycle_probe or (options.execution_mode=='native' and options.fresh_hle and options.no_publish);assert not options.hle_asset_clock or options.hle_assets;assert not options.hle_assets or options.fresh_hle;assert options.execution_mode is None or (options.fresh_hle and options.no_publish);assert 2<=options.rounds<=1200;assert not options.live_header or options.live_4000;assert not options.live_4000 or (options.entry_proof and options.music_words and options.jerry_events and options.event_core and options.no_publish);assert not options.entry_proof or (options.entry_export_proof and options.no_publish);assert not options.normalize_jerry_queue or options.jerry_events;assert not options.jerry_events or (options.music_words and options.event_core and options.no_publish and 0<options.jerry_slice_us<=20000);assert not options.music_words or options.no_publish,'Experimental music path must retain the accepted current pointer'
controller_windows=[]
if options.controller_script:
 import emulated_pad_input
 data=json.loads(options.controller_script.read_text())
 for window in data['windows']:
  assert set(window)=={'start_poll','stop_poll','buttons'} and 0<=window['start_poll']<window['stop_poll']<=1200
  indices=[emulated_pad_input.BUTTON_NAMES.index('BUTTON_'+name)for name in window['buttons']]
  controller_windows.append({**window,'indices':indices})
source=Path(json.loads((options.entry_proof or ROOT/'verification/captured-source-music-entry-current.json').read_text())['directory']);export_proof=json.loads((options.entry_export_proof or ROOT/'verification/captured-entry-exports-current.json').read_text());assert export_proof['source_directory']==str(source)
out=ROOT/'verification/BIWN-entry-natural-task-rounds'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+uuid.uuid4().hex[:8]);out.mkdir(parents=True);print(out,flush=True)
session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);lib=options.cpu_library or (Path(json.loads((ROOT/'verification/source-runtime-rebuild-current.json').read_text())['library'])if (ROOT/'verification/source-runtime-rebuild-current.json').exists()else ROOT/'verification/BIWN-game-firstboot-movie-transport-music-cold-entry-timer-startup-loading-movie-world/20261015T001755.513281Z/libscheduled-startup.dylib');assert lib.exists();mappings=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup']];rows=[]
for p in session.glob('*-fullCPU-generation.json'):rows+=json.loads(p.read_text()).get('instructions_decoded',[])
ram=Path(json.loads((source/'native-continuation.json').read_text())['source_checkpoint']).parent.joinpath('RAM.bin').read_bytes();rows+=json.loads((session/'input-dispatch-fullCPU-workmap.json').read_text())['instructions']
for a,b in base.joined.actor.navigation.RANGES+base.joined.actor.rng_cpu.RANGES+[(0x4088,0x408a),(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xdf7a,0xdf7c),(0xdeb6,0xdee2),(0xe4c0,0xe53c),(0xeac4,0xec04),(0x13440,0x134dc),(0x13c9a,0x13f12),(0xe220,0xe26c),(0x13b5a,0x13c9a),(0x1028e,0x10430),(0x10652,0x106c4),(0x191f4,0x192a2),(0x192bc,0x19f2c),(0xf360,0xf368),(0xf880,0xf888),(0xf0fa,0xf35e),(0x20820,0x20a9c)]:rows+=base.fixtures.gen.loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
entry.Runtime.entry_rows=json.loads((session/'entry-setup-fullCPU-generation.json').read_text())['instructions_decoded'];disc=base.joined.Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';results=[];original_Native=media.scheduler.Native;original_device_init=media.scheduler.movement.Device.__init__
try:
 for mode in ([options.execution_mode] if options.execution_mode else ['native','C']):
  export=json.loads((source/(mode+'-continuation.json')).read_text())
  def selected_Native(*args,**kwargs):kwargs['diagnostic_core']=options.event_core or Path(export['core_path']);return original_Native(*args,**kwargs)
  def selected_device_init(self,*args,**kwargs):kwargs['core']=options.event_core or Path(export['core_path']);return original_device_init(self,*args,**kwargs)
  media.scheduler.Native=selected_Native;media.scheduler.movement.Device.__init__=selected_device_init
  try:runtime=(JerryEventRuntime if options.jerry_events else MusicRuntime if options.music_words else entry.Runtime)(lib,rows,*[m['instructions_decoded']for m in mappings],disc=disc,out=out,frame_directory=frames)
  finally:media.scheduler.Native=original_Native;media.scheduler.movement.Device.__init__=original_device_init
  try:
   runtime.gate=next(g for g in json.loads((ROOT/'verification/biwn-startup-loaded-doorway-candidates.json').read_text())['candidates']if g['target']==312)
   extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());message=next(m for m in extraction['messages']if m['message_id']==60);record=next(r for r in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']if r['message_id']==60);message={**message,'marker':int(record['source_long_fields'][2],16)}
   runtime.health_addresses={r['address']for r in json.loads((session/'health-timeout-fullCPU-generation.json').read_text())['instructions_decoded']};runtime.entry_coverage=set();runtime.timer_enabled=True
   def adopt(self,unused_ram,case,selected_mode):
    assert selected_mode==mode;self.mode=mode;core=self.core
    core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool;assert core.CDIntfOpenImage(export['disc_image'].encode());core.CDROMInit();core.CDROMReset();core.BIWNDiagnosticRepeatSeek.argtypes=[c.c_uint32];core.BIWNDiagnosticRepeatSeek(int(export['force_repeated_seek_diagnostic']));core.BIWNDiagnosticTOCOrigin.argtypes=[c.c_uint32];core.BIWNDiagnosticTOCOrigin(int(export['TOC_origin_diagnostic'])+2*int(export['TOC_read_origin_diagnostic']));c.c_bool.in_dll(core,'bootConfig').value=export['native_CD_scheduler_enabled']
    captured=None
    if options.live_4000:
     captured=json.loads((ROOT/'verification/BIWN-firmware-header-resume/20261015T105258.234232Z/resume-checkpoint/checkpoint.json'if options.live_header else Path(export['source_checkpoint'])).read_text());captured_folder=Path(captured['directory']);ROM=(captured_folder/'ROM-provider.bin').read_bytes();blob=(captured_folder/'libretro-state.bin').read_bytes();assert sha(ROM)==captured['ROM_provider_sha256'] and sha(blob)==captured['libretro_state_sha256']
    else:
     ROM=Path(export['ROM_provider_file']).read_bytes();blob=Path(export['shared_core_file']).read_bytes();assert sha(ROM)==export['ROM_provider_sha256'] and sha(blob)==export['shared_core_sha256']
    self.rom=c.c_void_p.in_dll(core,'jaguarMainROM').value;c.memmove(self.rom,ROM,len(ROM));core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool;assert core.retro_unserialize(c.create_string_buffer(blob),len(blob))
    if export.get('single_SSI_chain_diagnostic'):
     core.BIWNSetSSISingleChain.argtypes=[c.c_uint32];core.BIWNSetSSISingleChain(1)
    if options.live_4000:
     self.gpu=GPU.state_from_raw(gpu_state(core)[0])if mode=='C'else None;self.C_DSP=DSP.state_from_raw(self.raw_DSP())if mode=='C'else None
    else:
     self.gpu=GPU.state_from_raw(Path(export['GPU_logical_file']).read_bytes())if mode=='C'else None;self.C_DSP=(music.state_from_raw if options.music_words else DSP.state_from_raw)(Path(export['DSP_logical_file']).read_bytes())if mode=='C'else None
    self.entry_CPU=media.CPU();CPU_input=captured['CPU']if captured else export['CPU'];self.entry_CPU.registers[:]=CPU_input['registers']
    for field in ['pc','sr','usp','ssp']:setattr(self.entry_CPU,field,CPU_input[field])
    self.device.pointer=self.device.lib.lab_device_ram();self.trace=hashlib.sha256();self.trace_count=0;self.bus_events=[]
    expected_RAM_sha=captured['RAM_sha256']if captured else sha(Path(export['RAM_file']).read_bytes())
    save(out/(mode+'-adoption-debug.json'),dict(core_path=core._name,expected_core_path=export['core_path'],device_pointer=self.device.pointer,core_RAM_pointer=c.c_void_p.in_dll(core,'jaguarMainRAM').value,actual_RAM_sha256=sha(self.device.ram()),input_RAM_sha256=expected_RAM_sha,initial_restore_PC=hex(self.entry_CPU.pc),DD40_export_loaded=not options.live_4000))
    assert sha(self.device.ram())==expected_RAM_sha and self.entry_CPU.pc==(0x361e if options.live_header else 0x4000 if options.live_4000 else 0xdd40)
    self.C_CPU=self.entry_CPU if mode=='C'else None;self.C_stopped=False;self.pending_init=False;self.pending_overlay=False;self.music_started=False;self.entry_active=False;self.gpu_calls=[];self.errors=[];self.C_original_CPU_attempts=0
    if options.live_4000:
     prefix_proof=json.loads(options.entry_proof.read_text());prefix_library=Path(prefix_proof['compiler'][-1]);assert prefix_library.exists()
     if options.live_header:
      tail_proof=json.loads((ROOT/'verification/header-handoff-tail-current.json').read_text());tail_folder=Path(tail_proof['directory']);tail_output=out/(mode+'-header-tail');tail_output.mkdir();reference=json.loads((out/'native-header-tail/native-CPU-instruction-checkpoints.json').read_text())if mode=='C'else None
      self.live_header_tail=biwn_live_header_handoff.run(self,tail_folder/'libhandoff.dylib',mode,tail_output,reference_points=reference);assert self.entry_CPU.pc==0x4000
     self.live_prefix=biwn_live_source_prefix.run(self,prefix_library,mode,initial_CPU=self.entry_CPU,preserve_owned_processors=options.live_header);save(out/(mode+'-live4000-prefix.json'),self.live_prefix)
     assert self.entry_CPU.pc==0xdd40
     if mode=='C':
      old=self.C_DSP;converted=music.State()
      for name,_ in DSP.State._fields_:
       if name=='registers':
        for bank in range(2):converted.registers[bank][:]=old.registers[bank]
       elif name=='local_RAM':converted.local_RAM[:]=old.local_RAM
       else:setattr(converted,name,getattr(old,name))
      converted.bank=converted.prestore_bank=0;assert not old.flags&0x4000;self.C_DSP=converted;self.C_CPU=self.entry_CPU
    self.gpu_calls=[];self.errors=[]
    self.queries=[];self.deliveries=[];self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0
    track=self.asset_disc.manifest['track'];TOC=self.device.ram()[0x2c00:0x3000];index=track['track']*8;assert TOC[index]==track['track'];origin=TOC[index+1]*4500+TOC[index+2]*75+TOC[index+3];old_origin=track['declared_start_lba']+150+track['pregap_sectors'];assert origin==old_origin-150
    def source_TOC_file_start(disc,start,end,packed):
     minute,second,frame=(packed>>16)&255,(packed>>8)&255,packed&255;assert packed>>24==0 and second<60 and frame<75
     absolute=minute*4500+second*75+frame;offset=(absolute-origin)*2352+disc.manifest['captured_CD_buffer_witness']['within_sector_phase'];count=end-start;assert start==0x1c0000 and 0<count<=0x40000 and 0<=offset<=len(disc.data)-count
     data=disc.data[offset:offset+count];disc.pending=(start,end,data);disc.requests.append(dict(destination_start=start,destination_end=end,packed_binary_MSF=packed,normalized_track_offset=offset,bytes=count,sha256=sha(data),track_origin_frames_from_source_TOC=origin,old_provider_track_origin_frames=old_origin,origin_delta_frames=origin-old_origin,existing674byte_stream_phase_retained=True))
    self.asset_disc.start=types.MethodType(source_TOC_file_start,self.asset_disc);save(out/(mode+'-source-TOC-file-origin.json'),dict(source_TOC_track_record=TOC[index:index+8].hex(),origin_frames=origin,old_origin_frames=old_origin,delta_frames=origin-old_origin,phase_bytes=674,physical_timing_verified=False))
    if options.music_words:
     if options.jerry_events:self.setup_event_owner()
     self.music_engine_active=True;self.engine_pump('source_DD40_mixer_resume')
    return dict(source_state_export=str(source/(mode+'-continuation.json'))if not options.live_4000 else None,initial_checkpoint=str(ROOT/'verification/BIWN-firmware-header-resume/20261015T105258.234232Z/resume-checkpoint/checkpoint.json')if options.live_header else export['source_checkpoint']if options.live_4000 else None,live_source4000_to_DD40=options.live_4000,no_DD40_export_restore=options.live_4000,no_baseline_reset=True,no_CPU_reseed=True,no_extracted_payload=True),dict(export_roundtrip_proof=export_proof['directory'])
   if options.fresh_hle:
    assert options.no_publish and options.music_words and options.jerry_events and options.event_core
    import biwn_fresh_HLE_platform,biwn_fresh_HLE_entry
    def fresh_adopt(self,unused_ram,case,selected_mode):
     assert selected_mode==mode;self.mode=mode
     platform=biwn_fresh_HLE_platform.load(self,out)
     core=self.core
     core.BIWNSetSSISingleChain.argtypes=[c.c_uint32];core.BIWNSetSSISingleChain(1)
     folder=out/(mode+'-fresh-HLE-entry');folder.mkdir()
     self.fresh_HLE_entry=biwn_fresh_HLE_entry.run(core,self.device.pointer,folder,mode,cycle_clock=options.loader_cycle_clock)
     self.live_prefix=biwn_live_source_prefix.run(self,lib,mode,initial_CPU=core._biwn_fresh_entry_CPU,platform_API=core._biwn_HLE_API_body,instruction_probe=options.prefix_instruction_probe,instruction_clock=options.prefix_instruction_clock)
     save(out/(mode+'-live4000-prefix.json'),self.live_prefix)
     if mode=='C':
      old=self.C_DSP;converted=music.State()
      for name,_ in DSP.State._fields_:
       if name=='registers':
        for bank in range(2):converted.registers[bank][:]=old.registers[bank]
       elif name=='local_RAM':converted.local_RAM[:]=old.local_RAM
       else:setattr(converted,name,getattr(old,name))
      converted.bank=converted.prestore_bank=0;assert not old.flags&0x4000;self.C_DSP=converted;self.C_CPU=self.entry_CPU
     # The bounded startup already supplies a file-backed CD adapter on both sides.
     # Disable HLE dispatch afterDD40 so native RTS cannot arm a second transport.
     core.JaguarCDHLESetActive.argtypes=[c.c_bool];core.JaguarCDHLESetActive(bool(options.hle_assets))
     self.C_stopped=False;self.pending_init=False;self.pending_overlay=False;self.music_started=False;self.entry_active=False;self.gpu_calls=[];self.errors=[];self.C_original_CPU_attempts=0
     self.queries=[];self.deliveries=[];self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0
     track=self.asset_disc.manifest['track'];TOC=self.device.ram()[0x2c00:0x3000];index=track['track']*8;assert TOC[index]==track['track'];origin=TOC[index+1]*4500+TOC[index+2]*75+TOC[index+3]
     def source_TOC_file_start(disc,start,end,packed):
      minute,second,frame=(packed>>16)&255,(packed>>8)&255,packed&255;assert packed>>24==0 and second<60 and frame<75
      absolute=minute*4500+second*75+frame;offset=(absolute-origin)*2352+disc.manifest['captured_CD_buffer_witness']['within_sector_phase'];count=end-start;assert start==0x1c0000 and 0<count<=0x40000 and 0<=offset<=len(disc.data)-count
      data=disc.data[offset:offset+count];disc.pending=(start,end,data);disc.requests.append(dict(destination_start=start,destination_end=end,packed_binary_MSF=packed,normalized_track_offset=offset,bytes=count,sha256=sha(data),track_origin_frames_from_source_TOC=origin,existing674byte_stream_phase_retained=True))
     self.asset_disc.start=types.MethodType(source_TOC_file_start,self.asset_disc)
     self.setup_event_owner();self.music_engine_active=True;self.engine_pump('source_DD40_mixer_resume')
     if options.hle_assets:
      import biwn_HLE_asset_owner
      if options.hle_asset_clock:
       import biwn_HLE_asset_clock
       biwn_HLE_asset_clock.install(self,options.jerry_slice_us)
      else:biwn_HLE_asset_owner.install(self)
     if options.cpu_cycle_probe:
      import biwn_cycle_cost_probe
      biwn_cycle_cost_probe.install(self)
     if options.prefix_instruction_clock and mode=='C':
      import biwn_pending_CPU_irq
      biwn_pending_CPU_irq.install(self)
     if options.startup_instruction_probe:
      import biwn_startup_instruction_probe
      biwn_startup_instruction_probe.install(self,state_trace=options.startup_state_probe,cost_trace=options.startup_cost_probe)
     if options.startup_elapsed_clock:
      import biwn_startup_elapsed_clock
      biwn_startup_elapsed_clock.install(self,options.jerry_slice_us)
     if options.startup_single_step and mode=='C':
      import biwn_startup_single_step
      biwn_startup_single_step.install(self)
     if options.frontend_video_layout:
      import biwn_host_video_layout
      biwn_host_video_layout.install(self)
     if options.startup_boundary_events:
      import biwn_startup_boundary_events
      biwn_startup_boundary_events.install(self)
     if options.OP_GPU_trace:
      import biwn_OP_GPU_trace
      biwn_OP_GPU_trace.install(self)
     if options.OP_GPU_owner:
      import biwn_OP_GPU_owner
      biwn_OP_GPU_owner.install(self)
     return {'fresh_HLE_platform':platform,'fresh_HLE_entry':self.fresh_HLE_entry,'live_prefix':self.live_prefix,'initial_capture_loaded':False,'HLE_disabled_after_DD40_for_shared_file_transport':not options.hle_assets}, {'fresh_HLE':True}
    runtime.source_entry=types.MethodType(fresh_adopt,runtime)
   else:
    runtime.source_entry=types.MethodType(adopt,runtime)
   if options.startup_clock_probe:
    clock_log=[];old_clock=runtime.clock_tick
    def observed_clock(self):
     s=self.cpu()if mode=='native'else self.C_CPU
     clock_log.append(dict(CPU=media.scheduler.cpu_dict(s),clock_before=self.device.read(0x778cc,4),last_clock_before=self.device.read(0xddee,4),handoffs=len(self.handoffs)))
     result=old_clock();clock_log[-1]['clock_after']=self.device.read(0x778cc,4)
     return result
    runtime.clock_tick=types.MethodType(observed_clock,runtime)
   try:
    startup,checks=runtime.source_startup(b'',dict(id=0,buttons=[]),mode)
   except BaseException as error:
    failure={'status':'startup_terminal_failure','error':repr(error),'errors':runtime.errors}
    if hasattr(runtime,'C_CPU')and mode=='C'and runtime.C_CPU is not None:failure['CPU']=media.scheduler.cpu_dict(runtime.C_CPU)
    elif mode=='native':failure['CPU']=media.scheduler.cpu_dict(runtime.cpu())
    (out/(mode+'-startup-failure-RAM.bin')).write_bytes(runtime.device.ram())
    if options.startup_instruction_probe:
     try:runtime.finish_startup_instruction_probe()
     except BaseException as probe_error:failure['probe_error']=repr(probe_error)
    save(out/(mode+'-startup-failure.json'),failure)
    raise

   if options.OP_GPU_trace:runtime.finish_OP_GPU_trace()
   if options.OP_GPU_owner:runtime.finish_OP_GPU_owner()
   if options.startup_boundary_events:runtime.finish_startup_boundary_events()
   if options.startup_instruction_probe:runtime.finish_startup_instruction_probe()
   if options.startup_elapsed_clock:runtime.finish_startup_elapsed_clock()
   if options.startup_single_step and mode=='C':del runtime.startup_single_step
   if options.startup_clock_probe:save(out/(mode+'-startup-clock-probe.json'),clock_log)
   save(out/(mode+'-startup.json'),dict(startup=startup,checks=checks))
   if hasattr(runtime,'pending_CPU_IRQ_events'):save(out/(mode+'-pending-CPU-IRQs.json'),runtime.pending_CPU_IRQ_events)
   if options.hle_assets:save(out/(mode+'-HLE-asset-VBIs.json'),runtime.HLE_asset_VBIs)
   if options.hle_asset_clock:save(out/(mode+'-HLE-asset-clock-events.json'),runtime.HLE_asset_clock_events)
   if options.cpu_cycle_probe:save(out/'native-startup-cycle-cost.json',runtime.cycle_cost_report())
   if options.world_instruction_probe:
    import biwn_startup_instruction_probe
    biwn_startup_instruction_probe.install(runtime,state_trace=True,cost_trace=True,label='world')
   if options.framebuffer_probe:
    ptr=c.c_void_p.in_dll(runtime.core,'videoBuffer').value;assert ptr
    pixels=c.string_at(ptr,1024*512*4);(out/(mode+'-startup-framebuffer.bin')).write_bytes(pixels)
    save(out/(mode+'-startup-framebuffer.json'),framebuffer_metadata(runtime,pixels))
   runtime.full_running=True;runtime.loading_active=False;runtime.prefix_running=False;runtime.near_supplied=True;runtime.dialogue_returned=False;runtime.renderer_active=False;runtime.pending_render=None;runtime.pending_movement=False;runtime.pending_init=False;runtime.pending_overlay=False;runtime.C_stopped=False;runtime.polls=[];runtime.global_clock_step=0
   CPU=media.CPU.from_buffer_copy(bytes(runtime.startup_final_CPU));assert CPU.pc==0x17dc2 and runtime.current()==0xc0d28
   if options.music_words:save(out/(mode+'-startup-music.json'),dict(calls=runtime.music_engine_calls,word_events=runtime.music_word_events))
   def begin_poll(self):
    poll=len(self.polls);directions={'up-left':(0,2),'down-right':(1,3)};pair=directions.get(options.input_plan);buttons=([pair[0]]if 5<=poll<65 else[pair[1]]if 65<=poll<95 else[])if pair else[]
    if options.sustained_input and pair and poll>=120:buttons=[pair[0]]
    if options.controller_script:
     buttons=sorted({i for w in controller_windows if w['start_poll']<=poll<w['stop_poll']for i in w['indices']})
    self.pad.set_buttons(buttons);self.polls.append(dict(poll=poll,buttons=buttons,clock=self.device.read(0x778cc,4),player_before=self.player_state(),no_host_clock_increment=True))
   runtime.begin_poll=types.MethodType(begin_poll,runtime)
   extra_src=ROOT/'projects/black-ice-white-noise/restoration/biwn_gpu_geometry_submit_cpu.c';extra_lib=out/'libgeometry-submit.dylib'
   if not extra_lib.exists():
    build=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(extra_src.parent),str(extra_src),'-o',str(extra_lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});assert not build.returncode,build.stderr
   extra=c.CDLL(str(extra_lib));geometry_submit=extra.biwn_gpu_geometry_submit_cpu_body;geometry_submit.argtypes=runtime.fn.argtypes;geometry_submit.restype=c.c_int;parent_service=runtime.service
   def natural_service(_,bus,cpu,target):
    try:
     if target==0xe0a6:return geometry_submit(bus,cpu,runtime.callbacks[5],runtime.service,None,1000000,1)
     if target==0xde08:return runtime.system_dispatch(bus,cpu,128)
     if target==0xe4c0:
      runtime.begin_poll();status=runtime.poll_body(bus,cpu)
      if status==0:runtime.end_poll()
      return status
     if target in runtime.render_groups:return runtime.render_CPU[runtime.render_groups[target]](bus,cpu,runtime.callbacks[5],runtime.service,None,1000000,1)
     if target in runtime.new_groups:return runtime.new_groups[target](bus,cpu,runtime.callbacks[5],runtime.service,None,1000000,1)
     if target==0xf0fa:return runtime.world_camera(bus,cpu,runtime.callbacks[5],runtime.service,None)
     if target==0x20820:return runtime.world_target(bus,cpu,runtime.service,None)
     return parent_service(_,bus,cpu,target)
    except BaseException as error:runtime.errors.append(repr(error));return 1
   runtime.service=media.world_cpu.SERVICE(natural_service)
   task_functions={};task_libs=[]
   for name in ['proximity-message','actor20','actor19','actor15','actor14','actor13','actor12','actor8','actor7','actor6','actor5','actor4']:
    proof=json.loads((ROOT/f'verification/{name}-task-current.json').read_text());mapping=json.loads((ROOT/f'verification/{name}-task-generation.json').read_text());dl=c.CDLL(str(Path(proof['directory'])/'libproximity.dylib'));task_libs.append(dl);symbol='biwn_proximity_message_task_cpu_body'if name=='proximity-message'else f'biwn_{name}_task_cpu_body';fn=getattr(dl,symbol);fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int
    for row in mapping['instructions_decoded']:task_functions[row['address']]=fn
   tile_proof=json.loads((ROOT/'verification/tile-task-candidate-current.json').read_text());tile_lib=c.CDLL(str(Path(tile_proof['directory'])/'libtile-task.dylib'));tile_fn=tile_lib.biwn_tile_task_cpu_run;tile_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];tile_fn.restype=c.c_int;tile_addresses={int(v,16)for v in re.findall(r'case\s+(0x[0-9a-fA-F]+)',Path(tile_proof['protocol']['candidate']).read_text())}
   if options.world_single_step:
    import biwn_world_single_step
    biwn_world_single_step.install(runtime)
   if options.world_boundary_events:
    import biwn_startup_boundary_events
    biwn_startup_boundary_events.install(runtime,label='world',stable=options.world_stable_clock)
    import biwn_world_GPU_IRQ_resume
    biwn_world_GPU_IRQ_resume.install(runtime)
    if mode=='C':
     import biwn_OP_GPU_owner
     biwn_OP_GPU_owner.install(runtime,compare_reference=False,label='world')
    else:
     runtime.on_native_source_instruction=lambda s:runtime.begin_poll()if s.pc==0xe4c0 else None
     import biwn_OP_GPU_trace
     biwn_OP_GPU_trace.install(runtime,label='world',capture_states=False)
   trace=array("I");visits=[hex(runtime.current())];checkpoints=[];rounds=0;left_world=True;timer_rounds=set();timer_events=0
   try:
    if mode=='native':
     for _ in range(options.world_step_budget or max(2000000,options.rounds*16000)):
      if options.world_boundary_events:runtime.startup_before_instruction(runtime.cpu())
      pc=runtime.cpu().pc;ctx=runtime.current()
      if visits[-1]!=hex(ctx):visits.append(hex(ctx))
      if ctx!=0xc2128:left_world=True
      if left_world and pc==0x1a550 and ctx==0xc2128:
       checkpoints.append(dict(world_return=rounds+1,CPU=media.scheduler.cpu_dict(runtime.cpu())if mode=='native'else media.scheduler.cpu_dict(final),RAM=sha(runtime.device.ram()),hardware=runtime.hardware(),player=runtime.player_state(),context_visits=list(visits)))
       if options.framebuffer_probe:checkpoints[-1]['framebuffer_sha256']=sha(c.string_at(c.c_void_p.in_dll(runtime.core,'videoBuffer').value,1024*512*4))
       rounds+=1;left_world=False
       if rounds==options.rounds:break
      if not options.world_boundary_events and pc==0xddec and ctx==0xc0928 and rounds not in timer_rounds:runtime.clock_tick();timer_rounds.add(rounds);timer_events+=1
      trace.append(pc)
      if pc==0xe4c0 and not options.world_boundary_events:runtime.begin_poll()
      runtime.core.m68k_execute(1)
      if (runtime.last_startup_executed_PC if options.world_boundary_events else pc)==0xe53a:runtime.end_poll()
      command=runtime.core.GPUReadLong(0xf03204,6)
      if command==0x4320:runtime.run_movement_request()
      elif command in [0x4b00,0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:runtime.run_render_request(command)
     else:raise AssertionError(('native entry task bound',hex(pc),hex(ctx)))
     final=runtime.cpu()
    else:
     final=CPU
     for _ in range(options.world_step_budget or(max(2000000,options.rounds*16000) if options.world_single_step else max(200000,options.rounds*1600))):
      runtime.C_CPU=final
      if options.world_boundary_events:
       runtime.startup_before_instruction(final)
      pc=final.pc;ctx=runtime.current();runtime.C_CPU=final
      if visits[-1]!=hex(ctx):visits.append(hex(ctx))
      if ctx!=0xc2128:left_world=True
      if left_world and pc==0x1a550 and ctx==0xc2128:
       checkpoints.append(dict(world_return=rounds+1,CPU=media.scheduler.cpu_dict(runtime.cpu())if mode=='native'else media.scheduler.cpu_dict(final),RAM=sha(runtime.device.ram()),hardware=runtime.hardware(),player=runtime.player_state(),context_visits=list(visits)))
       if options.framebuffer_probe:checkpoints[-1]['framebuffer_sha256']=sha(c.string_at(c.c_void_p.in_dll(runtime.core,'videoBuffer').value,1024*512*4))
       rounds+=1;left_world=False
       if rounds==options.rounds:break
      # Match the original loop: record a world return before executing
      # the next instruction, whose entry may service a pending CPU IRQ.
      if options.world_boundary_events and runtime.sample_pending_CPU_IRQ(final):continue
      if options.world_single_step:
       if not options.world_boundary_events and pc==0xddec and ctx==0xc0928 and rounds not in timer_rounds:runtime.clock_tick();timer_rounds.add(rounds);timer_events+=1
       runtime.world_single_step(final);continue
      if pc==0xdf60:assert runtime.yield_fn(c.byref(runtime.bus),c.byref(final),128)==0;continue
      if pc==0xdf66:assert runtime.resume_fn(c.byref(runtime.bus),c.byref(final))==0;continue
      if pc==0xdf7a:assert runtime.remove_fn(c.byref(runtime.bus),c.byref(final),128)==0;continue
      if pc in runtime.system_addresses:
       if pc==0xddec and rounds not in timer_rounds:runtime.clock_tick();timer_rounds.add(rounds);timer_events+=1
       status=runtime.system_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,1,0)
      elif pc in runtime.health_addresses:
       status=runtime.health_fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,1000000,1)
       if status==0:runtime.virtual_RTS(final)
      elif pc in task_functions:status=task_functions[pc](c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,1000000,1)
      elif pc in tile_addresses:status=tile_fn(c.byref(runtime.bus),c.byref(final),1000)
      elif pc in [0xf360,0xf366,0xf880,0xf886]:status=runtime.idle_body(c.byref(runtime.bus),c.byref(final),base.joined.actor.prior.BODY(),None,128)
      elif ctx in [0xc1528,0xc1928]and pc in [0xf4d8,0xf56e,0xf70c]:status=runtime.actor_body(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],c.cast(runtime.service,base.joined.actor.actor.SERVICE),None,1000000)
      elif pc in runtime.render_groups or pc in runtime.new_groups:
       fn=runtime.new_groups.get(pc)or runtime.render_CPU[runtime.render_groups[pc]];status=fn(c.byref(runtime.bus),c.byref(final),runtime.callbacks[5],runtime.service,None,1000000,1)
       if status==0:runtime.virtual_RTS(final)
      else:raise AssertionError(('entry task unknown continuation',hex(pc),hex(ctx)))
      assert status in [0,4,6,8]and not runtime.errors,('entry task dispatch',hex(pc),status,hex(final.pc),runtime.errors)
     else:raise AssertionError(('C entry task dispatch bound',hex(final.pc)))
    if mode=='C':
     for name in ['6860','65e0']:
      fn=getattr(runtime.device.lib,'lab_material'+name+'_calls');fn.restype=c.c_uint64;save(out/f'C-material{name}-calls.json',dict(calls=fn()))
    if options.world_boundary_events:
     runtime.finish_startup_boundary_events()
     if mode=='C':runtime.finish_OP_GPU_owner()
     else:runtime.finish_OP_GPU_trace()
    if options.world_boundary_events:save(out/(mode+'-world-GPU-IRQ-resumes.json'),runtime.world_GPU_IRQ_resumes)
    if options.frontend_video_layout:save(out/(mode+'-host-video-layout-changes.json'),runtime.host_video_layout_changes)
    if options.world_instruction_probe:runtime.finish_startup_instruction_probe()
    if options.framebuffer_probe:
     ptr=c.c_void_p.in_dll(runtime.core,'videoBuffer').value;assert ptr
     pixels=c.string_at(ptr,1024*512*4);(out/(mode+'-world-framebuffer.bin')).write_bytes(pixels)
     save(out/(mode+'-world-framebuffer.json'),framebuffer_metadata(runtime,pixels))
    save(out/(mode+'-world-return-checkpoints.json'),checkpoints)
    if options.music_words:save(out/(mode+'-music.json'),dict(calls=runtime.music_engine_calls,word_events=runtime.music_word_events))
    if options.jerry_events:save(out/(mode+'-JERRY-events.json'),dict(elapsed_us=runtime.jerry_elapsed,events=runtime.jerry_events,errors=runtime.jerry_owner_error))
    if options.cpu_cycle_probe:save(out/'native-cycle-cost.json',runtime.cycle_cost_report())
    if options.world_boundary_events and mode=='C':assert runtime.gpu_counter.value==runtime.counter.value==runtime.C_original_CPU_attempts==0,('world original processor escape',runtime.gpu_counter.value,runtime.counter.value,runtime.C_original_CPU_attempts)
    RAM=runtime.device.ram();(out/(mode+'-RAM.bin')).write_bytes(RAM);row=dict(CPU=media.scheduler.cpu_dict(final),RAM=sha(RAM),hardware=runtime.hardware(),GPU_calls=runtime.gpu_calls,polls=runtime.polls,context_visits=visits,timer_events=timer_events,rounds=rounds,source_clock=runtime.device.read(0x778cc,4),processor_instructions=len(trace)if mode=='native'else None,C_original_CPU_attempts=runtime.C_original_CPU_attempts);row.update(C_original_GPU_opcodes=runtime.gpu_counter.value if mode=='C'else None,C_original_DSP_opcodes=runtime.counter.value if mode=='C'else None);save(out/(mode+'.json'),row);results.append(row)
   except BaseException as error:
    save(out/(mode+'-partial-world-return-checkpoints.json'),checkpoints)
    if options.world_instruction_probe:
     try:runtime.finish_startup_instruction_probe()
     except BaseException as probe_error:save(out/(mode+'-partial-probe-error.json'),dict(error=repr(probe_error)))
    from probe_biwn_gpu_projection import gpu_state
    GPU_raw=gpu_state(runtime.core)[0];(out/(mode+'-failure-GPU.bin')).write_bytes(GPU_raw);save(out/(mode+'-failure-GPU.json'),dict(PC=hex(runtime.core.GPUGetPC()),header=hex(runtime.core.GPUReadLong(0xf03208,0)),rounds=rounds,polls=len(runtime.polls)))
    (out/(mode+'-failure-RAM.bin')).write_bytes(runtime.device.ram());save(out/(mode+'-failure.json'),dict(error=repr(error),CPU=media.scheduler.cpu_dict(runtime.cpu())if mode=='native'else media.scheduler.cpu_dict(final),context=hex(runtime.current()),errors=runtime.errors,visits=visits,polls=runtime.polls,trace_last=list(map(hex,trace[-40:]))));raise
  finally:
   if options.jerry_events and hasattr(runtime,'irq_owner'):runtime.core.BIWNSetDSPIRQOwner(runtime.IRQ_OWNER())
   runtime.oracle.close()
 if options.execution_mode is None:
  if options.live_header:
   N=json.loads((out/'native-header-tail/native.json').read_text());C=json.loads((out/'C-header-tail/C.json').read_text())
   for key in ['CPU_steps','CPU_PC_trace','final','GPU_calls','events','IRQ_events']:assert N[key]==C[key],('header tail mismatch',key)
  if options.live_4000:
   native_prefix=json.loads((out/'native-live4000-prefix.json').read_text());C_prefix=json.loads((out/'C-live4000-prefix.json').read_text())
   for key in ['CPU','RAM','BUTCH_poll_ticks','GPU_calls','music_calls','logical_GPU_sha256','logical_DSP_sha256']:assert native_prefix[key]==C_prefix[key],('liveprefixmismatch',key)
  native_start=json.loads((out/'native-startup.json').read_text())['startup'];C_start=json.loads((out/'C-startup.json').read_text())['startup']
  for key in ['CPU','RAM','hardware','contexts','disc','GPU_calls','handoffs','external_system_clock_ticks']:assert native_start[key]==C_start[key],('startup mismatch',key)
  for key in ['CPU','RAM','hardware','GPU_calls','polls','context_visits','timer_events','rounds','source_clock']:assert results[0][key]==results[1][key],('entry task mismatch',key)
  if options.jerry_events:
   assert json.loads((out/'native-JERRY-events.json').read_text())==json.loads((out/'C-JERRY-events.json').read_text()),'JERRY event timeline mismatch'
  if options.music_words:
   assert json.loads((out/'native-music.json').read_text())==json.loads((out/'C-music.json').read_text()),'native/C source music event mismatch'
  native_points=json.loads((out/'native-world-return-checkpoints.json').read_text());C_points=json.loads((out/'C-world-return-checkpoints.json').read_text());assert len(native_points)==len(C_points)==options.rounds
  for n,v in zip(native_points,C_points):assert n==v,('world return mismatch',n['world_return'])
 report=dict(status='source_DD40_startup_and_natural_task_rounds_native_C_match',directory=str(out),results=results,startup_full_states_compared=True,all_world_return_checkpoints_equal=True,input_plan=options.input_plan,CPU_runtime_library=str(lib.resolve()),CPU_runtime_library_sha256=sha(lib.read_bytes()),requested_world_returns=options.rounds,no_post_startup_CPU_reseed=True,no_controlled_stair_or_pose_entries=True,no_task_quiescence=True,declared_source_DSP_music_events=options.music_words,continuous_live_header_to_startup_tasks=options.live_header,initial4000_capture_loaded=options.live_4000 and not options.live_header,continuous_live4000_to_startup_tasks=options.live_4000,DD40_export_loaded=not options.live_4000,source_entry_report=str(options.entry_proof or ROOT/'verification/captured-source-music-entry-current.json'),source_single_SSI_chain_diagnostic=export.get('single_SSI_chain_diagnostic',False),actual_pinned_JERRY_event_queue_used=options.jerry_events,initial_JERRY_queue_normalized=options.normalize_jerry_queue,JERRY_time_slice_us=options.jerry_slice_us if options.jerry_events else None,diagnostic_event_core=str(options.event_core)if options.event_core else None,global_cycle_scheduling_verified=False,whole_game_complete=False,limits=['Source-derived DD40 export remains initial input; prior firmware/CD/SSI/GPU-stack providers.','Source startup and later task rounds share CPU/RAM/devices; explicit source GPU IRQ2 and synchronous GPU services. Video held; DSP also held unless declared music-word mode enabled. Music word/timer frequency is a host-supplied schedule, not global or physical timing.','No full normal firmware boot/physical/playability proof.']);
 if options.live_4000:
  report['status']='live_captured_header_handoff_entry_startup_and_natural_task_rounds_native_C_match'if options.live_header else'live_captured4000_entry_startup_and_natural_task_rounds_native_C_match'
  report['limits'][0]='Captured diagnostic native4000handoff remains initial input; checked original/Centry runs live into startup/tasks without aDD40exportrestore. Priorfirmware/CD/SSI/GPUstack providers andopt-inSSIchain model remain.'
 if options.live_header:report['limits'][0]='Captured diagnosticCPU361E firmware-header continuation remains initial input, with largerstagebytes alreadyloaded. The checked BIOS/GPU/event tail reaches4000live; no4000/DD40state file is loaded and no intermediateprocessor/memoryreset occurs. Priorfirmware/disc/ROM/stack/model/timing providers remain; notordinaryboot.'
 if options.fresh_hle:
  report.update(status='fresh_HLE_entry_startup_natural_tasks_native_C_match',fresh_HLE=True,initial_capture_loaded=False,initial4000_capture_loaded=False,DD40_export_loaded=False,source_single_SSI_chain_diagnostic=True)
  report['limits'][0]='Fresh libretro disc HLE boot supplies the platform/stub and BIOS API services; reconstructed game CPU/GPU entry runs directly through4000/DD40/startup/tasks. No captured machine state is loaded. Earlier snapshots are used only as static code-mapping metadata. Supplied poll quanta, file adapters/674byte phase, JERRY slices/synchronousGPU/blitter remain.'
 if options.hle_assets:
  assert options.fresh_hle
  report['experimental_HLE_asset_owner']=True
  report['limits'][0]='Fresh HLE disc boot retained through asset loading. Sector/sentinel HLE stream owns reads; sourceVBI owns RAMprogress. No captured674byte offset/file-payload memcpy. HLEticks/VBI still synchronous at taskhandoffs, not global scheduling.'
 if options.prefix_instruction_clock:
  report['experimental_prefix_CPU_cycle_clock']=True
  report['limits'].append('Entry4000->DD40 main event queue advances from observed CPU costs; GPU/DSP services synchronous and JERRY held in that prefix. Later startup/system/JERRY/asset clocks remain supplied, not global timing.')
 if options.loader_cycle_clock:
  report['experimental_loader_CPU_cycle_clock']=True
  report['limits'].append('Loader180000->4000 main events advance from CPU instruction costs rather than poll quanta. GPU services remain synchronous, JERRY held in that loader and later clocks remain supplied; not a globally scheduled game.')
 if options.hle_asset_clock:
  report['experimental_HLE_asset_clock']=True
  report['limits'][0]='Incremental HLE bytes and source VBI progress across supplied system-clock pulses; task handoffs cannot finish a read. No saved starting state/674byte phase/direct progress patch. System-clock cadence remains supplied, not globally cycle-coupled.'
 if options.startup_boundary_events:
  report['experimental_startup_boundary_events']=True
  report['limits'].append('Startup main and JERRY queues advance at individual CPU boundaries; actual main halfline HLE delivery and source CPU IRQ frames replace periodic safe-point pulses. GPU/DSP services still synchronous; global/cross-processor timing and later world timing remain unverified.')
 if options.execution_mode:
  assert options.fresh_hle and options.no_publish
  report.update(status='completed_unpaired_fresh_HLE_side',execution_mode=options.execution_mode,startup_full_states_compared=False,all_world_return_checkpoints_equal=False)
 save(out/'report.json',report);
 if not options.no_publish:save(ROOT/'verification/entry-natural-task-rounds-current.json',report)
 print(report['status'],flush=True)
except BaseException as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
finally:media.scheduler.Native=original_Native;media.scheduler.movement.Device.__init__=original_device_init
