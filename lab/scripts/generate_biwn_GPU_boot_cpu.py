"""Fixed source media setup: display18160, DSP loaderE840 and cart clearDC7C.

Hardware bus providers retain mapped/ignored writes. This candidate does not
implement the movie state machine, GPU overlay, DSP program or dialogue.
"""
import hashlib
import json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader

ROOT=loader.ROOT
RANGES={0xe00a:0xe03a}


def rename(text):
    return (loader.rename(text).replace('generate_biwn_interior_loading_cpu.py','generate_biwn_GPU_boot_cpu.py')
        .replace('biwn_interior_loading_cpu','biwn_GPU_boot_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_GPU_BOOT_CPU'))


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    stage=(session/'nextstage-68000-candidate.bin').read_bytes()
    ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(stage).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows=[]
    for a,b in RANGES.items():
        assert stage[a-0x4000:b-0x4000]==ram[a:b]
        rows+=loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];',
        'if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    # None of these fixed source routines use arithmetic shifts.
    a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
    prefix='\n'.join(line for line in prefix.splitlines() if not line.startswith(('static uint32_t sx16(', 'static uint32_t sx8(', 'static uint32_t alu(')))+'\n'
    prefix=prefix.replace('struct dispatch s;uint32_t v,u;','struct dispatch s;uint32_t v;')
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_GPU_BOOT_CPU_H')
    a=header.index('/* Static');b=header.index('enum biwn_GPU_boot_cpu_status biwn_GPU_boot_cpu_body',a)
    header=header[:a]+'''/* SourceE00A159word mainGPU image copy, BIOS3000(A0F03050),
 * PCF03224/GO1. FullCPU/stackbanks/sourceJSRframe. body leaves RTS,
 * call consumes RTS. BIOS3000 is a required explicit provider; no actual
 * firmware/wholeCPUboot/physicalGPU/game proof. No runtime instruction
 * decoder or original CPU execution. GPUprograms require a source provider.
 */
'''+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration'
    files=['biwn_GPU_boot_cpu.c','biwn_GPU_boot_cpu.h']
    (source/files[0]).write_text(prefix+'\n'.join(rename(loader.emit(row)) for row in rows)+'\n'+rename(loader.base.SUFFIX))
    (source/files[1]).write_text(header)
    record=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,
        ranges={hex(a):hex(b) for a,b in RANGES.items()},stage_sha256=hashlib.sha256(stage).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_sha256={name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in files},
        new_published_components=0,whole_game_complete=False)
    (session/'GPU-boot-fullCPU-generation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='instructions_decoded'}))


if __name__=='__main__':main()
