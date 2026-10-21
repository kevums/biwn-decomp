"""Separate cache save/restore/freeze providers and dispatcher continuation ABI."""
import json,hashlib
import generate_scene_constructor_cpu as generator
ROOT=generator.ROOT

def main():
 s=ROOT/'projects/black-ice-white-noise/restoration/experimental/mode3-inventory';s.mkdir(parents=True,exist_ok=True)
 atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();ranges={0x1aade:0x1ac3c,0xdf22:0xdf60,0x190bc:0x191f4,0x12620:0x12896,0x1a0f8:0x1a188,0x10c6e:0x10cb6,0x10e72:0x10ed2,0x10ede:0x1102a,0x1102a:0x110d4};rows=[]
 for low,high in ranges.items():rows+=generator.loader.base.binary_tools.m68k_instructions(atlas[low:high],low)[0]
 def rename(text):return text.replace('biwn_scene_constructor_cpu','biwn_mode3_inventory_helpers_cpu').replace('BIWN_SCENE_CONSTRUCTOR_CPU','BIWN_MODE3_INVENTORY_HELPERS_CPU')
 old=ROOT/'projects/black-ice-white-noise/restoration/experimental/biwn_scene_constructor_cpu.c';text=rename(old.read_text());start=text.index('  case ');end=text.index('  default:',start);text=text[:start]+'\n'.join(rename(generator.emit(row))for row in rows)+'\n'+text[end:]
 (s/'biwn_mode3_inventory_helpers_cpu.c').write_text(text);(s/'biwn_mode3_inventory_helpers_cpu.h').write_text(rename(old.with_suffix('.h').read_text()).replace('BIWN_MODE3_INVENTORY_HELPERS_CPU_BAD_PC=7','BIWN_MODE3_INVENTORY_HELPERS_CPU_BAD_PC=7,BIWN_MODE3_INVENTORY_HELPERS_CPU_DIVISION_BY_ZERO=8,BIWN_MODE3_INVENTORY_HELPERS_CPU_DIVISION_OVERFLOW=9'))
 original=ROOT/'projects/black-ice-white-noise/restoration/biwn_input_dispatch_cpu.c';dispatch=original.read_text();needle='if(status==6&&s->cpu.pc==0xdf60u)return 6;';assert needle in dispatch
 dispatch=dispatch.replace(needle,'if(status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu||s->cpu.pc==0x11e86u))return 6;')
 (s/'biwn_input_dispatch_cpu.c').write_text(dispatch)
 world=(ROOT/'projects/black-ice-white-noise/restoration/biwn_world_flow_cpu.c').read_text();world=world.replace('status==6&&s->cpu.pc==0xdf60u','status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0x11e86u)');world=world.replace('struct dispatch s;uint32_t v,u;','struct dispatch s;uint32_t v,u,start_budget=budget;').replace('while(budget--){switch(s.cpu.pc){','while(budget--){if(stop_on_yield&&s.cpu.pc==0x1a54au&&budget+1u!=start_budget){*state=s.cpu;return BIWN_WORLD_FLOW_CPU_YIELDED;}switch(s.cpu.pc){');(s/'biwn_world_flow_cpu.c').write_text(world)
 manifest=dict(status='generated_unverified_inventory_bridge',directory=str(s),instructions_decoded=rows,instructions=len(rows),source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in s.glob('*.c')},canonical_dispatcher_modified=False,scope='Source cache snapshot/restore and task freeze/unfreeze blocks. Separate dispatcher copy only broadens suspension protocol for nested source observer boundary11E86/DF8C; instruction bodies unchanged. Not naturally reached view/return proof until native comparison.')
 (ROOT/'verification/mode3-inventory-bridge-generation-current.json').write_text(json.dumps(manifest,indent=2)+'\n');print(manifest['status'],len(rows))
if __name__=='__main__':main()
