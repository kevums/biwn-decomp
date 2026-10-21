"""Compare existing C entry prefix with original CPU from native handoff snapshot.

No reset/reseed after restore, payload substitution, or firmware ABI adapter.
Stops at selected helper/BIOS service before executing it; poll clocks explicit.
"""
import types,argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import observe_biwn_relocated_firmware as host
import biwn_firmware_checkpoint as checkpoint
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
ROOT=host.ROOT;save=host.save;sha=host.sha;media=host.media
parser=argparse.ArgumentParser();parser.add_argument('--stop-at',choices=['DD40'],default='DD40');parser.add_argument('--core',type=Path);parser.add_argument('--single-SSI-chain',action='store_true');parser.add_argument('--no-publish',action='store_true');opt=parser.parse_args();assert not opt.single_SSI_chain or (opt.core and opt.no_publish);target_stop=int(opt.stop_at,16)
out=ROOT/'verification/BIWN-captured-source-music-entry'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
handoff=json.loads((ROOT/'verification/source-stage-handoff-current.json').read_text());input_path=Path(handoff['captured']['directory'])/'checkpoint.json';src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_entry_setup_cpu.c','biwn_media_setup_cpu.c','biwn_bios_controller_cpu.c','biwn_bios_mode_cpu.c','biwn_bios_toc_cpu.c','biwn_video_cpu.c','biwn_movie_relocation_GPU.c','biwn_GPU_boot_cpu.c','biwn_bios_setup_cpu.c','biwn_dsp_music_bootstrap.c','biwn_gpu_main_boot.c','biwn_gpu_dispatcher.c'];library=out/'libentry-prefix.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n)for n in names],'-o',str(library)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
results=[];RAMs=[]
try:
 for mode in ['native','C']:
  runtime,loaded,checks=checkpoint.restore_current(host,input_path,core_override=opt.core);core=runtime.core;
  if opt.single_SSI_chain:
   core.BIWNSetSSISingleChain.argtypes=[c.c_uint32];core.BIWNSetSSISingleChain(1)
  ticks=[0];core.BUTCHExec.argtypes=[c.c_uint32];initial=runtime.cpu();assert initial.pc==0x4000;trace=[];errors=[]
  runtime.mode=mode;runtime.gpu_counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');runtime.gpu_calls=[];runtime.gpu_trace=__import__('hashlib').sha256();runtime.gpu_blocks=0;runtime.gpu=state_from_raw(gpu_state(core)[0])if mode=='C'else None;pending=[False];runtime.counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count');runtime.music_calls=[];runtime.music_trace=[];runtime.music_started=False
  def raw_DSP():
   buffer=c.create_string_buffer(12000);size=core.DSPStateSave(buffer);return buffer.raw[:size]
  runtime.raw_DSP=raw_DSP;runtime.C_DSP=dsp.state_from_raw(raw_DSP())if mode=='C'else None;runtime.music_segment=types.MethodType(EntryBootMixin.music_segment,runtime)
  core.DSPExec.argtypes=[c.c_int32];core.DSPGetPC.restype=c.c_uint32;core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32;core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.DSPWriteWord.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
  core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16;core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8
  runtime.run_dispatch=types.MethodType(GPUoverlay.Runtime.run_dispatch,runtime);runtime.run_boot_exit=types.MethodType(GPUboot.Runtime.run_boot_exit,runtime);runtime.native_GPU=types.MethodType(video.Runtime.native_GPU,runtime);runtime.run_C_GPU=types.MethodType(video.Runtime.run_C_GPU,runtime)
  try:
   if mode=='native':
    for _ in range(100000):
     pc=runtime.cpu().pc
     if pc==target_stop:break
     trace.append(pc)
     if pc in {0x3544,0x3910,0x392e,0x37e0}:core.BUTCHExec(0);ticks[0]+=1
     if pc==0xd384 and core.GPUGetPC()!=0xf032c8:runtime.native_GPU(True)
     if pc==0xe038:runtime.run_boot_exit('main_boot');runtime.run_dispatch(True)
     if pc==0xe9a8:runtime.music_segment(0xf1b144)
     if pc==0xea08 and core.DSPGetPC()!=0xf1b148:runtime.music_segment(0xf1b148)
     core.m68k_execute(1)
    else:raise AssertionError(('native prefix limit',hex(pc)))
    final=runtime.cpu();status=0
   else:
    helper=c.CDLL(str(library));fn=helper.biwn_entry_setup_cpu_call;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;helper.biwn_entry_setup_cpu_body.argtypes=fn.argtypes;helper.biwn_entry_setup_cpu_body.restype=c.c_int;helper.biwn_bios_controller_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_controller_cpu_body.restype=c.c_int;helper.biwn_bios_mode_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_mode_cpu_body.restype=c.c_int;helper.biwn_bios_toc_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_toc_cpu_body.restype=c.c_int;helper.biwn_video_cpu_body.argtypes=fn.argtypes;helper.biwn_video_cpu_body.restype=c.c_int;helper.biwn_GPU_boot_cpu_body.argtypes=fn.argtypes;helper.biwn_GPU_boot_cpu_body.restype=c.c_int;helper.biwn_bios_setup_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_setup_cpu_body.restype=c.c_int;captured=[]
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
   RAM=runtime.device.ram();RAMs.append(RAM);(out/(mode+'-RAM.bin')).write_bytes(RAM);hardware=runtime.snapshot()['hardware'];GPU_bytes=logical(runtime.gpu)if mode=='C'else gpu_state(core)[0][:4396];(out/(mode+'-logical-GPU.bin')).write_bytes(GPU_bytes);hardware['GPU']=dict(size=4396,sha256=sha(GPU_bytes));DSP_bytes=dsp.logical(runtime.C_DSP)if mode=='C'else raw_DSP()[:8496];(out/(mode+'-logical-DSP.bin')).write_bytes(DSP_bytes);hardware['DSP']=dict(size=8496,sha256=sha(DSP_bytes));row=dict(mode=mode,CPU=media.scheduler.cpu_dict(final),RAM_sha256=sha(RAM),hardware=hardware,GPU_calls=runtime.gpu_calls,music_calls=runtime.music_calls,restore=checks,native_PC_trace=list(map(hex,trace)),C_status=status,BUTCH_poll_ticks=ticks[0]);results.append(row);save(out/(mode+'.json'),row)
   core_state=c.create_string_buffer(loaded['libretro_state_bytes']);assert core.retro_serialize(core_state,len(core_state));(out/(mode+'-shared-libretro-state.bin')).write_bytes(core_state.raw);ROM=c.string_at(runtime.rom,0x102000);(out/(mode+'-ROM-provider.bin')).write_bytes(ROM)
   export=dict(mode=mode,status='captured4000_continuation_DD40_processor_context_and_shared_devices_exported',source_checkpoint=str(input_path),core_path=checks['execution_core_path'],core_sha256=checks['execution_core_sha256'],CPU=row['CPU'],RAM_file=str(out/(mode+'-RAM.bin')),GPU_logical_file=str(out/(mode+'-logical-GPU.bin')),DSP_logical_file=str(out/(mode+'-logical-DSP.bin')),shared_core_file=str(out/(mode+'-shared-libretro-state.bin')),shared_core_sha256=sha(core_state.raw),ROM_provider_file=str(out/(mode+'-ROM-provider.bin')),ROM_provider_sha256=sha(ROM),hardware=row['hardware'],native_CD_scheduler_enabled=loaded['native_CD_scheduler_enabled'],force_repeated_seek_diagnostic=loaded['force_repeated_seek_diagnostic'],TOC_origin_diagnostic=loaded['TOC_origin_diagnostic'],TOC_read_origin_diagnostic=loaded['TOC_read_origin_diagnostic'],disc_image=loaded['disc_image'],external_SSI_previous_right_word=loaded['external_SSI_previous_right_word'],C_owned_processor_state_required=mode=='C',shared_core_CPU_GPU_DSP_shadows_authoritative=mode=='native',scope='C shared core image contains stale original processor shadows; consume explicitly exported C-owned CPU/GPU/DSP with shared devices. Not a normal native/full-frame C checkpoint. Native image may resume originals; globaltiming remains unverified.')
   if opt.core:
    core.EventStateSave.argtypes=[c.c_void_p];core.EventStateSave.restype=c.c_size_t;event_buffer=c.create_string_buffer(100000);event_bytes=core.EventStateSave(event_buffer);(out/(mode+'-event-queue.bin')).write_bytes(event_buffer.raw[:event_bytes])
   export['single_SSI_chain_diagnostic']=opt.single_SSI_chain
   if opt.single_SSI_chain:
    core.BIWNGetSSISourceReschedules.restype=c.c_uint32;export['source_SCLK_reschedules']=core.BIWNGetSSISourceReschedules()
   save(out/(mode+'-continuation.json'),export)
  finally:runtime.oracle.close()
 assert results[0]['music_calls']==results[1]['music_calls'],'DSP trace/count/logical state mismatch'
 assert results[0]['GPU_calls']==results[1]['GPU_calls'],'GPU trace/count/logical state mismatch'
 assert results[0]['BUTCH_poll_ticks']==results[1]['BUTCH_poll_ticks'],'poll clock mismatch'
 assert results[0]['CPU']==results[1]['CPU'] and RAMs[0]==RAMs[1] and results[0]['hardware']==results[1]['hardware'],'CPU/RAM/hardware mismatch'
 report=dict(status='captured_native4000_C_GPU_DSP_entry_to_DD40_match',directory=str(out),input_checkpoint=str(input_path),source_jump_predecessor=handoff['source_jump_predecessor'],native_instructions=len(results[0]['native_PC_trace']),stop_PC=hex(target_stop),full_CPU_RAM_logical_GPU_DSP_checked_hardware_match=True,independently_supplied_game_payload=False,CPU_reseed_after_restore=False,source_sha256={n:sha((src/n).read_bytes())for n in names},compiler=cmd,results=results,whole_game_complete=False,full_C_startup_linked_from_source_firmware=False,limits=['Captured diagnostic firmware/CD/GPU-stack state remains input; no fresh ordinary boot or physical timing proof.','CPU/GPU relocation atD384 and musicDSP bootstrap/command2 acknowledgement at sourceE9A8/EA08; video held. DSP comparison uses8496logical bytes, backend233bytes excluded. MainGPU initializer and resident dispatcher run atE038 to idleF031CE. One BUTCH tick per source3544/3910/392E/37E0 poll. GPU remains at dispatcher idleF031CE before DD40 startup; GPU comparison uses4396 logical bytes, excluding backend20-byte tail. No global/physical scheduling proof.','READY8 commits finalC CPU atDD40. Original CPU/GPU/DSP execution functions reject calls on C path. Actual BIOS3000/3048/3006/305A functions used with pinned hardware; no ABI/no-op/syntheticTOC substitution.'])
 report['single_SSI_chain_diagnostic']=opt.single_SSI_chain;report['initial_queue_rebuilt_at_restore']=False
 save(out/'report.json',report)
 if not opt.no_publish:save(ROOT/'verification/captured-source-music-entry-current.json',report)
 save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(status=report['status'],instructions=report['native_instructions'],stop=report['stop_PC'])),flush=True)
except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
