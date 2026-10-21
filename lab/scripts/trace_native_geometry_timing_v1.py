"""Read-only instruction-boundary timeline for the existing fresh gameplay pair.

Preserve both discs, controller inputs, stopping conditions and original guards.
Compare every saved frame observation with the earlier lane before interpreting
the added trace. A preceding observed PC is a clue, not proof of a RAM writer.
"""
import hashlib,json,os,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

TRACE=r'''
/* Host-only trace storage. Guest RAM/CPU and existing observers are read-only. */
struct timing_row { uint32_t frame,ordinal,pc,previous,reason,movie0,movie1,held,task,sp; };
static struct timing_row timing_rows[65536];
static uint32_t timing_count,timing_overflow,timing_frame,timing_ordinal,timing_previous;
static uint32_t timing_movie0,timing_movie1,timing_held;
static void timing_watch(uint32_t pc){
 if(frame<24565u||frame>24966u)return;
 uint32_t m0=rd16(0x47b80u),m1=rd16(0x47b82u),held=rd32(0x49ba4u);
 unsigned reason=0;
 if(timing_frame!=frame){timing_frame=frame;timing_ordinal=0;reason|=1u;}
 timing_ordinal++;
 if(m0!=timing_movie0||m1!=timing_movie1||held!=timing_held)reason|=2u;
 if(pc==0x11ad4u||pc==0x11b4au||pc==1498928u||pc==1499116u||pc==0xdf60u||pc==0xdf8cu)reason|=4u;
 if(reason){
  if(timing_count==65536u)timing_overflow++;
  else {struct cpu current;read_cpu(&current);
   timing_rows[timing_count++]=(struct timing_row){frame,timing_ordinal,pc,timing_previous,reason,m0,m1,held,rd32(0xc0920u),current.r[15]};}
 }
 timing_previous=pc;timing_movie0=m0;timing_movie1=m1;timing_held=held;
}
int timeline_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"overflow\":%u,\"rows\":[",timing_overflow);
 for(unsigned i=0;i<timing_count;i++){
  struct timing_row *r=&timing_rows[i];
  fprintf(file,"%s[%u,%u,%u,%u,%u,%u,%u,%u,%u,%u]",i?",":"",r->frame,r->ordinal,r->pc,r->previous,r->reason,r->movie0,r->movie1,r->held,r->task,r->sp);
 }
 return fputs("]}\n",file)<0||fclose(file);
}
'''

def main():
 out=V/'native-geometry-timing-trace-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='preparing',directory=str(out),pid=os.getpid(),lanes={},new_predictions=0,new_training=False,discs_changed=False,inputs_changed=False,scope=__doc__)
 pointer=V/'native-geometry-timing-trace-v1-current.json'
 def mark():save(out/'protocol.json',state);save(pointer,state)
 mark();print(out,flush=True);deps=[Path(__file__)]
 try:
  for lane in ['candidate','control']:
   jp=V/f'native-Deck-debug-geometry-v1-{lane}-current.json';job=read(jp);old=Path(job['directory']);prior=read(job['report']);assert sha(job['report'])==job['report_sha256'];assert prior['ordinary_Deck_input_trial']['start_frame']==24564
   folder=out/lane;folder.mkdir();source=folder/'observer.c';text=(old/'observer.c').read_text();anchor='int32_t observe(uint32_t pc){o6_watch(pc);return o6_retained_observe(pc);}'
   assert text.count(anchor)==1;text=text.replace(anchor,TRACE+'\nint32_t observe(uint32_t pc){timing_watch(pc);o6_watch(pc);return o6_retained_observe(pc);}')
   source.write_text(text);lib=folder/'observer.dylib';compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),str(old/'direction-shadow-model.c'),'-o',str(lib)],capture_output=True,text=True);(folder/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
   text=(old/'probe.py').read_text();text,n=re.subn(r"(?m)^        observer=c.CDLL\('[^']+'\)",'        observer=c.CDLL('+repr(str(lib))+')',text);assert n==1
   anchor="        assert observer.outer_dump(str(out/'outer-observation.json').encode())==0";assert text.count(anchor)==1
   text=text.replace(anchor,anchor+"\n        observer.timeline_dump.argtypes=[c.c_char_p];observer.timeline_dump.restype=c.c_int\n        assert observer.timeline_dump(str(out/'timeline.json').encode())==0")
   probe=folder/'probe.py';probe.write_text(text);command=list(job['command']);command[2]=str(probe);command[command.index('--output')+1]=str(folder/'run')
   disc=Path(command[command.index('--disc')+1]);disc_digest=sha(disc)
   with(folder/'runtime.log').open('w')as log:
    child=subprocess.Popen(command,cwd='/',stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')});state.update(status='tracing_'+lane,child_pid=child.pid);mark();code=child.wait(timeout=900)
   state['child_pid']=None;assert code==0,(folder/'runtime.log').read_text()[-3000:];assert sha(disc)==disc_digest
   rp=folder/'run/report.json';actual=read(rp);assert actual['frames']==prior['frames'],'Added observation changed a frame record';assert actual['ordinary_Deck_input_trial']==prior['ordinary_Deck_input_trial'];assert actual['final_RAM_sha256']==prior['final_RAM_sha256']and actual['final_serialized_state_sha256']==prior['final_serialized_state_sha256']
   tp=folder/'run/timeline.json';timeline=read(tp);assert not timeline['overflow'];rows=timeline['rows'];assert rows and rows[0][0]==24565
   for name in ['gameplay-observation.json','shared-observation.json','face-observation.json','geometry-observation.json','outer-observation.json']:
    assert read(folder/'run'/name)==read(old/'candidate'/name),('guard observations changed',lane,name)
   state['lanes'][lane]=dict(frames=len(actual['frames']),trace_rows=len(rows),report=str(rp),timeline=str(tp),all_frame_records_and_final_state_equal_prior=True,all_guard_observations_equal_prior=True,disc_sha256=disc_digest)
   deps.extend([jp,Path(job['report']),old/'observer.c',old/'probe.py',old/'direction-shadow-model.c',source,lib,probe,rp,tp]);mark();print(lane,len(rows),'timeline rows; all baseline frame records equal',flush=True)
  state.update(status='terminal_read_only_geometry_timing_timelines_baseline_identical',source_sha256={str(p):sha(p)for p in deps},fidelity_verified=False);mark();print(state['status'],flush=True)
 except BaseException as error:
  state.update(status='terminal_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
