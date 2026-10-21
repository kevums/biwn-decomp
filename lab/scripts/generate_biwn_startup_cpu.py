"""Static source startup blocks; generation is not integration acceptance."""
import hashlib,json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader
ROOT=loader.ROOT
RANGES={0x17c40:0x17dc2,0x1a6e0:0x1a77c,0x1a7f4:0x1a87a,
        0x1a87a:0x1a91e,0xe2f4:0xe300,0x21242:0x212e8,
        0x18ba8:0x18df2,0xdfc0:0xdff4,0x1aeda:0x1af04,0xf0c0:0xf0fa}
def rename(text):
    return loader.rename(text).replace('generate_biwn_interior_loading_cpu.py','generate_biwn_startup_cpu.py').replace('biwn_interior_loading_cpu','biwn_startup_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_STARTUP_CPU')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows=[]
    for a,b in RANGES.items():
        assert image[a-0x4000:b-0x4000]==ram[a:b]
        rows+=loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    assert len(rows)==411
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('switch(s.cpu.pc){','if(s.cpu.pc==0x17dc2u){*state=s.cpu;return BIWN_STARTUP_CPU_READY;}switch(s.cpu.pc){')
    prefix=prefix.replace('status==6&&s->cpu.pc==0xdf60u','status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)')
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_STARTUP_CPU_H').replace('BIWN_STARTUP_CPU_BAD_PC=7','BIWN_STARTUP_CPU_BAD_PC=7,BIWN_STARTUP_CPU_READY=8')
    a=header.index('/* Static');b=header.index('enum biwn_startup_cpu_status biwn_startup_cpu_body',a)
    header=header[:a]+'''/* Fixed source blocks for17C40startup, RNG initialization/fill/setters,
 * E2F4/21242/18BA8/DFC0/1AEDA/F0C0. Full CPU/source private frames;
 * both stack banks. Helper bodies are supplied up to their outer RTS.
 * At17DC2 commits state and returns READY8 before executing renderloop.
 * DF60/DF8C nested suspension retains helper frames and returns YIELDED6.
 * No runtime decoding/original CPU calls. Generated blocks alone do not
 * prove source boot, all helpers, scheduling, devices, or playability. */
'''+header[b:]
    text=prefix+'\n'.join(rename(loader.emit(r))for r in rows)+'\n'+rename(loader.base.SUFFIX)
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_startup_cpu.c','biwn_startup_cpu.h']
    (source/names[0]).write_text(text);(source/names[1]).write_text(header)
    # Preserve the accepted user-only math interface. This separately named
    # derivative changes stack-bank bookkeeping and its mode guard only.
    math_names=['biwn_startup_rng_math_cpu.c','biwn_startup_rng_math_cpu.h']
    original_math=(source/'biwn_rng_cpu.c').read_text()
    math=original_math.replace('biwn_rng_cpu','biwn_startup_rng_math_cpu').replace('BIWN_RNG_CPU','BIWN_STARTUP_RNG_MATH_CPU')
    math=math.replace('s->usp=s->registers[15];','if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];')
    math=math.replace('s.usp=s.registers[15];','if(s.sr&0x2000u)s.ssp=s.registers[15];else s.usp=s.registers[15];')
    math=math.replace('||state->sr&0x2000u','')
    math='/* Generated separately from the accepted user-only RNG math.\n * Both-stack-bank derivative; see startup generator and comparison. */\n'+math
    math_header=(source/'biwn_rng_cpu.h').read_text().replace('biwn_rng_cpu','biwn_startup_rng_math_cpu').replace('BIWN_RNG_CPU','BIWN_STARTUP_RNG_MATH_CPU').replace('User mode,','User or supervisor mode, both stack banks,')
    (source/math_names[0]).write_text(math);(source/math_names[1]).write_text(math_header)
    manifest=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,ranges={hex(a):hex(b)for a,b in RANGES.items()},stage_sha256=hashlib.sha256(image).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},new_published_components=0,whole_game_complete=False)
    manifest['math_derivative_source_sha256']={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in math_names}
    manifest['math_derivative_parent_sha256']=hashlib.sha256(original_math.encode()).hexdigest()
    (session/'startup-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
