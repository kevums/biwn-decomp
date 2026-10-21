"""Compact-only compiler-independent keypad ABI vs original68000."""
from pathlib import Path
from datetime import datetime,timezone
import itertools,json,random
from check_biwn_native_button_digit import ROOT,sha,save
from check_biwn_native_button_movable import CPU

def main():
 pp=ROOT/'verification/native-load-bundle-preflight-current.json';p=json.loads(pp.read_text());binary=Path(p['binary']);assert sha(binary)==p['binary_sha256'];payload=binary.read_bytes();base=p['resident_base'];source=ROOT/'verification/zero-warm-startup-instruction-atlas.bin';original=source.read_bytes();candidate=bytearray(original);candidate[base:base+len(payload)]=payload;candidate[0x1b718:0x1b71e]=b'\x4e\xf9'+p['symbols']['biwn_native_button_digit'].to_bytes(4,'big')
 bits=[19,18,17,7,6,5,4,3,2,1];incoming=[0,0x8000ffff,0xdeadbeef];cases=list(dict.fromkeys([(sum(1<<b for b,f in zip(bits,flags)if f),d,0x2000)for flags in itertools.product([0,1],repeat=10)for d in incoming]+[(m,d,mode|ccr)for m in [0]+[1<<bit for bit in bits]for d in incoming for mode in [0,0x2000]for ccr in range(32)]));assert len(cases)==5151
 rng=random.Random(0xCC12)
 for i in range(512):cases.append((rng.getrandbits(32),rng.getrandbits(32),(0x2000 if i&1 else 0)|(i%32)))
 out=ROOT/'verification/load-keypad'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);cpu=CPU();rows=[]
 try:
  for i,(mask,d,sr)in enumerate(cases):
   a,_=cpu.execute_ranges(original,0x1b718,[(0x1b718,0x1b780)],mask,d,sr);b,pcs=cpu.execute_ranges(candidate,0x1b718,[(0x1b718,0x1b71e),(base,base+len(payload))],mask,d,sr)
   if a!=b:save(out/'mismatch.json',dict(case=i,mask=mask,incoming_D0=d,incoming_SR=sr,original=a,compiled=b));raise AssertionError(str(out/'mismatch.json'))
   rows.append(dict(case=i,mask=mask,incoming_D0=d,incoming_SR=sr,full_registers_PC_SR_and_nonprivateRAM_match=True))
 finally:cpu.close()
 save(out/'cases.json',rows);report=dict(status='terminal_compact_keypad_compiler_independent_native_ABI_pass',directory=str(out),cases=len(rows),original5151_matrix_cases=5151,extra_full32bit_masks=512,bundle_proof=str(pp),bundle_proof_sha256=sha(pp),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'projects/black-ice-white-noise/restoration/native-m68k/button-digit-compact-shim.S']},scope='OriginalnativeM68000 vs compactnewshim/C:5151button/CCR/mode matrix plus512full32bitmasks. FullD/A/PC/SR/RTS and nonprivateRAM match. IncomingX preserved despite compilerCCR clobber, sourceTST.W return flags explicit; A0/A1 saved. No IRQ/fault/cycle/physical/generalgame proof.')
 assert len(rows)==5663;save(out/'protocol.json',report);save(ROOT/'verification/load-keypad-current.json',report);print(report['status'],len(rows),flush=True)
if __name__=='__main__':main()
