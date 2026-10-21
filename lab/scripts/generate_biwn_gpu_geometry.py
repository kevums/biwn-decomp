"""Build-time fixed GPU4D80 C blocks. No runtime opcode decoding or core calls."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HEADER='''#ifndef BIWN_GPU_GEOMETRY_H
#define BIWN_GPU_GEOMETRY_H
#include <stdint.h>
struct biwn_gpu_geometry_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_geometry_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_geometry_status {BIWN_GPU_GEOMETRY_OK=0,
 BIWN_GPU_GEOMETRY_BAD_ARGUMENT=1,BIWN_GPU_GEOMETRY_BUS_ERROR=2,
 BIWN_GPU_GEOMETRY_BAD_PC=3,BIWN_GPU_GEOMETRY_WORK_LIMIT=4,
 BIWN_GPU_GEOMETRY_BAD_DELAY=5};
/* Source-specific GPU4D80 program,434 fixed instructions and source data.
 * No runtime opcode decoding or originalGPU/core calls. init supplies the
 * checked bank0 entry/mailboxes/divider mode and register seed. Optional
 * initialRAM supplies4096bytes of otherwise untouched localRAM; NULL fillsFF.
 * run stops
 * at dispatcher returnF031BE; executes mandatory branch delay slots.
 * Full integer registers/flags/localRAM and external memory effects.
 * No dispatcher acknowledgement, interrupts, bank switching or timing.
 * Budget/bus errors retain prior external stores, leave inputstate unchanged.
 * Valid finite source buffers required; this alone is no full viewport. */
enum biwn_gpu_geometry_status biwn_gpu_geometry_init(struct biwn_gpu_geometry_state *,uint32_t,const uint8_t *);
enum biwn_gpu_geometry_status biwn_gpu_geometry_run(struct biwn_gpu_geometry_bus *,struct biwn_gpu_geometry_state *,uint32_t);
#endif
'''
PREFIX='''/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_gpu_geometry.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_geometry.h"
#include <string.h>
static uint32_t sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_gpu_geometry_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_geometry_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
static void divide(struct biwn_gpu_geometry_state *s,unsigned m,unsigned n){uint32_t q=s->registers[0][n],r=0,d=s->registers[0][m];unsigned i;if(s->division_control&1u){r=q>>16;q<<=16;}for(i=0;i<32;i++){uint32_t sign=r&0x80000000u;r=(r<<1)|(q>>31);r+=sign?d:0u-d;q=(q<<1)|((~r)>>31);}s->registers[0][n]=q;s->remainder=r;}
static int matrix(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,unsigned m,unsigned n){unsigned i,count=s->matrix_control&15u;uint32_t a=s->matrix_pointer,v;int64_t sum=0;for(i=0;i<count;i++){uint32_t packed=s->registers[1][m+(i>>1)];int32_t x=(int32_t)sx16(packed>>(i&1u?16:0));int status=rd16(bus,s,a+2,&v);if(status)return status;sum+=(int64_t)x*(int32_t)sx16(v);a+=(s->matrix_control&16u)?4u*count:4u;}s->registers[0][n]=(uint32_t)sum;zn(s,(uint32_t)sum);return 0;}
'''

def emit(row):
    pc=row['address'];data=bytes.fromhex(row['bytes']);word=int.from_bytes(data[:2],'big');op=word>>10;m=(word>>5)&31;n=word&31;imm=m or 32
    M=f's.registers[0][{m}]';N=f's.registers[0][{n}]';nxt=pc+row['size'];lines=[]
    if op==0:lines=[f'{N}=add(&s,{N},{M});']
    elif op==2:lines=[f'{N}=add(&s,{N},{imm}u);']
    elif op==3:lines=[f'{N}+={imm}u;']
    elif op==4:lines=[f'{N}=sub(&s,{N},{M});']
    elif op==6:lines=[f'{N}=sub(&s,{N},{imm}u);']
    elif op==8:lines=[f'{N}=sub(&s,0,{N});']
    elif op in [9,10]:lines=[f'{N}'+('&='if op==9 else'|=')+f'{M};',f'zn(&s,{N});']
    elif op==13:lines=[f's.z=((~{N})>>{m})&1u;']
    elif op in [14,15]:lines=[f'{N}'+('|='if op==14 else'&=~')+f'(1u<<{m});',f'zn(&s,{N});']
    elif op in [16,17]:
        expr=f'({N}&0xffffu)*({M}&0xffffu)'if op==16 else f'(uint32_t)((int64_t)(int32_t)sx16({N})*(int32_t)sx16({M}))'
        lines=[f'{N}={expr};',f'zn(&s,{N});']
    elif op==21:lines=[f'divide(&s,{m},{n});']
    elif op==22:lines=[f's.c={N}>>31;if({N}==0x80000000u){{s.n=1;s.z=0;}}else{{if(s.c){N}=0u-{N};s.n=0;s.z={N}==0;}}']
    elif op==24:lines=[f's.c={N}>>31;{N}='+('0'if 32-m==32 else f'{N}<<{32-m}')+f';zn(&s,{N});']
    elif op==25:lines=[f's.c={N}&1u;{N}='+('0'if imm==32 else f'{N}>>{imm}')+f';zn(&s,{N});']
    elif op==27:lines=[f's.c={N}&1u;{N}=sar({N},{imm});zn(&s,{N});']
    elif op==30:lines=[f'(void)sub(&s,{N},{M});']
    elif op==31:lines=[f'(void)sub(&s,{N},{hex(m if m<16 else (m-32)&0xffffffff)}u);']
    elif op==34:lines=[f'{N}={M};']
    elif op==35:lines=[f'{N}={m}u;']
    elif op==36:lines=[f's.registers[1][{n}]={M};']
    elif op==38:
        value=int.from_bytes(data[2:4],'big')|(int.from_bytes(data[4:6],'big')<<16);lines=[f'{N}={hex(value)}u;']
    elif op==40:lines=[f'CHECK(loadw(bus,&s,{M},&v));{N}=v;']
    elif op==41:lines=[f'CHECK(rd32(bus,&s,{M}&~3u,&v));{N}=v;']
    elif op==46:lines=[f'CHECK(wr16(bus,&s,{M},{N}));']
    elif op==47:lines=[f'CHECK(wr32(bus,&s,local({M})?({M}&~3u):{M},{N}));']
    elif op==51:lines=[f'{N}={hex(pc)}u;']
    elif op in [52,53]:
        target=M if op==52 else hex((pc+2+2*(m if m<16 else m-32))&0xffffffff)+'u'
        lines=[f'if(condition(&s,{n})){{pending=1;target={target};}}']
    elif op==54:lines=[f'CHECK(matrix(bus,&s,{m},{n}));']
    elif op==57:lines=[]
    else:raise ValueError(row)
    lines += [f's.pc={hex(nxt)}u;break;']
    return f'  case {hex(pc)}u: /* {row["assembly"]} */\n   '+'\n   '.join(lines)

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);folder=session/'gpu-geometry-overlay';mapping=json.loads((folder/'initial-linear-decode.json').read_text());probe=json.loads((folder/'original-probe-current.json').read_text());payload=(folder/'original-overlay.bin').read_bytes()
    assert hashlib.sha256(payload).hexdigest()==mapping['payload_sha256']=='b68e6bbe4208ceabd8be44e7b92cae57762ba910f993e2dbc2862eee37206def'
    assert probe['observed_instruction_addresses']==434
    rows=[r for r in mapping['rows']if r['address']<0xf03634];assert len(rows)==434
    bytearray='static const uint8_t source_image[1360]={\n'+',\n'.join(','.join(hex(x)for x in payload[i:i+24])for i in range(0,len(payload),24))+'\n};\n'
    init='''enum biwn_gpu_geometry_status biwn_gpu_geometry_init(struct biwn_gpu_geometry_state *s,uint32_t seed,const uint8_t *initial_RAM){unsigned i;if(!s)return 1;memset(s,0,sizeof(*s));if(initial_RAM)memcpy(s->local_RAM,initial_RAM,4096);else memset(s->local_RAM,0xff,4096);memcpy(s->local_RAM+0x240,source_image,1360);for(i=0;i<32;i++){seed=1664525u*seed+1013904223u;s->registers[0][i]=seed;s->registers[1][i]=~seed;}put32(s->local_RAM+0x20c,0x47b88);put32(s->local_RAM+0x210,0x49b8c);put32(s->local_RAM+0x214,0x49bb4);put32(s->local_RAM+0x218,0x49b88);s->division_control=0xa5a50001u;s->pc=0xf03240;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_geometry_status)status;}while(0)
enum biwn_gpu_geometry_status biwn_gpu_geometry_run(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *state,uint32_t budget){struct biwn_gpu_geometry_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    suffix='''  default:return BIWN_GPU_GEOMETRY_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_GEOMETRY_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_GEOMETRY_OK;}}return BIWN_GPU_GEOMETRY_WORK_LIMIT;}
'''
    text=PREFIX+bytearray+init+'\n'.join(emit(r)for r in rows)+'\n'+suffix;source=ROOT/'projects/black-ice-white-noise/restoration';(source/'biwn_gpu_geometry.c').write_text(text);(source/'biwn_gpu_geometry.h').write_text(HEADER)
    manifest=dict(status='generated_unverified',instructions=434,source_interval=['0xf03240','0xf03634'],payload_bytes=1360,payload_sha256=mapping['payload_sha256'],generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_gpu_geometry.c','biwn_gpu_geometry.h']},instructions_decoded=rows,whole_game_complete=False)
    (folder/'C-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
