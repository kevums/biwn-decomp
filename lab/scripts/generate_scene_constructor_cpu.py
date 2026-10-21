"""Fixed full-CPU constructor continuations for scheduler integration."""
import hashlib,json
from pathlib import Path
import generate_biwn_interior_loading_cpu as loader
ROOT=loader.ROOT
RANGES={0x10990:0x10a6a,0x10a6a:0x10ba4,0x1ae88:0x1aeda,0x10968:0x10990,0x11762:0x11808}


def rename(text):
    return loader.rename(text).replace('biwn_interior_loading_cpu','biwn_scene_constructor_cpu').replace('BIWN_INTERIOR_LOADING_CPU','BIWN_SCENE_CONSTRUCTOR_CPU').replace('generate_biwn_interior_loading_cpu.py','generate_scene_constructor_cpu.py')


def emit(row):
    op,_,tail=row['assembly'].partition(' ')
    if op=='mulu.w':
        args=loader.base.split(tail);register=loader.base.register(args[1]);assert register is not None
        code=loader.resource.load(args[0],2)
        code+=f'v=(uint32_t)(uint16_t)v*(uint32_t)(uint16_t)s.cpu.registers[{register}];put(&s,{register},4,v);nz(&s,v,32);s.cpu.pc={hex(row["address"]+row["size"])}u;break;'
        return f'  case {hex(row["address"])}u: /* {row["assembly"]} */\n   '+code
    return rename(loader.emit(row))


def main():
    source=ROOT/'projects/black-ice-white-noise/restoration/experimental'
    atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    rows=[]
    for low,high in RANGES.items():
        part,_=loader.base.binary_tools.m68k_instructions(atlas[low:high],low);rows+=part
    prefix=rename(loader.base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];',
        'if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('status==6&&s->cpu.pc==0xdf60u','status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)')
    header=rename(loader.base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_SCENE_CONSTRUCTOR_CPU_H')
    a=header.index('/* Static');b=header.index('enum biwn_scene_constructor_cpu_status biwn_scene_constructor_cpu_body',a)
    header=header[:a]+'''/* Fixed constructor10990,selector10A6A,reference release1AE88,
 * slot clear10968 andrecord insert11762. Both stack banks/fullCPU/private
 * frames retained. Nested source bodies/providers stop before RTS.
 * DF60/DF8C suspension commits CPU/frames for actual scheduler resumption.
 * Coordinator build-time translation,no runtime decode/originalCPU calls.
 * Generation alone does not prove constructor,disc or gameplay behavior.
 */
'''+header[b:]
    (source/'biwn_scene_constructor_cpu.h').write_text(header)
    (source/'biwn_scene_constructor_cpu.c').write_text(prefix+'\n'.join(emit(row)for row in rows)+'\n'+rename(loader.base.SUFFIX))
    record=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,
        ranges={hex(a):hex(b)for a,b in RANGES.items()},atlas_sha256=hashlib.sha256(atlas).hexdigest(),
        source_sha256={name:hashlib.sha256((source/name).read_bytes()).hexdigest()for name in ['biwn_scene_constructor_cpu.c','biwn_scene_constructor_cpu.h']},
        coordinator_authored=True,new_training=False,natural_gameplay_verified=False)
    (ROOT/'verification/scene-constructor-CPU-generation-current.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Generated fixed constructor continuation blocks',len(rows))


if __name__=='__main__':main()
