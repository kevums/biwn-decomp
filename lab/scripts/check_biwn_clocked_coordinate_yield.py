"""Run a task-owned request through actual clocked source game execution.

The request is issued at the native caller's real DF60/18FAA boundary.
Attach/poll never substitutes guest CPU/RAM or runs helpers twice. Existing
instruction-compatible source CPU/GPU/IRQ and device/HLE services continue.
This verifies the request backend, not installation of the whole logical
coordinate engine or an emulator-free/standalone game.
"""
from datetime import datetime,timezone
import json,os,shutil,subprocess
from pathlib import Path
from check_biwn_natural_coordinate_scheduler import ROOT,sha,save,DTYPE
import numpy as np

MONITOR=r'''
static struct biwn_coordinate_yield coordinate_ticket;
static struct biwn_coordinate_request coordinate_request;
static uint64_t coordinate_start,coordinate_polls,coordinate_IRQs;
static uint32_t coordinate_owner,coordinate_owners[64],coordinate_owner_count;
static uint32_t coordinate_body_owners[64],coordinate_body_count;
static unsigned coordinate_active,coordinate_finished;
static int coordinate_add_owner(uint32_t *owners,uint32_t *count,uint32_t owner)
{
    uint32_t i;for(i=0;i<*count;i++)if(owners[i]==owner)return 0;
    if(*count>=64)return 1;owners[(*count)++]=owner;return 0;
}
static int coordinate_monitor(const struct biwn_task_cpu *s)
{
    struct biwn_coordinate_completion reply={0},sentinel={0};
    uint32_t target,owner;uint64_t index=S.calls-1;char path[4096];
    const char *directory;FILE *f;unsigned i;int status,length,failed;
    if(coordinate_finished)return 0;
    if(!coordinate_active){
        if(s->pc!=0xdf60u)return 0;
        if(rd32(NULL,s->registers[15],&target))return 1;
        if(target!=0x18faau)return 0;
        coordinate_request.context=1;coordinate_request.sequence=1;
        coordinate_request.kind=BIWN_COORDINATE_CALL;coordinate_request.address=0xdf60u;
        coordinate_request.incoming_d0=s->registers[0];
        if(biwn_coordinate_yield_attach(&bus,&coordinate_ticket,&coordinate_request,s)!=BIWN_COORDINATE_YIELD_PENDING)return 1;
        coordinate_owner=coordinate_ticket.owner;coordinate_start=index;coordinate_active=1;
    }
    if(rd32(NULL,0xc0920u,&owner))return 1;
    if(coordinate_add_owner(coordinate_owners,&coordinate_owner_count,owner))return 1;
    if(owner!=coordinate_owner && !(s->sr&0x2000u) &&
       !(s->pc>=0xde08u&&s->pc<0xde5cu) && !(s->pc>=0xdf60u&&s->pc<0xdf6cu))
        if(coordinate_add_owner(coordinate_body_owners,&coordinate_body_count,owner))return 1;
    if(s->pc==0xe7d4u)coordinate_IRQs++;
    status=biwn_coordinate_yield_poll(&bus,&coordinate_ticket,s,&reply);
    coordinate_polls++;
    if(status==BIWN_COORDINATE_YIELD_PENDING)return 0;
    if(status!=BIWN_COORDINATE_YIELD_COMPLETE)return 1;
    if(reply.context!=1||reply.sequence!=1||reply.value!=s->registers[0]||reply.status)return 1;
    sentinel.context=99;sentinel.sequence=98;sentinel.value=97;sentinel.status=-96;
    if(biwn_coordinate_yield_poll(&bus,&coordinate_ticket,s,&sentinel)!=BIWN_COORDINATE_YIELD_CONSUMED||
       sentinel.context!=99||sentinel.sequence!=98||sentinel.value!=97||sentinel.status!=-96)return 1;
    directory=getenv("BIWN_CLOCKED_YIELD_DIR");if(!directory)return 1;
    length=snprintf(path,sizeof(path),"%s/live-request.json",directory);
    if(length<0||(size_t)length>=sizeof(path))return 1;
    f=fopen(path,"w");if(!f)return 1;
    failed=fprintf(f,"{\"first\":%llu,\"last\":%llu,\"polls\":%llu,\"IRQs\":%llu,\"owner\":%u,\"return_PC\":%u,\"return_SP\":%u,\"D0\":%u,\"completion_count\":1,\"duplicate_poll_consumed\":true,\"contexts\":[",
        (unsigned long long)coordinate_start,(unsigned long long)index,
        (unsigned long long)coordinate_polls,(unsigned long long)coordinate_IRQs,
        owner,s->pc,s->registers[15],reply.value)<0;
    for(i=0;i<coordinate_owner_count;i++)if(fprintf(f,"%s%u",i?",":"",coordinate_owners[i])<0)failed=1;
    if(fprintf(f,"],\"other_executed_user_body_contexts\":[")<0)failed=1;
    for(i=0;i<coordinate_body_count;i++)if(fprintf(f,"%s%u",i?",":"",coordinate_body_owners[i])<0)failed=1;
    if(fprintf(f,"]}\n")<0)failed=1;
    if(fclose(f))failed=1;if(failed)return 1;
    coordinate_active=0;coordinate_finished=1;return 0;
}
'''

def ownership_summary(folder):
 report=json.loads((Path(folder)/'C/report.json').read_text())
 gpu=json.loads(Path(report['regular_GPU_report']).read_text())
 dsp=json.loads(Path(report['DSP_report']).read_text())
 irq=json.loads(Path(report['CPU_IRQ_report']).read_text())
 assert not report['errors']and report['owned_CPU_instructions']>0
 assert report['original_CPU_instructions']==report['rejected_CPU_instructions']==0
 assert gpu['counts']['Owned']>0 and gpu['counts']['Original']==gpu['counts']['Rejected']==0
 assert irq['core']['Owned']>0 and irq['core']['Original']==irq['core']['Rejected']==0
 assert irq['selection']['Owned']>0 and irq['selection']['Original']==irq['selection']['Rejected']==0
 assert dsp['core_counts']=={'Owned':0,'Original':0,'Rejected':0}
 return dict(owned_CPU_instructions=report['owned_CPU_instructions'],original_CPU_instructions=0,rejected_CPU_instructions=0,
             GPU_callbacks=gpu['counts'],GPU_source_instructions=gpu['C_source_instructions'],IRQ_selection=irq['selection'],IRQ_entry=irq['core'],
             DSP_counts=dsp['core_counts'],DSP_inactive_qualified=True,source_checkpoint=report['restored_source_checkpoint'],
             inherited_repair_bytes=report['restored_source_checkpoint']['inherited_repair_bytes'],
             GPU_all_internal_instruction_states_compared=False)

def main():
 out=ROOT/'verification/clocked-coordinate-yield'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 attach_path=ROOT/'verification/coordinate-yield-attach-current.json';attach=json.loads(attach_path.read_text())
 for path,digest in attach['source_sha256'].items():assert sha(path)==digest
 runtime=json.loads((ROOT/'verification/unified-restore-runtime-candidate.json').read_text());base=json.loads(Path(runtime['native_CPU_candidate']).read_text())
 source_path=Path(base['directory'])/'fast_CPU_bridge.c';assert sha(source_path)==base['source_sha256'];source=source_path.read_text()
 marker='int32_t biwn_fast_CPU_owner(uint32_t PC)';assert source.count(marker)==1;source=source.replace(marker,MONITOR+'\n'+marker)
 marker='if(s.pc!=PC)return fail(PC,91);if(state_file)';assert source.count(marker)==1;source=source.replace(marker,'if(s.pc!=PC)return fail(PC,91);if(coordinate_monitor(&s))return fail(PC,180);if(state_file)')
 source='#include "biwn_coordinate_yield_attach.h"\n'+source
 target=out/'clocked_bridge.c';target.write_text(source);shutil.copytree(source_path.parent/'pinned-CPU-headers',out/'pinned-CPU-headers')
 restore=ROOT/'projects/black-ice-white-noise/restoration';command=runtime['commands'][1][:];command[command.index(str(source_path))]=str(target);command[-1]=str(out/'libclocked-yield.dylib')
 command[command.index('-o'):command.index('-o')]=[str(restore/name)for name in ['biwn_coordinate_yield_attach.c','biwn_coordinate_yield.c','biwn_scheduler.c']]
 env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'};compiled=subprocess.run(command,capture_output=True,text=True,env=env);(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
 candidate=out/'candidate.json';save(candidate,dict(base,directory=str(out),library=command[-1],source_sha256=sha(target),scope='Task-owned request monitor; actual existing clocked source scheduler runs, no guest replacement.'))
 natural_path=ROOT/'verification/natural-coordinate-gameplay-current.json';natural=json.loads(natural_path.read_text());confirm=next(row for row in natural['cases']if row['case']=='confirm');assert sha(confirm['source_trace'])==confirm['source_trace_sha256']
 baseline=Path(confirm['source_trace']).parent.parent;protocol=json.loads((baseline/'protocol.json').read_text());run=next(row['command'][:]for row in protocol['commands']if row['phase']=='C')
 run[run.index('--native-CPU-candidate')+1]=str(candidate);run[run.index('--output')+1]=str(out/'C')
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),compile_command=command,command=run,
            native_boundary_request=True,whole_logical_coordinate_engine_in_frames=False,guest_snapshots_installed_by_backend=0,
            standalone_native_game=False,whole_game_complete=False,baseline=str(baseline),baseline_natural_proof=str(natural_path),baseline_natural_proof_sha256=sha(natural_path),
            attach_guards_proof=str(attach_path),attach_guards_proof_sha256=sha(attach_path),attach_source_sha256=attach['source_sha256'],
            runtime_dependencies_sha256={str(path):sha(path)for path in [base['CPU_library'],base['cost_library'],base['original_marker_CPU_library'],runtime['core']]},
            monitor_source_sha256=sha(target),monitor_library_sha256=sha(command[-1]),new_training=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/clocked-coordinate-yield-active.json',state)
 checkpoint()
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(run,stdout=log,stderr=subprocess.STDOUT,env={**env,'BIWN_CLOCKED_YIELD_DIR':str(out)})
   state.update(status='running_clocked_source',child_pid=child.pid);checkpoint();print(out,'PID',child.pid,flush=True);code=child.wait()
  state['exit_code']=code;assert code==0,out/'runtime.log'
  names=['CPU-before-instructions.bin','retired-instruction-costs.bin','warm-RAM.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']
  same={name:sha(out/'C'/name)==sha(baseline/'C'/name)for name in names};assert all(same.values()),same
  original_same={name:sha(out/'C'/name)==sha(baseline/'reference'/name)for name in names};assert all(original_same.values()),original_same
  request=json.loads((out/'live-request.json').read_text());assert request['first']==14189255 and request['last']==14203138
  assert request['polls']==request['last']-request['first']+1 and request['IRQs']==5 and request['return_PC']==0x18faa
  assert len(request['contexts'])==18 and len(request['other_executed_user_body_contexts'])==17
  trace=np.memmap(out/'C/CPU-before-instructions.bin',mode='r',dtype=DTYPE)
  assert request['D0']==int(trace[request['last']]['registers'][0])and request['return_SP']==int(trace[request['last']]['registers'][15])
  state.update(status='terminal_clocked_task_owned_request_matches',frames=1500,CPU_instructions=len(trace),unchanged_source_run=same,request=request,
               direct_original_reference_files_match=original_same,
               ownership=ownership_summary(out),
               monitored_source_CPU_instructions=request['last']-request['first'],actual_other_source_task_body_contexts=17,actual_source_IRQ_entries=5,
               intermediate_task_CPU_or_RAM_transplants=0,test_supplied_MMIO_results=0,test_supplied_OP_writebacks=0,test_supplied_firmware_ABI_outputs=0,
               code_authorship='Codex coordinator wrote attach backend, runtime wiring and checks; existing instruction-compatible source CPU/GPU/IRQ bodies reused.',
               scope='Native-boundary DF60request attaches to actual original coordinate frame. Actual clocked instruction-compatible source runtime executes scheduler,17other user task bodies, GPU work, firmware and5interrupts before one owner-matched completion. All1500frames reproduce the earlier original-matched CPU/cost/RAM/video/finalmachine/PCM bytes. No intermediate task snapshot or recorded MMIO/OP/firmware outputs are injected by this check. Existing HLE/device/clock/commit services remain; this is the request backend, not installation of the whole high-level logical coordinate caller.',
               remaining_providers=['Existing Object Processor/blitter and hardware device models','Original HLE/CD bootstrap/poll and drive stream services','Clock/queue/ACK-vector/commit/prefetch/cycle charge in current core'],
               logical_flow_prefix_fixture_used=False)
  checkpoint();save(ROOT/'verification/clocked-coordinate-yield-current.json',state)
  print(json.dumps({key:state[key]for key in ['status','directory','monitored_source_CPU_instructions','actual_other_source_task_body_contexts','actual_source_IRQ_entries']}),flush=True)
 except BaseException as error:
  state.update(status='terminal_failed',error=repr(error));checkpoint();raise

if __name__=='__main__':main()
