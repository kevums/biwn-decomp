"""Fixed resident BIOS GPU IRQ1 DSA/FIFO handler with own event frame."""
import hashlib,json,subprocess
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
rename=lambda t:t.replace('gpu_geometry','gpu_cd_ISR').replace('GPU_GEOMETRY','GPU_CD_ISR')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();assert hashlib.sha256(bios).hexdigest()=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b';payload=bytearray(4096);payload[0x50:0x130]=bios[0x84a6+0xea:0x84a6+0x1ca];payload[0x10:0x1c]=bytes.fromhex('981e305c00f0d3c0e400e400');rows=[]
    for a,b in [(0xf03010,0xf0301a),(0xf0305c,0xf0312e)]:
        data=payload[a-0xf03000:b-0xf03000];decoded=subprocess.check_output([str(ROOT/'tools/jaguar-disasm/jaguar-disasm'),'gpu',hex(a)],input=data).decode().strip().splitlines()
        for line in decoded:
            pc,size,asm=line.split('\t');pc=int(pc,16);size=int(size,16);rows.append(dict(address=pc,size=size,bytes=payload[pc-0xf03000:pc-0xf03000+size].hex(),assembly=asm))
    header=rename(base.HEADER).replace('uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;','uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n uint32_t accumulator,hidata,flags,data_organization,control,active_bank;')
    a=header.index('/* Source-specific');b=header.index('enum biwn_gpu_cd_ISR_status biwn_gpu_cd_ISR_init',a);header=header[:a]+'''/* Resident BIOS GPU IRQ1 vector/DSA-FIFO handler and private return frame.
 * Fixed source blocks, own timer event/PC-2 frame, full logical state.
 * Handler uses bank0; event may enter from bank1 and return to it.
 * Source handles DSA/seek replies, enables I2S, drains FIFO into pointer/end buffer and stores progress. BaseF03050 descriptor/image only; dynamic patched/encrypted variants unverified.
 * No runtime decoder/originalGPU calls. run stops on returned originalPC.
 * Controller data/events and their delivery/scheduling remain explicit dependencies. */
'''+header[b:];a=header.index('enum biwn_gpu_cd_ISR_status biwn_gpu_cd_ISR_init');b=header.index('enum biwn_gpu_cd_ISR_status biwn_gpu_cd_ISR_run',a);header=header[:a]+header[b:];header=header.replace('struct biwn_gpu_cd_ISR_state *,uint32_t);','struct biwn_gpu_cd_ISR_state *,uint32_t,uint32_t);')
    header=header.replace('#endif','enum biwn_gpu_cd_ISR_status biwn_gpu_cd_ISR_assert(struct biwn_gpu_cd_ISR_bus *,struct biwn_gpu_cd_ISR_state *);\n#endif')
    prefix=rename(base.PREFIX);remove=('static uint32_t sx16(','static uint32_t sar(','static void divide(','static int matrix(');prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith(remove))+'\n'
    prefix=prefix.replace('if(a==0xf02104u){*v=s->matrix_control;return 0;}','if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}')
    prefix=prefix.replace('if(a==0xf02104u){s->matrix_control=v;return 0;}','if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}')
    prefix+='''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_cd_ISR_status)status;}while(0)
enum biwn_gpu_cd_ISR_status biwn_gpu_cd_ISR_run(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *state,uint32_t budget,uint32_t returnPC){struct biwn_gpu_cd_ISR_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    cases='\n'.join(rename(base.emit(r))for r in rows)
    suffix='''default:return BIWN_GPU_CD_ISR_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_CD_ISR_BAD_DELAY;s.pc=resume;}if(!pending&&s.pc==returnPC){*state=s;return 0;}}return BIWN_GPU_CD_ISR_WORK_LIMIT;}
enum biwn_gpu_cd_ISR_status biwn_gpu_cd_ISR_assert(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *state){struct biwn_gpu_cd_ISR_state s;uint32_t a;if(!bus||!state||!bus->write32||state->active_bank>1||state->z>1||state->c>1||state->n>1)return 1;s=*state;if(!(s.control&1u))return 6;s.control|=0x80u;if((s.control&8u)||(s.flags&8u)||!(s.flags&0x20u)){*state=s;return 7;}s.flags|=8u;s.active_bank=0;s.registers[0][31]-=4u;a=s.registers[0][31]&~3u;CHECK(wr32(bus,&s,a,s.pc-2u));s.pc=s.registers[0][30]=0xf03010u;*state=s;return 0;}
'''
    header=header.replace('BIWN_GPU_CD_ISR_BAD_DELAY=5','BIWN_GPU_CD_ISR_BAD_DELAY=5,BIWN_GPU_CD_ISR_HALTED=6,BIWN_GPU_CD_ISR_LATCHED=7')
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_gpu_cd_ISR.c','biwn_gpu_cd_ISR.h'];(src/names[0]).write_text(prefix+cases+suffix);(src/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,source_payload_sha256=hashlib.sha256(payload).hexdigest(),source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False,new_published_components=0);(session/'GPU-CD-ISR-C-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
