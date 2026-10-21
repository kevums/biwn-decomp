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
source=Path(json.loads((ROOT/'verification/captured-source-music-entry-current.json').read_text())['directory']);export_proof=json.loads((ROOT/'verification/captured-entry-exports-current.json').read_text());assert export_proof['source_directory']==str(source)
out=ROOT/'verification/BIWN-captured-entry-scheduled-startup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);lib=ROOT/'verification/BIWN-game-firstboot-movie-transport-music-cold-entry-timer-startup-loading-movie-world/20261015T001755.513281Z/libscheduled-startup.dylib';assert lib.exists();mappings=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup']];rows=[]
for p in session.glob('*-fullCPU-generation.json'):rows+=json.loads(p.read_text()).get('instructions_decoded',[])
ram=Path(json.loads((source/'native-continuation.json').read_text())['source_checkpoint']).parent.joinpath('RAM.bin').read_bytes();rows+=json.loads((session/'input-dispatch-fullCPU-workmap.json').read_text())['instructions']
for a,b in base.joined.actor.navigation.RANGES+base.joined.actor.rng_cpu.RANGES+[(0x4088,0x408a),(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xdf7a,0xdf7c),(0xdeb6,0xdee2),(0xe4c0,0xe53c),(0xeac4,0xec04),(0x13440,0x134dc),(0x13c9a,0x13f12),(0xe220,0xe26c),(0x13b5a,0x13c9a),(0x1028e,0x10430),(0x10652,0x106c4),(0x191f4,0x192a2),(0x192bc,0x19f2c),(0xf360,0xf368),(0xf880,0xf888),(0xf0fa,0xf35e),(0x20820,0x20a9c)]:rows+=base.fixtures.gen.loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
entry.Runtime.entry_rows=json.loads((session/'entry-setup-fullCPU-generation.json').read_text())['instructions_decoded'];disc=base.joined.Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';results=[];original_Native=media.scheduler.Native;original_device_init=media.scheduler.movement.Device.__init__
try:
 for mode in ['native','C']:
  export=json.loads((source/(mode+'-continuation.json')).read_text())
  def selected_Native(*args,**kwargs):kwargs['diagnostic_core']=Path(export['core_path']);return original_Native(*args,**kwargs)
  def selected_device_init(self,*args,**kwargs):kwargs['core']=Path(export['core_path']);return original_device_init(self,*args,**kwargs)
  media.scheduler.Native=selected_Native;media.scheduler.movement.Device.__init__=selected_device_init
  try:runtime=entry.Runtime(lib,rows,*[m['instructions_decoded']for m in mappings],disc=disc,out=out,frame_directory=frames)
  finally:media.scheduler.Native=original_Native;media.scheduler.movement.Device.__init__=original_device_init
  try:
   runtime.health_addresses={r['address']for r in json.loads((session/'health-timeout-fullCPU-generation.json').read_text())['instructions_decoded']};runtime.entry_coverage=set();runtime.timer_enabled=False
   def adopt(self,unused_ram,case,selected_mode):
    assert selected_mode==mode;self.mode=mode;core=self.core
    core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool;assert core.CDIntfOpenImage(export['disc_image'].encode());core.CDROMInit();core.CDROMReset();core.BIWNDiagnosticRepeatSeek.argtypes=[c.c_uint32];core.BIWNDiagnosticRepeatSeek(int(export['force_repeated_seek_diagnostic']));core.BIWNDiagnosticTOCOrigin.argtypes=[c.c_uint32];core.BIWNDiagnosticTOCOrigin(int(export['TOC_origin_diagnostic'])+2*int(export['TOC_read_origin_diagnostic']));c.c_bool.in_dll(core,'bootConfig').value=export['native_CD_scheduler_enabled']
    self.rom=c.c_void_p.in_dll(core,'jaguarMainROM').value;ROM=Path(export['ROM_provider_file']).read_bytes();assert sha(ROM)==export['ROM_provider_sha256'];c.memmove(self.rom,ROM,len(ROM));blob=Path(export['shared_core_file']).read_bytes();assert sha(blob)==export['shared_core_sha256'];core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool;assert core.retro_unserialize(c.create_string_buffer(blob),len(blob))
    self.gpu=GPU.state_from_raw(Path(export['GPU_logical_file']).read_bytes())if mode=='C'else None;self.C_DSP=DSP.state_from_raw(Path(export['DSP_logical_file']).read_bytes())if mode=='C'else None;self.entry_CPU=media.CPU();self.entry_CPU.registers[:]=export['CPU']['registers']
    for field in ['pc','sr','usp','ssp']:setattr(self.entry_CPU,field,export['CPU'][field])
    self.device.pointer=self.device.lib.lab_device_ram();self.trace=hashlib.sha256();self.trace_count=0;self.bus_events=[]
    save(out/(mode+'-adoption-debug.json'),dict(core_path=core._name,expected_core_path=export['core_path'],device_pointer=self.device.pointer,core_RAM_pointer=c.c_void_p.in_dll(core,'jaguarMainRAM').value,actual_RAM_sha256=sha(self.device.ram()),export_RAM_sha256=sha(Path(export['RAM_file']).read_bytes()),actual_core_RAM_sha256=sha(c.string_at(c.c_void_p.in_dll(core,'jaguarMainRAM').value,0x200000))))
    assert self.entry_CPU.pc==0xdd40 and self.device.ram()==Path(export['RAM_file']).read_bytes();self.C_CPU=self.entry_CPU if mode=='C'else None;self.C_stopped=False;self.pending_init=False;self.pending_overlay=False;self.music_started=False;self.entry_active=False;self.gpu_calls=[];self.errors=[];self.C_original_CPU_attempts=0
    self.queries=[];self.deliveries=[];self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0
    track=self.asset_disc.manifest['track'];TOC=self.device.ram()[0x2c00:0x3000];index=track['track']*8;assert TOC[index]==track['track'];origin=TOC[index+1]*4500+TOC[index+2]*75+TOC[index+3];old_origin=track['declared_start_lba']+150+track['pregap_sectors'];assert origin==old_origin-150
    def source_TOC_file_start(disc,start,end,packed):
     minute,second,frame=(packed>>16)&255,(packed>>8)&255,packed&255;assert packed>>24==0 and second<60 and frame<75
     absolute=minute*4500+second*75+frame;offset=(absolute-origin)*2352+disc.manifest['captured_CD_buffer_witness']['within_sector_phase'];count=end-start;assert start==0x1c0000 and 0<count<=0x40000 and 0<=offset<=len(disc.data)-count
     data=disc.data[offset:offset+count];disc.pending=(start,end,data);disc.requests.append(dict(destination_start=start,destination_end=end,packed_binary_MSF=packed,normalized_track_offset=offset,bytes=count,sha256=sha(data),track_origin_frames_from_source_TOC=origin,old_provider_track_origin_frames=old_origin,origin_delta_frames=origin-old_origin,existing674byte_stream_phase_retained=True))
    self.asset_disc.start=types.MethodType(source_TOC_file_start,self.asset_disc);save(out/(mode+'-source-TOC-file-origin.json'),dict(source_TOC_track_record=TOC[index:index+8].hex(),origin_frames=origin,old_origin_frames=old_origin,delta_frames=origin-old_origin,phase_bytes=674,physical_timing_verified=False))
    return dict(source_state_export=str(source/(mode+'-continuation.json')),no_baseline_reset=True,no_CPU_reseed=True,no_extracted_payload=True),dict(export_roundtrip_proof=export_proof['directory'])
   runtime.source_entry=types.MethodType(adopt,runtime);save(out/'status.json',dict(status='running',mode=mode));
   try:snapshot,checks=runtime.source_startup(b'',dict(id=0,buttons=[]),mode)
   except BaseException as error:
    RAM=runtime.device.ram();(out/(mode+'-failure-RAM.bin')).write_bytes(RAM);save(out/(mode+'-failure.json'),dict(error=repr(error),CPU=media.scheduler.cpu_dict(runtime.cpu())if mode=='native'else media.scheduler.cpu_dict(runtime.C_CPU),hardware=runtime.hardware(),clock_ticks=runtime.clock_ticks,handoffs=runtime.handoffs,disc_requests=runtime.asset_disc.requests,disc_completions=runtime.asset_disc.completions,disc_pending=runtime.asset_disc.pending,source_state_export=str(source/(mode+'-continuation.json')),actual_RAM_sha256=sha(RAM)));raise
   save(out/(mode+'.json'),dict(snapshot=snapshot,checks=checks));results.append(snapshot)
  finally:runtime.oracle.close()
 for key in ['disc','GPU_calls','handoffs','contexts','begin_hardware','external_system_clock_ticks']:assert results[0][key]==results[1][key],('startup event/state mismatch',key)
 assert results[0]['CPU']==results[1]['CPU'] and results[0]['RAM']==results[1]['RAM'] and results[0]['hardware']==results[1]['hardware'],'startup CPU/RAM/hardware mismatch'
 report=dict(status='source_derived_DD40_context_resource_startup_native_C_match',directory=str(out),source_directory=str(source),results=results,no_baseline_reset_after_export=True,no_extracted_stage_or_stub_supplied=True,no_CPU_reseed_after_export=True,whole_game_complete=False,full_movie_world_linked=False,limits=['Explicit sourceDD40 CPU/GPU/DSP context and shared device export. Original firmware diagnostic inputs persist.','Existing externally supplied system clock ticks, buttons, BIOS303C/3042 ABI,674byte stream phase/completion after source handoff, synchronous GPU/blitter and processor alternation remain. File track origin now derives from actual BIOS305A TOC (13227frames),150frames earlier than old provider; no TOC RAM rewrite. No globalclock/normalboot/movie/world/playability proof.']);save(out/'report.json',report);save(ROOT/'verification/captured-entry-scheduled-startup-current.json',report);save(out/'status.json',dict(status='terminal_pass'));print(report['status'],flush=True)
except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
finally:media.scheduler.Native=original_Native;media.scheduler.movement.Device.__init__=original_device_init
