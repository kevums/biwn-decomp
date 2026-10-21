"""Offline original/compiled replay of the actual pre-corruption formatter call."""
import ctypes as c,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_native_format_core as gate
ROOT=gate.ROOT
def main():
 capturep=ROOT/'verification/native-core-route-diagnosis-active.json';capture=json.loads(capturep.read_text());d=Path(capture['directory']);metap=d/'odd-PC.json';meta=json.loads(metap.read_text());entryram=d/'odd-PC-entry-RAM.bin';captured=entryram.read_bytes();ram=captured;bundlep=ROOT/'verification/native-fast-core-format-bundle-current.json';bundle=json.loads(bundlep.read_text());proof=json.loads((ROOT/'verification/native-core-format-core-current.json').read_text());baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
 out=ROOT/'verification/native-fast-core-capture-replay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);candidate=bytearray(ram);candidate[bundle['base']:bundle['base']+bundle['reserved_bytes']]=Path(bundle['binary']).read_bytes()+bytes(bundle['padding_bytes']);ram=bytes(candidate);original=bytearray(captured)
 for entry in [0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a,0xe61c,0xe67c]:original[entry:entry+6]=baseline[entry:entry+6]
 assert ram[bundle['base']:bundle['base']+bundle['binary_bytes']]==Path(bundle['binary']).read_bytes()
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'formatter-fullCPU-generation.json').read_text());mask=bytearray(0x200000)
 for row in mapping['instructions_decoded']:mask[row['address']]=1
 cmask=bytearray(0x200000);cmask[bundle['base']:bundle['base']+bundle['binary_bytes']]=bytes([1])*bundle['binary_bytes'];masks=[(c.c_uint8*len(x)).from_buffer_copy(x)for x in [mask,cmask]];covers=[(c.c_uint8*0x200000)()for _ in range(2)]
 driverpath=Path(proof['directory'])/'driver.dylib';driver=c.CDLL(str(driverpath));driver.run.argtypes=[c.c_void_p,c.c_void_p,c.POINTER(c.c_uint8),c.POINTER(c.c_uint8),c.c_uint32,c.c_uint32,c.c_uint64,c.POINTER(gate.Stats)];driver.run.restype=c.c_int
 n=gate.Native();entry=meta['entry'];sp=entry['registers'][15];ret=meta['return_PC'];states=[]
 try:
  for index,image,target in [(0,bytes(original),entry['pc']),(1,ram,bundle['symbols'][gate.ENTRIES[entry['pc']]])]:
   l=n.lib;n.device.seed(image,0);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,entry['ssp']);l.m68k_set_reg(17,0);l.m68k_set_reg(15,entry['usp']);l.m68k_set_reg(17,entry['sr'])
   for i,v in enumerate(entry['registers']):l.m68k_set_reg(i,v)
   l.m68k_set_reg(16,target);stats=gate.Stats();status=driver.run(c.cast(l.m68k_execute,c.c_void_p),c.cast(l.m68k_get_reg,c.c_void_p),masks[index],covers[index],ret,sp,10000000,c.byref(stats));assert not status,(index,status,hex(stats.pc));states.append((gate.cpu(n),n.device.ram(),stats))
  a,b=states;normalized=bytearray(b[1]);normalized[bundle['base']:bundle['base']+bundle['reserved_bytes']]=a[1][bundle['base']:bundle['base']+bundle['reserved_bytes']];normalized[sp-gate.PRIVATE:sp-gate.DEPTH[entry['pc']]]=a[1][sp-gate.PRIVATE:sp-gate.DEPTH[entry['pc']]]
  for pc in [0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a,0xe61c,0xe67c]:normalized[pc:pc+6]=a[1][pc:pc+6]
  diff=[dict(address=hex(i),original=x,native=y)for i,(x,y)in enumerate(zip(a[1],normalized))if x!=y]
  args=[int.from_bytes(ram[sp+i:sp+i+4],'big')for i in [4,8]];fmt=args[1];text=ram[fmt:fmt+256].split(b'\0')[0]
  state=dict(status='terminal_actual_formatter_capture_replay_equal'if a[0]==b[0]and not diff else'terminal_actual_formatter_capture_replay_mismatch',directory=str(out),captured_frame=meta['frame'],entry_PC=hex(entry['pc']),return_PC=hex(ret),task=hex(meta['task']),entry_SP=hex(sp),destination=hex(args[0]),format_pointer=hex(fmt),format_bytes=text.hex(),format_text=text.decode('latin1'),original_CPU=a[0],native_CPU=b[0],public_RAM_differences=diff[:64],full_public_RAM_equal=not diff,CPU_equal=a[0]==b[0],original_steps=a[2].steps,native_steps=b[2].steps,minimum_native_real_SP=hex(b[2].min_sp),minimum_native_real_SP_minus_task_base=b[2].min_sp-meta['task'],scope='One actual pre-failure call replayed offline from exact capturedRAM/CPU with IRQdisabled. Original entry JMPs restored, same live code/data otherwise. New compiler-inline payload inserted into capturedRAM; original captured resident bytes normalized. Candidate-only private8KB below public138byte frame excluded; no arbitrary liveIRQ/taskstate or original-read privatealias claim. Does not identify the live corruption cause by itself.',source_sha256={str(p):gate.sha(p)for p in [Path(__file__),metap,entryram,bundlep,driverpath]})
  gate.save(out/'replay.json',state);gate.save(ROOT/'verification/native-fast-core-capture-replay-current.json',state);print(json.dumps(state,indent=2))
 finally:n.close()
if __name__=='__main__':main()
