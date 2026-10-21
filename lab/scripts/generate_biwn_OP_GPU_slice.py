"""Fixed resident IRQ2/IRQ3 and dispatcher GPU slices, separate candidate."""
import json,re,hashlib,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
import generate_biwn_gpu_geometry as base
ROOT=base.ROOT
rename=lambda s:s.replace('gpu_timer','gpu_OP_slice').replace('GPU_TIMER','GPU_OP_SLICE')
def emit(row):
    word=int(row['bytes'][:4],16);op=word>>10;m=(word>>5)&31;n=word&31;pc=row['address'];nxt=pc+row['size'];M=f's.registers[s.active_bank][{m}]';N=f's.registers[s.active_bank][{n}]'
    if op==42:code=f'{{uint32_t a={M};a=local(a)?(a&~7u):a;CHECK(rd32(bus,&s,a,&v));s.hidata=v;CHECK(rd32(bus,&s,a+4u,&v));{N}=v;}}'
    elif op==48:code=f'{{uint32_t a={M}&~7u;CHECK(wr32(bus,&s,a,s.hidata));CHECK(wr32(bus,&s,a+4u,{N}));}}'
    else:return rename(base.emit(row)).replace('s.registers[0]','s.registers[s.active_bank]')
    return f'case {hex(pc)}u: /* {row["assembly"]} */\n {code}s.pc={hex(nxt)}u;break;'
def main():
    prior=json.loads((ROOT/'verification/startup-single-step-current.json').read_text());source=Path(prior['directory'])/'source';out=ROOT/'verification/OP-GPU-slice-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    payload=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0x40a8:0x4324];rows=[]
    for a,b in [(0xf03020,0xf03040),(0xf03140,0xf03200)]:
        result=subprocess.run([str(ROOT/'tools/jaguar-disasm/jaguar-disasm'),'gpu',hex(a)],input=payload[a-0xf03000:b-0xf03000],capture_output=True);assert result.returncode==0,result.stderr.decode()
        for line in result.stdout.decode().strip().splitlines():
            pc,size,asm=line.split('\t');pc=int(pc,16);size=int(size,16);rows.append(dict(address=pc,size=size,assembly=asm,bytes=payload[pc-0xf03000:pc-0xf03000+size].hex()))
    old=(source/'biwn_gpu_timer.c').read_text();prefix=rename(old[:old.index('#define CHECK')]);prefix=prefix.replace('return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u)','return 0;}if(a==0xf02104u)',1)
    header=rename((ROOT/'projects/black-ice-white-noise/restoration/biwn_gpu_timer.h').read_text());header=re.sub(r'enum biwn_gpu_OP_slice_status biwn_gpu_OP_slice_run\([^;]+;', 'enum biwn_gpu_OP_slice_status biwn_gpu_OP_slice_run(struct biwn_gpu_OP_slice_bus *,struct biwn_gpu_OP_slice_state *,uint32_t);',header)
    prefix+='''static int irq(struct biwn_gpu_OP_slice_bus *bus,struct biwn_gpu_OP_slice_state *s,uint32_t return_pc){unsigned bits,which;if(!(s->control&1u)||(s->control&8u)||(s->flags&8u))return 0;bits=((s->control>>6)&31u)&((s->flags>>4)&31u);if(!bits)return 0;which=0;while(bits>>1){bits>>=1;which++;}s->flags|=8u;s->active_bank=0;s->registers[0][31]-=4u;if(wr32(bus,s,s->registers[0][31]&~3u,return_pc-2u))return 2;s->pc=s->registers[0][30]=0xf03000u+which*16u;return 0;}
#define CHECK(e) do{int status=(e);if(status)return status;}while(0)
enum biwn_gpu_OP_slice_status biwn_gpu_OP_slice_run(struct biwn_gpu_OP_slice_bus *bus,struct biwn_gpu_OP_slice_state *state,uint32_t budget){struct biwn_gpu_OP_slice_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||state->active_bank>1)return 1;s=*state;CHECK(irq(bus,&s,s.pc));while(budget||pending){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed){budget--;if(bus->observe_PC)bus->observe_PC(bus->context,s.pc);}s.instructions++;switch(s.pc){
'''
    cases='\n'.join(emit(row)for row in rows)
    suffix='''default:return 3;}
if(delayed){if(pending)return 5;s.pc=resume;CHECK(irq(bus,&s,resume));}
if(!(s.control&1u))break;
}*state=s;return 0;}
'''
    text=prefix+cases+suffix;(out/'biwn_gpu_OP_slice.c').write_text(text);(out/'biwn_gpu_OP_slice.h').write_text(header);library=out/'libGPU-OP-slice.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/'biwn_gpu_OP_slice.c'),'-o',str(library)];result=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    report=dict(status='compiled_unverified_fixed_OP_GPU_slice',directory=str(out),library=str(library),library_sha256=hashlib.sha256(library.read_bytes()).hexdigest(),instructions_decoded=rows,source_sha256=hashlib.sha256(text.encode()).hexdigest(),coordinator_authored=True,new_training=False,limits=['Fixed resident instruction set only; requested16cycles assumed unit-cost with mandatory free delay slot, unsupported profiles unverified.','IRQ/latch and partial-slice behavior requires original-state gates; no integration or playable-game claim.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/OP-GPU-slice-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
