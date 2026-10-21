"""Fixed fullCPU scene caller/render/slot update candidate; no promotion."""
import json,hashlib
from pathlib import Path
import generate_scene_constructor_cpu as constructor
ROOT=constructor.ROOT
RANGES={0x11e6c:0x11f6c,0x11828:0x1186a,0x11b4c:0x11e64,0x11ad4:0x11b4c,0x10ba4:0x10c18,0x11384:0x1142e,0x110d4:0x11104,0x11110:0x11384,0x1142e:0x114c0,0x114cc:0x11762,0x10734:0x10968}

def rename(text):return text.replace('biwn_scene_constructor_cpu','biwn_mode3_scene_flow_cpu').replace('BIWN_SCENE_CONSTRUCTOR_CPU','BIWN_MODE3_SCENE_FLOW_CPU')
def emit(row):
 if row['assembly']=='lsr.l d3, d0':
  return f'  case {hex(row["address"])}u: /* lsr.l d3,d0 */\n   {{unsigned count=s.cpu.registers[3]&63u;uint32_t old=s.cpu.registers[0];unsigned carry=count&&count<=32u?((old>>(count-1u))&1u):0u;v=count<32u?old>>count:0u;put(&s,0,4,v);nz(&s,v,32);if(count)s.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(carry?0x11u:0));}}s.cpu.pc={hex(row["address"]+row["size"])}u;break;'
 return rename(constructor.emit(row))
def main():
 atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rows=[];failures=[]
 for low,high in RANGES.items():rows+=constructor.loader.base.binary_tools.m68k_instructions(atlas[low:high],low)[0]
 outputs=[]
 for row in rows:
  try:outputs.append(emit(row))
  except Exception as error:failures.append(dict(address=hex(row['address']),assembly=row['assembly'],error=str(error)))
 if failures:
  (ROOT/'verification/mode3-scene-flow-generation-unsupported.json').write_text(json.dumps(failures,indent=2)+'\n');print(json.dumps(failures));raise SystemExit(1)
 source=ROOT/'projects/black-ice-white-noise/restoration/experimental/mode3-flow';source.mkdir(parents=True,exist_ok=True)
 canonical=ROOT/'projects/black-ice-white-noise/restoration/experimental/biwn_scene_constructor_cpu.c';text=rename(canonical.read_text());start=text.index('  case ');end=text.index('  default:',start);text=text[:start]+'\n'.join(outputs)+'\n'+text[end:]
 text=text.replace('struct dispatch s;uint32_t v,u;','struct dispatch s;uint32_t v,u,start_budget=budget;')
 text=text.replace('while(budget--){switch(s.cpu.pc){','while(budget--){if(stop_on_yield&&s.cpu.pc==0x11e86u&&budget+1u!=start_budget){*state=s.cpu;return BIWN_MODE3_SCENE_FLOW_CPU_YIELDED;}switch(s.cpu.pc){')
 (source/'biwn_mode3_scene_flow_cpu.c').write_text(text);(source/'biwn_mode3_scene_flow_cpu.h').write_text(rename(canonical.with_suffix('.h').read_text()))
 report=dict(status='generated_unverified_mode3_source_flow',directory=str(source),instructions_decoded=rows,instructions=len(rows),ranges={hex(a):hex(b)for a,b in RANGES.items()},source_sha256=hashlib.sha256(text.encode()).hexdigest(),atlas_sha256=hashlib.sha256(atlas).hexdigest(),canonical_source_modified=False,coordinator_authored=True,new_training=False,scope='Generated fullCPU source11E6C outer task,11828 update,11B4C/11D1A helpers,seven scene/render routines. All privateframes/registers remain candidates until native comparison. External source bodies/BIOS/devices are providers; generation isnot integration or gameplay proof.')
 (ROOT/'verification/mode3-scene-flow-generation-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows))
if __name__=='__main__':main()
