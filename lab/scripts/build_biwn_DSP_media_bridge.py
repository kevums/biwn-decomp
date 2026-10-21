"""Fixed source DSP media kernel in a native scheduler owner; isolated candidate."""
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'media-dsp-e840/C-generation.json').read_text());owner=json.loads((ROOT/'verification/DSP-owner-experimental-candidate.json').read_text())
    out=ROOT/'verification/DSP-media-owner-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    original=ROOT/'projects/black-ice-white-noise/restoration';body=(original/'biwn_dsp_media_audio.c').read_text();header=(original/'biwn_dsp_media_audio.h').read_text()
    # Preserve actual device side effects and delayed D_FLAGS retirement.
    marker='s->control&=~((s->flags&0x20000u)>>1);return 0;';assert body.count(marker)==1
    body=body.replace(marker,'s->control&=~((s->flags&0x20000u)>>1);return b->write32(b->context,a,v)?2:0;')
    marker='s->control=(s->control&mask)|(v&~mask);return 0;';assert body.count(marker)==1
    body=body.replace(marker,'s->control=(s->control&mask)|(v&~mask);return b->write32(b->context,a,v)?2:0;')
    body='static unsigned biwn_DSP_last_operands[2];\n'+body
    for row in mapping['instructions_decoded']:
        pc=row['address'];word=int(row['bytes'][:4],16);needle='case '+hex(pc)+'u:';assert body.count(needle)==1
        body=body.replace(needle,needle+'biwn_DSP_last_operands[0]='+str((word>>5)&31)+'u;biwn_DSP_last_operands[1]='+str(word&31)+'u;')
    body+='\nvoid biwn_DSP_get_last_operands(unsigned*p){p[0]=biwn_DSP_last_operands[0];p[1]=biwn_DSP_last_operands[1];}\n'
    (out/'biwn_dsp_media_audio.c').write_text(body);(out/'biwn_dsp_media_audio.h').write_text(header)
    rows=[]
    for row in sorted(mapping['instructions_decoded'],key=lambda x:x['address']):
        data=bytes.fromhex(row['bytes']);rows.append('{'+str(row['address'])+','+str(len(data))+',{'+','.join(str(b)for b in data)+'}},')
    bridge='''#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "biwn_dsp_media_audio.h"
struct host {size_t(*save)(void*);size_t(*commit)(const void*);uint8_t(*read8)(uint32_t,uint32_t);uint32_t(*read32)(uint32_t,uint32_t);void(*write32)(uint32_t,uint32_t,uint32_t);void(*operands)(uint32_t,uint32_t);};
struct stats {uint64_t calls,owned,uncovered,errors;uint32_t error_PC,error_code;};
static struct host H;static struct stats S;static uint8_t raw[32768];
struct identity {uint32_t PC;uint8_t size,bytes[6];};
static const struct identity identities[]={'''+''.join(rows)+'''};
extern void biwn_DSP_get_last_operands(unsigned*);
static uint32_t get32(unsigned off){uint32_t v;memcpy(&v,raw+off,4);return v;}
static void set32(unsigned off,uint32_t v){memcpy(raw+off,&v,4);}
static void unpack(struct biwn_dsp_media_audio_state*s){unsigned i;memcpy(s->local_RAM,raw,8192);s->pc=get32(8192);memcpy(&s->accumulator,raw+8196,8);s->remainder=get32(8204);s->modulo=get32(8208);s->flags=get32(8212);s->matrix_control=get32(8216);s->matrix_pointer=get32(8220);s->data_organization=get32(8224);s->control=get32(8228);s->division_control=get32(8232);s->z=raw[8236];s->n=raw[8237];s->c=raw[8238];for(i=0;i<64;i++)s->registers[i/32][i%32]=get32(8239+i*4);s->instructions=0;}
static void pack(const struct biwn_dsp_media_audio_state*s){unsigned i;memcpy(raw,s->local_RAM,8192);set32(8192,s->pc);memcpy(raw+8196,&s->accumulator,8);set32(8204,s->remainder);set32(8208,s->modulo);set32(8212,s->flags);set32(8216,s->matrix_control);set32(8220,s->matrix_pointer);set32(8224,s->data_organization);set32(8228,s->control);set32(8232,s->division_control);raw[8236]=(uint8_t)s->z;raw[8237]=(uint8_t)s->n;raw[8238]=(uint8_t)s->c;for(i=0;i<64;i++)set32(8239+i*4,s->registers[i/32][i%32]);raw[8495]=0;}
static int rd8(void*x,uint32_t a,uint8_t*v){(void)x;*v=H.read8(a,2);return 0;}
static int rd32(void*x,uint32_t a,uint32_t*v){(void)x;*v=H.read32(a,2);return 0;}
static int wr32(void*x,uint32_t a,uint32_t v){(void)x;H.write32(a,v,2);return 0;}
static struct biwn_dsp_media_audio_bus B={rd8,rd32,wr32,NULL,NULL};
static const struct identity*find(uint32_t pc){size_t lo=0,hi=sizeof(identities)/sizeof(identities[0]);while(lo<hi){size_t m=(lo+hi)/2;if(identities[m].PC==pc)return &identities[m];if(identities[m].PC<pc)lo=m+1;else hi=m;}return NULL;}
static int fail(uint32_t pc,uint32_t code){S.errors++;S.error_PC=pc;S.error_code=code;return -1;}
int biwn_DSP_media_owner(uint32_t pc,uint16_t opcode,uint32_t unsupported){const struct identity*i;struct biwn_dsp_media_audio_state s;unsigned operands[2];int status;size_t n;S.calls++;if(S.errors)return -1;i=find(pc);if(!i){S.uncovered++;return 0;}if(unsupported)return fail(pc,100+unsupported);n=H.save(raw);if(n<8496||n>sizeof(raw)||raw[8495])return fail(pc,91);if(pc<0xf1b000u||pc+i->size>0xf1d000u||memcmp(raw+pc-0xf1b000u,i->bytes,i->size))return fail(pc,92);if((opcode>>10)==52||(opcode>>10)==53){const struct identity*d=find(pc+2u);if(!d||memcmp(raw+pc+2u-0xf1b000u,d->bytes,d->size))return fail(pc,93);}unpack(&s);status=biwn_dsp_media_audio_step(&B,&s);if(status)return fail(pc,200+(uint32_t)status);if(s.instructions<1||s.instructions>2)return fail(pc,94);pack(&s);if(H.commit(raw)!=8496)return fail(pc,95);biwn_DSP_get_last_operands(operands);H.operands(operands[0],operands[1]);S.owned+=s.instructions;return(int)s.instructions;}
int biwn_DSP_media_begin(const struct host*h){if(!h||!h->save||!h->commit||!h->read8||!h->read32||!h->write32||!h->operands)return 1;H=*h;memset(&S,0,sizeof(S));return 0;}
const struct stats*biwn_DSP_media_stats(void){return &S;}
size_t biwn_DSP_media_host_size(void){return sizeof(struct host);}size_t biwn_DSP_media_stats_size(void){return sizeof(struct stats);}size_t biwn_DSP_media_state_size(void){return sizeof(struct biwn_dsp_media_audio_state);}
'''
    (out/'DSP_media_bridge.c').write_text(bridge);library=out/'libDSP-media-owner.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/'DSP_media_bridge.c'),str(out/'biwn_dsp_media_audio.c'),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    proof={'status':'compiled_pending_owned_normal_DSP_audio_comparison','directory':str(out),'library':str(library),'required_core_sha256':owner['core_sha256'],'source_sha256':hashlib.sha256(body.encode()).hexdigest(),'bridge_sha256':hashlib.sha256(bridge.encode()).hexdigest(),'DSP_device_side_effects_retained':True,'private_retirement_state_preserved':True,'whole_game_complete':False}
    (ROOT/'verification/DSP-media-owner-experimental-candidate.json').write_text(json.dumps(proof,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
