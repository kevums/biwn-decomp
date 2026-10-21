"""Read-only live entry/return, retired cycles and interleaving of first2free calls."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 cp=ROOT/'verification/native-free-timing-controls-current.json';control=json.loads(cp.read_text());cd=Path(control['directory']);host_source=cd/'timing-observer.c';template=cd/'fresh-timing-controls.py'
 for p in [host_source,template]:assert sha(p)==control['source_sha256'][str(p)]
 rp=ROOT/'verification/native-free-route-current.json';route=json.loads(rp.read_text());build=json.loads(Path(route['build_proof']).read_text());out=ROOT/'verification/native-free-live-returns'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 host=host_source.read_text();needle='static FILE *events;';assert host.count(needle)==1
 host=host.replace(needle,needle+'\nstatic void live_start(const char *);\nstatic void live_step(uint32_t);\nstatic void live_finish(void);')
 needle='    payload=code;payload_size=length;events=fopen(path,"wb");';assert host.count(needle)==1;host=host.replace(needle,needle+'live_start(path);')
 needle='    steps++;';assert host.count(needle)==1;host=host.replace(needle,needle+'live_step(pc);')
 needle='int finish_observe(const char *path){';assert host.count(needle)==1;host=host.replace(needle,needle+'\n    live_finish();')
 host+=r'''
struct live_info {uint32_t frame,entry_sp,return_pc,task,entry_sr,min_sp,steps,outside_steps,high_sr_steps,task_change_steps,overlapping_entries,return_frame;uint64_t retired_cycles;};
struct live_step_record {uint32_t frame,pc,task;struct cpu cpu;};
static struct live_info live_cases[2];static unsigned live_done,live_active;static char live_prefix[2048];static FILE *live_trace;
static void live_start(const char *path){if(snprintf(live_prefix,sizeof(live_prefix),"%s",path)<0)errors++;}
static void live_dump(unsigned i,const char *phase,const struct cpu *cpu){
 char path[2304];FILE *f;
 if(snprintf(path,sizeof(path),"%s.live-%u-%s-RAM.bin",live_prefix,i,phase)<0){errors++;return;}
 f=fopen(path,"wb");if(!f){errors++;return;}if(fwrite(ram,1,0x200000,f)!=0x200000)errors++;if(fclose(f))errors++;
 if(snprintf(path,sizeof(path),"%s.live-%u-%s-CPU.bin",live_prefix,i,phase)<0){errors++;return;}
 f=fopen(path,"wb");if(!f){errors++;return;}if(fwrite(cpu,sizeof(*cpu),1,f)!=1)errors++;if(fclose(f))errors++;
}
static void live_step(uint32_t pc){
 struct cpu cpu;struct live_info *info;uint32_t task;
 if(!live_active&&(pc!=0x1545c||live_done>=2))return;
 memset(&cpu,0,sizeof(cpu));read_cpu(&cpu);task=rd32(0xc0920);
 if(live_active){
  info=&live_cases[live_done];
  if(pc==info->return_pc&&cpu.r[15]==info->entry_sp+4){
   live_dump(live_done,"return",&cpu);info->return_frame=frame;
   if(live_trace&&fclose(live_trace))errors++;live_trace=NULL;live_active=0;live_done++;
   return;
  }
  if(pc==0x1545c)info->overlapping_entries++;
 }else{
  char path[2304];info=&live_cases[live_done];memset(info,0,sizeof(*info));
  info->frame=frame;info->entry_sp=cpu.r[15];info->return_pc=rd32(cpu.r[15]);info->task=task;info->entry_sr=cpu.sr;info->min_sp=cpu.r[15];
  live_dump(live_done,"entry",&cpu);
  if(snprintf(path,sizeof(path),"%s.live-%u-steps.bin",live_prefix,live_done)<0){errors++;return;}
  live_trace=fopen(path,"wb");if(!live_trace){errors++;return;}live_active=1;
 }
 info=&live_cases[live_done];info->steps++;
 if(cpu.r[15]<info->min_sp)info->min_sp=cpu.r[15];
 if((cpu.sr&0xff00)!=(info->entry_sr&0xff00))info->high_sr_steps++;
 if(task!=info->task)info->task_change_steps++;
 if(!(pc>=0x1545c&&pc<0x1557a)&&!(pc>=0x15edc0&&pc<0x1605c0))info->outside_steps++;
 if(info->steps<20000){struct live_step_record rec;memset(&rec,0,sizeof(rec));rec.frame=frame;rec.pc=pc;rec.task=task;rec.cpu=cpu;if(fwrite(&rec,sizeof(rec),1,live_trace)!=1)errors++;}
}
void live_retired_observer(uint32_t pc,int32_t cycles){(void)pc;if(live_active){if(cycles<=0)errors++;else live_cases[live_done].retired_cycles+=(uint32_t)cycles;}}
static void live_finish(void){
 char path[2304];FILE *f;
 if(live_trace&&fclose(live_trace))errors++;live_trace=NULL;
 if(snprintf(path,sizeof(path),"%s.live.json",live_prefix)<0){errors++;return;}
 f=fopen(path,"w");if(!f){errors++;return;}
 fprintf(f,"{\"completed\":%u,\"pending\":%u,\"cases\":[",live_done,live_active);
 for(unsigned i=0;i<live_done;i++){struct live_info *p=&live_cases[i];fprintf(f,"%s{\"frame\":%u,\"entry_sp\":%u,\"return_pc\":%u,\"task\":%u,\"entry_sr\":%u,\"min_sp\":%u,\"steps\":%u,\"outside_steps\":%u,\"high_sr_steps\":%u,\"task_change_steps\":%u,\"overlapping_entries\":%u,\"return_frame\":%u,\"retired_cycles\":%llu}",i?",":"",p->frame,p->entry_sp,p->return_pc,p->task,p->entry_sr,p->min_sp,p->steps,p->outside_steps,p->high_sr_steps,p->task_change_steps,p->overlapping_entries,p->return_frame,(unsigned long long)p->retired_cycles);}
 fprintf(f,"]}\n");if(fclose(f))errors++;
}
'''
 source=out/'live-observer.c';source.write_text(host);library=out/'liblive-observer.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 text=template.read_text();needle='        observer=c.CDLL('+repr(str(cd/'libtiming-observer.dylib'))+')';assert text.count(needle)==1;text=text.replace(needle,'        observer=c.CDLL('+repr(str(library))+')')
 needle='        core.BIWNSetCPUExecOwner(native_observer,0)';assert text.count(needle)==1
 text=text.replace(needle,needle+"\n        RETIRED=c.CFUNCTYPE(None,c.c_uint32,c.c_int32)\n        live_retired=RETIRED(('live_retired_observer',observer))\n        core.BIWNSetCPURetiredObserver.argtypes=[RETIRED]\n        core.BIWNSetCPURetiredObserver(live_retired)")
 probe=out/'fresh-live-returns.py';probe.write_text(text);compile(text,str(probe),'exec');core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';inputs=cd/'prefix-input.json'
 for p in [core,inputs]:assert sha(p)==control['source_sha256'][str(p)]
 lanes={'original_free':control['variants']['initializer_only']['disc'],'source_free':build['derived_disc']}
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),frames=6400,commands=[],lanes=lanes,control_proof=str(cp),control_proof_sha256=sha(cp),source_sha256={str(p):sha(p)for p in [Path(__file__),host_source,template,source,library,probe,core,inputs]},host_game_state_writes=0,checkpoint_restores=0,CPU_execution_owner=False,retired_observer_changes_cycles=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-free-live-returns-active.json',state)
 mark();children=[]
 try:
  for name,disc in lanes.items():
   command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','6400','--core',str(core),'--disc',disc,'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/name)];log=(out/(name+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((name,child,log));state['commands'].append(dict(name=name,pid=child.pid,command=command))
  state['status']='running_live_entry_return_pair';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True);codes={}
  for name,child,log in children:codes[name]=child.wait();log.close()
  state['exit_codes']=codes;assert not any(codes.values()),codes;results={}
  for name,_,_ in children:
   data=json.loads((out/name/'gameplay-events.bin.live.json').read_text());obs=json.loads((out/name/'gameplay-observation.json').read_text());assert data['completed']==2 and not data['pending']and not(obs['errors']or obs['copy_errors']);results[name]=data
  state.update(status='terminal_live_free_entries_returns_captured_pending_analysis',results=results,finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-free-live-returns-current.json',state);print(json.dumps(results),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
