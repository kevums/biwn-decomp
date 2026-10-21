"""Fresh matched-layout first-call capture. Read-only CPU/RAM observer; no restores."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,os
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 bp=ROOT/'verification/native-load-disc-build-current.json';build=json.loads(bp.read_text());cp=ROOT/'verification/native-load-layout-control-active.json';control=json.loads(cp.read_text());assert control['build_proof_sha256']==sha(bp)
 rp=ROOT/'verification/native-load-route-current.json';route=json.loads(rp.read_text());rd=Path(route['directory']);source=rd/'load-observer.c';assert sha(source)==route['source_sha256'][str(source)]
 out=ROOT/'verification/native-loader-call-pair'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 code=source.read_text();needle='int32_t observe(uint32_t pc) {';assert code.count(needle)==1
 extra=r'''
struct load_capture { uint32_t task,sp,ret,seq,active,yields; };
static struct load_capture load_captures[16];
static unsigned load_capture_count,load_capture_event;
static char capture_prefix[4096];
static void capture_state(const char *phase,struct load_capture *call,uint32_t pc,int memory) {
 struct cpu value;read_cpu(&value);char name[4300];
 snprintf(name,sizeof(name),"%s-loader-%02u-%s-%x-%05u.json",capture_prefix,call->seq,phase,pc,load_capture_event++);
 FILE *file=fopen(name,"w");if(!file){errors++;return;}
 fprintf(file,"{\"frame\":%u,\"PC\":%u,\"task\":%u,\"entry_SP\":%u,\"return_PC\":%u,\"SR\":%u,\"USP\":%u,\"SSP\":%u,\"registers\":[",frame,pc,call->task,call->sp,call->ret,value.sr,value.usp,value.ssp);
 for(unsigned i=0;i<16;i++)fprintf(file,"%s%u",i?",":"",value.r[i]);
 fprintf(file,"],\"args\":[");for(unsigned i=0;i<5;i++)fprintf(file,"%s%u",i?",":"",rd32(call->sp+4+4*i));fprintf(file,"]}\n");fclose(file);
 if(memory){snprintf(name,sizeof(name),"%s-loader-%02u-%s-RAM.bin",capture_prefix,call->seq,phase);file=fopen(name,"wb");if(!file){errors++;return;}if(fwrite(ram,1,0x200000,file)!=0x200000)errors++;fclose(file);}
}
static void loader_capture_observe(uint32_t pc) {
 if(pc==0x1b044&&load_capture_count<16){struct cpu value;read_cpu(&value);struct load_capture *call=&load_captures[load_capture_count];call->task=rd32(0xc0920);call->sp=value.r[15];call->ret=rd32(call->sp);call->seq=load_capture_count++;call->active=1;capture_state("entry",call,pc,1);}
 for(unsigned i=0;i<load_capture_count;i++)if(load_captures[i].active){struct load_capture *call=&load_captures[i];
  if(pc==call->ret){struct cpu value;read_cpu(&value);if(value.r[15]==call->sp+4&&rd32(0xc0920)==call->task){capture_state("return",call,pc,1);call->active=0;continue;}}
  if(rd32(0xc0920)==call->task&&(pc==0xd206||pc==0xd2f0||pc==0xd306||pc==0xe3e0||(pc==0xdf60&&call->yields++<4)))capture_state("helper",call,pc,0);
 }
}
'''
 # Helpers are inserted before observe, after rd32/read_cpu definitions.
 code=code.replace(needle,extra+'\n'+needle+'\n    loader_capture_observe(pc);')
 needle='    payload=code;payload_size=length;events=fopen(path,"wb");';assert code.count(needle)==1
 # Declaration needs to precede begin_observe while helper definitions follow it.
 decl='static char capture_prefix[4096];\n';code=code.replace(decl,'',1);code=code.replace('int begin_observe(',decl+'int begin_observe(',1);code=code.replace(needle,'    snprintf(capture_prefix,sizeof(capture_prefix),"%s",path);\n'+needle)
 host=out/'capture-observer.c';host.write_text(code);library=out/'libcapture-observer.dylib';run=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(host),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 original_inputs=Path(control['command'][control['command'].index('--frame-controller-script')+1]);input_data=json.loads(original_inputs.read_text());prefix_inputs=out/'prefix-controller-input.json';input_data['windows']=[{**w,'stop_frame':min(w['stop_frame'],4001)}for w in input_data['windows']if w['start_frame']<4001];save(prefix_inputs,input_data)
 template=Path(control['directory'])/'fresh-layout-control.py';text=template.read_text();lines=text.splitlines(keepends=True);found=0
 for i,line in enumerate(lines):
  if line.startswith('        observer=c.CDLL('):lines[i]='        observer=c.CDLL('+repr(str(library))+')\n';found+=1
 assert found==1;text=''.join(lines);needle="range(window['start_frame'],window['stop_frame'])";assert text.count(needle)==1;text=text.replace(needle,"range(window['start_frame'],min(window['stop_frame'],args.frames+1))")
 probe=out/'fresh-call-capture.py';probe.write_text(text);compile(text,str(probe),'exec');oldcmd=control['command'];state=dict(status='prepared',pid=os.getpid(),directory=str(out),build_proof=str(bp),build_proof_sha256=sha(bp),control_preparation_snapshot=control,frames=4000,host_guest_RAM_writes=0,checkpoint_restores=0,commands=[],source_sha256={str(p):sha(p)for p in [Path(__file__),source,host,library,template,probe]})
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-loader-call-pair-active.json',state)
 mark();children=[]
 for lane,disc in [('compiled',build['derived_disc']),('original_control',control['disc'])]:
  cmd=list(oldcmd);cmd[2]=str(probe);cmd[cmd.index('--disc')+1]=disc;cmd[cmd.index('--frames')+1]='4000';cmd[cmd.index('--frame-controller-script')+1]=str(prefix_inputs);cmd[cmd.index('--output')+1]=str(out/lane);log=(out/(lane+'.log')).open('w');child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=cmd))
 state['status']='running_fresh_matched_layout_first_loader_calls';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True)
 codes={}
 for lane,child,log in children:codes[lane]=child.wait();log.close()
 state.update(status='terminal_failed'if any(codes.values())else'terminal_call_pair_pending_comparison',exit_codes=codes);mark();assert not any(codes.values()),codes;save(ROOT/'verification/native-loader-call-pair-current.json',state);print(state['status'],flush=True)
if __name__=='__main__':main()
