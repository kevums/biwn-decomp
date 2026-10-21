"""Check the whole parked C continuation, beyond its semantic register object."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from diagnose_native_formatter_parent_context import PARENTS
def main():
 sourcep=ROOT/'verification/native-core-route-diagnosis-current.json';prior=json.loads(sourcep.read_text());parent=Path(prior['directory']);bundle=json.loads((ROOT/'verification/native-core-format-bundle-current.json').read_text());out=ROOT/'verification/native-core-parent-stack-diagnosis'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 helper=PARENTS.replace('uint32_t sp,ret,ctx,task;unsigned char saved[72]','uint32_t sp,ret,ctx,task,lo,size;unsigned char saved[2048]')
 old='memcpy(paused_parent[i].saved,ram+paused_parent[i].ctx,72);paused_parent[i].watch=1;'
 new='paused_parent[i].lo=rd32(paused_parent[i].ctx+68u);uint32_t lo=paused_parent[i].lo,hi=paused_parent[i].ctx+72u;paused_parent[i].watch=0;if(lo<hi&&hi-lo<=2048u){paused_parent[i].size=hi-lo;memcpy(paused_parent[i].saved,ram+lo,hi-lo);paused_parent[i].watch=1;}'
 assert old in helper;helper=helper.replace(old,new).replace('memcmp(paused_parent[i].saved,ram+paused_parent[i].ctx,72)','memcmp(paused_parent[i].saved,ram+paused_parent[i].lo,paused_parent[i].size)').replace('j<72','j<paused_parent[i].size').replace('ram[paused_parent[i].ctx+j]','ram[paused_parent[i].lo+j]')
 marker='parent_capture_done=1;capture_formatter("parent-context",(unsigned)format_latest,pc);';assert marker in helper
 helper=helper.replace(marker,marker+'\n   FILE *range=fopen("CAPTURE_DIRECTORY/parent-stack-range.json","w");if(range){fprintf(range,"{\\"start\\":%u,\\"size\\":%u,\\"context\\":%u}\\n",paused_parent[i].lo,paused_parent[i].size,paused_parent[i].ctx);fclose(range);}')
 helper=helper.replace('CAPTURE_DIRECTORY',str(out)).replace('ACQUIRE_BODY',hex(bundle['symbols']['biwn_native_resource_acquire_body'])+'u').replace('LOAD_BODY',hex(bundle['symbols']['biwn_native_resource_load_body'])+'u')
 text=(parent/'diagnosis-observer.c').read_text().replace(str(parent),str(out));marker='static void watch_formatter(uint32_t pc){';assert text.count(marker)==1;text=text.replace(marker,helper+'\n'+marker+'\n watch_parent(pc);')
 observer=out/'parent-stack-observer.c';observer.write_text(text);library=out/'parent-stack-observer.dylib';result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
 probe=out/'probe.py';src=(parent/'probe.py').read_text();old=str(parent/'diagnosis-observer.dylib');assert src.count(old)==1;src=src.replace(old,str(library));compile(src,str(probe),'exec');probe.write_text(src)
 command=list(prior['command']);command[2]=str(probe);command[command.index('--output')+1]=str(out/'core')
 state=dict(status='running_readonly_parent_stack_capture',pid=os.getpid(),directory=str(out),command=command,host_guest_RAM_writes=0,checkpoint_restores=0,source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/diagnose_native_formatter_parent_context.py',parent/'diagnosis-observer.c',parent/'probe.py',observer,library,probe]})
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-core-parent-stack-diagnosis-active.json',state)
 mark();print(out,flush=True)
 with(out/'core.log').open('w')as log:
  child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
 state.update(status='terminal_readonly_parent_stack_capture_completed'if not code else'terminal_failed',exit_code=code,capture_found=(out/'parent-stack-range.json').exists());mark()
 if not code:save(ROOT/'verification/native-core-parent-stack-diagnosis-current.json',state)
 print(json.dumps(dict(status=state['status'],capture_found=state['capture_found'])),flush=True);assert not code
if __name__=='__main__':main()
