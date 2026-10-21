"""One captured entry: independent native emulated cycles, not wall FPS."""
import json
from datetime import datetime,timezone
from pathlib import Path
from check_biwn_scheduler import Native
from check_biwn_native_format_core import cpu
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 capture=json.loads((ROOT/'verification/native-core-route-diagnosis-current.json').read_text());d=Path(capture['directory']);meta=json.loads((d/'odd-PC.json').read_text());seed=(d/'odd-PC-entry-RAM.bin').read_bytes();original=bytearray(seed);baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
 for pc in [0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a,0xe61c,0xe67c]:original[pc:pc+6]=baseline[pc:pc+6]
 paths={k:ROOT/'verification'/(v+'-bundle-current.json')for k,v in [('slow','native-core-format'),('inline','native-fast-core-format')]};bundles={k:json.loads(p.read_text())for k,p in paths.items()};images={'original':(bytes(original),meta['entry']['pc'])}
 for name,b in bundles.items():
  ram=bytearray(seed);payload=Path(b['binary']).read_bytes();assert sha(b['binary'])==b['binary_sha256'];ram[b['base']:b['base']+b['reserved_bytes']]=payload+bytes(b['padding_bytes']);images[name]=(bytes(ram),b['symbols']['biwn_native_format_variadic'])
 n=Native();rows={};reference=None;entry=meta['entry'];sp=entry['registers'][15];ret=meta['return_PC']
 try:
  for name,(image,pc)in images.items():
   n.device.seed(image,0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,entry['ssp']);l.m68k_set_reg(17,0);l.m68k_set_reg(15,entry['usp']);l.m68k_set_reg(17,entry['sr'])
   for i,v in enumerate(entry['registers']):l.m68k_set_reg(i,v)
   l.m68k_set_reg(16,pc);cycles=0;minimum=sp
   for step in range(1000000):
    pc=l.m68k_get_reg(None,16);minimum=min(minimum,l.m68k_get_reg(None,15))
    if pc==ret and l.m68k_get_reg(None,15)==sp+4:break
    if name!='original':b=bundles[name];assert b['base']<=pc<b['base']+b['binary_bytes'],hex(pc)
    cycles+=l.m68k_execute(1)
   else:raise AssertionError('Cost replay budget')
   state=cpu(n)
   if reference is None:reference=state
   assert state==reference
   rows[name]=dict(instructions=step,emulated_m68k_cycles=cycles,minimum_real_SP=hex(minimum),minimum_SP_minus_task=minimum-meta['task'],full_return_CPU_equal=True)
 finally:n.close()
 out=ROOT/'verification/native-formatter-capture-cost'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 result=dict(status='terminal_one_captured_formatter_cost_classified',directory=str(out),capture=str(d/'odd-PC.json'),captured_frame=meta['frame'],format=' %03d:%03d:%d',rows=rows,inline_instruction_reduction_vs_slow=1-rows['inline']['instructions']/rows['slow']['instructions'],inline_cycle_reduction_vs_slow=1-rows['inline']['emulated_m68k_cycles']/rows['slow']['emulated_m68k_cycles'],inline_cycle_multiple_vs_original=rows['inline']['emulated_m68k_cycles']/rows['original']['emulated_m68k_cycles'],scope='One exact captured call replayed offline withIRQdisabled, retainedNativeCPU, same incoming semanticCPU/data. Emulated native cycles include compiled caller/helper work. Not hardware timing,whole-gameFPS,an IRQ-cause isolation or all-input cost result. PublicRAM semantics use separate full/replay gates.',dependencies_sha256={str(p):sha(p)for p in [Path(__file__),d/'odd-PC.json',d/'odd-PC-entry-RAM.bin',*paths.values(),*[Path(b['binary'])for b in bundles.values()]]})
 save(out/'cost.json',result);save(ROOT/'verification/native-formatter-capture-cost-current.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
