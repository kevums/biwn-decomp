"""Static C blocks observed in six real first-frame movie GPU command traces.

Only execution-proven code addresses and mandatory delays are generated.
Unobserved entries fail BAD_PC; no linear-decoded data is called code.
"""
import json,hashlib,subprocess
from pathlib import Path
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
def rename(s):return s.replace('gpu_geometry','movie_GPU').replace('GPU_GEOMETRY','MOVIE_GPU')
def main():
    report=json.loads((ROOT/'verification/BIWN-original-movie-frames.json').read_text());directory=Path(report['directory']);fixtures=json.loads((directory/'fixtures.json').read_text())
    relocation=json.loads((ROOT/'verification/BIWN-movie-GPU-original.json').read_text());image=(Path(relocation['directory'])/'relocated-GPU.bin').read_bytes()[:4096]
    pcs=set()
    for f in fixtures:
        for key in ['codebook','frame']:
            for command in f[key]['GPU_commands']:
                for step in command['PC_sequence']:
                    pc=step['pc'];pcs.add(pc);word=int(step['bytes'][:4],16)
                    assert image[pc-0xf03000:pc-0xf03000+len(bytes.fromhex(step['bytes']))].hex()==step['bytes']
                    if word>>10 in [52,53] and step['after_pc']!=pc+2:pcs.add(pc+2)
    rows=[];decoder=ROOT/'tools/jaguar-disasm/jaguar-disasm'
    for pc in sorted(pcs):
        off=pc-0xf03000;word=int.from_bytes(image[off:off+2],'big');size=6 if word>>10==38 else 2;data=image[off:off+size]
        result=subprocess.run([str(decoder),'gpu',hex(pc)],input=data,capture_output=True);assert result.returncode==0,result.stderr
        address,length,assembly=result.stdout.decode().strip().split('\t');assert int(address,16)==pc and int(length,16)==size
        rows.append(dict(address=pc,size=size,bytes=data.hex(),assembly=assembly,classification='native execution or mandatory branch delay'))
    header=rename(base.HEADER).replace(' int (*read16)', ' int (*read8)(void *,uint32_t,uint8_t *);\n int (*read16)')
    header=header.replace(' int (*write16)(void *,uint32_t,uint16_t);\n','')
    header=header.replace('uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;','uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;\n uint32_t accumulator,hidata,flags,data_organization,control,active_bank;')
    a=header.index('/* Source-specific');b=header.index('enum biwn_movie_GPU_status biwn_movie_GPU_init',a)
    header=header[:a]+'''/* Execution-proven blocks from six first real movie frames, bank0.
 * Relocated source image must already be installed; caller supplies exact
 * inherited banks/flags/local RAM and actual command parameters. Stops at
 * idle F032C8 after command flag clears. No runtime decoding/original GPU
 * calls. Unobserved PCs fail explicitly; no complete-program claim.
 * Core bus callback supplies external memory and GPU CPU-interrupt signal.
 * External LOAD preserves source byte address; local LOAD aligns32bit.
 * LOADB in local RAM returns the whole32bit word, as source hardware does.
 * Taken branches execute their delay; trace reports outer instruction PCs.
 * Host errors retain prior external writes and leave input state unchanged.
 * Timing, CPU wrapper/IRQ and whole movie/game remain separate. */
''' + header[b:]
    a=header.index('enum biwn_movie_GPU_status biwn_movie_GPU_init');b=header.index('enum biwn_movie_GPU_status biwn_movie_GPU_run',a);header=header[:a]+header[b:]
    prefix=rename(base.PREFIX)
    prefixes=('static uint32_t sx16(', 'static uint32_t sar(', 'static int wr16(', 'static void divide(', 'static int matrix(')
    prefix='\n'.join(line for line in prefix.splitlines() if not line.startswith(prefixes))+'\n'
    prefix=prefix.replace('if(a==0xf02104u){*v=s->matrix_control;return 0;}', 'if(a==0xf02114u){*v=s->control;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}')
    prefix=prefix.replace('if(a==0xf02104u){s->matrix_control=v;return 0;}', 'if(a==0xf02114u){s->control=(s->control&0xf7c0u)|(v&~0xf7c6u);return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}')
    prefix+='''static int rd8(struct biwn_movie_GPU_bus *b,struct biwn_movie_GPU_state *s,uint32_t a,uint32_t *v){uint8_t x;if(a>=0xf03000u&&a<=0xf03fffu)return rd32(b,s,a&~3u,v);if(b->read8(b->context,a,&x))return 2;*v=x;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_movie_GPU_status)status;}while(0)
enum biwn_movie_GPU_status biwn_movie_GPU_run(struct biwn_movie_GPU_bus *bus,struct biwn_movie_GPU_state *state,uint32_t budget){struct biwn_movie_GPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''
    cases=[]
    for row in rows:
        word=int(row['bytes'][:4],16);op=word>>10;m=(word>>5)&31;n=word&31;M=f's.registers[0][{m}]';N=f's.registers[0][{n}]';lines=None
        if op==29:
            count=m&31;lines=[f'v={N};s.c=v>>31;{N}=(v>>{count})|(v<<{(-count)&31});zn(&s,{N});']
        elif op==39:lines=[f'CHECK(rd8(bus,&s,{M},&v));{N}=v;']
        elif op==41:lines=[f'CHECK(rd32(bus,&s,local({M})?({M}&~3u):{M},&v));{N}=v;']
        elif op==58:lines=[f'{{uint32_t a=s.registers[0][14]+{M};CHECK(rd32(bus,&s,local(a)?(a&~3u):a,&v));{N}=v;}}']
        if lines is None:cases.append(rename(base.emit(row)));continue
        lines.append(f's.pc={hex(row["address"]+row["size"])}u;break;');cases.append(f'case {hex(row["address"])}u: /* {row["assembly"]} */\n '+'\n '.join(lines))
    suffix='''default:return BIWN_MOVIE_GPU_BAD_PC;
}if(delayed){if(pending)return BIWN_MOVIE_GPU_BAD_DELAY;s.pc=resume;}if(s.pc==0xf032c8u&&be32(s.local_RAM+0x9f0)==0){*state=s;return 0;}}return BIWN_MOVIE_GPU_WORK_LIMIT;}
'''
    source=ROOT/'projects/black-ice-white-noise/restoration';files=['biwn_movie_GPU.c','biwn_movie_GPU.h']
    (source/files[0]).write_text(prefix+'\n'.join(cases)+'\n'+suffix);(source/files[1]).write_text(header)
    record=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,observed_first_frames=6,source_native_report=str(ROOT/'verification/BIWN-original-movie-frames.json'),relocated_RAM_sha256=sha(image),
        generator_sha256=sha(Path(__file__).read_bytes()),source_sha256={n:sha((source/n).read_bytes()) for n in files},unobserved_PC_behavior='BAD_PC; no runtime decoder or silent fallback',whole_game_complete=False,new_published_components=0)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);save=session/'media-video-gpu-21ea0/first-frames-C-generation.json';save.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='instructions_decoded'}))

sha=lambda b:hashlib.sha256(b).hexdigest()
if __name__=='__main__':main()
