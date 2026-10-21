"""Declared captured-state continuation of original firmware header processing."""
import ctypes as c,json,hashlib,sys,os
from collections import Counter
from pathlib import Path
from datetime import datetime,timezone
from argparse import Namespace,ArgumentParser
import observe_biwn_relocated_firmware as host
import observe_biwn_CD_challenge_phases as phases
ROOT=host.ROOT;save=host.save;sha=host.sha

def main():
 parser=ArgumentParser();parser.add_argument('--processor',choices=['DSP','CPU','GPU','FRAME'],default='DSP');parser.add_argument('--frames',type=int,default=60);parser.add_argument('--continue-after-stage-match',action='store_true');parser.add_argument('--GPU-budget',type=int,default=2000000);parser.add_argument('--checkpoint',type=Path);parser.add_argument('--GPU-stack-diagnostic',type=lambda x:int(x,0));options=parser.parse_args();assert 0<options.GPU_budget<=20000000
 checkpoint=json.loads((options.checkpoint or ROOT/'verification/BIWN-firmware-resume-current.json').read_text());assert checkpoint['status']=='live_full_state_saved_roundtrip_CPU_RAM_and_checked_hardware_match'
 folder=Path(checkpoint['directory']);blob=(folder/'libretro-state.bin').read_bytes();ROM=(folder/'ROM-provider.bin').read_bytes()
 assert sha(blob)==checkpoint['libretro_state_sha256']and sha(ROM)==checkpoint['ROM_provider_sha256'];core_path=Path(checkpoint['execution_core_path']);assert sha(core_path.read_bytes())==checkpoint['execution_core_sha256']
 assert sha(ROM[:262144])==checkpoint['BIOS_sha256'];assert sha(Path(checkpoint['disc_image']).read_bytes())=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
 proof=Path(json.loads((ROOT/'verification/firmware-relocation-CPU-checks.json').read_text())['directory']);mapping=json.loads((proof/'protocol.json').read_text())['source_mapping']
 out=ROOT/'verification/BIWN-firmware-header-resume'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 runtime=host.relocation.Runtime(proof/'libfirmware-relocation.dylib',mapping['instructions_decoded'],diagnostic_core=core_path);core=runtime.core
 protocol=dict(status='running',directory=str(out),source_checkpoint=str(folder),captured_full_core_state_input=True,ROM_provider_input=True,CDI_reattached=True,previous_right_word_provider_reinstated=True,execution_core_sha256=checkpoint['execution_core_sha256'],scope='Captured full core checkpoint/ROM/SSI provider and reattached CDI/diagnostic switches. Cross-process source continuation, not a fresh zeroRAM boot, C firmware replacement or physical/global timing proof.',normal_boot=False,whole_game_complete=False)
 parent_protocol=folder.parent/'protocol.json'
 if parent_protocol.exists():
  parent=json.loads(parent_protocol.read_text());protocol['inherited_diagnostic_inputs']=parent.get('inherited_diagnostic_inputs',[])
  if 'supplied_GPU_stack_diagnostic' in parent:protocol['inherited_diagnostic_inputs'].append(parent['supplied_GPU_stack_diagnostic'])
 save(out/'protocol.json',protocol)
 try:
  runtime.reset(bytes(0x200000),0);runtime.bios=ROM[:262144];c.memmove(runtime.rom,ROM,len(ROM))
  core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool;assert core.CDIntfOpenImage(os.fsencode(checkpoint['disc_image']));core.CDROMInit();core.CDROMReset()
  core.BIWNDiagnosticRepeatSeek.argtypes=[c.c_uint32];core.BIWNDiagnosticRepeatSeek(int(checkpoint['force_repeated_seek_diagnostic']))
  core.BIWNDiagnosticTOCOrigin.argtypes=[c.c_uint32];core.BIWNDiagnosticTOCOrigin(int(checkpoint['TOC_origin_diagnostic'])+2*int(checkpoint['TOC_read_origin_diagnostic']))
  # settings.h: isCDGame is the first bool field of exported BootConfig.
  native_CD_flag=c.c_bool.in_dll(core,'bootConfig')
  native_CD_flag.value=checkpoint.get('native_CD_scheduler_enabled',False)
  core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool;assert core.retro_unserialize(c.create_string_buffer(blob),len(blob))
  for name in checkpoint['hardware']:
   if hasattr(core,name+'StateSave'):
    fn=getattr(core,name+'StateSave');fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t;runtime.savers[name]=fn
  actual=runtime.snapshot()['hardware'];assert actual==checkpoint['hardware'];assert host.media.scheduler.cpu_dict(runtime.cpu())==checkpoint['CPU'];assert sha(runtime.device.ram())==checkpoint['RAM_sha256']
  core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool;buffer=c.create_string_buffer(len(blob));assert core.retro_serialize(buffer,len(blob));assert buffer.raw==blob
  protocol['cross_process_full_serialized_state_CPU_RAM_checked_hardware_match']=True;save(out/'protocol.json',protocol)
  if options.GPU_stack_diagnostic is not None:
   assert options.processor=='GPU' and options.GPU_stack_diagnostic in [0xf04000,0xf03fe0]
   core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
   raw=c.create_string_buffer(12000);assert runtime.savers['GPU'](raw)==4416;image=bytearray(raw.raw[:4416]);assert __import__('struct').unpack_from('=I',image,4263)[0]==0
   __import__('struct').pack_into('=I',image,4263,options.GPU_stack_diagnostic);assert core.GPUStateLoad(c.create_string_buffer(bytes(image)))==4416
   assert runtime.savers['GPU'](raw)==4416 and raw.raw[:4416]==bytes(image)
   protocol['supplied_GPU_stack_diagnostic']=dict(bank=0,R31=hex(options.GPU_stack_diagnostic),original_R31=0,source_initializer_proven=False,scope='One explicitly supplied register input for causal test. No source payload or GPU PC change; not normal boot or a production fix.')
   save(out/'protocol.json',protocol)
  core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32;core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.DSPGetPC.restype=c.c_uint32;core.DSPExec.argtypes=[c.c_int32]
  runtime.SSI_receive_swaps=0;runtime.SSI_register_samples=Counter();runtime.SSI_pair_samples=[];runtime.SSI_previous_right_word=checkpoint['external_SSI_previous_right_word'];runtime.SSI_previous_right_applications=0
  if options.processor=='DSP':assert runtime.cpu().pc==0x3a34 and core.DSPReadLong(0xf1b020,0)==2
  args=Namespace(advance_fourth_DSP_phases=4,third_DSP_budget=10000000,fourth_DSP_budget=None,CPU_continuation_budget=2000000,SSI_receive_word_swap_diagnostic=False,SSI_previous_right_word_diagnostic=True)
  clock=checkpoint['CD_clock_provider']
  if options.processor=='DSP':
   result,remainder=phases.advance_fourth(host,runtime,out,args,clock['CPU_cycles_per_BUTCH_tick'],clock['CPU_cycle_us'],checkpoint['CD_cycle_remainder'])
  elif options.processor=='FRAME':
   assert 0<options.frames<=600
   protocol['native_CD_scheduler_was_enabled']=native_CD_flag.value
   native_CD_flag.value=True
   protocol['native_CD_scheduler_enabled']=True
   protocol['native_CD_scheduler_scope']='Bind already attached CDI to core halfline CD scheduling via BootConfig.isCDGame. Strategy pointer/HLE state/ROM unchanged. This configuration is external to core savestate.'
   save(out/'protocol.json',protocol)
   core.GPUGetPC.restype=c.c_uint32;core.retro_run.argtypes=[]
   frames=[];frame_folder=out/'full-frame-continuation';frame_folder.mkdir()
   for index in range(options.frames):
    core.retro_run();image=runtime.device.ram();stage_hash=sha(image[0x4000:0x100000]);frame=dict(frame=index+1,CPU_PC=hex(runtime.cpu().pc),GPU_PC=hex(core.GPUGetPC()),RAM_stage_prefix=image[0x4000:0x4010].hex(),stage_sha256=stage_hash,stage_matches_reference=stage_hash=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453');frames.append(frame)
    if index%10==0:print(json.dumps(frame),flush=True)
    if frame['stage_matches_reference'] and not options.continue_after_stage_match:break
   (frame_folder/'RAM-after.bin').write_bytes(runtime.device.ram())
   result=dict(phases=[dict(frames=frames,directory=str(frame_folder))],stop_reason=('stage_payload_matched_reference'if frames[-1]['stage_matches_reference'] and not options.continue_after_stage_match else'full_core_frame_budget'),scope='Native retro_run full core scheduler from captured state with inherited diagnostic inputs; source CPU/GPU/DSP/devices run together. No host frame counter or CPU/GPU PC write. No physical hardware proof.')
   remainder=checkpoint['CD_cycle_remainder']
   protocol['clock_regime_changed_to_full_core_frames']=True
  elif options.processor=='GPU':
   import observe_biwn_source_stage_GPU as stage
   args.GPU_budget=options.GPU_budget
   gpu,remainder=stage.run(host,runtime,out,args,clock,checkpoint['CD_cycle_remainder'])
   result=dict(phases=[dict(GPU=gpu,directory=str(out))],stop_reason=gpu['stop_reason'])
  else:
   cpu_folder=out/'CPU-continuation';cpu_folder.mkdir()
   cpu,remainder=phases.CPU_phase(host,runtime,cpu_folder,args,clock['CPU_cycles_per_BUTCH_tick'],checkpoint['CD_cycle_remainder'],allow_CD_seek_wait=True)
   result=dict(phases=[dict(CPU=cpu,directory=str(cpu_folder))],stop_reason=cpu['stop_reason'])
  protocol.update(status='terminal_original_source_header_continuation',result=result,CD_cycle_remainder=remainder,final_CPU=host.media.scheduler.cpu_dict(runtime.cpu()),final_RAM_sha256=sha(runtime.device.ram()));save(out/'report.json',protocol)
  # Save new resume point and preserve all declared external providers.
  import biwn_firmware_checkpoint as state
  provider=dict(source_BIOS_sha256=checkpoint['BIOS_sha256'],execution_core_path=str(core_path),execution_core_sha256=checkpoint['execution_core_sha256'],disc_image=checkpoint['disc_image'],CD_clock_provider=clock,force_repeated_seek_diagnostic=checkpoint['force_repeated_seek_diagnostic'],TOC_origin_diagnostic=checkpoint['TOC_origin_diagnostic'],TOC_read_origin_diagnostic=checkpoint['TOC_read_origin_diagnostic'])
  provider['additional_diagnostic_inputs']=protocol.get('inherited_diagnostic_inputs',[])+([protocol['supplied_GPU_stack_diagnostic']]if 'supplied_GPU_stack_diagnostic' in protocol else [])
  protocol['next_checkpoint']=state.save_current(host,runtime,out,provider,remainder);save(out/'report.json',protocol);save(ROOT/'verification/BIWN-firmware-header-resume-current.json',protocol)
  print(json.dumps(dict(status=protocol['status'],final_CPU=hex(runtime.cpu().pc),phases=len(result['phases']),stop=result['stop_reason'])),flush=True)
 except BaseException as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
 finally:runtime.oracle.close()
if __name__=='__main__':main()
