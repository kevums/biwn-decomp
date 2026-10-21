"""Capture first shared monitor disagreement in a short fresh original-routine control."""
import json,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,save,sha
V=ROOT/'verification'
DIAG=r'''
static unsigned md_captured;
static uint32_t md_pc,md_task,md_kind,md_ack,md_command,md_peek;
static uint64_t md_errors_before,md_errors_after;
static uint16_t md_expected_cmp;
static struct cpu md_incoming,md_current;
static void watch_mailbox_diag(uint32_t pc){
 uint64_t before=mb_errors;watch_mailbox(pc);
 if(mb_errors>before&&!md_captured){
  md_captured=1;md_pc=pc;md_task=rd32(0xc0920u);md_errors_before=before;md_errors_after=mb_errors;read_cpu(&md_current);
  for(unsigned i=0;i<mb_slots;i++)if(mb_calls[i].task==md_task){struct mb_call*call=&mb_calls[i];md_incoming=call->incoming;md_kind=call->kind;md_ack=call->ack;md_command=mb_command[call->kind];md_expected_cmp=mb_cmp_sr(call);break;}
  md_peek=mb_gpu_read?mb_gpu_read(0xf03204u,0):0;
 }
}
static void mb_diag_dump(FILE*file){
 fprintf(file,",\"mb_first_error\":{\"captured\":%u,\"pc\":%u,\"task\":%u,\"kind\":%u,\"ack\":%u,\"command\":%u,\"peek_now\":%u,\"expected_cmp_SR\":%u,\"actual_SR\":%u,\"incoming_SR\":%u,\"errors_before\":%llu,\"errors_after\":%llu,\"incoming_regs\":[",md_captured,md_pc,md_task,md_kind,md_ack,md_command,md_peek,md_expected_cmp,md_current.sr,md_incoming.sr,(unsigned long long)md_errors_before,(unsigned long long)md_errors_after);
 for(unsigned i=0;i<16;i++)fprintf(file,"%s%u",i?",":"",md_incoming.r[i]);fputs("],\"actual_regs\":[",file);for(unsigned i=0;i<16;i++)fprintf(file,"%s%u",i?",":"",md_current.r[i]);fputs("]}",file);
}
'''
def main():
 parent=json.loads((V/'native-gpu-command-family-v1-quiescent-control-current.json').read_text());assert parent['status']=='terminal_native_GPU_command_family_route_pending_review' and not parent['live_monitor_pass']
 prior=Path(parent['directory']);out=V/'GPU-family-live-oracle-diagnostic'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 source=(prior/'frame-acquire-observer.c').read_text();marker='int32_t observe(uint32_t pc) {';assert source.count(marker)==1;source=source.replace(marker,DIAG+'\n'+marker);source=source.replace('watch_pool_arena(pc);watch_mailbox(pc);','watch_pool_arena(pc);watch_mailbox_diag(pc);');assert source.count('mb_dump(file);arena_dump(file);')==1;source=source.replace('mb_dump(file);arena_dump(file);','mb_dump(file);mb_diag_dump(file);arena_dump(file);');cpp=out/'observer.c';cpp.write_text(source);lib=out/'observer.dylib';build=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),str(prior/'direction-shadow-model.c'),'-o',str(lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
 probe=out/'probe.py';probe.write_text((prior/'probe.py').read_text().replace(str(prior/'libframe-acquire-observer.dylib'),str(lib)));command=parent['command'][:];command[1]=str(probe);command[command.index('--frames')+1]='1200';command[command.index('--output')+1]=str(out/'run');state=dict(status='running_short_original_control_oracle_diagnostic',pid=os.getpid(),directory=str(out),command=command,production_checks_changed=False,guest_code_changed=False,new_predictions=0,new_training=False)
 def mark():save(out/'protocol.json',state);save(V/'GPU-family-live-oracle-diagnostic-current.json',state)
 mark()
 with(out/'run.log').open('w')as log:
  child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
 state.update(status='terminal_short_original_control_oracle_diagnostic',exit_code=code)
 if(out/'run/gameplay-observation.json').exists():state['first_error']=json.loads((out/'run/gameplay-observation.json').read_text())['mb_first_error']
 mark();print(json.dumps(state.get('first_error',state)))
if __name__=='__main__':main()
