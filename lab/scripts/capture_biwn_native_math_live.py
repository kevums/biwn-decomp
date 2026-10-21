"""Record actual completed native arithmetic calls without guest writes.
One fresh candidate run; compare it to the existing candidate to verify that
new read-only boundary observation leaves its game/video/audio unchanged.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,os
from check_biwn_native_button_digit import ROOT,sha,save
TAP=r'''
struct math_pair {uint32_t entry,numerator,denominator,start_frame,end_frame,depth,return_pc;struct cpu before,after;};
_Static_assert(sizeof(struct cpu)==80,"CPU ABI");
_Static_assert(sizeof(struct math_pair)==188,"record ABI");
static struct math_pair math_stack[16];static unsigned math_depth,math_errors,math_frame;
static uint64_t math_entered,math_written;static FILE *math_log;
static uint32_t rd32(uint32_t);
int math_log_begin(const char *path){math_log=fopen(path,"wb");return math_log?0:1;}
void math_set_frame(uint32_t value){math_frame=value;}
static void math_tap(uint32_t pc){struct cpu s;struct math_pair*p;
 if(math_depth&&pc==math_stack[math_depth-1].return_pc){
  readstate(&s);p=&math_stack[math_depth-1];
  if(s.r[15]==p->before.r[15]+4){p->after=s;p->end_frame=math_frame;
   if(!math_log||fwrite(p,sizeof(*p),1,math_log)!=1)math_errors++;
   math_written++;math_depth--;
  }
 }
 if(pc==0xe540||pc==0xe588||pc==0xe60a){
  if(math_depth>=16){math_errors++;return;}
  p=&math_stack[math_depth];memset(p,0,sizeof(*p));readstate(&p->before);
  p->entry=pc;p->numerator=rd32(p->before.r[15]+4);p->denominator=rd32(p->before.r[15]+8);
  p->start_frame=math_frame;p->return_pc=rd32(p->before.r[15]);p->depth=math_depth;
  math_depth++;math_entered++;
 }
}
int math_log_end(const char*path){FILE*f;int failed=0;
 if(math_log){failed=fclose(math_log)!=0;math_log=NULL;}else failed=1;
 f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"entered\":%llu,\"completed\":%llu,\"pending\":%u,\"errors\":%u,\"record_bytes\":188,\"last_frame\":%u}\n",(unsigned long long)math_entered,(unsigned long long)math_written,math_depth,math_errors,math_frame);
 return fclose(f)!=0||failed;
}
'''
def main():
 out=ROOT/'verification/native-math-live-capture'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 proof=ROOT/'verification/native-bundle-disc-cold-boot-current.json';p=json.loads(proof.read_text());base=Path(p['directory']);build=json.loads(Path(p['build_proof']).read_text())
 for path,digest in p['runtime_dependencies_sha256'].items():assert sha(path)==digest
 ctext=(base/'native_observer.c').read_text();marker='static uint32_t heap_base;';assert ctext.count(marker)==1;ctext=ctext.replace(marker,TAP+'\n'+marker);marker='struct cpu s;instructions++;';assert ctext.count(marker)==1;ctext=ctext.replace(marker,marker+'math_tap(pc);')
 source=out/'capture_observer.c';source.write_text(ctext);lib=out/'libcapture-observer.dylib';cmd=['clang','-dynamiclib','-std=c11','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)]
 compiled=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
 text=(base/'fresh_native_disc_probe.py').read_text();old=str(base/'libnative-observer.dylib');assert text.count(old)==1;text=text.replace(old,str(lib))
 marker="        OWNER=c.CFUNCTYPE(c.c_int32,c.c_uint32)";assert text.count(marker)==1;text=text.replace(marker,"        observer.math_log_begin.argtypes=[c.c_char_p];observer.math_log_begin.restype=c.c_int\n        assert observer.math_log_begin(str(out/'math-calls.bin').encode())==0\n        observer.math_set_frame.argtypes=[c.c_uint32]\n"+marker)
 marker='            current_frame = i+1';assert text.count(marker)==1;text=text.replace(marker,marker+'\n            observer.math_set_frame(current_frame)')
 marker='        observer.finish_observe.argtypes=';assert text.count(marker)==1;text=text.replace(marker,"        observer.math_log_end.argtypes=[c.c_char_p];observer.math_log_end.restype=c.c_int\n        assert observer.math_log_end(str(out/'math-capture.json').encode())==0\n"+marker)
 probe=out/'capture_probe.py';probe.write_text(text);run=next(x['command'][:]for x in p['commands']if x['lane']=='candidate');run[1]=str(probe);run[run.index('--output')+1]=str(out/'candidate')
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),baseline_proof=str(proof),baseline_proof_sha256=sha(proof),command=run,whole_game_complete=False,guest_writes_by_recorder=0,game_frames=24000)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-math-live-capture-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(run,stdout=log,stderr=subprocess.STDOUT);state.update(status='capturing_fresh_native_game',child_pid=child.pid);checkpoint();code=child.wait()
  assert code==0,out/'runtime.log';report=json.loads((out/'candidate/report.json').read_text());oldreport=json.loads((base/'candidate/report.json').read_text());capture=json.loads((out/'candidate/math-capture.json').read_text());assert capture['errors']==capture['pending']==0
  assert capture['entered']==capture['completed']==138014
  # Full recorded frame rows include game fields, CPU PC, video/RAM hashes,
  # device PCs and active actor snapshots. No state is supplied by this host.
  assert report['frames']==oldreport['frames'],'Observer changed recorded game frames'
  names=['RAM-final.bin','GPU-final.bin','state-final.bin','video-final.xrgb8888','frontend-PCM.s16le'];same={name:sha(out/'candidate'/name)==sha(base/'candidate'/name)for name in names};assert all(same.values()),same
  calls=out/'candidate/math-calls.bin';assert calls.stat().st_size==capture['completed']*188
  state.update(status='terminal_actual_native_math_calls_captured_unchanged_game',capture=capture,all24000recorded_frame_rows_equal=True,baseline_files_equal=same,records=str(calls),records_sha256=sha(calls),record_bytes=188,source_sha256={str(path):sha(path)for path in [source,lib,probe,Path(__file__)]},scope='Read-only native observer captures full entry/return CPU and scalar args for138014actual arithmetic calls. Fresh24000frame candidate exactly reproduces previous candidate frame rows/finalRAM/GPU/machine/video/silentPCM. Offline original-function replay is a separate next gate, not yet proved.')
  checkpoint();save(ROOT/'verification/native-math-live-capture-current.json',state);print(json.dumps({k:state[k]for k in ['status','records','capture','all24000recorded_frame_rows_equal']}),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise
if __name__=='__main__':main()
