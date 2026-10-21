"""Review unedited local clear body after correcting the native harness environment."""
import json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def main():
    state=read(V/'local-scene-clear-worker-v2-current.json');assert state['status']=='terminal_local_clear_workflow_pending_coordinator_review' and state['new_predictions']==3
    run=Path(state['directory']);a,b=state['rounds'];assert a['accepted_host'] and b['accepted_host']
    assert sha(a['candidate'])==sha(b['candidate'])==a['candidate_sha256']==b['candidate_sha256']
    for p,h in state['source_sha256'].items():assert sha(p)==h,p
    for role in ['Author','Repair']:
        host=read(run/role/'host-gate/protocol.json');assert host['completed']==256 and host['host_guards']==14
        assert 'ModuleNotFoundError' in (run/role/'native-check.log').read_text()
    native=read(a['native_gate']);assert native['status']=='terminal_scene17_shared_bridge_original_CPU_fixtures_match' and native['completed']==772
    assert native['maximum_C_stack_bytes']==156 and native['original_clear_instructions_executed']==native['original_rotation_instructions_executed']==0
    assert native['actual_clear_read_counts_match'] and native['ordered_MMIO_matches']
    for p,h in native['source_sha256'].items():assert sha(p)==h,p
    body=Path(a['candidate']).read_text();assert body.count('deck_pop(s)')==1 and '0xCu' in body and 'registers[15]' in body
    baseline=read(V/'scene17-clear-bridge-v1-current.json')
    same=Path(native['payload']).read_bytes()==Path(baseline['payload']).read_bytes()
    assert not same and native['payload_bytes']==46562
    out=V/'local-scene-clear-worker-reviewed-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    shutil.copy2(__file__,out/'reviewer-source.py');save(out/'worker-as-run.json',state);save(out/'native-gate.json',native)
    subprocess.run(['/bin/cp','-cR',str(run),str(out/'raw-model-run')],check=True,capture_output=True)
    subprocess.run(['/bin/cp','-cR',native['directory'],str(out/'native-execution')],check=True,capture_output=True)
    report=ROOT/'reports/Local Clear Scaffolding and Native Execution Review.txt'
    report.write_text('LOCAL CLEAR V2 — one unchanged generated function passes component execution\n\n'
      'The copied 27B 6-bit daily model generated Author code in 19.33 seconds. It passes 256 host comparisons against the original pinned 68000 and Unicorn, including full CPU, both banks, all CCR values, 2 MB RAM, private stack, ordered access, pattern edges and 14 guard checks.\n\n'
      'The first native invocation failed before testing because the saved harness lacked its scripts import path. The workflow unnecessarily requested Repair, which took 17.79 seconds and returned identical code. Both original failures and the advisory response remain preserved. They are harness failures, not semantic code failures.\n\n'
      'Running the exact saved Author harness with the scripts directory in PYTHONPATH completes all 772 native scene cases, including busy reads. Full CPU, non-arena RAM, helper records, MMIO order, task fences and stack checks pass; peak scene C stack is 156 of 208 bytes. Original clear and rotation bodies execute zero instructions on this component path. The generated shared module is 46,562 bytes and differs from the coordinator module. It is not installed in the game image and has no fresh-gameplay, same-console, IRQ or physical-console proof.\n\n'
      'There were three predictions in this second trial and three in the earlier rejected trial. No optimizer updates or trained-model quality gain. The successful prompt explicitly supplied primitive declarations, stack-addressing guidance and a different-instruction example after the earlier failure. Wait, flag and MMIO primitives are coordinator supplied. This is scaffolded development assistance, not untouched decompilation or a training comparison. Author and Repair share weights and produce one unique function.\n\n'
      'The advisory Reviewer saw the original import failures, so its denial of full gate acceptance was appropriate at that time. Its phrase "No execution proof" is too broad because host execution had passed, and it predates the corrected native run. No new advisory prediction was made after correction.\n\n'
      'Exact prompts and responses: '+str(run/'prompts-and-responses.txt')+'\nNative proof: '+a['native_gate']+'\n')
    evidence={str(p):sha(p)for p in out.rglob('*')if p.is_file()};evidence[str(report)]=sha(report)
    review=dict(status='terminal_local_clear_scaffolded_host_and_native_pass_unpromoted',directory=str(run),frozen_directory=str(out),report=str(report),new_predictions=3,optimizer_updates=0,new_training=False,model=state['model']['identifier'],author_seconds=19.33,repair_seconds=17.79,accepted_complete_functions=1,unique_generated_bodies=1,raw_body_sha256=a['candidate_sha256'],host_cases=256,host_guards=14,target_native_cases=772,native_payload=str(native['payload']),native_payload_sha256=native['payload_sha256'],native_payload_bytes=46562,native_payload_byte_identical_to_coordinator=False,maximum_C_stack_bytes=156,model_source_installed=False,fresh_gameplay_verified=False,native_Chat_verified=False,supplied_primitives=True,untouched_benchmark=False,roles_share_weights=True,initial_native_harness_import_failure=True,corrected_environment='PYTHONPATH='+str(ROOT/'scripts'),native_gate=a['native_gate'],raw_worker_result_preserved=True,advisory_review_current_after_native_fix=False,advisory_review_approved=False,transcript=str(run/'prompts-and-responses.txt'),dependencies_sha256=evidence)
    save(out/'review.json',review);atomic(V/'local-scene-clear-worker-reviewed-v2-current.json',review)
    print(review['status'],flush=True)
if __name__=='__main__':main()
