"""Fixed firstboot GPU startup/RLE blocks observed in original execution."""
import json,hashlib,subprocess
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
rename=lambda t:t.replace('gpu_geometry','game_firstboot_GPU').replace('GPU_GEOMETRY','GAME_FIRSTBOOT_GPU')
def emit(r):
    word=int(r['bytes'][:4],16);op=word>>10;m=(word>>5)&31;n=word&31;M=f's.registers[0][{m}]';N=f's.registers[0][{n}]';lines=None
    if op==7:lines=[f'{N}-={m or 32}u;']
    if op==11:lines=[f'{N}^={M};zn(&s,{N});']
    if op==23:lines=[f'if({M}&0x80000000u){{s.c={N}>>31;{N}=(int32_t){M}<=-32?0u:{N}<<(0u-{M});}}else{{s.c={N}&1u;{N}={M}>=32?0u:{N}>>{M};}}zn(&s,{N});']
    if op==39:lines=[f'CHECK(rd8(bus,&s,{M},&v));{N}=v;']
    if op==41:lines=[f'CHECK(rd32(bus,&s,local({M})?({M}&~3u):{M},&v));{N}=v;']
    if lines is None:return rename(base.emit(r))
    return f'case {hex(r["address"])}u: /* {r["assembly"]} */\n '+'\n '.join(lines+[f's.pc={hex(r["address"]+r["size"])}u;break;'])
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);probe=json.loads((ROOT/'verification/game-firstboot-GPU-probe.json').read_text());boot=(session/'boot-payload-68000-candidate.bin').read_bytes();assert hashlib.sha256(boot).hexdigest()==probe['boot_sha256']
    image=bytes(0x200)+boot[0x188:0x95c]+bytes(4096-0x200-2004);pcs=set(probe['selected_PC']);rows=[]
    extra=subprocess.check_output([str(ROOT/'tools/jaguar-disasm/jaguar-disasm'),'gpu','0xf032aa'],input=image[0x2aa:0x32c]).decode().strip().splitlines();pcs.update(int(row.split('\t')[0],16)for row in extra)
    for pc in sorted(pcs):
        off=pc-0xf03000;w=int.from_bytes(image[off:off+2],'big');size=6 if w>>10==38 else 2
        line=subprocess.check_output([str(ROOT/'tools/jaguar-disasm/jaguar-disasm'),'gpu',hex(pc)],input=image[off:off+size]).decode().strip();address,length,asm=line.split('\t');assert int(address,16)==pc
        rows.append(dict(address=pc,size=size,bytes=image[off:off+size].hex(),assembly=asm,classification='observed startup/delay or separately selected poll/shutdown code'))
    header=rename(base.HEADER).replace(' int (*read16)', ' int (*read8)(void *,uint32_t,uint8_t *);\n int (*read16)').replace('uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;','uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n uint32_t accumulator,hidata,flags,data_organization,control,active_bank;')
    a=header.index('/* Source-specific');b=header.index('enum biwn_game_firstboot_GPU_status biwn_game_firstboot_GPU_init',a);header=header[:a]+'''/* Source game180000 loader GPU initialization/RLE/object-list plus
 * selected poll/shutdown blocks. Fixed observed code addresses, data tables
 * stay data. Supplied exact boot payload/inherited GPU/bus state. Stops at
 * caller-supplied PC. No runtime decoder or original GPU execution.
 * Frame timing/VCOUNT, CPU/BIOS/controller/complete firmware boot separate. */
'''+header[b:];a=header.index('enum biwn_game_firstboot_GPU_status biwn_game_firstboot_GPU_init');b=header.index('enum biwn_game_firstboot_GPU_status biwn_game_firstboot_GPU_run',a);header=header[:a]+header[b:];header=header.replace('struct biwn_game_firstboot_GPU_state *,uint32_t);','struct biwn_game_firstboot_GPU_state *,uint32_t,uint32_t);')
    prefix=rename(base.PREFIX);prefix='\n'.join(l for l in prefix.splitlines()if not l.startswith(('static uint32_t sx16(', 'static void divide(', 'static int matrix(')))+'\n'
    prefix=prefix.replace('if(a==0xf02104u){*v=s->matrix_control;return 0;}','if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02114u){*v=s->control;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}')
    prefix=prefix.replace('if(a==0xf02104u){s->matrix_control=v;return 0;}','if(a==0xf02114u){s->control=(s->control&0xf7c0u)|(v&~0xf7c6u);return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}')
    prefix+='''static int rd8(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t *v){uint8_t b;if(local(a))return rd32(bus,s,a&~3u,v);if(bus->read8(bus->context,a,&b))return 2;*v=b;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_game_firstboot_GPU_status)status;}while(0)
enum biwn_game_firstboot_GPU_status biwn_game_firstboot_GPU_run(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *state,uint32_t budget,uint32_t stopPC){struct biwn_game_firstboot_GPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    suffix='''default:return BIWN_GAME_FIRSTBOOT_GPU_BAD_PC;
}if(delayed){if(pending)return BIWN_GAME_FIRSTBOOT_GPU_BAD_DELAY;s.pc=resume;}if(!pending&&s.pc==stopPC){*state=s;return 0;}}return BIWN_GAME_FIRSTBOOT_GPU_WORK_LIMIT;}
'''
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_game_firstboot_GPU.c','biwn_game_firstboot_GPU.h'];(src/names[0]).write_text(prefix+'\n'.join(emit(r)for r in rows)+suffix);(src/names[1]).write_text(header)
    report=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,boot_sha256=probe['boot_sha256'],GPU_payload_sha256=probe['GPU_payload_sha256'],source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_game_complete=False)
    (session/'game-firstboot-GPU-C-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
