"""Capture original world task entry without supplied poses/task quiescence."""
import ctypes as c,json
from pathlib import Path
from datetime import datetime,timezone
import observe_biwn_relocated_firmware as host
import biwn_firmware_checkpoint as checkpoint
ROOT=host.ROOT;save=host.save;sha=host.sha
source=json.loads((ROOT/'verification/source-stage-handoff-current.json').read_text());input_path=Path(source['captured']['directory'])/'checkpoint.json';out=ROOT/'verification/BIWN-natural-world-entry'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);captured={};errors=[];controls=[];frame=[0]
for mode in ['observer_off','observer_on']:
 runtime,record,loaded=checkpoint.restore_current(host,input_path);core=runtime.core
 try:
  if mode=='observer_on':
   CALLBACK=c.CFUNCTYPE(None,c.c_uint32,c.c_uint32)
   def observe(previous,pc):
    try:
     assert pc==0x1a544 and not captured;CPU=host.media.scheduler.cpu_dict(runtime.cpu());size=record['libretro_state_bytes'];buffer=c.create_string_buffer(size);assert core.retro_serialize(buffer,size);ROM=c.string_at(runtime.rom,0x102000);RAM=runtime.device.ram();folder=out/'preinstruction-world';folder.mkdir();(folder/'libretro-state.bin').write_bytes(buffer.raw);(folder/'ROM-provider.bin').write_bytes(ROM);(folder/'RAM.bin').write_bytes(RAM)
     result={**record,'directory':str(folder),'CPU':CPU,'libretro_state_sha256':sha(buffer.raw),'ROM_provider_sha256':sha(ROM),'RAM_sha256':sha(RAM),'hardware':runtime.snapshot()['hardware'],'status':'natural_world_preinstruction_snapshot_pending','captured_inside_native_instruction_hook':True,'previous_source_CPU_PC':hex(previous),'target_source_CPU_PC':hex(pc),'native_frame':frame[0],'source_current_task':hex(int.from_bytes(RAM[0xc0920:0xc0924],'big')),'world_poses_or_task_quiescence_supplied':False,'scope':'Source world entry during full native scheduler from source4000 snapshot. No poses/task-quiescence/CPU reseed or asset/movie ABI/phase providers added. Earlier firmware/ROM/CD/SSI/GPU-stack diagnostics still captured inputs.'};save(folder/'checkpoint.json',result);captured.update(result)
    except BaseException as e:errors.append(repr(e))
   callback=CALLBACK(observe);core.BIWNArmCPUObserver.argtypes=[c.c_uint32,CALLBACK];core.BIWNArmCPUObserver(0x1a544,callback)
  for number in range(1,241):frame[0]=number;core.retro_run()
  CPU=host.media.scheduler.cpu_dict(runtime.cpu());size=record['libretro_state_bytes'];buffer=c.create_string_buffer(size);assert core.retro_serialize(buffer,size);row=dict(mode=mode,CPU=CPU,serialized_sha256=sha(buffer.raw),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware']);controls.append(row);save(out/(mode+'.json'),row)
 finally:runtime.oracle.close()
assert not errors and captured,errors;assert controls[0]['serialized_sha256']==controls[1]['serialized_sha256'] and controls[0]['hardware']==controls[1]['hardware'];runtime,record,loaded=checkpoint.restore_current(host,Path(captured['directory'])/'checkpoint.json')
try:assert runtime.cpu().pc==0x1a544;record.update(status='natural_world_preinstruction_cross_process_checked',observer_on_off_full_state_inertness_checked=True,cross_process_full_serialized_state_checked=True);save(Path(record['directory'])/'checkpoint.json',record)
finally:runtime.oracle.close()
report=dict(status='natural_world_entry_original_task_snapshot_checked',directory=str(out),captured=record,controls=controls,world_poses_or_task_quiescence_supplied=False,ordinary_fresh_boot=False,whole_game_complete=False);save(out/'report.json',report);save(ROOT/'verification/natural-world-entry-current.json',report);print(json.dumps(dict(status=report['status'],frame=record['native_frame'],context=record['source_current_task'],PC='0x1a544')),flush=True)
