"""Fixed music-loader init and command2 acknowledgement source blocks."""
import hashlib,json
from pathlib import Path
import generate_biwn_dsp_media_audio as audio
ROOT=audio.ROOT
def rename(s):return s.replace('biwn_dsp_media_audio','biwn_dsp_music_bootstrap').replace('BIWN_DSP_MEDIA_AUDIO','BIWN_DSP_MUSIC_BOOTSTRAP').replace('generate_biwn_dsp_media_audio.py','generate_biwn_music_DSP_bootstrap.py')
def main():
    probe=json.loads((ROOT/'verification/music-DSP-bootstrap-probe.json').read_text());rows=probe['visited_rows'];ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();payload=ram[0x7248:0x8458];assert hashlib.sha256(payload).hexdigest()==probe['original_source_payload_sha256']
    for r in rows:
        o=r['address']-0xf1b000;assert payload[o:o+r['size']].hex()==r['bytes']
    header=rename(audio.HEADER).replace(' int (*write32)(void *,uint32_t,uint32_t);',' int (*write32)(void *,uint32_t,uint32_t);\n int (*write16)(void *,uint32_t,uint16_t);')
    a=header.index('/* Fixed');b=header.index('enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_step',a)
    header=header[:a]+'''/* Source F1B126 flag/register bootstrap to F1B144 idle, and CPU IRQ0
 * command2 handler to F1B148 (before the music engine starts).
 * Bank0 only; source command2 and valid song/resource tables required.
 * boundary run accepts stopPC F1B144/F1B148; own cpu_interrupt models
 * enabled IRQ0 at the idle boundary. No runtime decoder/original DSP.
 * Source SSI/music mixer/bank1 engine/other commands, actual CPU/DSP
 * interleaving period and full boot/audio are not implemented here. */
'''+header[b:]
    header=header.replace('struct biwn_dsp_music_bootstrap_state *,uint32_t);','struct biwn_dsp_music_bootstrap_state *,uint32_t,uint32_t);').replace('biwn_dsp_music_bootstrap_ssi_interrupt','biwn_dsp_music_bootstrap_cpu_interrupt')
    prefix=rename(audio.PREFIX).replace('||!bus->write32)return 1','||!bus->write32||!bus->write16)return 1')
    prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith('static int rd8('))+'\n'
    position=prefix.index('static int valid(')
    prefix=prefix[:position]+'''static int wr16(struct biwn_dsp_music_bootstrap_bus *b,struct biwn_dsp_music_bootstrap_state *s,uint32_t a,uint32_t v){(void)s;if(local(a))return 1;return b->write16(b->context,a&~1u,(uint16_t)v)?2:0;}
'''+prefix[position:]
    emitted=[]
    for row in rows:
        word=int(row['bytes'][:4],16);op=word>>10
        emitted.append(rename(audio.gpu.emit(row)if op==46 else audio.emit(row)))
    suffix=rename(audio.SUFFIX);suffix=suffix[:suffix.index('enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_run')]+'''enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_run(struct biwn_dsp_music_bootstrap_bus *bus,struct biwn_dsp_music_bootstrap_state *state,uint32_t budget,uint32_t stopPC){struct biwn_dsp_music_bootstrap_state s;int status;if(!bus||!valid(state)||!budget||!bus->read8||!bus->read32||!bus->write32||!bus->write16||(stopPC!=0xf1b144u&&stopPC!=0xf1b148u))return 1;s=*state;while(budget--){if(s.pc==stopPC){*state=s;return 0;}status=biwn_dsp_music_bootstrap_step(bus,&s);if(status)return(enum biwn_dsp_music_bootstrap_status)status;}return 4;}
enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_cpu_interrupt(struct biwn_dsp_music_bootstrap_state *state){struct biwn_dsp_music_bootstrap_state s;uint32_t sp;if(!valid(state)||state->pc!=0xf1b144u||!(state->control&1u)||(state->flags&8u)||!(state->flags&0x10u))return 1;s=*state;s.control|=0x40u;s.flags|=8u;sp=s.registers[0][31]-4u;if(!local(sp)||sp>0xf1cffcu)return 1;s.registers[0][31]=sp;s.registers[0][30]=s.pc-2u;put32(s.local_RAM+(sp&~3u)-0xf1b000u,s.pc-2u);s.pc=s.registers[0][30]=0xf1b000u;*state=s;return 0;}
'''
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_dsp_music_bootstrap.c','biwn_dsp_music_bootstrap.h'];(src/names[0]).write_text(prefix+'\n'.join(emitted)+'\n'+suffix);(src/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,payload_sha256=hashlib.sha256(payload).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native_discovery=probe['directory'],whole_game_complete=False,full_DSP_music_program=False)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);(session/'music-DSP-bootstrap-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
