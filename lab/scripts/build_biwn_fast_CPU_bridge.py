"""Native instruction-boundary bridge to accepted5426CPUcases, with cost-only model."""
import argparse,capstone,hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--CPU-candidate',type=Path);parser.add_argument('--candidate-output',type=Path);parser.add_argument('--CPU-private-source',type=Path);parser.add_argument('--cost-candidate',type=Path);args=parser.parse_args()
    CPU=json.loads((args.CPU_candidate or ROOT/'verification/extended-frame-CPU-candidate.json').read_text())
    if not args.CPU_candidate:
        accepted=json.loads((ROOT/'verification/extended-frame-CPU-accepted.json').read_text());assert CPU['library']==accepted['library']
    else:
        assert args.candidate_output, 'Experimental bridge must use isolated output manifest'
    assert not CPU.get('movie_privileged_event_tokens') or args.CPU_private_source, 'STOP tokens require explicit pinned private CPU bridge'
    assert not args.CPU_private_source or (args.CPU_candidate and args.candidate_output)
    cost=json.loads((args.cost_candidate or ROOT/'verification/native-cycle-cost-candidate.json').read_text());assert (ROOT/'verification/native-cycle-cost-current.json').exists()
    out=ROOT/'verification/fast-CPU-bridge-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);RAM=Path(CPU.get('instruction_RAM_source',CPU['warm_RAM_source'])).read_bytes();decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000);rows=[]
    for pc in sorted(map(lambda x:int(x,16),CPU['selected_case_sources'])):
        if pc in [0x303c,0x3042,0x304e,0x4088]:continue
        ins=next(decoder.disasm(RAM[pc:pc+24],pc,count=1));raw=RAM[pc:pc+ins.size];assert len(raw)<=22 and not ins.mnemonic.startswith('dc.')
        rows.append('{'+str(pc)+','+str(len(raw))+',{'+','.join(str(x)for x in raw)+'}},')
    source='''#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "biwn_input_dispatch_cpu.h"
struct host {void(*read_cpu)(struct biwn_task_cpu*);void(*write_cpu)(const struct biwn_task_cpu*);uint32_t(*read8)(uint32_t);uint32_t(*read16)(uint32_t);uint32_t(*read32)(uint32_t);void(*write8)(uint32_t,uint32_t);void(*write16)(uint32_t,uint32_t);void(*write32)(uint32_t,uint32_t);const uint8_t*RAM;};
struct stats {uint64_t calls,steps,HLE,retired,errors;uint32_t error_PC,error_code;};
struct identity {uint32_t PC;uint8_t size,bytes[22];};
static const struct identity identities[]={'''+''.join(rows)+'''};
extern int biwn_extended_CPU_step(struct biwn_world_bus*,struct biwn_task_cpu*,biwn_input_write8,biwn_world_cpu_service,void*);
extern int biwn_native_cycle_cost(uint16_t,const struct biwn_task_cpu*,const uint8_t*);
static struct host H;static struct stats S;static int mode;static FILE*state_file,*cost_file;
static int rd8(void*x,uint32_t a,uint8_t*p){(void)x;*p=(uint8_t)H.read8(a);return 0;}static int rd16(void*x,uint32_t a,uint16_t*p){(void)x;*p=(uint16_t)H.read16(a);return 0;}static int rd32(void*x,uint32_t a,uint32_t*p){(void)x;*p=H.read32(a);return 0;}
static int wr8(void*x,uint32_t a,uint8_t v){(void)x;H.write8(a,v);return 0;}static int wr16(void*x,uint32_t a,uint16_t v){(void)x;H.write16(a,v);return 0;}static int wr32(void*x,uint32_t a,uint32_t v){(void)x;H.write32(a,v);return 0;}
static int service(void*x,struct biwn_world_bus*b,struct biwn_task_cpu*s,uint32_t target){(void)x;(void)b;(void)s;S.errors++;S.error_PC=target;S.error_code=90;return 1;}
static struct biwn_world_bus bus={rd8,rd16,rd32,wr16,wr32,NULL,NULL,0};
static void put32(uint8_t*p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int fail(uint32_t PC,uint32_t code){S.errors++;S.error_PC=PC;S.error_code=code;return -1;}
static const struct identity*find(uint32_t PC){size_t lo=0,hi=sizeof(identities)/sizeof(identities[0]);while(lo<hi){size_t m=(lo+hi)/2;uint32_t p=identities[m].PC;if(p==PC)return &identities[m];if(p<PC)lo=m+1;else hi=m;}return NULL;}
int32_t biwn_fast_CPU_owner(uint32_t PC){struct biwn_task_cpu s;uint8_t record[78];uint16_t op;const struct identity*i;int cycles,status;unsigned r;S.calls++;if(S.errors)return -1;H.read_cpu(&s);if(s.pc!=PC)return fail(PC,91);if(state_file){for(r=0;r<16;r++)put32(record+r*4,s.registers[r]);put32(record+64,s.pc);put32(record+68,s.usp);put32(record+72,s.ssp);record[76]=(uint8_t)(s.sr>>8);record[77]=(uint8_t)s.sr;if(fwrite(record,1,78,state_file)!=78)return fail(PC,92);}if(mode==1)return 0;if(PC>0x1ffffeu)return fail(PC,93);op=((uint16_t)H.RAM[PC]<<8)|H.RAM[PC+1];cycles=biwn_native_cycle_cost(op,&s,H.RAM);if(cycles<=0)return fail(PC,94);if(PC==0x303c||PC==0x3042||PC==0x304e||PC==0x4088){if(op!=0x4e75)return fail(PC,95);s.pc=H.read32(s.registers[15]);s.registers[15]+=4;if(s.sr&0x2000)s.ssp=s.registers[15];else s.usp=s.registers[15];S.HLE++;}else{i=find(PC);if(!i||memcmp(H.RAM+PC,i->bytes,i->size))return fail(PC,96);status=biwn_extended_CPU_step(&bus,&s,wr8,service,NULL);if((status!=0&&status!=6)||S.errors)return fail(PC,100+(uint32_t)status);S.steps++;}H.write_cpu(&s);return cycles;}
void biwn_fast_CPU_retired(uint32_t PC,int32_t cycles){uint8_t r[8];S.retired++;if(cost_file){put32(r,PC);put32(r+4,(uint32_t)cycles);if(fwrite(r,1,8,cost_file)!=8)fail(PC,92);}}
int biwn_fast_CPU_begin(const struct host*h,int m,const char*state,const char*cost){if(!h||!h->read_cpu||!h->write_cpu||!h->read8||!h->read16||!h->read32||!h->write8||!h->write16||!h->write32||!h->RAM||(m!=1&&m!=2))return 1;H=*h;mode=m;memset(&S,0,sizeof(S));state_file=state?fopen(state,"wb"):NULL;cost_file=cost?fopen(cost,"wb"):NULL;if((state&&!state_file)||(cost&&!cost_file))return 2;return 0;}
const struct stats*biwn_fast_CPU_end(void){if(state_file)fclose(state_file);if(cost_file)fclose(cost_file);state_file=cost_file=NULL;return &S;}
size_t biwn_fast_CPU_host_size(void){return sizeof(struct host);}size_t biwn_fast_CPU_stats_size(void){return sizeof(struct stats);}size_t biwn_fast_CPU_cpu_size(void){return sizeof(struct biwn_task_cpu);}
'''
    private_provenance={}
    if args.CPU_private_source:
        import shutil
        private_dir=out/'pinned-CPU-headers';private_dir.mkdir()
        for name in ['cpudefs.h','sysdeps.h']:
            p=args.CPU_private_source/'src/m68000'/name
            shutil.copy2(p,private_dir/name);private_provenance[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        source='#include "pinned-CPU-headers/cpudefs.h"\n'+source
        source=source.replace('const uint8_t*RAM;};','const uint8_t*RAM;struct regstruct*CPU_private;void(*set_reg)(int,uint32_t);};')
        old='if((status!=0&&status!=6)||S.errors)return fail(PC,100+(uint32_t)status);'
        assert source.count(old)==1
        source=source.replace(old,'if((status!=0&&status!=6&&status!=10&&status!=11)||S.errors)return fail(PC,100+(uint32_t)status);')
        source=source.replace('int cycles,status;','int cycles,status=0;')
        source=source.replace('H.write_cpu(&s);return cycles;','H.write_cpu(&s);if(status==10){H.CPU_private->stopped=1;H.CPU_private->remainingCycles=0;}else if(status==11)H.set_reg(16,s.pc);return cycles;')
        source=source.replace('H=*h;mode=m;','if(!h->CPU_private||!h->set_reg)return 1;H=*h;mode=m;')
    source=source.replace('biwn_extended_CPU_step',CPU.get('function','biwn_extended_CPU_step'))
    p=out/'fast_CPU_bridge.c';p.write_text(source);library=out/'libfast-CPU-bridge.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT/'projects/black-ice-white-noise/restoration'),str(p),CPU['library'],cost['library'],'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    report=dict(status='compiled_unverified',directory=str(out),library=str(library),CPU_library=CPU['library'],cost_library=cost['library'],cost_candidate=str(args.cost_candidate.resolve())if args.cost_candidate else None,identity_count=len(rows),source_sha256=hashlib.sha256(source.encode()).hexdigest(),new_training=False,coordinator_authored=True,whole_game_complete=False)
    if args.CPU_private_source:
        report.update(private_CPU_state=True,CPU_header_sha256=private_provenance,
                      required_core_sha256=hashlib.sha256((args.CPU_private_source/'virtualjaguar_libretro.dylib').read_bytes()).hexdigest(),
                      private_state_scope='Only STOP stopped/remainingCycles fields. Privilege exception prefetch flush uses public m68k_set_reg(PC); no original opcode handler. Core unchanged.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(args.candidate_output or ROOT/'verification/fast-CPU-bridge-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
