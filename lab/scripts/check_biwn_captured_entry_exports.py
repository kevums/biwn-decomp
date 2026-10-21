"""Check exported native/C continuation contexts in separate restored runtimes."""
import ctypes as c,json,argparse
from pathlib import Path
from datetime import datetime,timezone
import observe_biwn_relocated_firmware as host
import biwn_firmware_checkpoint as checkpoint
import check_biwn_movie_GPU as GPU
import check_biwn_dsp_media_audio as DSP
from probe_biwn_gpu_projection import gpu_state
ROOT=host.ROOT;save=host.save;sha=host.sha
parser=argparse.ArgumentParser();parser.add_argument('--source-proof',type=Path);parser.add_argument('--no-publish',action='store_true');options=parser.parse_args();assert not options.source_proof or options.no_publish
prior=json.loads((options.source_proof or ROOT/'verification/captured-source-music-entry-current.json').read_text());source=Path(prior['directory']);out=ROOT/'verification/BIWN-captured-entry-export-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);rows=[]
try:
 for mode in ['native','C']:
  record=json.loads((source/(mode+'-continuation.json')).read_text());runtime,loaded,checks=checkpoint.restore_current(host,record['source_checkpoint'],core_override=record['core_path']);core=runtime.core
  if record.get('single_SSI_chain_diagnostic'):
   core.BIWNSetSSISingleChain.argtypes=[c.c_uint32];core.BIWNSetSSISingleChain(1)
  try:
   blob=Path(record['shared_core_file']).read_bytes();ROM=Path(record['ROM_provider_file']).read_bytes();assert sha(blob)==record['shared_core_sha256'] and sha(ROM)==record['ROM_provider_sha256'];c.memmove(runtime.rom,ROM,len(ROM));assert core.retro_unserialize(c.create_string_buffer(blob),len(blob))
   assert runtime.device.ram()==Path(record['RAM_file']).read_bytes();buffer=c.create_string_buffer(len(blob));assert core.retro_serialize(buffer,len(blob)) and buffer.raw==blob
   GPU_bytes=Path(record['GPU_logical_file']).read_bytes();DSP_bytes=Path(record['DSP_logical_file']).read_bytes();g=GPU.state_from_raw(GPU_bytes);d=DSP.state_from_raw(DSP_bytes);assert GPU.logical(g)==GPU_bytes and DSP.logical(d)==DSP_bytes
   CPU=host.media.CPU();CPU.registers[:]=record['CPU']['registers'];CPU.pc=record['CPU']['pc'];CPU.sr=record['CPU']['sr'];CPU.usp=record['CPU']['usp'];CPU.ssp=record['CPU']['ssp'];assert host.media.scheduler.cpu_dict(CPU)==record['CPU'] and CPU.pc==0xdd40
   hw=runtime.snapshot()['hardware'];hw['GPU']=dict(size=4396,sha256=sha(GPU_bytes));hw['DSP']=dict(size=8496,sha256=sha(DSP_bytes));assert hw==record['hardware']
   if mode=='native':
    assert host.media.scheduler.cpu_dict(runtime.cpu())==record['CPU'] and gpu_state(core)[0][:4396]==GPU_bytes
    raw=c.create_string_buffer(12000);size=core.DSPStateSave(raw);assert raw.raw[:8496]==DSP_bytes
   else:assert runtime.cpu().pc==0x4000,'C image unexpectedly passed off native shadow as reconstructedCPU'
   row=dict(mode=mode,full_shared_core_bytes_reloaded_and_roundtrip_exact=True,RAM_export_exact=True,C_owned_processor_context_roundtrip_exact=True,checked_hardware_match_with_owned_GPU_DSP=True,owned_CPU_PC=hex(CPU.pc),shared_original_CPU_shadow_PC=hex(runtime.cpu().pc),GPU_PC=hex(g.pc),DSP_PC=hex(d.pc));rows.append(row);save(out/(mode+'.json'),row)
  finally:runtime.oracle.close()
 report=dict(status='captured_DD40_native_and_C_owned_context_exports_cross_process_checked',directory=str(out),source_directory=str(source),rows=rows,full_frame_C_emulation_verified=False,whole_game_complete=False,limits=['C processor shadows remain stale; subsequent C harness must consume ownedCPU/GPU/DSP context with shared devices and continue forbidding original processor execution. No native fullframe execution of this C context.','Native/C state comparison excludes20byte GPU and233byte DSP backendtails and timing/opcode/pipeline microstate. Earlier declared source/ROM/CD/SSI/GPUstack inputs and poll/instruction scheduling persist.'])
 report['single_SSI_chain_diagnostic']=prior.get('single_SSI_chain_diagnostic',False)
 save(out/'report.json',report)
 if not options.no_publish:save(ROOT/'verification/captured-entry-exports-current.json',report)
 save(out/'status.json',dict(status='terminal_pass'));print(report['status'],flush=True)
except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
