"""Compare existing C entry prefix with original CPU from native handoff snapshot.

No reset/reseed after restore, payload substitution, or firmware ABI adapter.
Stops at selected helper/BIOS service before executing it; poll clocks explicit.
"""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import observe_biwn_relocated_firmware as host
import biwn_firmware_checkpoint as checkpoint
ROOT=host.ROOT;save=host.save;sha=host.sha;media=host.media
parser=argparse.ArgumentParser();parser.add_argument('--stop-at',choices=['DFF4','3048','3006','305A','D340'],default='DFF4');opt=parser.parse_args();target_stop=int(opt.stop_at,16)
out=ROOT/'verification/BIWN-captured-source-entry-prefix'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
handoff=json.loads((ROOT/'verification/source-stage-handoff-current.json').read_text());input_path=Path(handoff['captured']['directory'])/'checkpoint.json';src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_entry_setup_cpu.c','biwn_media_setup_cpu.c','biwn_bios_controller_cpu.c','biwn_bios_mode_cpu.c','biwn_bios_toc_cpu.c'];library=out/'libentry-prefix.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n)for n in names],'-o',str(library)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
results=[];RAMs=[]
try:
 for mode in ['native','C']:
  runtime,loaded,checks=checkpoint.restore_current(host,input_path);core=runtime.core;ticks=[0];core.BUTCHExec.argtypes=[c.c_uint32];initial=runtime.cpu();assert initial.pc==0x4000;trace=[];errors=[]
  try:
   if mode=='native':
    for _ in range(100000):
     pc=runtime.cpu().pc
     if pc==target_stop:break
     trace.append(pc)
     if target_stop in [0x305a,0xd340] and pc in {0x3544,0x3910,0x392e,0x37e0}:core.BUTCHExec(0);ticks[0]+=1
     core.m68k_execute(1)
    else:raise AssertionError(('native prefix limit',hex(pc)))
    final=runtime.cpu();status=0
   else:
    helper=c.CDLL(str(library));fn=helper.biwn_entry_setup_cpu_call;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;helper.biwn_entry_setup_cpu_body.argtypes=fn.argtypes;helper.biwn_entry_setup_cpu_body.restype=c.c_int;helper.biwn_bios_controller_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_controller_cpu_body.restype=c.c_int;helper.biwn_bios_mode_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_mode_cpu_body.restype=c.c_int;helper.biwn_bios_toc_cpu_body.argtypes=fn.argtypes;helper.biwn_bios_toc_cpu_body.restype=c.c_int;captured=[]
    def reader(w):
     def cb(_,a,v):
      try:
       if target_stop in [0x305a,0xd340] and a==0xdfff00 and w==4:core.BUTCHExec(0);ticks[0]+=1
       v[0]=runtime.read(a,w);return 0
      except BaseException as e:errors.append(repr(e));return 1
     return cb
    def writer(w):
     def cb(_,a,v):
      try:runtime.write(a,w,v);return 0
      except BaseException as e:errors.append(repr(e));return 1
     return cb
    world=media.scheduler.cleanup.world
    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),media.W8(writer(1))];bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
    def stop(_,passed,cpu,target):
     if target==0xdff4 and target_stop!=0xdff4:return helper.biwn_entry_setup_cpu_body(passed,cpu,callbacks[5],service,None,1000,0)
     if target==0x3048 and target_stop in [0x3006,0x305a,0xd340]:return helper.biwn_bios_controller_cpu_body(passed,cpu,callbacks[5],service,None,1000,0)
     if target_stop in [0x305a,0xd340] and target in [0x3006,0x3544]:return helper.biwn_bios_mode_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
     if target_stop==0xd340 and target in [0x305a,0x390e]:return helper.biwn_bios_toc_cpu_body(passed,cpu,callbacks[5],service,None,100000,0)
     if target!=target_stop:errors.append('unexpected service '+hex(target))
     captured.append(media.CPU.from_buffer_copy(bytes(cpu.contents)));return 1
    service=media.world_cpu.SERVICE(stop);original_CPU_before=bytes(runtime.cpu())
    status=fn(c.byref(bus),c.byref(initial),callbacks[5],service,None,1000,0);assert status==3 and len(captured)==1 and not errors,(status,errors);final=captured[0]
    # A rejected service leaves the caller object unchanged; compare captured
    # service-boundary CPU, never treat error return as a resumable C state.
    assert original_CPU_before==bytes(runtime.cpu()),'original CPU unexpectedly changed on C path'
   RAM=runtime.device.ram();RAMs.append(RAM);row=dict(mode=mode,CPU=media.scheduler.cpu_dict(final),RAM_sha256=sha(RAM),hardware=runtime.snapshot()['hardware'],restore=checks,native_PC_trace=list(map(hex,trace)),C_status=status,BUTCH_poll_ticks=ticks[0]);results.append(row);save(out/(mode+'.json'),row)
  finally:runtime.oracle.close()
 assert results[0]['BUTCH_poll_ticks']==results[1]['BUTCH_poll_ticks'],'poll clock mismatch'
 assert results[0]['CPU']==results[1]['CPU'] and RAMs[0]==RAMs[1] and results[0]['hardware']==results[1]['hardware'],'CPU/RAM/hardware mismatch'
 report=dict(status='captured_native4000_C_prefix_match',directory=str(out),input_checkpoint=str(input_path),source_jump_predecessor=handoff['source_jump_predecessor'],native_instructions=len(results[0]['native_PC_trace']),stop_PC=hex(target_stop),full_CPU_RAM_checked_hardware_match=True,independently_supplied_game_payload=False,CPU_reseed_after_restore=False,source_sha256={n:sha((src/n).read_bytes())for n in names},compiler=cmd,results=results,whole_game_complete=False,full_C_startup_linked_from_source_firmware=False,limits=['Captured diagnostic firmware/CD/GPU-stack state remains input; no fresh ordinary boot or physical timing proof.','CPU-only prefix; GPU/DSP/video held. For stops305A/D340 one BUTCH tick per source3544/3910/392E/37E0 poll traverses mode/TOC replies; earlier stops hold CD too. Tick provider is explicit, not native frame/physical time.','Stops before helper DFF4, BIOS3048, BIOS3006, BIOS305A or D340 according to stop_PC; no firmware body/ABI/provider substitution. C callback copies boundary CPU then rejects; caller error state is not resumable.'])
 save(out/'report.json',report);save(ROOT/'verification/captured-source-entry-prefix-current.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(status=report['status'],instructions=report['native_instructions'],stop=report['stop_PC'])),flush=True)
except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
