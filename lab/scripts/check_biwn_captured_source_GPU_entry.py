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
from check_biwn_movie_GPU import state_from_raw,logical
from probe_biwn_gpu_projection import gpu_state
ROOT=host.ROOT;save=host.save;sha=host.sha;media=host.media
parser=argparse.ArgumentParser();parser.add_argument('--stop-at',choices=['E6A0','E00A','3000','1557A','E942'],default='E942');opt=parser.parse_args();target_stop=int(opt.stop_at,16)
out=ROOT/'verification/BIWN-captured-source-GPU-entry'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
handoff=json.loads((ROOT/'verification/source-stage-handoff-current.json').read_text());input_path=Path(handoff['captured']['directory'])/'checkpoint.json';src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_entry_setup_cpu.c','biwn_media_setup_cpu.c','biwn_bios_controller_cpu.c','biwn_bios_mode_cpu.c','biwn_bios_toc_cpu.c','biwn_video_cpu.c','biwn_movie_relocation_GPU.c','biwn_GPU_boot_cpu.c','biwn_bios_setup_cpu.c'];library=out/'libentry-prefix.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n)for n in names],'-o',str(library)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
results=[];RAMs=[]
try:
 for mode in ['native','C']:
  runtime,loaded,checks=checkpoint.restore_current(host,input_path);core=runtime.core;ticks=[0];core.BUTCHExec.argtypes=[c.c_uint32];initial=runtime.cpu();assert initial.pc==0x4000;trace=[];errors=[]
  runtime.mode=mode;runtime.gpu_counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');runtime.gpu_calls=[];runtime.gpu_trace=__import__('hashlib').sha256();runtime.gpu_blocks=0;runtime.gpu=state_from_raw(gpu_state(core)[0])if mode=='C'else None;pending=[False]
  core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16;core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];core.JaguarReadByte.restype=c.c_uint8
  runtime.native_GPU=types.MethodType(video.Runtime.native_GPU,runtime);runtime.run_C_GPU=types.MethodType(video.Runtime.run_C_GPU,runtime)
  try:
   if mode=='native':
    for _ in range(100000):
     pc=runtime.cpu().pc
     if pc==target_stop:break
     trace.append(pc)
     if pc in {0x3544,0x3910,0x392e,0x37e0}:core.BUTCHExec(0);ticks[0]+=1
     if pc==0xd384 and core.GPUGetPC()!=0xf032c8:runtime.native_GPU(True)
     core.m68k_execute(1)
    else:raise AssertionError(('native prefix limit',hex(pc)))
    final=runtime.cpu();status=0
   else:
    helper=c.CDLL(str(library));fn=helper.biwn_entry_setup_cpu_call;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;helper.biwn_entry_setup_cpu_body.argtypes=fn.argtypes;helper.biwn_entry_setup_cpu_body.restype=c.c_int;helper.biwn_bios_controller_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_controller_cpu_body.restype=c.c_int;helper.biwn_bios_mode_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_mode_cpu_body.restype=c.c_int;helper.biwn_bios_toc_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_toc_cpu_body.restype=c.c_int;helper.biwn_video_cpu_body.argtypes=fn.argtypes;helper.biwn_video_cpu_body.restype=c.c_int;helper.biwn_GPU_boot_cpu_body.argtypes=fn.argtypes;helper.biwn_GPU_boot_cpu_body.restype=c.c_int;helper.biwn_bios_setup_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_setup_cpu_body.restype=c.c_int;captured=[]
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
       if 0xf03000<=a<=0xf04000-w:runtime.gpu.local_RAM[a-0xf03000:a-0xf03000+w]=v.to_bytes(w,'big')
       if w==4:
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
     if target==0xe00a and target_stop in [0x3000,0x1557a,0xe942]:return helper.biwn_GPU_boot_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
     if target==0x3000 and target_stop in [0x1557a,0xe942]:return helper.biwn_bios_setup_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
     if target in [0x1557a,0x17340] and target_stop==0xe942:return helper.biwn_entry_setup_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
     if target!=target_stop:errors.append('unexpected service '+hex(target))
     captured.append(media.CPU.from_buffer_copy(bytes(cpu.contents)));return 1
    service=media.world_cpu.SERVICE(stop);original_CPU_before=bytes(runtime.cpu())
    def forbidden(*args):raise AssertionError('Original processor execution forbidden on C path')
    core.m68k_execute=forbidden;core.GPUExec=forbidden;core.DSPExec=forbidden
    status=fn(c.byref(bus),c.byref(initial),callbacks[5],service,None,1000,0);assert status==3 and len(captured)==1 and not errors,(status,errors);final=captured[0]
    # A rejected service leaves the caller object unchanged; compare captured
    # service-boundary CPU, never treat error return as a resumable C state.
    assert original_CPU_before==bytes(runtime.cpu()),'original CPU unexpectedly changed on C path'
   RAM=runtime.device.ram();RAMs.append(RAM);(out/(mode+'-RAM.bin')).write_bytes(RAM);hardware=runtime.snapshot()['hardware'];GPU_bytes=logical(runtime.gpu)if mode=='C'else gpu_state(core)[0][:4396];(out/(mode+'-logical-GPU.bin')).write_bytes(GPU_bytes);hardware['GPU']=dict(size=4396,sha256=sha(GPU_bytes));row=dict(mode=mode,CPU=media.scheduler.cpu_dict(final),RAM_sha256=sha(RAM),hardware=hardware,GPU_calls=runtime.gpu_calls,restore=checks,native_PC_trace=list(map(hex,trace)),C_status=status,BUTCH_poll_ticks=ticks[0]);results.append(row);save(out/(mode+'.json'),row)
  finally:runtime.oracle.close()
 assert results[0]['GPU_calls']==results[1]['GPU_calls'],'GPU trace/count/logical state mismatch'
 assert results[0]['BUTCH_poll_ticks']==results[1]['BUTCH_poll_ticks'],'poll clock mismatch'
 assert results[0]['CPU']==results[1]['CPU'] and RAMs[0]==RAMs[1] and results[0]['hardware']==results[1]['hardware'],'CPU/RAM/hardware mismatch'
 report=dict(status='captured_native4000_C_GPU_relocation_prefix_match',directory=str(out),input_checkpoint=str(input_path),source_jump_predecessor=handoff['source_jump_predecessor'],native_instructions=len(results[0]['native_PC_trace']),stop_PC=hex(target_stop),full_CPU_RAM_logical_GPU_checked_hardware_match=True,independently_supplied_game_payload=False,CPU_reseed_after_restore=False,source_sha256={n:sha((src/n).read_bytes())for n in names},compiler=cmd,results=results,whole_game_complete=False,full_C_startup_linked_from_source_firmware=False,limits=['Captured diagnostic firmware/CD/GPU-stack state remains input; no fresh ordinary boot or physical timing proof.','CPU and GPU relocation run at explicit CPU D384 poll boundary; DSP/video held. One BUTCH tick per source3544/3910/392E/37E0 poll. MainGPU initializer is not yet executed after sourceE00A GO; GPU comparison uses4396 logical bytes, excluding backend20-byte tail. No global/physical scheduling proof.','Stops before helper DFF4, BIOS3048, BIOS3006, BIOS305A or E6A0/E00A/3000/1557A/E942 according to stop_PC; no firmware body/ABI/provider substitution. C callback copies boundary CPU then rejects; caller error state is not resumable.'])
 save(out/'report.json',report);save(ROOT/'verification/captured-source-GPU-entry-current.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(status=report['status'],instructions=report['native_instructions'],stop=report['stop_PC'])),flush=True)
except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
