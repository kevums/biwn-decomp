"""Short fresh control: retired operand sampling must remove false alarms without changing game state."""
import json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,save,sha
from gpu_family_observer_source_v1 import render as old_render
from gpu_family_observer_source_v2 import render
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 qualified=read(V/'GPU-family-live-observer-current.json');assert qualified['completed']==1490 and str(ROOT/'scripts/gpu_family_observer_source_v2.py')in qualified['source_sha256']
 baseline=read(V/'GPU-family-live-oracle-diagnostic-current.json');assert baseline['exit_code']==0 and baseline['first_error']['captured']==1;baseline_dir=Path(baseline['directory'])
 parent=read(V/'native-gpu-command-family-v1-quiescent-control-current.json');prior=Path(parent['directory']);build=read(V/'native-gpu-command-family-disc-build-current.json');out=V/'GPU-family-retired-oracle-live'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 old,_=old_render(build);new,_=render(build);source=(prior/'frame-acquire-observer.c').read_text();assert source.count(old)==1;source=source.replace(old,new);cpp=out/'observer.c';cpp.write_text(source);lib=out/'observer.dylib';compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),str(prior/'direction-shadow-model.c'),'-o',str(lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
 text=(prior/'probe.py').read_text().replace(str(prior/'libframe-acquire-observer.dylib'),str(lib));marker='        observer.mb_set_gpu_reader.argtypes=[c.c_void_p];observer.mb_set_gpu_reader(c.cast(core.GPUReadLong,c.c_void_p))';assert text.count(marker)==1;text=text.replace(marker,marker+'\n        observer.mb_set_next_retired.argtypes=[c.c_void_p];observer.mb_set_next_retired(c.cast(retired,c.c_void_p))\n        core.BIWNSetCPURetiredObserver.argtypes=[c.c_void_p];core.BIWNSetCPURetiredObserver(c.cast(observer.mb_retired,c.c_void_p))');probe=out/'probe.py';probe.write_text(text);command=parent['command'][:];command[command.index(str(prior/'probe.py'))]=str(probe);command[command.index('--frames')+1]='1200';command[command.index('--output')+1]=str(out/'run')
 state=dict(status='running_actual_GPU_retired_oracle_control',pid=os.getpid(),directory=str(out),command=command,baseline=str(baseline_dir),guest_code_or_core_changed=False,flag_predicates_weakened=False,new_predictions=0,new_training=False)
 def mark():save(out/'protocol.json',state);save(V/'GPU-family-retired-oracle-live-current.json',state)
 mark()
 with(out/'run.log').open('w')as log:
  child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
 state['exit_code']=code;mark();assert code==0
 actual=read(out/'run/gameplay-observation.json');before=read(baseline_dir/'run/gameplay-observation.json');report=read(out/'run/report.json');reference=read(baseline_dir/'run/report.json');same_frames=report['frames']==reference['frames'];same_audio=sha(out/'run/frontend-PCM.s16le')==sha(baseline_dir/'run/frontend-PCM.s16le');assert len(report['frames'])==1200 and same_frames and same_audio
 assert before['mb_errors']>0 and actual['mb_errors']==actual['mb_context_errors']==actual['mb_stack_outside']==0 and actual['mb_stale_previews']>0 and actual['mb_entries']==before['mb_entries']==actual['mb_returns'];assert actual['mb_pending']==0
 paths=[Path(__file__),ROOT/'scripts/gpu_family_observer_source_v2.py',ROOT/'scripts/native_gpu_family_observer_v2.inc.c',cpp,lib,probe,out/'run/report.json',out/'run/gameplay-observation.json',out/'run/frontend-PCM.s16le',baseline_dir/'run/report.json',baseline_dir/'run/gameplay-observation.json',baseline_dir/'run/frontend-PCM.s16le']
 state.update(status='terminal_actual_GPU_retired_capture_removes_false_alarms_same_1200_frames_and_PCM',frames=1200,all_frame_fields_equal=True,PCM_equal=True,prior_false_errors=before['mb_errors'],current_errors=actual['mb_errors'],stale_previews=actual['mb_stale_previews'],mailbox_entries=actual['mb_entries'],source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Original control program/core unchanged. GPU synchronizes inside actual CPU operand read,after pre-read peek. Original CMPI captured at immediate retirement before furtherGPUadvance;nativeMOVEA captures actualA0. All exact flag checks retained. Full route must be repeated with this qualified observation timing.');mark();print({k:state[k]for k in['status','prior_false_errors','current_errors','stale_previews','mailbox_entries']})
if __name__=='__main__':main()
