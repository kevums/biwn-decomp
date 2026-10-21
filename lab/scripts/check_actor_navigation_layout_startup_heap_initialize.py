"""New reservation: exact loader RAM/CPU and declared raised-boundary heap init."""
import json,random
from pathlib import Path
from datetime import datetime,timezone
from check_biwn_scheduler import Native
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 bp=ROOT/'verification/native-actor-navigation-disc-build-current.json';b=read(bp);assert b['component_bytes']==30080 and b['heap_start']==0x166340
 out=ROOT/'verification/actor-navigation-layout-startup-heap-initialize'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);original_stage=(session/'nextstage-68000-candidate.bin').read_bytes();stage=Path(b['derived_stage']).read_bytes();payload=Path(b['component']).read_bytes();original=bytearray(0x200000);original[0x4000:0x100000]=original_stage;installed=bytearray(original);installed[0x4000:0x100000]=stage
 n=Native();rng=random.Random(0x166340)
 def cpu():
  l=n.lib;values=[l.m68k_get_reg(None,i)for i in range(18)];sr=values[17];return values+[n.prefix[16]if sr&0x2000 else values[15],values[15]if sr&0x2000 else n.prefix[17]]
 def setup(image,regs,sr,entry):
  n.device.seed(bytes(image),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,regs[15]if sr&0x2000 else 0x1fd000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fc000 if sr&0x2000 else regs[15]);l.m68k_set_reg(17,sr)
  for i,v in enumerate(regs):l.m68k_set_reg(i,v)
  l.m68k_set_reg(16,entry)
 def startup(image,regs,sr,new):
  setup(image,regs,sr,0x4000)
  for count in range(100000):
   pc=n.lib.m68k_get_reg(None,16)
   if pc==0x400a:break
   assert pc in [0x4000,0x4004]or(new and(b['staging_address']<=pc<b['staging_address']+b['native_entry_bytes']or b['resident_address']<=pc<b['resident_address']+b['component_bytes'])),hex(pc)
   n.lib.m68k_execute(1)
  else:raise AssertionError('Startup did not resume400A')
  return cpu(),n.device.ram()
 startup_rows=[];init_rows=[]
 try:
  for variant in range(3):
   for flags in range(32):
    regs=[rng.getrandbits(32)for _ in range(16)];regs[15]=0x180000;a,_=startup(original,regs,0x2000|flags,False);actual,ram=startup(installed,regs,0x2000|flags,True);assert a==actual
    expected=bytearray(installed);expected[b['resident_address']:b['resident_address']+len(payload)]=payload;expected[b['staging_address']:b['staging_address']+b['staging_bytes_cleared']]=bytes(b['staging_bytes_cleared']);assert ram[:0x1fffc4]==expected[:0x1fffc4]
    startup_rows.append(dict(variant=variant,flags=flags,CPU=actual,copy_and_clear_RAM_match=True))
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();common=bytearray(baseline);common[0x4000:0x100000]=stage;common[b['resident_address']:b['resident_address']+len(payload)]=payload
  block=bytearray(baseline[0x1557a:0x155c2]);counts=[]
  for delta,want in [(0,3),(4,1),(8,1)]:
   old=(0x15edc0+delta).to_bytes(4,'big');new=(b['heap_start']+delta).to_bytes(4,'big');indices=[i for i in range(len(block)-3)if block[i:i+4]==old];assert len(indices)==want,(delta,indices)
   for i in indices:block[i:i+4]=new
   counts.append(dict(delta=delta,operands=len(indices)))
  at=b['symbols']['biwn_native_heap_initialize']-b['resident_address'];assert payload[at:at+len(block)]==block,'Raised-boundary original heap initialization differs from source transcription'
  reference=bytearray(common);reference[0x1557a:0x155c2]=block;SP=0x1e0000;STOP=0x1f0000
  for image in [reference,common]:image[SP:SP+4]=STOP.to_bytes(4,'big')
  def initialize(image,regs,sr,new):
   setup(image,regs,sr,0x1557a)
   for steps in range(10000):
    pc=n.lib.m68k_get_reg(None,16)
    if pc==STOP:break
    assert ((pc==0x1557a or b['resident_address']<=pc<b['resident_address']+b['linked_component_bytes'])if new else 0x1557a<=pc<0x155c2),hex(pc)
    n.lib.m68k_execute(1)
   else:raise AssertionError('Heap initialize did not return')
   return cpu(),n.device.ram()
  for variant in range(3):
   for mode in [0,0x2000]:
    for flags in range(32):
     regs=[rng.getrandbits(32)for _ in range(16)];regs[15]=SP;a,left=initialize(reference,regs,mode|flags,False);actual,right=initialize(common,regs,mode|flags,True);assert a==actual
     normalized=bytearray(right);normalized[0x1557a:0x155c2]=left[0x1557a:0x155c2];assert normalized==left
     floor=b['heap_start'];word=lambda address:int.from_bytes(right[address:address+4],'big');assert word(0x112d60)==floor and word(0x112d64)==0x1c0000-floor and word(floor)==0x1c0000-floor and word(floor+4)==word(floor+8)==0 and not any(right[0x112960:0x112d60]);assert word(SP)==STOP
     init_rows.append(dict(variant=variant,mode=mode,flags=flags,CPU=actual,capacity=0x1c0000-floor))
  paths=[Path(__file__),bp,Path(b['derived_stage']),Path(b['component']),session/'nextstage-68000-candidate.bin',ROOT/'render-assets/biwn-inventory-baseline.bin',ROOT/'scripts/check_biwn_scheduler.py',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']
  state=dict(status='terminal_layout30080_startup_and_heap_initialize_pass',directory=str(out),startup_cases=len(startup_rows),heap_initialize_cases=len(init_rows),original_heap_initializer_declared_operand_changes=counts,source_assembly_byte_identity_after_floor_change=True,reserve=30080,heap_floor='0x166340',initial_heap_bytes=0x1c0000-b['heap_start'],source_sha256={str(p):sha(p)for p in paths},scope=__doc__,new_predictions=0,gameplay_verified=False)
  save(out/'startup-results.json',startup_rows);save(out/'heap-initialize-results.json',init_rows);save(out/'protocol.json',state);save(ROOT/'verification/actor-navigation-layout-startup-heap-initialize-current.json',state);print(json.dumps({k:state[k]for k in ['status','startup_cases','heap_initialize_cases','initial_heap_bytes']}))
 finally:n.close()

if __name__=='__main__':main()
