"""Fresh all-three source execution and original comparison, with role audit."""
import argparse,fcntl,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--with-local-review',action='store_true');args=parser.parse_args()
    out=ROOT/'runs/cold-start-launcher'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    template=ROOT/'verification/zero-warm-startup-three-processor-job.json'
    accepted=ROOT/'verification/CPU-GPU-DSP-IRQ-startup600-comparison.json'
    owns_IRQ=False
    if accepted.exists():
        checked=json.loads(accepted.read_text())
        if checked['status']=='CPU_GPU_DSP_frame_comparison_pass'and all(checked['checks'].values())and checked.get('source_IRQ_entry',{}).get('core',{}).get('Owned',0)>0:
            template=ROOT/'verification/CPU-GPU-DSP-IRQ-startup600-job.json';owns_IRQ=True
    saved=json.loads(template.read_text())
    rebuilt=list(saved['command']);rebuilt[rebuilt.index('--output')+1]=str(out/'C')
    core=rebuilt[rebuilt.index('--core')+1]
    reference=[sys.executable,str(ROOT/'scripts/probe_biwn_frame_CPU_owner.py'),'--mode','reference','--warm-frames','0','--frames','600','--core',core,'--capture-audio','--output',str(out/'reference')]
    provider_scope=('IRQentry is portableC; IRQselection/ACK,hostcommit/prefetch/cyclecharge,HLE/devices remain host services.'if owns_IRQ else'OriginalIRQ/HLE/devices remain.')
    record=dict(status='starting',directory=str(out),PID=__import__('os').getpid(),commands=[],new_training=False,verified_job_template=str(template),source_IRQ_entry_requested=owns_IRQ,
                scope='Fresh600frames; all3sourceprocessors fromframe1, no warmup or savedstate. '+provider_scope+' No fullgame/nativeChat claim.')
    def save():
        (out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n')
        (ROOT/'verification/cold-start-easy-workflow-current.json').write_text(json.dumps(record,indent=2)+'\n')
    save();print('Fresh source CPU/GPU/DSP cold-start test:600frames. This can take several minutes.',flush=True)
    if owns_IRQ:print('Portable IRQ entry enabled; device selection/ACK and host state/prefetch/cycle services remain.',flush=True)
    print('Commands/results: '+str(out),flush=True)
    started=time.monotonic()
    try:
        for name,command in [('reference',reference),('C',rebuilt)]:
            record.update(status='running_'+name);record['commands'].append(command);save();print('Running '+name,flush=True)
            with (out/(name+'.log')).open('w')as log:
                result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
        command=[sys.executable,str(ROOT/'scripts/compare_biwn_frame_CPU_only.py'),'--C-run',str(out/'C'),'--reference',str(out/'reference'),'--expected-frames','600','--output',str(out/'report.json')]
        record.update(status='comparing');record['commands'].append(command);save();subprocess.run(command,check=True)
        proof=json.loads((out/'report.json').read_text());assert all(proof['checks'].values())
        record.update(status='comparison_pass',test_seconds=time.monotonic()-started,comparison=str(out/'report.json'));save()
        print('Passed:600freshframes; sourceCPU/GPU/DSP, zero interpreter fallbacks; original state/video/PCM comparison.',flush=True)
        if proof.get('source_IRQ_entry'):print('Portable IRQ entries: '+str(proof['source_IRQ_entry']['core']['Owned'])+'; original-entry fallback/rejections:0.',flush=True)
        if args.with_local_review:
            sys.path.insert(0,str(ROOT));import lab
            from run_local_portal_author_test import ensure_game_model
            ensure_game_model()
            evidence={key:proof[key]for key in ['status','frames','owned_CPU_instructions','GPU_counts','DSP_counts','checks','remaining_providers']}
            if proof.get('source_IRQ_entry'):evidence['source_IRQ_entry']=proof['source_IRQ_entry']
            evidence.update(source_frames=dict(first=1,last=600,all_frames_inclusive=True),no_original_warmup=True,no_saved_starting_state=True,PCM='Silent startup; not audible music quality verification.',test_executor='Launcher ran both tests and deterministic comparison. Local roles read its saved proof.')
            roles=[]
            with (ROOT/'runs/.inference.lock').open('w')as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                for role in ['Explainer','Scope Reviewer']:
                    task='Act as '+role+'. In under90words explain this supplied cold-start result. State all3sourceprocessors coverframes1through600, no original warmup or savedstate. '+provider_scope+' Silent PCM equivalence does not establish audible music quality. The launcher executed the test, you explain its report. No fullgame or nativeChat claim.'
                    payload=dict(task=task,evidence=evidence)
                    if roles:payload['prior_response']=roles[-1]['response']['text'];payload['task']+=' Confirm accurate scope or correct actual overstatements; do not invent an error.'
                    response=lab.generate('game',lab.COMMON,json.dumps(payload),400);roles.append(dict(role=role,response=response));print(role+': '+response['text'],flush=True)
                    (out/'local-roles.json').write_text(json.dumps(roles,indent=2)+'\n')
                    with (out/'prompts-and-responses.txt').open('a')as f:f.write(role+'\nREQUEST\n'+json.dumps(response['request'],indent=2)+'\nRESPONSE\n'+response['text']+'\n\n')
            record.update(local_roles=[dict(role=x['role'],seconds=x['response']['seconds'])for x in roles],same_weights_correlated=True,semantic_role_review='pending coordinator check')
        record.update(status='completed_comparison_pass',total_seconds=time.monotonic()-started);save()
        print('Report: '+str(out/'report.json'),flush=True)
    except BaseException as error:
        record.update(status='terminal_failed',error=repr(error));save();raise


if __name__=='__main__':main()
