"""Source-specific fullCPU formatter plus unsigned arithmetic dependencies."""
import hashlib,json,re
from pathlib import Path
import generate_biwn_display_list_cpu as frame
resource=frame.resource;base=frame.base;ROOT=frame.ROOT
RANGES=[(0x1b160,0x1b1a0),(0x1b1a8,0x1b200),(0x1b212,0x1b478),(0xe61c,0xe68c)]
old_load=resource.load
def load(text,width,name='v'):
    match=re.fullmatch(r'-\((a[0-7])\)',text)
    if match:
        reg=base.register(match[1]);step=2 if width==1 and reg==15 else width
        return f's.cpu.registers[{reg}]-={step};bank(&s);CHECK(read_value(&s,s.cpu.registers[{reg}],{width},&{name}));'
    return old_load(text,width,name)
resource.load=load;resource.ns['load']=load

def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');kind=op.split('.')[0];parts=base.split(tail);code=None;terminal=False
    if kind=='divu':
        r=base.register(parts[1]);code=[load(parts[0],2),'v&=65535u;if(!v)return BIWN_FORMATTER_CPU_DIVIDE_ZERO;',f'u=s.cpu.registers[{r}];',
            'if(u/v>65535u)return BIWN_FORMATTER_CPU_DIVIDE_OVERFLOW;',f's.cpu.registers[{r}]=((u%v)<<16)|(u/v);nz(&s,u/v,16);']
    elif kind=='addx':
        assert asm=='addx.l d0, d0';code=['u=s.cpu.registers[0];v=addx32(&s,u,u);s.cpu.registers[0]=v;']
    elif kind=='exg':
        a,b=map(base.register,parts);code=[f'v=s.cpu.registers[{a}];s.cpu.registers[{a}]=s.cpu.registers[{b}];s.cpu.registers[{b}]=v;']
    elif kind=='bsr':
        target=base.number(parts[0]);code=[f'CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc={hex(target)}u;CHECK(invoke(&s,{hex(target)}u,{hex(nxt)}u));break;'];terminal=True
    if code is None:return frame.emit(row).replace('BIWN_DISPLAY_LIST_CPU','BIWN_FORMATTER_CPU')
    if not terminal:code.append(f's.cpu.pc={hex(nxt)}u;break;')
    return f'  case {hex(pc)}u: /* {asm} */\n   '+'\n   '.join(code)
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    assert hashlib.sha256(image).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    for lo,hi in RANGES:
        assert snapshot[lo:hi]==image[lo-0x4000:hi-0x4000];rows+=base.binary_tools.m68k_instructions(snapshot[lo:hi],lo)[0]
    assert len(rows)==323
    assert snapshot[0x1b1a0:0x1b1a8]==b'(null)\0\0' and snapshot[0x1b200:0x1b212]==b'0123456789ABCDEF\0\0'
    def rename(s):return s.replace('generate_biwn_input_dispatch_cpu.py','generate_biwn_formatter_cpu.py').replace('biwn_input_dispatch_cpu','biwn_formatter_cpu').replace('biwn_dispatch_cpu_status','biwn_formatter_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_FORMATTER_CPU')
    prefix=rename(base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    helper='''static uint32_t addx32(struct dispatch *s,uint32_t a,uint32_t b){
 uint64_t sum=(uint64_t)a+b+((s->cpu.sr>>4)&1u);uint32_t v=(uint32_t)sum;
 unsigned old_z=(s->cpu.sr&4u)!=0,carry=(unsigned)(sum>>32),ov=((~(a^b))&(a^v)&0x80000000u)!=0;
 s->cpu.sr=(uint16_t)((s->cpu.sr&~0x1fu)|(v&0x80000000u?8:0)|(!v&&old_z?4:0)|(carry?0x11u:0)|(ov?2:0));return v;}
'''
    prefix=prefix.replace('static int read_value',helper+'static int read_value')
    header=rename(base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_FORMATTER_CPU_H').replace('BIWN_FORMATTER_CPU_BAD_PC=7};','BIWN_FORMATTER_CPU_BAD_PC=7,BIWN_FORMATTER_CPU_DIVIDE_ZERO=8,BIWN_FORMATTER_CPU_DIVIDE_OVERFLOW=9};')
    a=header.index('/* Static');b=header.index('enum biwn_formatter_cpu_status biwn_formatter_cpu_body',a)
    header=header[:a]+'''/* Static323sourceinstruction blocks for1B160character,1B1A8string,
 * 1B212numeric,1B29Cformat,1B45Avarargs and E61Cunsigned quotient /
 * E67Cremainder. Bothstackbanks; fullCPU/private/global scratch effects.
 * Services execute nested bodies up toRTS; body stops beforeouterRTS,
 * call consumesit. Embedded null/digit literals remainbus data.
 * No runtime instructiondecode or originalCPUcalls. Zero division and
 * DIVUoverflow are explicit hosterrors, not reproduced processor traps.
 * Source formatting is finite/bounded254characters, not hostprintf. */
'''+header[b:]
    names=['biwn_formatter_cpu.c','biwn_formatter_cpu.h'];source=ROOT/'projects/black-ice-white-noise/restoration'
    (source/names[0]).write_text(prefix+'\n'.join(emit(row)for row in rows)+'\n'+rename(base.SUFFIX));(source/names[1]).write_text(header)
    manifest=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,source_function_entries=list(map(hex,[0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a,0xe61c,0xe67c])),ranges=[[hex(a),hex(b)]for a,b in RANGES],data_intervals=[['0x1b1a0','0x1b1a8'],['0x1b200','0x1b212']],stage_sha256=hashlib.sha256(image).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},whole_game_complete=False)
    (session/'formatter-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
