"""96loader CPU/bank/RAM cases for the complete28380byte payload."""
import json,random
from pathlib import Path
from datetime import datetime,timezone
from check_biwn_scheduler import Native
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 bp=ROOT/'verification/native-actor-collision-disc-build-current.json';b=json.loads(bp.read_text());assert b['linked_component_bytes']==28380 and b['component_bytes']==28544
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);original=bytearray(0x200000);original[0x4000:0x100000]=(session/'nextstage-68000-candidate.bin').read_bytes();stage=Path(b['derived_stage']).read_bytes();installed=bytearray(original);installed[0x4000:0x100000]=stage;payload=Path(b['component']).read_bytes();n=Native();rng=random.Random(0x28380);rows=[]
 def run(image,registers,sr,new):
  n.device.seed(bytes(image),0);lib=n.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0);lib.m68k_set_reg(17,0);lib.m68k_set_reg(15,0x1fc000);lib.m68k_set_reg(17,sr)
  for i,v in enumerate(registers):lib.m68k_set_reg(i,v)
  lib.m68k_set_reg(16,0x4000)
  for _ in range(100000):
   pc=lib.m68k_get_reg(None,16)
   if pc==0x400a:break
   assert pc in [0x4000,0x4004]or(new and(b['staging_address']<=pc<b['staging_address']+b['native_entry_bytes']or b['resident_address']<=pc<b['resident_address']+b['component_bytes']))
   lib.m68k_execute(1)
  else:raise AssertionError('Loader did not resume400A')
  cpu=[lib.m68k_get_reg(None,i)for i in range(18)];return cpu+[n.prefix[16],cpu[15]],n.device.ram()
 try:
  for variant in range(3):
   for flags in range(32):
    regs=[rng.getrandbits(32)for _ in range(16)];regs[15]=0x180000;a,_=run(original,regs,0x2000|flags,False);cpu,ram=run(installed,regs,0x2000|flags,True);assert a==cpu;expected=bytearray(installed);expected[b['resident_address']:b['resident_address']+len(payload)]=payload;expected[b['staging_address']:b['staging_address']+b['staging_bytes_cleared']]=bytes(b['staging_bytes_cleared']);assert ram[:0x1fffc4]==expected[:0x1fffc4];rows.append(dict(variant=variant,flags=flags,CPU=cpu))
  out=ROOT/'verification/actor-collision-final-startup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'cases.json',rows);state=dict(status='terminal_actor_collision_full_payload_startup_pass',directory=str(out),cases=len(rows),payload_bytes=28380,reservation_bytes=28544,heap_floor=hex(b['heap_start']),source_sha256={str(p):sha(p)for p in [Path(__file__),bp,Path(b['derived_stage']),Path(b['component']),session/'nextstage-68000-candidate.bin',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']});save(out/'protocol.json',state);save(ROOT/'verification/actor-collision-final-startup-current.json',state);print(state['status'],len(rows))
 finally:n.close()

if __name__=='__main__':main()
