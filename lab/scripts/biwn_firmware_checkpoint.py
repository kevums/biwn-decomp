"""Full libretro state plus explicit external providers, for declared resumes."""
import ctypes as c,json,hashlib
from pathlib import Path
from collections import Counter
sha=lambda b:hashlib.sha256(b).hexdigest()
def save_current(host,runtime,out,protocol,CD_remainder):
 folder=out/'resume-checkpoint';folder.mkdir()
 core=runtime.core;core.retro_serialize_size.restype=c.c_size_t;core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool;core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool
 for name in ['CDROM','M68K','Joystick','UART','MT','NVMBios']:
  if hasattr(core,name+'StateSave'):
   fn=getattr(core,name+'StateSave');fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t;runtime.savers[name]=fn
 size=core.retro_serialize_size();assert 0<size<100000000;buffer=c.create_string_buffer(size)
 before_CPU=bytes(runtime.cpu());before_RAM=runtime.device.ram();before=runtime.snapshot()['hardware'];assert core.retro_serialize(buffer,size)
 blob=buffer.raw;(folder/'libretro-state.bin').write_bytes(blob)
 ROM=c.string_at(runtime.rom,0x102000);(folder/'ROM-provider.bin').write_bytes(ROM)
 assert sha(ROM[:262144])==protocol['source_BIOS_sha256']
 record=dict(status='live_full_state_saved_roundtrip_CPU_RAM_and_checked_hardware_match',directory=str(folder),libretro_state_bytes=size,libretro_state_sha256=sha(blob),ROM_provider_sha256=sha(ROM),CPU=host.media.scheduler.cpu_dict(runtime.cpu()),RAM_sha256=sha(before_RAM),hardware=before,execution_core_path=protocol['execution_core_path'],execution_core_sha256=protocol['execution_core_sha256'],BIOS_sha256=protocol['source_BIOS_sha256'],disc_image=protocol['disc_image'],CD_clock_provider=protocol['CD_clock_provider'],CD_cycle_remainder=CD_remainder,force_repeated_seek_diagnostic=protocol['force_repeated_seek_diagnostic'],TOC_origin_diagnostic=protocol['TOC_origin_diagnostic'],TOC_read_origin_diagnostic=protocol['TOC_read_origin_diagnostic'],external_SSI_previous_right_word=runtime.SSI_previous_right_word,scope='Full core serialization with verified in-place roundtrip. CDI interface/files and diagnostic switches are external and must be explicitly reattached; ROM and previous-right SSI provider also external. Cross-process resume remains unverified until checked against saved CPU/RAM/hardware. This is a captured-state fixture, not fresh natural boot or physical timing proof.',cross_process_resume_verified=False,normal_boot_verified=False,additional_diagnostic_inputs=protocol.get('additional_diagnostic_inputs',[]))
 record['native_CD_scheduler_enabled']=c.c_bool.in_dll(core,'bootConfig').value
 record['status']='saved_roundtrip_pending'
 host.save(folder/'checkpoint.json',record)
 try:
  assert core.retro_unserialize(c.create_string_buffer(blob),size)
  after=runtime.snapshot()['hardware'];assert bytes(runtime.cpu())==before_CPU and runtime.device.ram()==before_RAM
  assert before==after,(before,after)
  second=c.create_string_buffer(size);assert core.retro_serialize(second,size)
  record['full_serialized_bytes_identical_after_roundtrip']=(second.raw==blob)
  assert second.raw==blob,'Serialized core state changed after roundtrip'
 except BaseException as error:
  record.update(status='roundtrip_failed',error=repr(error));host.save(folder/'checkpoint.json',record);host.save(host.ROOT/'verification/BIWN-firmware-resume-current.json',record);raise
 record['status']='live_full_state_saved_roundtrip_CPU_RAM_and_checked_hardware_match'
 host.save(folder/'checkpoint.json',record);host.save(host.ROOT/'verification/BIWN-firmware-resume-current.json',record);print(json.dumps(dict(checkpoint=str(folder),CPU_PC=hex(record['CPU']['pc']),bytes=size)),flush=True);return record

def restore_current(host,checkpoint_path,core_override=None):
 """Restore declared snapshot/providers and verify exact saved machine state."""
 import check_biwn_firmware_relocation_cpu as relocation
 checkpoint=json.loads(Path(checkpoint_path).read_text());folder=Path(checkpoint['directory']);blob=(folder/'libretro-state.bin').read_bytes();ROM=(folder/'ROM-provider.bin').read_bytes()
 assert sha(blob)==checkpoint['libretro_state_sha256']and sha(ROM)==checkpoint['ROM_provider_sha256']
 parent_core=Path(checkpoint['execution_core_path']);assert sha(parent_core.read_bytes())==checkpoint['execution_core_sha256'];core_path=Path(core_override)if core_override else parent_core
 proof=Path(json.loads((host.ROOT/'verification/firmware-relocation-CPU-checks.json').read_text())['directory']);mapping=json.loads((proof/'protocol.json').read_text())['source_mapping'];runtime=relocation.Runtime(proof/'libfirmware-relocation.dylib',mapping['instructions_decoded'],diagnostic_core=core_path);core=runtime.core
 try:
  runtime.reset(bytes(0x200000),0);runtime.bios=ROM[:262144];assert sha(runtime.bios)==checkpoint['BIOS_sha256'];c.memmove(runtime.rom,ROM,len(ROM))
  core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool;assert core.CDIntfOpenImage(checkpoint['disc_image'].encode());core.CDROMInit();core.CDROMReset()
  core.BIWNDiagnosticRepeatSeek.argtypes=[c.c_uint32];core.BIWNDiagnosticRepeatSeek(int(checkpoint['force_repeated_seek_diagnostic']));core.BIWNDiagnosticTOCOrigin.argtypes=[c.c_uint32];core.BIWNDiagnosticTOCOrigin(int(checkpoint['TOC_origin_diagnostic'])+2*int(checkpoint['TOC_read_origin_diagnostic']))
  c.c_bool.in_dll(core,'bootConfig').value=checkpoint.get('native_CD_scheduler_enabled',False)
  core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool;assert core.retro_unserialize(c.create_string_buffer(blob),len(blob))
  for name in checkpoint['hardware']:
   if hasattr(core,name+'StateSave'):
    fn=getattr(core,name+'StateSave');fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t;runtime.savers[name]=fn
  assert runtime.snapshot()['hardware']==checkpoint['hardware'];assert host.media.scheduler.cpu_dict(runtime.cpu())==checkpoint['CPU'];assert sha(runtime.device.ram())==checkpoint['RAM_sha256']
  core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool;buffer=c.create_string_buffer(len(blob));assert core.retro_serialize(buffer,len(blob)) and buffer.raw==blob
  runtime.SSI_receive_swaps=0;runtime.SSI_register_samples=Counter();runtime.SSI_pair_samples=[];runtime.SSI_previous_right_word=checkpoint['external_SSI_previous_right_word'];runtime.SSI_previous_right_applications=0
  return runtime,checkpoint,dict(execution_core_path=str(core_path),execution_core_sha256=sha(core_path.read_bytes()),source_checkpoint_core_sha256=checkpoint['execution_core_sha256'],full_serialized_CPU_RAM_checked_hardware_match=True,core_override_selected=core_override is not None)
 except BaseException:
  runtime.oracle.close();raise
