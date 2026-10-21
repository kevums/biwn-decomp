"""One-shot preinstruction snapshot and paired observer-inertness check."""
import ctypes as c,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import observe_biwn_relocated_firmware as host
import biwn_firmware_checkpoint as state
ROOT=host.ROOT;save=host.save;sha=host.sha
checkpoint_path=ROOT/'verification/BIWN-firmware-header-resume/20261015T105258.234232Z/resume-checkpoint/checkpoint.json';build=json.loads((ROOT/'verification/BIWN-PC-observer-build-current.json').read_text());observer_core=Path(build['core_path']);out=ROOT/'verification/BIWN-source-stage-handoff'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);results=[];capture={};errors=[]
for label,core_override,enabled in [('parent_control',None,False),('observer_off',observer_core,False),('observer_on',observer_core,True)]:
 runtime,checkpoint,loaded=state.restore_current(host,checkpoint_path,core_override);core=runtime.core;folder=out/label;folder.mkdir();assert sha(runtime.device.ram()[0x4000:0x100000])=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
 callback=None
 try:
  if enabled:
   CALLBACK=c.CFUNCTYPE(None,c.c_uint32,c.c_uint32)
   def observe(previous,pc):
    try:
     assert not capture and pc==0x4000;cpu_at_entry=host.media.scheduler.cpu_dict(runtime.cpu());size=len((Path(checkpoint['directory'])/'libretro-state.bin').read_bytes());buffer=c.create_string_buffer(size);assert core.retro_serialize(buffer,size)
     target=out/'preinstruction-4000';target.mkdir();blob=buffer.raw;ROM=c.string_at(runtime.rom,0x102000);(target/'libretro-state.bin').write_bytes(blob);(target/'ROM-provider.bin').write_bytes(ROM);RAM=runtime.device.ram();(target/'RAM.bin').write_bytes(RAM)
     record={**checkpoint,'directory':str(target),'status':'preinstruction_snapshot_saved_roundtrip_pending','libretro_state_sha256':sha(blob),'ROM_provider_sha256':sha(ROM),'CPU':cpu_at_entry,'RAM_sha256':sha(RAM),'hardware':runtime.snapshot()['hardware'],'execution_core_path':str(observer_core),'execution_core_sha256':loaded['execution_core_sha256'],'captured_inside_native_instruction_hook':True,'previous_source_CPU_PC':hex(previous),'target_source_CPU_PC':hex(pc),'scope':'Preinstruction CPU4000 snapshot during native frame execution; snapshot observer does not halt/reseed processors. Captured state/ROM/CD configuration and prior diagnostic stack remain inputs. Cross-process replay and observer inertness must be checked separately.'}
     assert record['CPU']['pc']==0x4000 and sha(RAM[0x4000:0x100000])=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';save(target/'checkpoint.json',record);capture.update(record)
    except BaseException as error:errors.append(repr(error))
   callback=CALLBACK(observe);core.BIWNArmCPUObserver.argtypes=[c.c_uint32,CALLBACK];core.BIWNArmCPUObserver(0x4000,callback)
  core.retro_run();size=checkpoint['libretro_state_bytes'];buffer=c.create_string_buffer(size);assert core.retro_serialize(buffer,size);(folder/'state-after-frame.bin').write_bytes(buffer.raw);RAM=runtime.device.ram();(folder/'RAM-after-frame.bin').write_bytes(RAM);row=dict(label=label,loaded=loaded,CPU=host.media.scheduler.cpu_dict(runtime.cpu()),serialized_sha256=sha(buffer.raw),RAM_sha256=sha(RAM),hardware=runtime.snapshot()['hardware']);results.append(row);save(folder/'report.json',row)
 finally:runtime.oracle.close()
assert not errors,errors;assert capture
assert results[0]['serialized_sha256']==results[1]['serialized_sha256']==results[2]['serialized_sha256'];assert results[0]['hardware']==results[1]['hardware']==results[2]['hardware']
# Restore the captured instruction boundary in a new process-equivalent runtime.
runtime,captured,loaded=state.restore_current(host,out/'preinstruction-4000/checkpoint.json',observer_core)
try:
 assert runtime.cpu().pc==0x4000;captured.update(status='preinstruction_snapshot_cross_process_checked',full_serialized_bytes_restored_exactly=True,observer_on_off_parent_frame_inertness_verified=True);save(out/'preinstruction-4000/checkpoint.json',captured)
finally:runtime.oracle.close()
report=dict(status='source_stage_handoff_4000_observed_snapshot_checked',directory=str(out),captured=captured,frame_controls=results,source_jump_predecessor=capture['previous_source_CPU_PC'],target='0x4000',observer_does_not_set_PC=True,all_stage_bytes_match_at_entry=True,observer_inertness_full_serialized_frame_match=True,normal_boot=False,whole_game_complete=False);save(out/'report.json',report);save(ROOT/'verification/source-stage-handoff-current.json',report);print(json.dumps(dict(status=report['status'],previous=capture['previous_source_CPU_PC'],PC='0x4000',frame_inertness=True)),flush=True)
