"""Fixed DSP media audio program, source code before its mailbox/FIFO data.

Source caller enters F1B01C; SSI vector F1B010 branches to F1B10E.
The code/data boundary is F1B138. Bank0 is the source caller's declared mode.
Generation does not verify samples, IRQs, media playback or full-game audio.
"""
import hashlib
import json
from pathlib import Path
import generate_biwn_gpu_geometry as gpu

ROOT=gpu.ROOT
HEADER='''#ifndef BIWN_DSP_MEDIA_AUDIO_H
#define BIWN_DSP_MEDIA_AUDIO_H
#include <stdint.h>
struct biwn_dsp_media_audio_state {
 uint64_t accumulator;
 uint32_t registers[2][32],pc,z,c,n,flags,control;
 uint32_t remainder,modulo,matrix_control,matrix_pointer,data_organization,division_control,instructions;
 uint8_t local_RAM[8192];
};
struct biwn_dsp_media_audio_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
enum biwn_dsp_media_audio_status {BIWN_DSP_MEDIA_AUDIO_OK=0,
 BIWN_DSP_MEDIA_AUDIO_BAD_ARGUMENT=1,BIWN_DSP_MEDIA_AUDIO_BUS_ERROR=2,
 BIWN_DSP_MEDIA_AUDIO_BAD_PC=3,BIWN_DSP_MEDIA_AUDIO_WORK_LIMIT=4,
 BIWN_DSP_MEDIA_AUDIO_BAD_DELAY=5,BIWN_DSP_MEDIA_AUDIO_STOPPED=6};
/* Fixed source program, bank0; no runtime instruction decoding/core calls.
 * step executes one source instruction and any taken-branch delay slot.
 * run stops at the source idle poll F1B074 with r27=0, or DSPGO clear.
 * ssi_interrupt supplies a declared external SSI event, with exact source
 * vector/private DSP frame; local valid stack required. Timing, other IRQs,
 * bank1 execution, peripherals and game/media integration are not supplied.
 * Errors retain earlier external writes and leave input state unchanged.
 * Code ends before mailbox/FIFO atF1B138. Stop/alignment filler is retained.
 */
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_step(struct biwn_dsp_media_audio_bus *,struct biwn_dsp_media_audio_state *);
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_run(struct biwn_dsp_media_audio_bus *,struct biwn_dsp_media_audio_state *,uint32_t);
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_ssi_interrupt(struct biwn_dsp_media_audio_state *);
#endif
'''
PREFIX='''/* Source-specific static reconstruction by generate_biwn_dsp_media_audio.py.
 * Not recovered original source. See original-DSP comparison evidence. */
#include "biwn_dsp_media_audio.h"
static void zn(struct biwn_dsp_media_audio_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_dsp_media_audio_state *s,unsigned code){unsigned f=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(f&1u))&&!((code&2u)&&!(f&1u))&&!((code&4u)&&(f&(2u<<(code>>4))))&&!((code&8u)&&!(f&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf1b000u&&a<=0xf1cfffu;}
static int rd32(struct biwn_dsp_media_audio_bus *b,struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t *v){a&=~3u;if(local(a)){*v=be32(s->local_RAM+a-0xf1b000u);return 0;}if(a==0xf1a100u){s->flags=(s->flags&~7u)|s->z|(s->c<<1)|(s->n<<2);*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf1a114u){*v=s->control;return 0;}return b->read32(b->context,a,v)?2:0;}
static int rd8(struct biwn_dsp_media_audio_bus *b,struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t *v){uint8_t x;if(local(a))return rd32(b,s,a&~3u,v);if(b->read8(b->context,a,&x))return 2;*v=x;return 0;}
static int wr32(struct biwn_dsp_media_audio_bus *b,struct biwn_dsp_media_audio_state *s,uint32_t a,uint32_t v){a&=~3u;if(local(a)){put32(s->local_RAM+a-0xf1b000u,v);return 0;}if(a==0xf1a100u){if(v&0x4000u)return 1;s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1;s->c=(s->flags>>1)&1;s->n=(s->flags>>2)&1;s->control&=~((s->flags&0x3e00u)>>3);s->control&=~((s->flags&0x20000u)>>1);return 0;}if(a==0xf1a114u){uint32_t mask=0x1f7c0u;s->control=(s->control&mask)|(v&~mask);return 0;}return b->write32(b->context,a,v)?2:0;}
static int valid(struct biwn_dsp_media_audio_state *s){return s&&s->z<=1&&s->c<=1&&s->n<=1&&!(s->flags&0x4000u);}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_dsp_media_audio_status)status;}while(0)
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_step(struct biwn_dsp_media_audio_bus *bus,struct biwn_dsp_media_audio_state *state){struct biwn_dsp_media_audio_state s;uint32_t v,target=0;unsigned pending=0,delayed=0;if(!bus||!valid(state)||!bus->read8||!bus->read32||!bus->write32)return 1;if(!(state->control&1u))return 6;s=*state;
 do{pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
SUFFIX='''default:return BIWN_DSP_MEDIA_AUDIO_BAD_PC;
 }if(delayed){if(pending)return BIWN_DSP_MEDIA_AUDIO_BAD_DELAY;s.pc=target;break;}delayed=pending;
 }while(delayed);*state=s;return 0;}
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_run(struct biwn_dsp_media_audio_bus *bus,struct biwn_dsp_media_audio_state *state,uint32_t budget){struct biwn_dsp_media_audio_state s;int status;if(!bus||!valid(state)||!budget||!bus->read8||!bus->read32||!bus->write32)return 1;s=*state;while(budget--){if(!(s.control&1u)||(s.pc==0xf1b074u&&s.registers[0][27]==0&&!(s.flags&8u))){*state=s;return 0;}status=biwn_dsp_media_audio_step(bus,&s);if(status)return(enum biwn_dsp_media_audio_status)status;}return 4;}
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_ssi_interrupt(struct biwn_dsp_media_audio_state *state){struct biwn_dsp_media_audio_state s;uint32_t sp;if(!valid(state))return 1;s=*state;s.control|=0x80u;if((s.flags&8u)||!(s.flags&0x20u)){*state=s;return 0;}sp=s.registers[0][31]-4u;if(!local(sp)||sp>0xf1cffcu)return 1;s.flags|=8u;s.registers[0][31]=sp;s.registers[0][30]=s.pc-2u;put32(s.local_RAM+(sp&~3u)-0xf1b000u,s.pc-2u);s.pc=s.registers[0][30]=0xf1b010u;*state=s;return 0;}
'''


def emit(row):
    word=int(row['bytes'][:4],16);op=word>>10;m=(word>>5)&31;n=word&31
    if op==11:
        return f'case {hex(row["address"])}u: /* {row["assembly"]} */ s.registers[0][{n}]^=s.registers[0][{m}];zn(&s,s.registers[0][{n}]);s.pc={hex(row["address"]+row["size"])}u;break;'
    if op==39:
        return f'case {hex(row["address"])}u: /* {row["assembly"]} */ CHECK(rd8(bus,&s,s.registers[0][{m}],&v));s.registers[0][{n}]=v;s.pc={hex(row["address"]+row["size"])}u;break;'
    return gpu.emit(row)


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    folder=session/'media-dsp-e840';mapping=json.loads((folder/'initial-linear-decode.json').read_text())
    payload=(folder/'original-overlay.bin').read_bytes();assert hashlib.sha256(payload).hexdigest()==mapping['payload_sha256']
    rows=[r for r in mapping['rows'] if r['address']<0xf1b138]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_dsp_media_audio.c','biwn_dsp_media_audio.h']
    (source/names[0]).write_text(PREFIX+'\n'.join(emit(row) for row in rows)+'\n'+SUFFIX)
    (source/names[1]).write_text(HEADER)
    record=dict(status='generated_unverified',source_program_bytes=384,code_interval=['0xf1b010','0xf1b138'],data_interval=['0xf1b138','0xf1b190'],
        instructions=len(rows),instructions_decoded=rows,payload_sha256=mapping['payload_sha256'],
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        shared_emitter_sha256=hashlib.sha256(Path(gpu.__file__).read_bytes()).hexdigest(),
        source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in names},
        new_published_components=0,whole_game_complete=False)
    (folder/'C-generation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='instructions_decoded'}))


if __name__=='__main__':main()
