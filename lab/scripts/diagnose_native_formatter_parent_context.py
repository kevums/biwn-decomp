"""Capture formatter writes into paused resource-call private contexts."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
PARENTS=r'''
struct paused_parent {unsigned live,kind,watch;uint32_t sp,ret,ctx,task;unsigned char saved[72];};
static struct paused_parent paused_parent[16];
static unsigned parent_capture_done;static uint32_t parent_previous_pc;
static void watch_parent(uint32_t pc){
 struct cpu value;read_cpu(&value);uint32_t sp=value.r[15],task=rd32(0xc0920u);
 for(unsigned i=0;i<16;i++)if(paused_parent[i].live&&pc==paused_parent[i].ret&&sp==paused_parent[i].sp+4u)paused_parent[i].live=0;
 if(pc==ACQUIRE_BODY||pc==LOAD_BODY){
  unsigned i;for(i=0;i<16;i++)if(!paused_parent[i].live)break;
  if(i<16){uint32_t ctx=rd32(sp+4u);if(ctx<=0x1fffb8u)paused_parent[i]=(struct paused_parent){.live=1u,.kind=pc==LOAD_BODY,.sp=sp,.ret=rd32(sp),.ctx=ctx,.task=task};}
 }
 if(pc==0x1b29cu||pc==0x1b45au){
  for(unsigned i=0;i<16;i++)if(paused_parent[i].live&&paused_parent[i].task==task){memcpy(paused_parent[i].saved,ram+paused_parent[i].ctx,72);paused_parent[i].watch=1;}
 }
 if(!parent_capture_done&&format_latest>=0&&format_pending[format_latest].live&&format_pending[format_latest].task==task){
  for(unsigned i=0;i<16;i++)if(paused_parent[i].live&&paused_parent[i].watch&&paused_parent[i].task==task&&memcmp(paused_parent[i].saved,ram+paused_parent[i].ctx,72)){
   parent_capture_done=1;capture_formatter("parent-context",(unsigned)format_latest,pc);
   FILE *f=fopen("CAPTURE_DIRECTORY/parent-context-detail.json","w");if(f){fprintf(f,"{\"frame\":%u,\"writer_PC\":%u,\"observed_PC\":%u,\"parent_kind\":%u,\"parent_context\":%u,\"parent_C_entry_SP\":%u,\"parent_return\":%u,\"task\":%u,\"current_SP\":%u,\"before_hex\":\"",frame,parent_previous_pc,pc,paused_parent[i].kind,paused_parent[i].ctx,paused_parent[i].sp,paused_parent[i].ret,task,sp);
    for(unsigned j=0;j<72;j++)fprintf(f,"%02x",paused_parent[i].saved[j]);fprintf(f,"\",\"after_hex\":\"");for(unsigned j=0;j<72;j++)fprintf(f,"%02x",ram[paused_parent[i].ctx+j]);fprintf(f,"\"}\n");fclose(f);}
   break;
  }
 }
 parent_previous_pc=pc;
}
'''
def main():
 sourcep=ROOT/'verification/native-core-route-diagnosis-active.json';prior=json.loads(sourcep.read_text());parent=Path(prior['directory']);bundle=json.loads((ROOT/'verification/native-core-format-bundle-current.json').read_text());out=ROOT/'verification/native-core-parent-context-diagnosis'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 original=(parent/'diagnosis-observer.c').read_text();text=original.replace(str(parent),str(out));helper=PARENTS.replace('CAPTURE_DIRECTORY',str(out)).replace('ACQUIRE_BODY',hex(bundle['symbols']['biwn_native_resource_acquire_body'])+'u').replace('LOAD_BODY',hex(bundle['symbols']['biwn_native_resource_load_body'])+'u')
 marker='static void watch_formatter(uint32_t pc){';assert text.count(marker)==1;text=text.replace(marker,helper+'\n'+marker+'\n watch_parent(pc);')
 observer=out/'parent-observer.c';observer.write_text(text);library=out/'parent-observer.dylib';result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
 probe=out/'probe.py';src=(parent/'probe.py').read_text();old=str(parent/'diagnosis-observer.dylib');assert src.count(old)==1;src=src.replace(old,str(library));compile(src,str(probe),'exec');probe.write_text(src)
 command=list(prior['command']);command[2]=str(probe);command[command.index('--output')+1]=str(out/'core')
 state=dict(status='running_readonly_parent_context_capture',pid=os.getpid(),directory=str(out),command=command,source_capture=str(sourcep),host_guest_RAM_writes=0,checkpoint_restores=0,source_sha256={str(p):sha(p)for p in [Path(__file__),parent/'diagnosis-observer.c',parent/'probe.py',observer,library,probe]})
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-core-parent-context-diagnosis-active.json',state)
 mark();print(out,flush=True)
 with(out/'core.log').open('w')as log:
  child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
 state.update(status='terminal_readonly_parent_context_capture_completed'if not code else'terminal_failed',exit_code=code,capture_found=(out/'parent-context-detail.json').exists());mark()
 if not code:save(ROOT/'verification/native-core-parent-context-diagnosis-current.json',state)
 print(json.dumps(dict(status=state['status'],capture_found=state['capture_found'])),flush=True);assert not code
if __name__=='__main__':main()
