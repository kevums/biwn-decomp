"""Static fullCPU reconstruction of185B2, retaining its private link table."""
import hashlib,json,re
from pathlib import Path
import generate_biwn_resource_cpu as resource
base=resource.base;ROOT=base.ROOT
old_address=resource.ns['address']
def address(text):
    if text.startswith('-$'):
        displacement,rest=text[1:].split('(',1)
        return '('+old_address('('+rest)+'-'+hex(base.number(displacement))+'u)'
    return old_address(text)
resource.ns['address']=address
old_load=resource.load
def load(text,width,name='v'):
    if text.startswith('-$'):return f'CHECK(read_value(&s,{address(text)},{width},&{name}));'
    return old_load(text,width,name)
resource.load=load;resource.ns['load']=load

def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=base.split(tail);code=None
    if op=='link.w':
        r=base.register(parts[0]);displacement=base.number(parts[1]);code=[f'CHECK(push(&s,s.cpu.registers[{r}],4));s.cpu.registers[{r}]=s.cpu.registers[15];s.cpu.registers[15]+=sx16({hex(displacement)}u);bank(&s);']
    elif op=='unlk':
        r=base.register(parts[0]);code=[f's.cpu.registers[15]=s.cpu.registers[{r}];bank(&s);CHECK(read_value(&s,s.cpu.registers[15],4,&v));s.cpu.registers[{r}]=v;pop(&s,4);']
    elif op=='movem.l'and parts[0].startswith('-$'):
        code=['u='+address(parts[0])+';']+[f'CHECK(read_value(&s,u,4,&v));s.cpu.registers[{r}]=v;u+=4u;'for r in resource.indices(parts[1])]
    elif op=='lsr.w':
        assert asm=='lsr.w #$4, d2'
        code=['v=s.cpu.registers[2]&0xffffu;u=(v>>3)&1u;v>>=4;put(&s,2,2,v);nz(&s,v,16);s.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(u?0x11u:0));']
    if code is None:return resource.emit(row).replace('BIWN_RESOURCE_CPU','BIWN_DISPLAY_LIST_CPU')
    code.append(f's.cpu.pc={hex(nxt)}u;break;')
    return f'  case {hex(pc)}u: /* {asm} */\n   '+'\n   '.join(code)
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    assert hashlib.sha256(image).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    for lo,hi in [(0x185b2,0x18690),(0x1869a,0x18854)]:
        assert snapshot[lo:hi]==image[lo-0x4000:hi-0x4000];rows+=base.binary_tools.m68k_instructions(snapshot[lo:hi],lo)[0]
    assert len(rows)==254
    def rename(s):return s.replace('generate_biwn_input_dispatch_cpu.py','generate_biwn_display_list_cpu.py').replace('biwn_input_dispatch_cpu','biwn_display_list_cpu').replace('biwn_dispatch_cpu_status','biwn_display_list_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_DISPLAY_LIST_CPU')
    prefix=rename(base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    a=prefix.index('static int invoke(');b=prefix.index('#define CHECK',a);prefix=prefix[:a]+prefix[b:]
    header=rename(base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_DISPLAY_LIST_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_display_list_cpu_status biwn_display_list_cpu_body',a)
    header=header[:a]+'''/* Static254sourceinstruction blocks185B2displaylist. Bothstackbanks,
 * full registers/CCR and actualLINK/MOVEM/dynamicprivate link table.
 * body stops beforeRTS;call executesit. No nestedhelpers/originalCPUcalls
 * or runtime instructiondecode. Tabledata read through suppliedbus.
 * Finite valid descriptor lists/source table indices; explicit budget.
 * This alone does not execute the objectprocessor or display scanout. */
'''+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_display_list_cpu.c','biwn_display_list_cpu.h']
    (source/names[0]).write_text(prefix+'\n'.join(emit(row)for row in rows)+'\n'+rename(base.SUFFIX));(source/names[1]).write_text(header)
    manifest=dict(status='generated_unverified',instructions=254,instructions_decoded=rows,stage_sha256=hashlib.sha256(image).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},jump_table_interval=['0x18690','0x1869a'],whole_game_complete=False)
    (session/'display-list-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
