"""Read-only scene-transition failure capture, no guest/CPU interventions."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from prepare_core_format_gameplay import OBSERVER,REPORT
CAPTURE=r'''
static unsigned char *format_entry_ram[64];
static struct cpu format_entry_cpu[64];
static int format_latest=-1;
static unsigned format_bad_stack_captured,format_odd_PC_captured;
static void capture_formatter(const char *stem,unsigned j,uint32_t pc){
 char path[4096];struct cpu current;read_cpu(&current);
 snprintf(path,sizeof(path),"CAPTURE_DIRECTORY/%s-entry-RAM.bin",stem);FILE *f=fopen(path,"wb");if(f){fwrite(format_entry_ram[j],1,0x200000,f);fclose(f);}
 snprintf(path,sizeof(path),"CAPTURE_DIRECTORY/%s-current-RAM.bin",stem);f=fopen(path,"wb");if(f){fwrite(ram,1,0x200000,f);fclose(f);}
 snprintf(path,sizeof(path),"CAPTURE_DIRECTORY/%s.json",stem);f=fopen(path,"w");if(!f)return;
 fprintf(f,"{\"frame\":%u,\"observed_PC\":%u,\"task\":%u,\"kind\":%u,\"entry_SP\":%u,\"return_PC\":%u,\"entry\":{\"registers\":[",frame,pc,format_pending[j].task,format_pending[j].kind,format_pending[j].sp,format_pending[j].ret);
 for(unsigned i=0;i<16;i++)fprintf(f,"%s%u",i?",":"",format_entry_cpu[j].r[i]);
 fprintf(f,"],\"pc\":%u,\"sr\":%u,\"usp\":%u,\"ssp\":%u},\"current\":{\"registers\":[",format_entry_cpu[j].pc,format_entry_cpu[j].sr,format_entry_cpu[j].usp,format_entry_cpu[j].ssp);
 for(unsigned i=0;i<16;i++)fprintf(f,"%s%u",i?",":"",current.r[i]);
 fprintf(f,"],\"pc\":%u,\"sr\":%u,\"usp\":%u,\"ssp\":%u}}\n",current.pc,current.sr,current.usp,current.ssp);fclose(f);
}
'''
def main():
 routep=ROOT/'verification/native-core-format-long-route-current.json';route=json.loads(routep.read_text());parent=Path(route['directory']);bundle=json.loads((ROOT/'verification/native-core-format-bundle-current.json').read_text());out=ROOT/'verification/native-core-route-diagnosis'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 text=(parent/'resource-observer.c').read_text();watch=OBSERVER.replace('CORE_BODY',hex(bundle['symbols']['biwn_native_format_core_body'])+'u').replace('VAR_BODY',hex(bundle['symbols']['biwn_native_format_variadic_body'])+'u')
 marker='static void watch_formatter(uint32_t pc){';assert watch.count(marker)==1;watch=watch.replace(marker,CAPTURE.replace('CAPTURE_DIRECTORY',str(out))+'\n'+marker)
 marker='if(!any&&kind<0)return;';assert watch.count(marker)==1;watch=watch.replace(marker,'if((pc&1u)&&format_latest>=0&&!format_odd_PC_captured){format_odd_PC_captured=1;capture_formatter("odd-PC",(unsigned)format_latest,pc);}\n '+marker)
 marker='format_pending[j]=(struct format_pending){1u,(unsigned)kind,sp,rd32(sp),task};';assert watch.count(marker)==1
 watch=watch.replace(marker,marker+'\n   if(!format_entry_ram[j])format_entry_ram[j]=malloc(0x200000);\n   if(format_entry_ram[j]){memcpy(format_entry_ram[j],ram,0x200000);format_entry_cpu[j]=value;format_latest=(int)j;}')
 marker='if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)formatter_stack_outside[k]++;';assert watch.count(marker)==1
 watch=watch.replace(marker,'if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u){formatter_stack_outside[k]++;if(!format_bad_stack_captured&&format_entry_ram[j]){format_bad_stack_captured=1;capture_formatter("bad-stack",j,pc);}}')
 text='#include <stdlib.h>\n'+text;marker='int32_t observe(uint32_t pc) {';assert text.count(marker)==1;text=text.replace(marker,watch+'\n'+marker)
 marker='    steps++;';assert text.count(marker)==1;text=text.replace(marker,marker+'\n    watch_formatter(pc);')
 marker='    array(file,"rng_entries",rng_entries,8);';assert text.count(marker)==1;text=text.replace(marker,'\n{\n'+REPORT+'\n}\n'+marker)
 observer=out/'diagnosis-observer.c';observer.write_text(text);library=out/'diagnosis-observer.dylib';result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
 probe=out/'probe.py';source=(parent/'fresh-route.py').read_text();old=str(parent/'resource-observer.dylib');assert source.count(old)==1;source=source.replace(old,str(library));compile(source,str(probe),'exec');probe.write_text(source)
 command=list(next(row['command']for row in route['commands']if row['lane']=='core'));command[2]=str(probe);command[command.index('--frames')+1]='9000';command[command.index('--output')+1]=str(out/'core')
 state=dict(status='running_readonly_transition_capture',directory=str(out),pid=os.getpid(),source_route=str(routep),source_route_sha256=sha(routep),command=command,checkpoint_restores=0,host_guest_RAM_writes=0,source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/prepare_core_format_gameplay.py',parent/'resource-observer.c',parent/'fresh-route.py',observer,library,probe]})
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-core-route-diagnosis-active.json',state)
 mark();print(out,flush=True)
 with(out/'core.log').open('w')as log:
  child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
 state.update(status='terminal_readonly_transition_capture_completed'if not code else'terminal_failed',exit_code=code,captures=[str(p)for p in out.glob('*.json')if p.name not in ['protocol.json']]);mark()
 if not code:save(ROOT/'verification/native-core-route-diagnosis-current.json',state)
 print(json.dumps(dict(status=state['status'],captures=state['captures'])),flush=True);assert not code
if __name__=='__main__':main()
