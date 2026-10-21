"""Read-only producer/completion wait chronology for the failed control."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

EXTRA=r'''
static const unsigned char *wait_gpu_ram;
void configure_wait_trace(const void *memory){wait_gpu_ram=memory;}
static uint32_t wait_word(unsigned at){return((uint32_t)wait_gpu_ram[at]<<24)|((uint32_t)wait_gpu_ram[at+1]<<16)|((uint32_t)wait_gpu_ram[at+2]<<8)|wait_gpu_ram[at+3];}
static void wait_watch(unsigned phase,uint32_t pc){
 if(frame<1428u||frame>1429u||trace_captured)return;
 unsigned selected=0;struct cpu value;
 if(phase!=2u){
  read_cpu(&value);
  selected=pc==0xe0a4u||pc==0x17e64u||pc==0x17e6au||pc==0x181f8u||pc==0x183e0u;
  if((pc==0xe098u&&phase==1u&&(value.sr&4u))||(pc==0xe0a2u&&(value.sr&4u)))selected=1;
 }else if(pc==0xf031c6u||pc==0xf031d6u||pc==0xf031dau){selected=1;read_cpu(&value);}
 if(!selected)return;
 FILE *f=fopen("WAIT_DIRECTORY/wait-events.jsonl","a");if(!f)return;
 fprintf(f,"{\"frame\":%u,\"phase\":%u,\"PC\":%u,\"CPU_PC\":%u,\"SR\":%u,\"SP\":%u,\"task\":%u,\"busy\":%u,\"command\":%u,\"previous_command\":%u}\n",frame,phase,pc,value.pc,value.sr,value.r[15],rd32(0xc0920u),wait_word(0x200u),wait_word(0x204u),wait_word(0x208u));fclose(f);
}
'''

def main():
 pp=ROOT/'verification/native-fast-core-blitter-handoff-current.json';parent=json.loads(pp.read_text());source=Path(parent['directory']);assert parent['exit_code']==0
 for p,h in parent['source_sha256'].items():assert sha(p)==h,p
 out=ROOT/'verification/native-fast-core-GPU-wait'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 text=(source/'observer.c').read_text();marker='static void trace_memory(unsigned phase,uint32_t pc,int32_t cycles){';assert text.count(marker)==1
 text=text.replace(marker,EXTRA.replace('WAIT_DIRECTORY',str(out))+'\n'+marker+'\n wait_watch(phase,pc);');text=text.replace(str(source),str(out))
 observer=out/'observer.c';observer.write_text(text);library=out/'observer.dylib'
 result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
 text=(source/'probe.py').read_text();assert text.count(str(source/'observer.dylib'))==1;text=text.replace(str(source/'observer.dylib'),str(library))
 marker='        core.BIWNSetGPUBundleOwner(gpu_trace)';assert text.count(marker)==1
 text=text.replace(marker,marker+'\n        core.GPUGetRAM.restype=c.c_void_p\n        observer.configure_wait_trace.argtypes=[c.c_void_p]\n        observer.configure_wait_trace(core.GPUGetRAM())\n')
 probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
 command=list(parent['command']);command[2]=str(probe);command[command.index('--output')+1]=str(out/'control')
 state=dict(status='running_readonly_GPU_wait_chronology',directory=str(out),pid=os.getpid(),source_proof=str(pp),source_proof_sha256=sha(pp),command=command,source_sha256={str(p):sha(p)for p in [Path(__file__),pp,source/'observer.c',source/'probe.py',observer,library,probe]},host_guest_RAM_writes=0,checkpoint_restores=0,core_binary_modified=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-fast-core-GPU-wait-active.json',state)
 mark()
 with(out/'control.log').open('w')as log:
  child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
 state.update(status='terminal_readonly_GPU_wait_chronology_completed'if not code else'terminal_failed',exit_code=code,output_sha256={str(p):sha(p)for p in out.glob('*')if p.is_file()and p.name!='protocol.json'})
 mark()
 if not code:save(ROOT/'verification/native-fast-core-GPU-wait-current.json',state)
 print(state['status'],flush=True);assert not code

if __name__=='__main__':main()
