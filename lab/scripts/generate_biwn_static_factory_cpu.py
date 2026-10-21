"""Fixed CPU static/sprite object factory; its inline table remains data."""
import hashlib,json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader
ROOT=loader.ROOT
RANGES={0x137e0:0x138bc,0x13902:0x13ae0}
def rename(text):return loader.rename(text).replace('generate_biwn_interior_loading_cpu.py','generate_biwn_static_factory_cpu.py').replace('biwn_interior_loading_cpu','biwn_static_factory_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_STATIC_FACTORY_CPU')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows=[]
    for a,b in RANGES.items():assert stage[a-0x4000:b-0x4000]==ram[a:b];rows+=loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    assert len(rows)==184
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_STATIC_FACTORY_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_static_factory_cpu_status biwn_static_factory_cpu_body',a)
    header=header[:a]+'''/* Source137E0 static/sprite factory,184 fixed instruction blocks.
 * Inline138BC..13902 callback/jump table stays source data read via bus.
 * Full CPU/private frames/both stack banks; helpers run up to outer RTS.
 * 105DA position,152A2 allocator andE2B8 sprite submission are providers.
 * No runtime decoding or original CPU calls. Generated code alone proves
 * no scene, GPU/context, source boot or complete game behavior. */
'''+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_static_factory_cpu.c','biwn_static_factory_cpu.h'];(source/names[0]).write_text(prefix+'\n'.join(rename(loader.emit(r))for r in rows)+'\n'+rename(loader.base.SUFFIX));(source/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=184,instructions_decoded=rows,ranges={hex(a):hex(b)for a,b in RANGES.items()},inline_table_data=['0x138bc','0x13902'],stage_sha256=hashlib.sha256(stage).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),new_published_components=0,whole_game_complete=False)
    (session/'static-factory-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
