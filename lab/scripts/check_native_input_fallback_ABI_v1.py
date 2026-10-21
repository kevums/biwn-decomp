"""Observe deployed fallback versus original at E4C0, plus MOVEM negatives.

Full CPU and all2MB RAM compare without normalization. Finite both-bank,
all-CCR cases provide an execution-backed answer to the local model's errors.
"""
from datetime import datetime,timezone
import json
from pathlib import Path
import random
import subprocess
import check_native_deck_input_v1 as m

ROOT=m.ROOT;V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 b=read(V/'native-Deck-input-disc-build-current.json');out=V/'native-input-fallback-ABI-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=out/'movem-negative.S';source.write_text('.text\n.global start\nstart:\nmovem.l %d2-%d3,-(%sp)\npea 0x11b56\njmp 0xe4c0\n')
 tool=ROOT/'tools/m68k-elf/bin/m68k-elf-';subprocess.run([str(tool)+'as','-m68000','-o',str(out/'negative.o'),str(source)],check=True);subprocess.run([str(tool)+'objcopy','-O','binary',str(out/'negative.o'),str(out/'negative.bin')],check=True)
 image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());base=b['resident_address'];component=Path(b['component']).read_bytes();image[base:base+len(component)]=component;negative=(out/'negative.bin').read_bytes();image[0x190000:0x190000+len(negative)]=negative
 fallback=b['input_symbols']['biwn_native_input_original_fallback'];rng=random.Random(0x11b5616);n=m.Engine();rows=[];rejected=0
 def run(ram,initial,entry):
  state=m.CPU.from_buffer_copy(bytes(initial));state.pc=entry;n.native.device.seed(ram,0);n.set_cpu(state,True)
  for count in range(10):
   if n.cpu().pc==0xe4c0:break
   n.core.m68k_execute(1)
  else:raise AssertionError('Fallback did not reach original poll helper')
  return n.native.device.ram(),n.cpu(),count
 try:
  for mode in [0,0x2000]:
   for flags in range(32):
    for d2 in [0,1,0xffffffff,0x80000000,0x7fffffff,0xaabb0000]:
     initial=m.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[m.SP];initial.registers[2]=d2;initial.sr=mode|flags;initial.usp=m.SP if not mode else 0x1d8000;initial.ssp=m.SP if mode else 0x1ff000
     memory=bytearray(image);memory[m.SP-32:m.SP+16]=rng.randbytes(48);ram=bytes(memory)
     left,cpu,a=run(ram,initial,0x11b4c);right,got,c=run(ram,initial,fallback);assert left==right and m.cpu_dict(cpu)==m.cpu_dict(got)
     sp=cpu.registers[15];assert sp==m.SP-12 and int.from_bytes(left[sp:sp+4],'big')==0x11b56
     assert int.from_bytes(left[sp+4:sp+8],'big')==d2 and int.from_bytes(left[sp+8:sp+12],'big')==initial.registers[3]
     wrong,changed,w=run(ram,initial,0x190000);assert wrong==left
     assert list(changed.registers)==list(cpu.registers) and changed.pc==cpu.pc and changed.usp==cpu.usp and changed.ssp==cpu.ssp
     differs=changed.sr!=cpu.sr;rejected+=differs
     assert changed.sr==initial.sr
     rows.append(dict(supervisor=bool(mode),incoming_CCR=flags,D2=hex(d2),return_address_width=32,helper_SP=hex(sp),return_PC=hex(int.from_bytes(left[sp:sp+4],'big')),original_CCR=cpu.sr&31,MOVEM_CCR=changed.sr&31,MOVEM_rejected=differs,original_instructions=a,fallback_instructions=c,negative_instructions=w))
 finally:n.native.close()
 assert len(rows)==384 and 0<rejected<384
 m.save(out/'cases.json',rows);proof=dict(status='terminal_deployed_input_fallback_full_CPU_full_RAM_ABI_match',directory=str(out),cases=len(rows),MOVEM_flag_counterexamples=rejected,return_address_bits=32,normalization='none',source_sha256={str(p):m.sha(p.read_bytes())for p in [Path(__file__),Path(m.__file__),Path(m.original.scene.__file__),Path(m.original.scene.coordinate.__file__),source,out/'negative.bin',Path(b['component']),V/'native-Deck-input-disc-build-current.json',ROOT/'render-assets/biwn-inventory-baseline.bin',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']},scope=__doc__,new_predictions=0,new_training=False,whole_game_complete=False)
 m.save(out/'review.json',proof);m.save(V/'native-input-fallback-ABI-v1-current.json',proof);print(proof['status'],len(rows),rejected,flush=True)

if __name__=='__main__':main()
