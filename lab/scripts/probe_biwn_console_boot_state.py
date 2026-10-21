"""Original bundled SeriesK console ROM under full core frame scheduling."""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import observe_biwn_relocated_firmware as host
ROOT=host.ROOT
prior=json.loads((ROOT/'verification/firmware-relocation-CPU-checks.json').read_text());proof=Path(prior['directory']);mapping=json.loads((proof/'protocol.json').read_text())['source_mapping'];build=json.loads((ROOT/'verification/BIWN-TOC-origin-build-current.json').read_text());out=ROOT/'verification/BIWN-console-boot-probe'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
runtime=host.relocation.Runtime(proof/'libfirmware-relocation.dylib',mapping['instructions_decoded'],diagnostic_core=Path(build['core_path']));core=runtime.core
try:
 runtime.reset(bytes(0x200000),0);BIOS=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();c.memmove(runtime.rom,BIOS,len(BIOS));runtime.bios=BIOS
 core.m68k_set_reg(17,0x2700);core.m68k_set_reg(16,0xe00008);core.m68k_set_irq(0);core.GPUGetPC.restype=c.c_uint32;core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.retro_run.argtypes=[]
 buffer=c.create_string_buffer(12000);rows=[];stop='frame_budget'
 for i in range(180):
  core.retro_run();assert runtime.savers['GPU'](buffer)==4416;raw=buffer.raw[:4416];R31=[struct.unpack_from('=I',raw,o)[0]for o in [4263,4391]];row=dict(frame=i+1,CPU=hex(runtime.cpu().pc),GPU=hex(core.GPUGetPC()),R31_banks=[hex(x)for x in R31],bank=raw[4395]);rows.append(row)
  if i%10==0:print(json.dumps(row),flush=True)
  if 0xf03000<R31[0]<=0xf04000 or 0xf03000<R31[1]<=0xf04000:
   stop='source_GPU_stack_in_local_RAM_observed';break
 (out/'GPU-final.bin').write_bytes(raw);(out/'RAM-final.bin').write_bytes(runtime.device.ram());report=dict(status='terminal_console_boot_frame_probe',directory=str(out),stop_reason=stop,frames=rows,initial_CPU_PC='0xe00008',initial_SR='0x2700',bundled_console_ROM='SeriesK in pinned source/core',supplied_cart_ROM_sha256=host.sha(BIOS),disc_attached=False,source_R31_written_by_native_execution=True,host_R31_write=False,scope='Full core retro_run frame schedule from supplied zeroRAM/canonical consoleROM entry with CD cartridge ROM mapped, no disc. This is a console initialization probe, not a connected CD game boot or hardware validation. No stack value supplied.',whole_game_complete=False)
 host.save(out/'report.json',report);host.save(ROOT/'verification/BIWN-console-boot-probe-current.json',report);print(json.dumps(dict(directory=str(out),stop=stop,final=rows[-1])),flush=True)
finally:runtime.oracle.close()
