"""FullCPU overlay, text/font routines and signed32 multiply dependency."""
import hashlib,json
from pathlib import Path
import generate_biwn_formatter_cpu as formatter
frame=formatter.frame;resource=formatter.resource;base=formatter.base;ROOT=formatter.ROOT
RANGES=[(0x181f8,0x18554),(0x14776,0x14800),(0x14842,0x14caa),(0xe540,0xe588)]
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');kind=op.split('.')[0];parts=base.split(tail);code=None
    if kind=='movem'and op.endswith('.w'):
        assert parts==['$4(a7)','d0-d3'];code=['u=s.cpu.registers[15]+4u;']+[f'CHECK(read_value(&s,u,2,&v));s.cpu.registers[{r}]=sx16((uint16_t)v);u+=2u;'for r in range(4)]
    elif kind=='negx':
        r=base.register(parts[0]);assert op=='negx.w';code=[f'v=negx16(&s,(uint16_t)s.cpu.registers[{r}]);put(&s,{r},2,v);']
    elif kind=='mulu':
        code=[resource.load(parts[0],2),resource.load(parts[1],2,'u'),'v=(u&65535u)*(v&65535u);',resource.store(parts[1],4),'nz(&s,v,32);']
    elif kind=='ori':
        width={'b':1,'w':2,'l':4}[op[-1]];code=[resource.load(parts[0],width),resource.load(parts[1],width,'u'),'v=u|v;',resource.store(parts[1],width),f'nz(&s,v,{width*8});']
    elif kind=='bset':
        r=base.register(parts[1]);assert r is not None and r<8 and parts[0]=='#$10'
        code=[f'v=s.cpu.registers[{r}];s.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|(v&0x10000u?0:4));s.cpu.registers[{r}]=v|0x10000u;']
    elif kind=='lsr':
        assert op=='lsr.w';count=base.number(parts[0]);r=base.register(parts[1]);assert 1<=count<=8
        code=[f'v=s.cpu.registers[{r}]&65535u;u=(v>>{count-1})&1u;v>>={count};put(&s,{r},2,v);nz(&s,v,16);s.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(u?0x11u:0));']
    if code is None:return frame.emit(row).replace('BIWN_DISPLAY_LIST_CPU','BIWN_OVERLAY_TEXT_CPU')
    code.append(f's.cpu.pc={hex(nxt)}u;break;')
    return f'  case {hex(pc)}u: /* {asm} */\n   '+'\n   '.join(code)
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    assert hashlib.sha256(image).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    for lo,hi in RANGES:
        assert snapshot[lo:hi]==image[lo-0x4000:hi-0x4000];rows+=base.binary_tools.m68k_instructions(snapshot[lo:hi],lo)[0]
    assert len(rows)==642
    def rename(s):return s.replace('generate_biwn_input_dispatch_cpu.py','generate_biwn_overlay_text_cpu.py').replace('biwn_input_dispatch_cpu','biwn_overlay_text_cpu').replace('biwn_dispatch_cpu_status','biwn_overlay_text_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_OVERLAY_TEXT_CPU')
    prefix=rename(base.PREFIX).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    helper='''static uint32_t negx16(struct dispatch *s,uint16_t a){
 uint32_t x=(s->cpu.sr>>4)&1u,v=(0u-a-x)&65535u;unsigned z=(s->cpu.sr&4u)!=0,c=(uint32_t)a+x!=0,ov=(a&v&0x8000u)!=0;
 s->cpu.sr=(uint16_t)((s->cpu.sr&~0x1fu)|(v&0x8000u?8:0)|(!v&&z?4:0)|(c?0x11u:0)|(ov?2:0));return v;}
'''
    prefix=prefix.replace('static int read_value',helper+'static int read_value')
    header=rename(base.HEADER).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_OVERLAY_TEXT_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_overlay_text_cpu_status biwn_overlay_text_cpu_body',a)
    header=header[:a]+'''/* Static642sourceinstruction blocks181F8overlay,14776alignment,
 * 147A6font3,149AEtext andE540multiply. Bothstackbanks/fullCPU/private
 * frames; original font3jumptable remainsbus data. body stops beforeRTS;
 * call consumesit. Nested helper providers execute up toRTS, including
 * separate fullCPU1B45Aformatter. No originalCPUcalls/runtimedecode.
 * Drawing device is an explicit bus provider; no scanout/fullgame proof. */
'''+header[b:]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_overlay_text_cpu.c','biwn_overlay_text_cpu.h']
    (source/names[0]).write_text(prefix+'\n'.join(emit(row)for row in rows)+'\n'+rename(base.SUFFIX));(source/names[1]).write_text(header)
    manifest=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,ranges=[[hex(a),hex(b)]for a,b in RANGES],source_function_entries=list(map(hex,[0x181f8,0x14776,0x147a6,0x149ae,0xe540])),font3_jump_table_interval=['0x14800','0x14842'],stage_sha256=hashlib.sha256(image).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},whole_game_complete=False)
    (session/'overlay-text-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
