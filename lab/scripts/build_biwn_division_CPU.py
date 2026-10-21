"""Isolated fixed-division provider and cost repair; no running/default changes."""
import argparse,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from check_biwn_division_CPU import inventory
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--review',type=Path,required=True);args=parser.parse_args()
    review=json.loads(args.review.read_text());source=Path(review['source'])
    assert review['status']=='coordinator_reviewed_local_divzero_C_for_compile' and sha(source)==review['source_sha256']
    parentp=ROOT/'verification/native-formatter-C-bridge-current.json';parent=json.loads(parentp.read_text());cp=Path(parent['CPU_candidate']);candidate=json.loads(cp.read_text());atlas,entries=inventory(candidate)
    out=ROOT/'verification/CPU-division-provider-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    text='''#include "biwn_input_dispatch_cpu.h"
extern int biwn_divzero_entry(struct biwn_world_bus*,struct biwn_task_cpu*,uint32_t);
extern int biwn_native_formatter_wait_C_step(struct biwn_world_bus*,struct biwn_task_cpu*,biwn_input_write8,biwn_world_cpu_service,void*);
static int divide(struct biwn_world_bus*b,struct biwn_task_cpu*cpu,uint16_t operand,unsigned target,unsigned sign,uint32_t resume){
 struct biwn_task_cpu next=*cpu;uint32_t dividend=next.registers[target],packed;int overflow;
 if(!operand)return biwn_divzero_entry(b,cpu,resume);
 if(sign){int64_t a=(dividend&0x80000000u)?(int64_t)dividend-4294967296LL:(int64_t)dividend;
  int64_t divisor=(operand&0x8000u)?(int64_t)operand-65536:(int64_t)operand;
  int64_t q=a/divisor,r=a%divisor;overflow=q< -32768||q>32767;
  packed=((uint32_t)(uint16_t)r<<16)|(uint16_t)q;
 }else{uint32_t q=dividend/operand,r=dividend%operand;overflow=q>65535u;packed=(r<<16)|(q&65535u);}
 if(overflow)next.sr=(uint16_t)((next.sr&~11u)|10u);
 else{uint16_t q=(uint16_t)packed;next.registers[target]=packed;next.sr=(uint16_t)((next.sr&0xfff0u)|(q==0?4u:0u)|(q&0x8000u?8u:0u));}
 next.pc=resume;*cpu=next;return 0;
}
int biwn_division_checked_CPU_step(struct biwn_world_bus*b,struct biwn_task_cpu*s,biwn_input_write8 w,biwn_world_cpu_service service,void*context){
 uint16_t operand=0;if(!b||!s)return 1;(void)operand;switch(s->pc){
'''
    for row in entries:
        text+='case '+hex(row['pc'])+'u: /* '+row['assembly']+' */\n'
        if row['operand_kind']=='register':text+='operand=(uint16_t)s->registers['+str(row['operand'])+'];\n'
        elif row['operand_kind']=='immediate':text+='operand='+str(row['operand'])+'u;\n'
        else:text+='if(!b->read16)return 1;if(b->read16(b->context,'+hex(row['operand'])+'u,&operand))return 2;\n'
        text+='return divide(b,s,operand,'+str(row['destination'])+'u,'+str(int(row['signed']))+'u,'+hex(row['pc']+row['size'])+'u);\n'
    text+='default:return biwn_native_formatter_wait_C_step(b,s,w,service,context);}}\n'
    wrapper=out/'division-CPU.c';wrapper.write_text(text);lib=out/'libdivision-CPU.dylib';rest=ROOT/'projects/black-ice-white-noise/restoration'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(rest),str(wrapper),str(source),candidate['library'],'-o',str(lib)]
    result=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    costp=ROOT/'verification/main-static-cycle-cost-experimental-candidate.json';cost=json.loads(costp.read_text());original=Path(cost['source']);assert sha(original)==cost['source_sha256']
    code=original.read_text();old='if(operand(m,s,RAM,2,&x)||!x)return -1;';assert code.count(old)==1
    code=code.replace(old,'if(operand(m,s,RAM,2,&x))return -1;if(!x)return m->base;')
    old='if(a==(-2147483647-1))return -1;aa=(uint32_t)(a<0?-a:a);';assert code.count(old)==1
    code=code.replace(old,'aa=a<0?0u-(uint32_t)a:(uint32_t)a;')
    costsource=out/'native_cycle_cost.c';costsource.write_text(code);costlib=out/'libdivision-cycle-cost.dylib'
    result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(costsource),'-o',str(costlib)],capture_output=True,text=True);(out/'cost-compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    cdata={**candidate,'library':str(lib),'function':'biwn_division_checked_CPU_step','directory':str(out),'status':'compiled_division_provider_pending_native_checks'}
    cdata['selected_case_sources']=dict(candidate['selected_case_sources'])
    for row in entries:cdata['selected_case_sources'][hex(row['pc'])]='division-CPU.c'
    newcp=out/'CPU-candidate.json';save(newcp,cdata)
    newcost=out/'cost-candidate.json';save(newcost,dict(status='compiled_zero_divisor_and_INT_MIN_cost_pending_checks',source=str(costsource),source_sha256=sha(costsource),library=str(costlib),parent=str(costp),parent_sha256=sha(costp),scope='Pinned emulator instruction charge, not physicalCPUtiming. Opcode model table unchanged.'))
    state=dict(status='terminal_division_C_and_cost_compiled_pending_checks',directory=str(out),CPU_candidate=str(newcp),cost_candidate=str(newcost),
        local_exception_source=str(source),local_source_unedited=True,coordinator_authored_normal_division_and_cost=True,
        fixed_instruction_entries=len(entries),new_original_game_functions_claimed=False,new_training=False,default_promoted=False,
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',args.review,source,parentp,cp,Path(candidate['library']),wrapper,lib,costp,original,costsource,costlib,newcp,newcost]})
    save(out/'build.json',state);save(ROOT/'verification/CPU-division-provider-build-current.json',state);print(json.dumps(state,indent=2),flush=True)

if __name__=='__main__':main()
