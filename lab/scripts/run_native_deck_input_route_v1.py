"""Fresh repaired-disc input candidate/control with retained read-only monitors."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
import task_arena_observer_source_v2 as regions

V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())

def observer_source(build,parent):
 source=ROOT/'verification/native-Deck-coordinate-v2-route/20261019T182433.767570Z-candidate-1851/frame-acquire-observer.c'
 text=source.read_text();old=regions.checker(parent);assert old in text
 checker=regions.checker(build)
 anchor='  if(!used[i]&&memcmp'
 assert anchor in checker
 checker=checker.replace(anchor,'''  for(unsigned j=0;j<3;j++){uint32_t f=p+(uint32_t[]){128,256,704}[j];if(memcmp(memory+f,expected+f-'''+str(build['resident_address'])+'''u,16))errors++;}
'''+anchor)
 text=text.replace(old,checker)
 text=text.replace(str(parent['heap_start'])+'u',str(build['heap_start'])+'u')
 assert text.count('int32_t observe(uint32_t pc) {')==1
 text=text.replace('int32_t observe(uint32_t pc) {','int32_t retained_observe(uint32_t pc) {')
 syms=build['input_symbols'];start=build['input_code_address'];end=start+build['input_code_bytes'];arena=build['deck_arena_address']
 extra=r'''
static uint64_t input_public,input_native,input_returns,input_old,input_fallback,input_errors,input_helpers,input_helper_returns,input_C_observations,input_C_outside;
static uint32_t input_low=704;
static unsigned input_pending[101];static struct cpu input_incoming[101];
static unsigned input_any_pending(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=input_pending[i];return n;}
static void input_watch(uint32_t pc){
 if(pc==0x11b4cu)input_public++;
 if(pc>0x11b4cu&&pc<0x11d1au)input_old++;
 if(pc<INPUT_START||pc>=INPUT_END){
  if(pc!=0xe4c0u&&pc!=0x10c6eu&&pc!=0x10e72u&&pc!=0x10cb6u&&pc!=0x1102au)return;
 }
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==INPUT_ENTRY)input_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=INPUT_ARENA+delta,frame=base+144u;struct cpu current;
 if(pc==INPUT_ENTRY){input_native++;if(input_pending[slot])input_errors++;input_pending[slot]=1;deck_used[slot]=1;read_cpu(&input_incoming[slot]);}
 if(pc==INPUT_FALLBACK)input_fallback++;
 if(!input_pending[slot])return;
 read_cpu(&current);
 if(pc==INPUT_RETURN){
  input_returns++;input_pending[slot]=0;
  if(current.r[2]!=input_incoming[slot].r[2]||current.r[3]!=input_incoming[slot].r[3]||current.r[15]!=input_incoming[slot].r[15]||rd32(frame+100u))input_errors++;
 }
 if(pc==INPUT_HELPER_RETURN){input_helper_returns++;if(current.r[15]!=rd32(frame+88u)+4u)input_errors++;}
 if((pc==0xe4c0u||pc==0x10c6eu||pc==0x10e72u||pc==0x10cb6u||pc==0x1102au)&&current.r[15]==rd32(frame+88u)&&rd32(current.r[15])==INPUT_HELPER_RETURN)input_helpers++;
 if(pc>=INPUT_C_START&&pc<INPUT_END){input_C_observations++;if(current.r[15]<base+272u||current.r[15]>base+704u)input_C_outside++;else if(current.r[15]-base<input_low)input_low=current.r[15]-base;}
}
int32_t observe(uint32_t pc){input_watch(pc);return retained_observe(pc);}
int input_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"public_entries\":%llu,\"native_entries\":%llu,\"native_returns\":%llu,\"original_body_steps\":%llu,\"fallback_entries\":%llu,\"errors\":%llu,\"pending\":%u,\"helper_entries\":%llu,\"helper_returns\":%llu,\"C_stack_observations\":%llu,\"C_stack_outside\":%llu,\"C_stack_low_offset\":%u}\n",(unsigned long long)input_public,(unsigned long long)input_native,(unsigned long long)input_returns,(unsigned long long)input_old,(unsigned long long)input_fallback,(unsigned long long)input_errors,input_any_pending(),(unsigned long long)input_helpers,(unsigned long long)input_helper_returns,(unsigned long long)input_C_observations,(unsigned long long)input_C_outside,input_low);
 return fclose(f)!=0;
}
'''
 values=dict(INPUT_START=start,INPUT_END=end,INPUT_ENTRY=syms['biwn_native_deck_input'],INPUT_RETURN=syms['biwn_native_deck_input_return'],INPUT_FALLBACK=syms['biwn_native_input_original_fallback'],INPUT_HELPER_RETURN=syms['biwn_native_input_helper_return'],INPUT_ARENA=arena,INPUT_C_START=syms['r8'])
 for k,v in sorted(values.items(),key=lambda x:-len(x[0])):extra=extra.replace(k,hex(v)+'u')
 return text+extra,source

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--control',action='store_true');args=ap.parse_args()
 bp=V/'native-Deck-input-disc-build-current.json';build=read(bp);assert sha(build['derived_disc'])==build['derived_disc_sha256']
 startup=read(V/'native-Deck-input-startup-heap-current.json');assert startup['startup_cases']==6 and startup['heap_initialize_cases']==192
 capacity=read(V/'native-Deck-input-capacity-current.json');assert capacity['cases']==36
 for proof in [startup,capacity]:
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p
 parent=read(V/'native-Deck-coordinate-disc-build-current.json');old_job=read(V/'native-Deck-asset-repair-gameplay-current.json')
 out=V/'native-Deck-input-route-v1'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+('-control' if args.control else '-candidate'));out.mkdir(parents=True);print(out,flush=True)
 text,old_observer=observer_source(build,parent);cfile=out/'observer.c';cfile.write_text(text);library=out/'observer.dylib'
 direction_source=old_observer.with_name('direction-shadow-model.c');direction_model=out/'direction-shadow-model.c';direction_model.write_bytes(direction_source.read_bytes())
 result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cfile),str(direction_model),'-o',str(library)],capture_output=True,text=True);(out/'observer-compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 disc=Path(build['derived_disc'])
 if args.control:
  disc=out/'same-layout-original-input.cdi';subprocess.run(['/bin/cp','-c',build['derived_disc'],str(disc)],check=True)
  session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);at=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']+0x11b4c-0x4000
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();before=Path(build['derived_stage']).read_bytes()[0x11b4c-0x4000:0x11b52-0x4000]
  with disc.open('r+b')as f:f.seek(at);assert f.read(6)==swap16(before);f.seek(at);f.write(swap16(baseline[0x11b4c:0x11b52]));f.flush();os.fsync(f.fileno())
  save(out/'control-delta.json',dict(address='0x11b4c',declared_bytes=6,before=before.hex(),after=baseline[0x11b4c:0x11b52].hex(),parent_sha256=sha(build['derived_disc']),control_sha256=sha(disc)))
 probe_source=Path(old_job['directory'])/'probe.py';probe_text=probe_source.read_text()
 probe_text,n=re.subn(r"(?m)^        observer=c.CDLL\('[^']+'\)",'        observer=c.CDLL('+repr(str(library))+')',probe_text);assert n==1
 probe_text,n=re.subn(r"observer_payload=c.create_string_buffer\(Path\('[^']+'\).read_bytes\(\)\)",'observer_payload=c.create_string_buffer(Path('+repr(build['component'])+').read_bytes())',probe_text);assert n==1
 anchor="        assert observer.finish_observe(str(out/'gameplay-observation.json').encode())==0";assert probe_text.count(anchor)==1
 probe_text=probe_text.replace(anchor,anchor+"\n        observer.input_dump.argtypes=[c.c_char_p];observer.input_dump.restype=c.c_int\n        assert observer.input_dump(str(out/'input-observation.json').encode())==0")
 probe=out/'probe.py';probe.write_text(probe_text);command=list(old_job['command']);command[2]=str(probe);command[command.index('--disc')+1]=str(disc);command[command.index('--output')+1]=str(out/'candidate')
 pointer=V/('native-Deck-input-'+('control' if args.control else 'candidate')+'-current.json')
 state=dict(status='running_fresh_native_input_route',directory=str(out),pid=os.getpid(),command=command,control=args.control,build=str(bp),build_sha256=sha(bp),source_sha256={str(p):sha(p)for p in[Path(__file__),old_observer,cfile,library,probe_source,probe,direction_source,direction_model,Path(regions.__file__)]},snapshot_restores=0,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,new_training=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(pointer,state)
 mark();child=None
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(command,cwd='/',stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},start_new_session=True);state['child_pid']=child.pid;mark()
   try:code=child.wait(timeout=900)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();raise
  state['child_pid']=None;assert code==0,(out/'runtime.log').read_text()[-4000:]
  report=read(out/'candidate/report.json');observed=read(out/'candidate/gameplay-observation.json');inputs=read(out/'candidate/input-observation.json')
  assert len(report['ordinary_Deck_input_trial']['inputs'])==400
  assert not any(inputs[k]for k in ['errors','pending','C_stack_outside'])
  if not args.control:assert inputs['native_entries']==inputs['native_returns']>0 and inputs['original_body_steps']==inputs['fallback_entries']==0 and inputs['helper_entries']==inputs['helper_returns']>0
  state.update(status='terminal_fresh_input_route_pending_review',frames=len(report['frames']),input_observation=inputs,retained_observation=observed,report=str(out/'candidate/report.json'),report_sha256=sha(out/'candidate/report.json'));mark();print(state['status'],inputs,flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error),child_pid=None if child is None or child.poll()is not None else child.pid);mark();raise

if __name__=='__main__':main()
