"""Captured-boundary origin hypothesis; no whole-boot claim."""
import ctypes as c,struct,json,hashlib
from datetime import datetime,timezone
import check_biwn_scheduler as scheduler
import check_biwn_TOC_compression as ref
ROOT=scheduler.ROOT
source=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T083153.831713Z/fourth-DSP-command'
incoming=(source/'DSP-after-CPU.bin').read_bytes();ram=(source/'RAM-after-CPU.bin').read_bytes()
layout=json.loads((ROOT/'projects/black-ice-white-noise/analysis/session-20261012T191624.705232Z/cdi-layout.json').read_text())
toc=bytearray(incoming[0x800:0xc00]);old=bytes(toc)
def msf(n):return bytes([n//4500,n//75%60,n%75])
def frames(b):return b[0]*4500+b[1]*75+b[2]
# Coordinate hypothesis derived from descriptor pregap; no expected bytes used.
origin=layout['tracks'][0]['pregap_sectors'] if 'pregap_sectors' in layout['tracks'][0] else layout['tracks'][0]['pregap']
assert origin==150
for t in layout['tracks']:
 o=8*t['track'];toc[o+1:o+4]=msf(frames(toc[o+1:o+4])-origin)
toc[5:8]=msf(frames(toc[5:8])-origin)
toc[13:16]=msf(layout['tracks'][0]['program_sectors'])
expected=ram[0xfb004:0xfb014];reference,blocks=ref.compress(toc)
proof=json.loads((ROOT/'verification/BIWN-TOC-local-C-current.json').read_text())
fn=c.CDLL(str(__import__('pathlib').Path(proof['directory'])/'checksum.dylib')).biwn_firmware_TOC_checksum
fn.argtypes=[c.POINTER(c.c_uint8),c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];fn.restype=c.c_int
result=(c.c_uint32*4)();assert fn((c.c_uint8*1024).from_buffer_copy(toc),(c.c_uint32*64)(*ref.K),result)==0
model_C=struct.pack('>4I',*result);assert model_C==reference
out=ROOT/'verification/BIWN-TOC-origin-match'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
run=scheduler.Native();core=run.lib
core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t
core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32
core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.DSPExec.argtypes=[c.c_int32]
count=c.c_uint32.in_dll(core,'dsp_exec_opcode_count')
try:
 run.device.seed(ram,0);state=bytearray(incoming);state[0x800:0xc00]=toc;assert core.DSPStateLoad(c.create_string_buffer(bytes(state)))==8729
 start=count.value
 for i in range(200000):
  if i and core.DSPReadLong(0xf1b020,0)&0x80000000:break
  core.DSPExec(1)
 else:raise AssertionError('command timeout')
 command=(count.value-start)&0xffffffff
 core.DSPWriteLong(0xf1b3f8,0xffffffff,6);core.DSPWriteLong(0xf1a114,5,6);start=count.value
 for i in range(1000):
  if i and not core.DSPReadLong(0xf1b3f8,0)&0x80000000 and not core.DSPReadLong(0xf1a100,0)&8:break
  core.DSPExec(1)
 else:raise AssertionError('IRQ timeout')
 native=run.device.ram()[0xfb1b0:0xfb1c0];assert native==reference==model_C==expected
 report=dict(status='three_implementations_match_disc_header',directory=str(out),original_DSP=native.hex(),independent_compression=reference.hex(),unchanged_local_model_C=model_C.hex(),disc_header=expected.hex(),original_DSP_command_instructions=command,original_DSP_IRQ_instructions=(count.value-start)&0xffffffff,TOC_prefix=toc[:48].hex(),changed_offsets=[i for i,(a,b)in enumerate(zip(old,toc))if a!=b],input_derivation='Subtract first stored pregap150 from all track/global leadout positions; first program duration1079. This is an explicit coordinate-origin hypothesis, not established physical CD semantics.',scope='Captured DSP/RAM state; host supplies modified TOC and IRQ. CPU and clocks held. Expected checksum used only in assertion, never injected. No natural boot or hardware proof.',whole_boot=False)
 (out/'TOC.bin').write_bytes(toc);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/BIWN-TOC-origin-match-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
finally:run.close()
