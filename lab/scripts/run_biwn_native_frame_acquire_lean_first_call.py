"""Read-only first-call snapshots of the two already-reviewed native discs."""
import json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
from run_biwn_native_fast_gameplay_route import ROOT, sha, save

CAPTURE = r'''
static unsigned capture_stage, capture_steps;
static void capture_first(const char *phase, uint32_t pc) {
    char path[4096]; struct cpu state; read_cpu(&state);
    snprintf(path,sizeof(path),"CAPTURE_PREFIX/%s.ram",phase);
    FILE *f=fopen(path,"wb"); if(!f){errors++;return;}
    if(fwrite(ram,0x200000,1,f)!=1)errors++; fclose(f);
    snprintf(path,sizeof(path),"CAPTURE_PREFIX/%s.cpu",phase);
    f=fopen(path,"wb"); if(!f){errors++;return;}
    if(fwrite(&state,sizeof(state),1,f)!=1)errors++; fclose(f);
    snprintf(path,sizeof(path),"CAPTURE_PREFIX/%s.json",phase);
    f=fopen(path,"w"); if(!f){errors++;return;}
    fprintf(f,"{\"frame\":%u,\"pc\":%u,\"steps_between_entry_and_pre_RTS\":%u}\n",frame,pc,capture_steps);
    fclose(f);
}
'''

def main():
    out=ROOT/'verification/native-frame-acquire-lean-first-call'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True); print(out,flush=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    state=dict(status='running_read_only_first_call_pair',pid=os.getpid(),directory=str(out),jobs=[],new_training=False,default_promoted=False,guest_RAM_writes=0,checkpoint_restores=0,frames_per_lane=307)
    pointer=ROOT/'verification/native-frame-acquire-lean-first-call-current.json'
    def mark():save(out/'protocol.json',state);save(pointer,state)
    processes=[];logs=[]
    try:
        for name,pointer_name in [('candidate','native-frame-acquire-lean-route-current.json'),('control','native-frame-acquire-lean-layout-control-current.json')]:
            old= json.loads((ROOT/'verification'/pointer_name).read_text());folder=out/name;folder.mkdir()
            template=Path(old['directory'])/'frame-acquire-observer.c'
            probe_template=Path(old['directory'])/'probe.py'
            for p in [template,probe_template]:assert sha(p)==old['source_sha256'][str(p)]
            text=template.read_text();marker='static void watch_acquire(uint32_t pc){';assert text.count(marker)==1
            text=text.replace(marker,CAPTURE.replace('CAPTURE_PREFIX',str(folder))+'\n'+marker+'\n    if(capture_stage==1)capture_steps++;\n    if(pc==0x1ac68&&!capture_stage){capture_first("entry",pc);capture_stage=1;}')
            marker='        uint32_t s=slot->incoming.r[15];acquire_returns++;emit(pc);';assert text.count(marker)==1
            text=text.replace(marker,'        if(capture_stage==1){capture_first("return",pc);capture_stage=2;}\n'+marker)
            marker='    if(pc==0x1b044){';assert text.count(marker)==1
            text=text.replace(marker,'    if(capture_stage==1&&pc==0x1b044)capture_first("loader_entry",pc);\n'+marker)
            build=json.loads(Path(old['build_proof']).read_text());after=build['symbols']['biwn_frame_acquire_after_load'] if name=='candidate' else 0x1ad7a
            marker='static void watch_acquire(uint32_t pc){';assert text.count(marker)==1
            text=text.replace(marker,marker+'\n    if(capture_stage==1&&pc=='+hex(after)+')capture_first("loader_return",pc);')
            observer=folder/'observer.c';observer.write_text(text);library=folder/'observer.dylib'
            p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
            (folder/'observer-build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
            original_library=next(k for k in old['source_sha256']if k.endswith('libframe-acquire-observer.dylib'))
            text=probe_template.read_text();assert text.count(original_library)==1;text=text.replace(original_library,str(library))
            probe=folder/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
            cmd=list(old['command']);cmd[2]=str(probe);cmd[cmd.index('--frames')+1]='307';cmd[cmd.index('--output')+1]=str(folder/'run')
            disc=Path(cmd[cmd.index('--disc')+1]);expected=old['control_delta']['control_sha256']if name=='control'else json.loads(Path(old['build_proof']).read_text())['derived_disc_sha256'];assert sha(disc)==expected
            log=(folder/'run.log').open('w');logs.append(log);child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);processes.append(child)
            state['jobs'].append(dict(name=name,pid=child.pid,command=cmd,parent_protocol=str(Path(old['directory'])/'protocol.json'),source_sha256={str(p):sha(p)for p in [observer,library,probe,template,probe_template,disc]}));mark()
        for row,child in zip(state['jobs'],processes):
            row['exit_code']=child.wait();mark();assert row['exit_code']==0,row['name']+' failed'
            folder=out/row['name'];assert all((folder/(phase+'.'+ext)).exists()for phase in ['entry','loader_entry','loader_return','return']for ext in ['cpu','ram','json'])
            observation=json.loads((folder/'run/gameplay-observation.json').read_text());assert observation['acquire_monitor_errors']==observation['errors']==observation['copy_errors']==0
        state.update(status='terminal_read_only_first_call_pair_pending_review');mark();print(state['status'],flush=True)
    except BaseException as error:
        state.update(status='terminal_first_call_pair_failed',error=repr(error));mark();raise
    finally:
        for log in logs:log.close()

if __name__=='__main__':main()
