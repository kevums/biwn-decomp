"""Source-specific DSP bank1 mixer/SSI/timer blocks from native discovery."""
import hashlib,json
from pathlib import Path
import generate_biwn_dsp_media_audio as audio
ROOT=audio.ROOT
rename=lambda s:s.replace('biwn_dsp_media_audio','biwn_dsp_music_engine').replace('BIWN_DSP_MEDIA_AUDIO','BIWN_DSP_MUSIC_ENGINE').replace('generate_biwn_dsp_media_audio.py','generate_biwn_music_DSP_engine.py')
def emit(row):
    word=int(row['bytes'][:4],16);op,m,n=word>>10,(word>>5)&31,word&31;pc=row['address'];nxt=pc+row['size'];M=f's.registers[s.bank][{m}]';N=f's.registers[s.bank][{n}]'
    if op==36:line=f's.registers[1u-s.bank][{n}]={M};'
    elif op==46:line=f'CHECK(wr16(bus,&s,{M},{N}));'
    elif op==37:line=f'{N}=s.registers[1u-s.bank][{m}];'
    elif op==58:line=f'CHECK(rd32(bus,&s,s.registers[s.bank][14]+{M},&v));{N}=v;'
    elif op==44:line=f'CHECK(rd32(bus,&s,s.registers[s.bank][15]+{(m or 32)*4}u,&v));{N}=v;'
    elif op==50:line=f'CHECK(wr32(bus,&s,s.registers[s.bank][15]+{(m or 32)*4}u,{N}));'
    elif op==52:line=f'if(condition(&s,{n})){{pending=1;target=s.registers[s.flags_delay?s.prestore_bank:s.bank][{m}];}}'
    else:return rename(audio.emit(row)).replace('s.registers[0][','s.registers[s.bank][')
    return f'case {hex(pc)}u: /* {row["assembly"]} */ {line}s.pc={hex(nxt)}u;break;'
def main():
    probe=json.loads((ROOT/'verification/music-DSP-engine-probe.json').read_text());rows=probe['visited_rows'];sample_path=ROOT/'verification/music-DSP-sample-voice-probe.json'
    if sample_path.exists():
        sample=json.loads(sample_path.read_text());merged={r['address']:r for r in rows}
        for r in sample['visited_rows']:
            if r['address']in merged:assert merged[r['address']]['bytes']==r['bytes']
            merged[r['address']]=r
        rows=sorted(merged.values(),key=lambda r:r['address'])
    for extra_name in ['music-DSP-bootstrap-probe.json','music-command-probe.json']:
        extra=json.loads((ROOT/'verification'/extra_name).read_text());merged={r['address']:r for r in rows}
        for r in extra['visited_rows']:
            if r['address']in merged:assert merged[r['address']]['bytes']==r['bytes']
            merged[r['address']]=r
        rows=sorted(merged.values(),key=lambda r:r['address'])
    payload=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0x7248:0x8458]
    for r in rows:
        o=r['address']-0xf1b000;assert payload[o:o+r['size']].hex()==r['bytes']
    header=rename(audio.HEADER).replace(' int (*write32)(void *,uint32_t,uint32_t);',' int (*write32)(void *,uint32_t,uint32_t);\n int (*write16)(void *,uint32_t,uint16_t);').replace(' uint8_t local_RAM[8192];',' uint8_t local_RAM[8192];\n uint32_t bank,prestore_bank,flags_delay;');a=header.index('/* Fixed');b=header.index('enum biwn_dsp_music_engine_status biwn_dsp_music_engine_step',a)
    header=header[:a]+'''/* Fixed discovered bootstrap/CPU command1stop/command2reload and bank1 mixer/SSI IRQ1/timer IRQ2 blocks.
 * step uses source bank switching and branch-delay instructions, with the
 * pinned DSP flag-store retirement rule. assert_interrupt supplies declared
 * external IRQ0/1/2, including latches and source stack frame. No core calls
 * or runtime decoder. Only source discovered addresses are emitted; silent
 * startup song3BCE0/index0 is the current discovery, not complete music.
 * Physical clocks, arbitrary commands/voices/resources and fullgame remain
 * separate. Errors preserve input state with prior bus writes retained. */
'''+header[b:]
    a=header.index('enum biwn_dsp_music_engine_status biwn_dsp_music_engine_run');header=header[:a]+'''enum biwn_dsp_music_engine_status biwn_dsp_music_engine_assert_interrupt(struct biwn_dsp_music_engine_state *,uint32_t);
#endif
'''
    prefix=rename(audio.PREFIX);prefix='\n'.join(l for l in prefix.splitlines()if not l.startswith('static int rd8(')or any(int(r['bytes'][:4],16)>>10==39 for r in rows))+'\n'
    prefix=prefix.replace('static int valid(', 'static int wr16(struct biwn_dsp_music_engine_bus *b,struct biwn_dsp_music_engine_state *s,uint32_t a,uint32_t v){(void)s;if(local(a))return 1;return b->write16(b->context,a&~1u,(uint16_t)v)?2:0;}\nstatic int valid(').replace('||!bus->write32)return 1','||!bus->write32||!bus->write16)return 1')
    prefix=prefix.replace('static void zn(', 'static uint32_t sx16(uint32_t v){return (v&0x8000u)?(v|0xffff0000u):(v&0xffffu); }\nstatic uint32_t sar(uint32_t v,unsigned n){if(n>=32u)return(v&0x80000000u)?0xffffffffu:0u;return (v>>n)|((v&0x80000000u)&&n?(0xffffffffu<<(32u-n)):0u); }\nstatic void zn(')
    prefix=prefix.replace('if(v&0x4000u)return 1;', 's->prestore_bank=s->bank;s->flags_delay=2u;').replace('s->control&=~((s->flags&0x20000u)>>1);return 0;', 's->control&=~((s->flags&0x20000u)>>1);s->bank=(s->flags&8u)?0u:((s->flags>>14)&1u);return 0;')
    prefix=prefix.replace('if(a==0xf1a114u){uint32_t mask=', 'if(a==0xf1a118u){s->modulo=v;return 0;}if(a==0xf1a114u){uint32_t mask=')
    prefix=prefix.replace('&&!(s->flags&0x4000u)', '&&s->bank<=1u&&s->prestore_bank<=1u&&s->flags_delay<=2u&&s->bank==((s->flags&8u)?0u:((s->flags>>14)&1u))')
    suffix=rename(audio.SUFFIX);suffix=suffix[:suffix.index('enum biwn_dsp_music_engine_status biwn_dsp_music_engine_run')]
    suffix=suffix.replace('s.pc=target;break;', 's.pc=target;s.flags_delay=0;break;').replace(' }while(delayed);', ' if(s.flags_delay)s.flags_delay--; }while(delayed);')
    suffix+='''enum biwn_dsp_music_engine_status biwn_dsp_music_engine_assert_interrupt(struct biwn_dsp_music_engine_state *state,uint32_t irq){struct biwn_dsp_music_engine_state s;uint32_t mask,bits,sp;unsigned which=0;if(!valid(state)||(irq>2u))return 1;s=*state;mask=0x40u<<irq;s.control|=mask;if((s.flags&8u)||s.flags_delay){*state=s;return 0;}bits=((s.control>>6)&31u)&((s.flags>>4)&31u);if(!bits){*state=s;return 0;}for(unsigned i=0;i<5;i++)if(bits&(1u<<i))which=i;if(which>2u)return 1;s.flags|=8u;s.bank=0;s.flags_delay=0;s.prestore_bank=0;sp=s.registers[0][31]-4u;if(!local(sp)||sp>0xf1cffcu)return 1;s.registers[0][31]=sp;s.registers[0][30]=s.pc-2u;put32(s.local_RAM+(sp&~3u)-0xf1b000u,s.pc-2u);s.pc=s.registers[0][30]=0xf1b000u+which*16u;*state=s;return 0;}
'''
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_dsp_music_engine.c','biwn_dsp_music_engine.h'];(src/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+'\n'+suffix);(src/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,payload_sha256=hashlib.sha256(payload).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native_discovery=probe['directory'],full_music_playback_verified=False,whole_game_complete=False)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);(session/'music-DSP-engine-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
