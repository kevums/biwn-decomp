"""Captured source-loaded selector13 assets consumed by readable scene/GPU C.

Separate captured-RAM continuation with the existing explicit GPU reset/resident
and MMIO progress fixtures. Never uninterrupted loading-to-rendering proof.
"""
import ctypes as c,json,hashlib,random
from pathlib import Path
from datetime import datetime,timezone
import check_seven_function_scene_GPU as scene
ROOT=scene.ROOT;sha=lambda x:hashlib.sha256(x).hexdigest()
def save(p,j):p.write_text(json.dumps(j,indent=2)+'\n')

def main():
 loading=json.loads((ROOT/'verification/scene-selector13-all-assets-experiment-current.json').read_text());assert loading['all19_mode3_assets_controlled_lifecycle_verified']
 capture=Path(loading['directory']);proof=json.loads((ROOT/'verification/seven-function-scene-GPU-current.json').read_text())
 for path,digest in proof['source_sha256'].items():assert sha(Path(path).read_bytes())==digest
 library=Path(proof['directory'])/'libseven-scene-GPU.dylib';scene.DEVICE=scene.SceneDevice(library);lib=c.CDLL(str(library))
 accesses=[]
 # Observe the C kernel boundary without replacing its memory/device behavior.
 # Native GPU bus footprints are not observed by this diagnostic.
 original_callbacks=list(scene.DEVICE.kernel_cb)
 def read16(context,address,value):
  status=original_callbacks[0](context,address,value)
  if not status:accesses.append(['r',address&0xffffff,2,value[0]])
  return status
 def read32(context,address,value):
  status=original_callbacks[1](context,address,value)
  if not status:accesses.append(['r',address&0xffffff,4,value[0]])
  return status
 def write16(context,address,value):
  status=original_callbacks[2](context,address,value)
  if not status:accesses.append(['w',address&0xffffff,2,value])
  return status
 def write32(context,address,value):
  status=original_callbacks[3](context,address,value)
  if not status:accesses.append(['w',address&0xffffff,4,value])
 observed_callbacks=[scene.connection.gpu.R16(read16),scene.connection.gpu.R32(read32),scene.connection.joined.W16(write16),scene.connection.gpu.W32(write32)]
 for field,callback in zip(['read16','read32','write16','write32'],observed_callbacks):setattr(scene.DEVICE.kernel_bus,field,callback)
 scene.SUBMIT_FN=lib.biwn_gpu4720_submit_cpu_call;scene.SUBMIT_FN.argtypes=[c.POINTER(scene.connection.media.Bus),c.POINTER(scene.connection.media.CPU),c.c_uint32];scene.SUBMIT_FN.restype=c.c_int
 fn=lib.biwn_global_scene_prepare;tick=lib.biwn_global_animation_tick;scene.PREPARE_FN=lib.biwn_scene_slot_prepare
 for f in [fn,tick,scene.PREPARE_FN]:f.argtypes=[c.POINTER(scene.animation.boundary.world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];f.restype=c.c_int
 scene.SLOT_FN=lib.biwn_slot_clear;scene.SLOT_FN.argtypes=[c.POINTER(scene.slot.Bus),c.c_uint16,c.c_uint16,c.POINTER(c.c_uint32)];scene.SLOT_FN.restype=c.c_int
 scene.FACE_FN=lib.biwn_face_coordinates;scene.FACE_FN.argtypes=[c.POINTER(scene.animation.boundary.world.Bus),c.c_uint32,c.c_uint32,c.c_uint16,c.POINTER(c.c_uint32)];scene.FACE_FN.restype=c.c_int
 scene.EXPAND_FN=lib.biwn_scene_slots_expand;scene.EXPAND_FN.argtypes=[c.POINTER(scene.animation.boundary.world.Bus),c.POINTER(scene.expand.Seed),c.POINTER(c.c_uint32)];scene.EXPAND_FN.restype=c.c_int
 scene.DEBUG_FN=lib.biwn_debug_overlay;scene.DEBUG_FN.argtypes=[c.POINTER(scene.animation.boundary.world.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];scene.DEBUG_FN.restype=c.c_int
 scene.DRAW_FN=lib.biwn_text_draw;scene.DRAW_FN.argtypes=[c.POINTER(scene.debug.text.Bus),c.POINTER(scene.debug.text.Args),c.POINTER(c.c_uint32)];scene.DRAW_FN.restype=c.c_int
 scene.debug.FORMAT_FN=lib.biwn_formatter_cpu_call;scene.debug.FORMAT_FN.argtypes=[c.POINTER(scene.animation.boundary.world.Bus),c.POINTER(scene.debug.fullcpu.CPU),scene.debug.input_cpu.W8,scene.debug.fullcpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];scene.debug.FORMAT_FN.restype=c.c_int
 scene.debug.FORMAT_BODY=lib.biwn_formatter_cpu_body;scene.debug.FORMAT_BODY.argtypes=scene.debug.FORMAT_FN.argtypes;scene.debug.FORMAT_BODY.restype=c.c_int
 out=ROOT/'verification/selector13-loaded-scene-GPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 results=[];coverage=set();rng=random.Random(0x13004720)
 samples=next(x['asset_payloads']for x in loading['results']if x['case']==0 and x['mode']=='C')
 try:
  for sample in samples:
   before=(capture/f"case-0-asset-{sample['ordinal']}-C-render-input.bin").read_bytes()
   assert sha(before)==sample['render_input_RAM_sha256'];assert before==(capture/f"case-0-asset-{sample['ordinal']}-native-render-input.bin").read_bytes()
   for debug_enabled in [0,1]:
    case=dict(initial=[[0x403cc,2,debug_enabled]],incoming=[rng.getrandbits(32)for _ in range(15)],helper_effects={str(0xe26c):[]},helper_returns={},blitter_status=[1],draw_counts=[0],read_queues=[],gpu_seed=sample['ordinal']*2+debug_enabled,cache_hit=False,delays=[0,1,2])
    save(out/'status.json',dict(status='running',asset=sample['asset'],ordinal=sample['ordinal'],debug=debug_enabled))
    a=scene.Script(before,case);b=scene.Script(before,case);value,steps=scene.original(a,case,coverage);accesses.clear();status,actual,errors,ticks=scene.translated(fn,tick,b,case)
    match=a.memory[:scene.SP-0x1000]==b.memory[:scene.SP-0x1000]and a.memory[scene.SP+4:]==b.memory[scene.SP+4:]
    if status or errors or value!=actual or a.trace!=b.trace or not match or a.mmio!=b.mmio or ticks!=[0]or a.commands!=b.commands:
     save(out/'mismatch.json',dict(sample=sample,debug=debug_enabled,status=status,expected=value,actual=actual,errors=errors,ticks=ticks,original_trace=a.trace,C_trace=b.trace,original_GPU=a.commands,C_GPU=b.commands));raise AssertionError(str(out/'mismatch.json'))
    payload_start=int(sample['pointer'],16)
    footprint=dict(external_reads=sum(x[0]=='r'for x in accesses),external_writes=sum(x[0]=='w'for x in accesses),direct_reads_of_selected_payload=sum(x[0]=='r'and payload_start<=x[1]<payload_start+106496 for x in accesses),blitter_register_writes=sum(x[0]=='w'and 0xf02200<=x[1]<0xf02300 for x in accesses),blitter_register_addresses=sorted({hex(x[1])for x in accesses if x[0]=='w'and 0xf02200<=x[1]<0xf02300}),first_external_accesses=accesses[:12],scope='C kernel callback diagnostic only; excludes internal pinned blitter reads and unobserved native GPU bus footprint. Doesnot establish visible pixels/scanout.')
    results.append(dict(asset=sample['asset'],ordinal=sample['ordinal'],descriptor=sample['descriptor'],debug=debug_enabled,source_RAM_sha256=sha(before),full_D0=value,source_instruction_steps=len(steps),GPU_commands=len(b.commands),GPU_command_proofs=b.commands,formatter_calls=b.format_calls,text_calls=b.text_calls,trace_sha256=sha(json.dumps(b.trace).encode()),trace_events=len(b.trace),C_kernel_bus_footprint=footprint))
    if not debug_enabled:
     (out/f"asset-{sample['ordinal']}-C-geometry-RAM.bin").write_bytes(b.memory)
     raw=scene.connection.joined.video.gpu_state(scene.DEVICE.core)[0]
     (out/f"asset-{sample['ordinal']}-C-geometry-GPU.bin").write_bytes(scene.connection.gpu.logical(scene.DEVICE.s)+raw[4396:])
  report=dict(status='source_loaded_selector13_RAM_scene_CPU_GPU_continuation_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),assets=sorted({r['asset']for r in results}),GPU_commands=sum(r['GPU_commands']for r in results),cases_with_GPU_commands=sum(bool(r['GPU_commands'])for r in results),formatter_calls=sum(r['formatter_calls']for r in results),results=results,original_instruction_addresses=sorted(coverage),loading_proof=str(ROOT/'verification/scene-selector13-all-assets-experiment-current.json'),loading_proof_sha256=sha((ROOT/'verification/scene-selector13-all-assets-experiment-current.json').read_bytes()),source_sha256=proof['source_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),original_GPU_on_C_path=0,original_image_modified=False,default_promoted=False,natural_gameplay_integration_verified=False,uninterrupted_loading_to_rendering_verified=False,whole_game_complete=False,new_training=False,native_Chat_verified=False,scope='Readable scene sevenfunction chain plus actual E26C/E098/GPU4720/resident dispatcher consumes captured experimental source-loaded RAM after unchanged descriptors for19mode3groups and revisits. FullD0,externalRAM,logical CPU data/helpertrace,MMIO and percommandGPUarchitecture/RAM/stages match source68000Unicorn/pinnedGPU. Initial CPU registers/private caller frame and GPU reset/resident context/read-triggered progress are declared fixtures; device state is reset at captured-RAM continuation. OriginalGPU0 on C path. Doesnot prove physicalpixels/scanout/timing,intendedmode3schema,naturalcaller or uninterrupted loading/rendering/playable/fullgame.')
  report['C_kernel_direct_payload_reads']=sum(r['C_kernel_bus_footprint']['direct_reads_of_selected_payload']for r in results)
  report['C_kernel_blitter_register_writes']=sum(r['C_kernel_bus_footprint']['blitter_register_writes']for r in results)
  report['geometry_capture_scope']='C-side logicalexternalRAM plus4396checkedGPUbytes; private sourceCPU/GPU pipeline state is supplied capture data,not separately verified. Capturecontinuation needs declared device initialization; no uninterrupted integration claim.'
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/selector13-loaded-scene-GPU-current.json',report);print(report['status'],len(results),'GPUcommands',report['GPU_commands'],'directpayloadreads',report['C_kernel_direct_payload_reads'],'blitterwrites',report['C_kernel_blitter_register_writes'],flush=True)
 except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
 finally:scene.DEVICE.close()
if __name__=='__main__':main()
