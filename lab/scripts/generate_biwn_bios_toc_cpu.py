"""Actual resident BIOS305A/3742 TOC collector and390E DSA helper."""
import hashlib,json,re
from pathlib import Path
import generate_biwn_bios_mode_cpu as mode
entry=mode.entry;ROOT=entry.ROOT;resource=entry.loader.resource
rename=lambda s:s.replace('biwn_bios_mode_cpu','biwn_bios_toc_cpu').replace('BIWN_BIOS_MODE_CPU','BIWN_BIOS_TOC_CPU')
old_load=resource.load
def load(text,width,name='v'):
    match=re.fullmatch(r'-\((a[0-7])\)',text)
    if match:
        r=entry.loader.base.register(match[1]);step=2 if width==1 and r==15 else width
        return f's.cpu.registers[{r}]-={step}u;bank(&s);CHECK(read_value(&s,s.cpu.registers[{r}],{width},&{name}));'
    return old_load(text,width,name)
resource.load=load;resource.ns['load']=load

def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=entry.loader.base.split(tail);base=op.split('.')[0];code=None
    if base=='lsr' and op=='lsr.w':
        count=entry.loader.base.number(parts[0]);r=entry.loader.base.register(parts[1]);assert 1<=count<=8
        code=[f'v=s.cpu.registers[{r}]&0xffffu;u=(v>>{count-1})&1u;v>>={count};put(&s,{r},2,v);nz(&s,v,16);s.cpu.sr=(uint16_t)((s.cpu.sr&~0x13u)|(u?0x11u:0));']
    elif base=='ror':
        width=2 if op.endswith('.w')else 4;bits=width*8;mask=0xffff if width==2 else 0xffffffff;r=entry.loader.base.register(parts[1]);count=entry.loader.base.number(parts[0]);assert count==8
        code=[f'v=s.cpu.registers[{r}]&{hex(mask)}u;v=((v>>8)|(v<<{bits-8}))&{hex(mask)}u;put(&s,{r},{width},v);nz(&s,v,{bits});s.cpu.sr=(uint16_t)((s.cpu.sr&~1u)|((v>>{bits-1})&1u));']
    elif base=='subx':
        assert op=='subx.b';source=entry.loader.base.register(parts[0]);dest=entry.loader.base.register(parts[1]);assert source<8 and dest<8
        code=[f'{{uint32_t a=s.cpu.registers[{dest}]&255u,b=s.cpu.registers[{source}]&255u,x=(s.cpu.sr>>4)&1u,z=s.cpu.sr&4u;int32_t signed_result=(int32_t)(int8_t)a-(int32_t)(int8_t)b-(int32_t)x;v=(a-b-x)&255u;s.cpu.sr=(uint16_t)((s.cpu.sr&~31u)|((b+x>a)?17u:0u)|((v&128u)?8u:0u)|((!v&&z)?4u:0u)|((signed_result< -128||signed_result>127)?2u:0u));put(&s,{dest},1,v);}}']
    elif base=='subi':return rename(mode.emit({**row,'assembly':asm.replace('subi.','sub.',1)}))
    if code is None:return rename(mode.emit(row))
    return f'case {hex(pc)}u: /* {asm} */\n '+'\n '.join(code)+f's.cpu.pc={hex(nxt)}u;break;'
def main():
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();assert hashlib.sha256(bios).hexdigest()=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b';resident=bios[0x84a6:0x92a6];rows=[]
    for a,b in [(0x305a,0x305e),(0x3742,0x3954)]:rows+=entry.loader.base.binary_tools.m68k_instructions(resident[a-0x3000:b-0x3000],a)[0]
    prefix=rename(mode.rename(entry.rename(entry.loader.base.PREFIX))).replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','');a=prefix.index('static void shift(');b=prefix.index('static int read_value(',a);prefix=prefix[:a]+prefix[b:]
    header=rename(mode.rename(entry.rename(entry.loader.base.HEADER))).replace('BIWN_INPUT_DISPATCH_CPU_H','BIWN_BIOS_TOC_CPU_H');a=header.index('/* Static');b=header.index('enum biwn_bios_toc_cpu_status biwn_bios_toc_cpu_body',a)
    header=header[:a]+'''/* Actual BIOS305A TOC collection with390E DSA helper. Source clears
 * caller1KB, reads session/track tagged replies, computes MSF lengths,
 * preserves MOVEM/private BSR frames and reports3E00 status. Caller
 * supplies writable1KB and firmware image; bus supplies responses/timing.
 * Fixed source blocks, no runtime decoding/original CPU calls. Body
 * stops before outerRTS; call consumes it. Firmware boot separate. */
'''+header[b:]
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_bios_toc_cpu.c','biwn_bios_toc_cpu.h'];(src/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+'\n'+rename(mode.rename(entry.rename(entry.loader.base.SUFFIX))));(src/names[1]).write_text(header);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,BIOS_sha256=hashlib.sha256(bios).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False);(session/'bios-toc-fullCPU-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
